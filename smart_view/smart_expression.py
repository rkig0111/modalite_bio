#
# This file is part of the BIOM_AID distribution (https://bitbucket.org/kig13/dem/).
# Copyright (c) 2020-2021 Brice Nord, Romuald Kliglich, Alexandre Jaborska, Philomène Mazand.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# -*- coding: utf-8 -*-
import ast
import re
from _ast import Constant, Name, Call
from copy import deepcopy
from functools import partial
from logging import warning
from types import CodeType
from typing import Any, Optional, cast

import pandas as pd
from django.db.models import (
    Expression,
    F,
    Value,
    TextField,
    FloatField,
    IntegerField,
    CharField,
)
from django.db.models.functions import Concat, Extract, Now, Cast, LPad
from django.utils.timezone import now
from django.utils.translation import gettext as _

from common import config


def find_magh2_order(data: str) -> str:
    if data is not None:
        return ' '.join(
            [cmd.upper().replace(' ', '') for cmd in re.compile(r"((?:[0-9A-Za-z][0-9A-Za-z])\s?\d\d\d\d\d\d)").findall(data)]
        )
    else:
        return ''


def amount(data: str) -> float:
    """Get a amount (money) as a string (localized or not), an int or a float and return a float,"""
    ret = str(data).replace('\xa0', '')
    if ',' in ret and '.' in ret:
        ret = ret.replace(',', '')
    elif ',' in ret:
        ret = ret.replace(',', '.')
    fret: float = float(ret)
    # print(repr(data), '==>', repr(ret))
    return fret


def python_format(fmt: str, data: str) -> str:
    return fmt.format(data)


def django_format(fmt: Expression, data: Expression) -> Expression:
    if isinstance(fmt, Value):
        d_format = re.compile(r"%0(\d+)d").match(str(fmt.value))
        if d_format:
            return LPad(
                Cast(data, output_field=CharField()),
                int(d_format.groups()[0]),
                fill_text=Value('0'),
            )
    warning(_("Le format {} n'est pas pris en charge par django_format(). Valeur brute renvoyée.").format(fmt))
    return data


def concatenate(*args):
    ret = ''
    for arg in args:
        try:
            if isinstance(arg, str):
                ret += arg
            elif (arg is not None) and (arg is not pd.NA):
                ret += str(arg)
        except TypeError:
            print("Err:", arg)
    return ret


class SmartExpression:

    BUILTINS: dict = {
        'value': {
            '_help': 'litteral value (implicit)',
            '_signature': 'for future use',
            'python': lambda a: a,
            'django': Value,
            'form_helper_js': None,
        },
        'concat': {
            '_signature': 'for future use',
            'python': concatenate,
            'django': lambda a, b: Concat(a, b, output_field=TextField()),
        },
        'f': {
            '_help': 'get field value (implicit)',
            '_signature': 'for future use',
            'python': lambda a: a,
            'django': F,
        },
        'format': {
            'python': python_format,
            'django': django_format,
        },
        'to_amount': {
            'python': amount,
            'django': None,
        },
        'day_age': {
            'python': lambda a: (now() - a).days,
            'django': (
                lambda a: Cast(
                    Cast(Now() - a, output_field=FloatField()) / 86400000000.0,
                    output_field=IntegerField(),
                )
            )
            if 'sqlite3' in config.settings.DATABASES['default']['ENGINE']
            else (lambda a: Extract(Now() - a, 'day')),
        },
        'find_magh2_order': {
            'python': find_magh2_order,
            'django': None,
        },
        'is_in': {
            'python': lambda a, b: a in b,
            'django': None,
            'form_helper_js': lambda a, b: a + '.includes(' + b + ')',
        },
        'residuel': {
            'python': lambda actif, duree, mes: max((1 - (now() - mes).days / (duree * 365.2422)) * actif, 0),
            'django': None,
        },
    }

    PYTHON_VARS: dict = {
        '__builtins__': {},
    }

    DJANGO_VARS: dict = {
        '__builtins__': {},
        'concat': Concat,
    }

    class ExprTransformer(ast.NodeTransformer):
        def __init__(self, columns: list = None, mode='python') -> None:
            super().__init__()
            self._mode = mode
            self._columns = columns or []
            self._dependencies: set = set()

        def visit_Constant(self, node: Constant) -> Any:
            # print(f"  visiting constant {ast.dump(node)}")
            if self._mode == 'django':
                return ast.Call(ast.Name('value', ctx=ast.Load()), [ast.Str(node.value)], [])
            else:
                return self.generic_visit(node)

        def visit_Call(self, node: Call) -> Any:
            # print(f"  visiting call {ast.dump(node)}")
            if isinstance(node.func, ast.Name) and node.func.id in SmartExpression.BUILTINS.keys():
                return ast.Call(node.func, [self.visit(node) for node in node.args], node.keywords)
            else:
                raise SyntaxError(
                    _("Unable to find {} in defined functions: {}").format(
                        "'" + str(node.func.id) + "'",
                        ', '.join(sorted(SmartExpression.BUILTINS.keys())),
                    )
                )

        def visit_Name(self, node: Name) -> Any:
            if node.id in SmartExpression.BUILTINS.keys():
                return self.generic_visit(node)
            elif self._mode == 'django':
                if node.id == node.id.upper():
                    # The name is uppercase => it's a constant => treat as a Value()
                    return ast.Call(ast.Name('value', ctx=ast.Load()), [node], [], ctx=node.ctx)
                else:
                    self._dependencies.add(node.id)
                    return ast.Call(
                        ast.Name('f', ctx=node.ctx),
                        [ast.Str(node.id, ctx=node.ctx)],
                        [],
                        ctx=node.ctx,
                    )
            elif node.id in self._columns:
                self._dependencies.add(node.id)
                if self._mode == 'form_helper_js':
                    return ast.Subscript(
                        ast.Name('args', ctx=ast.Load()), ast.Constant(value=self._columns.index(node.id)), ctx=ast.Load()
                    )
                else:
                    return self.generic_visit(node)
            else:
                raise SyntaxError(
                    _("'{}' is neither a function nor a valid column. Possibles values are : {}").format(
                        node.id,
                        ', '.join(sorted(list(set(SmartExpression.BUILTINS.keys()) | set(self._columns)))),
                    )
                )

    def __init__(self, expression: str):
        self.tree = ast.parse(expression, mode='eval')
        self.python_code: Optional[CodeType] = None
        self.python_vars: Optional[dict] = None

    def syntax_is_valid(self, field_names: list) -> bool:
        """Check expression syntax (everything is defined)"""
        tree = deepcopy(self.tree)
        expr_transformer = self.ExprTransformer(field_names)
        try:
            expr_transformer.visit(tree)
            return True
        except SyntaxError as se_exp:
            warning(se_exp.msg)
            return False

    def dependencies(self) -> dict:
        ...
        return {}

    def python_eval(self, expr_vars: dict = None) -> Any:
        """
        Safely evaluate the expression as a python expression, using vars (= record fields)
        """
        if self.python_code is None:
            self.python_code = compile(self.tree, '<string>', 'eval')
            self.python_vars = self.PYTHON_VARS.copy()
            self.python_vars.update({n: v['python'] for n, v in self.BUILTINS.items()})
        python_vars = cast(dict, self.python_vars).copy()
        python_vars.update(expr_vars or {})
        return eval(self.python_code, python_vars)

    def as_django_orm(self) -> Expression:
        def f(tree, django_vars, view_attrs):
            # print("view_attrs:", view_attrs)
            all_vars = django_vars.copy()
            all_vars.update({key.upper(): value for key, value in view_attrs.items()})
            # print(ast.dump(tree))
            compiled = compile(tree, '<string>', 'eval')
            return eval(compiled, all_vars)

        tree = deepcopy(self.tree)
        tree = ast.fix_missing_locations(self.ExprTransformer([], mode='django').visit(tree))
        django_vars = self.DJANGO_VARS.copy()
        django_vars.update({n: v['django'] for n, v in self.BUILTINS.items()})
        return partial(f, tree, django_vars)

    def as_javascript_function(self, columns: list[str]) -> str:
        tree = deepcopy(self.tree)
        tree = ast.fix_missing_locations(self.ExprTransformer(columns, mode='form_helper_js').visit(tree))
        return f"return {ast.unparse(tree)};"
