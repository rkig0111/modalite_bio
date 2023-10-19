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
from __future__ import annotations

import ast
import copy
import datetime
import logging
from functools import reduce
from itertools import accumulate
from typing import Any, Optional

from django.apps import apps
from django.db.models import Value, F, CharField, ExpressionWrapper
from django.db.models.functions import Coalesce, Cast, Concat
from django.forms import MediaDefiningClass, NullBooleanSelect
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.forms import forms
from django.forms.widgets import (
    DateInput,
    Input,
    Textarea,
    CheckboxInput,
    Select,
)

# from document.forms import DocumentsSmartFormat
from smart_view.smart_expression import SmartExpression
from smart_view.smart_form import AutocompleteInputWidget, MultiChoiceInputWidget

logger = logging.getLogger(__name__)

sv_app_config = apps.get_app_config('smart_view')


class SmartFormat(metaclass=MediaDefiningClass):
    def __init__(self, field=None):
        self.field = field

    def get(self, prop_name, context=None, default=None):
        return self.field.get(prop_name, context=context, default=default)

    def get_definition(self, target=None, view_params: dict = None):
        return {}

    def get_form_helper_rules(self, form_prefix):
        """The 'format' dependant part of form helper rules"""
        return {}

    def get_widget(self, context=None, default=None, **kwargs):
        return default

    def api_handle(self, path: list[str], view_params: dict):
        return JsonResponse(
            {
                'error': 2,
                'message': _("No API defined for this SmartField : {smartfield_name}").format(smartfield_name=repr(self)),
            }
        )

    def __del__(self):
        # To avoid circular reference
        self.field = None


class StringSmartFormat(SmartFormat):
    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        # Well...  In a table, it seems this is always better to use a textarea formatter/editor...
        # settings["formatter"] = self.get('formatter', context=target, default="'plaintext'")
        # settings["editor"] = "'" + self.get("editor", context=target, default="input") + "'"
        settings["formatter"] = self.get('formatter', context=target, default="'textarea'")
        settings["editor"] = "'" + self.get("editor", context=target, default="textarea") + "'"
        return settings

    def get_widget(self, context=None, default=None, **kwargs):
        return Input()


class TextSmartFormat(SmartFormat):
    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["formatter"] = self.get('formatter', context=target, default="'textarea'")
        settings["editor"] = "'" + self.get("editor", context=target, default="textarea") + "'"
        return settings

    def get_widget(self, context=None, default=None, **kwargs):
        return Textarea()


class ConditionalTextSmartFormat(TextSmartFormat):
    class Media(forms.Media):
        js = (
            "smart_view/js/tabulator.min.js",
            "smart_view/js/smart-view-text.js",
        )

    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings['mutator'] = "'json'"
        settings['mutator_params'] = {}
        settings["editor"] = "'textConditionalEditor'"
        if 'editor_params' not in settings:
            settings['editor_params'] = {}
        settings['editor_params']['edited_fieldname'] = self.get('fields', default=(None,))[0]
        settings["formatter"] = "'text_conditional'"
        return settings


class BooleanSmartFormat(SmartFormat):
    class Media(forms.Media):
        # js = ("smart_view/js/tabulator-column-boolean.js",)
        pass

    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings['hoz_align'] = 'center'
        settings['formatter'] = 'checkbox'  # Attention : 'formatter' sans "'" => méthode de la classe JS SmartView !
        settings['editor'] = 'null'
        settings['editor_params'] = {'tristate': self.get('tristate', context=target, default=True)}
        return settings

    def get_widget(self, context=None, default=None, **kwargs):
        # En théorie, cette fonction n'est pas nécessaire, car Django gère le tristate nativement
        # Mais depuis Django 3.1, NullBooleanField est remplacé par BooleanField(null=True) dans django.forms
        # et django.forms n'a pas encore été adapté et ne "voit" donc pas que le champ est tristate...
        # Donc, ici, on indique 'manuellement' à django.forms quel widget utiliser.
        if self.get('tristate'):
            return NullBooleanSelect()
        else:
            return CheckboxInput()


class SmartDateInput(DateInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format_value(self, value: Any) -> Optional[str]:
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        elif isinstance(value, datetime.date):
            return value.isoformat()
        return str(value)


class DateSmartFormat(SmartFormat):
    class Media:
        js = (
            "smart_view/js/luxon.min.js",
            "smart_view/js/smart-table-datetime.js",
        )

    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["formatter"] = "'datetime'"
        # TODO : Better converter from C style to Tabulator style
        datetime_format = reduce(
            lambda f, c: f.replace(c[0], c[1]),
            (
                ('%d', 'dd'),
                ('%m', 'MM'),
                ('%y', 'yy'),
                ('%Y', 'yyyy'),
                (
                    '%Q',
                    'q',
                ),  # Celui-ci n'est pas standard... N° du trimestre (1er, 2e...)
            ),
            self.get("datetime_format", default="%d/%m/%Y"),
        )
        settings["formatter_params"] = {
            'inputFormat': 'iso',
            "outputFormat": datetime_format,
            'invalidPlaceholder': None,
            # 'timezone': timezone.get_current_timezone_name(),
        }
        settings["hoz_align"] = self.get("hoz_align", default="center")
        # TODO: A real date editor (cf. tabulator example)
        settings["editor"] = "'" + self.get("editor", context=target, default="date") + "'"
        return settings

    def get_widget(self, context=None, default=None, **kwargs):
        return SmartDateInput(attrs={'type': 'date'})


class DatetimeSmartFormat(SmartFormat):
    class Media:
        js = (
            "smart_view/js/luxon.min.js",
            "smart_view/js/smart-table-datetime.js",
        )

    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["formatter"] = "'datetime'"
        # TODO : Better converter from C style to Tabulator style
        datetime_format = reduce(
            lambda f, c: f.replace(c[0], c[1]),
            (
                ('%d', 'dd'),
                ('%m', 'MM'),
                ('%y', 'yy'),
                ('%Y', 'yyyy'),
                ('%H', 'hh'),
                ('%M', 'mm'),
                ('%S', 'ss'),
                (
                    '%Q',
                    'q',
                ),  # Celui-ci n'est pas standard... N° du trimestre (1er, 2e...)
            ),
            self.get("datetime_format", default="%d/%m/%Y %H:%M:%S"),
        )
        settings["formatter_params"] = {
            'inputFormat': 'iso',
            "outputFormat": datetime_format,
            'invalidPlaceholder': "(date/heure invalide)",
            # 'timezone': timezone.get_current_timezone_name(),
        }
        settings["hoz_align"] = self.get("hoz_align", default="center")
        # TODO: A real date editor (cf. tabulator example)
        settings["editor"] = "'" + self.get("editor", context=target, default="datetimeEditor") + "'"
        return settings


class IntegerSmartFormat(SmartFormat):
    class Media(forms.Media):
        js = (
            "smart_view/js/tabulator.min.js",
            "smart_view/js/smart-view-integer.js",
        )

    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["hoz_align"] = self.get("hoz_align", default="right")
        settings["editor"] = "'input'"
        settings['sorter'] = "'integerSorter'"
        settings['sorter_params'] = {}
        return settings


class ConditionalIntegerSmartFormat(IntegerSmartFormat):
    class Media(forms.Media):
        js = (
            "smart_view/js/tabulator.min.js",
            "smart_view/js/smart-view-integer.js",
        )

    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings['mutator'] = "'json'"
        settings['mutator_params'] = {}
        settings["editor"] = "'integerConditionalEditor'"
        if 'editor_params' not in settings:
            settings['editor_params'] = {}
        settings['editor_params']['edited_fieldname'] = self.get('fields', default=(None,))[0]
        settings["formatter"] = "'integer_conditional'"
        settings['sorter'] = "'conditionalIntegerSorter'"
        settings['sorter_params'] = {}
        return settings


class ChoiceSmartFormat(SmartFormat):
    class Media(forms.Media):
        js = (
            "smart_view/js/tabulator.min.js",
            "smart_view/js/smart-view-choice.js",
        )

    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["hoz_align"] = self.get("hoz_align", default="center")

        choices = self.get("choices")

        if callable(choices):
            choices = dict(choices(view_params))
        if self.get("null") or not self.get('no_default') is True:
            choices[None] = _("-- Indéfini --")
        editor = self.get("editor", context=target, default='autocomplete')
        if editor == 'autocomplete':
            editor_str = 'list'
        else:
            raise RuntimeError(_("SmartFormat editor for should be 'autocomplete' or ..., not '{}'").format(editor))
        settings["editor"] = "'" + editor_str + "'"
        settings["editor_params"] = {"values": choices, 'autocomplete': True}

        settings["formatter"] = "'lookup'"
        lookup = self.get('lookup', default=choices)
        if callable(lookup):
            lookup = dict(lookup(view_params))
        settings["formatter_params"] = lookup

        return settings

    def get_widget(self, context=None, default=None, **kwargs):
        if self.get('autocomplete', context):
            return AutocompleteInputWidget(smart_field=self.field)
        else:
            return Select()

    def api_handle(self, path: list[str], view_params: dict):
        if path[0] == 'get_flexdatalist_choices':
            # print(request.GET['keyword'])
            choices = self.get("choices")
            if callable(choices):
                choices = dict(
                    choices(
                        dict(
                            view_params,
                            **{
                                'keyword': view_params['request_get'].get('keyword', ['']),
                                'load': view_params['request_get'].get('load', ['']),
                            },
                        )
                    )
                )
            # print("  =>", choices)

            return JsonResponse(
                {
                    'results': [{'value': value, 'label': label} for value, label in choices.items()],
                    'options': {},
                }
            )
        else:
            return JsonResponse(
                {
                    'error': 3,
                    'message': _("Unkown API function : {funcname}").format(funcname=path[0]),
                }
            )


class ConditionalChoiceSmartFormat(ChoiceSmartFormat):
    class Media(forms.Media):
        js = (
            "smart_view/js/tabulator.min.js",
            "smart_view/js/smart-view-choice.js",
        )

    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings['mutator'] = "'json'"
        settings['mutator_params'] = {}
        settings["editor"] = "'choiceConditionalEditor'"
        if 'editor_params' not in settings:
            settings['editor_params'] = {}
        settings['editor_params']['edited_fieldname'] = self.get('fields', default=(None,))[0]
        settings["formatter"] = "'choice_conditional'"
        return settings


class MoneySmartFormat(SmartFormat):
    class Media(forms.Media):
        js = (
            "smart_view/js/tabulator.min.js",
            "smart_view/js/smart-view-money.js",
        )

    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["hoz_align"] = self.get("hoz_align", default="right")
        settings["formatter"] = "'money_ext'"
        settings["formatter_params"] = {
            "decimal": self.get("decimal_symbol"),
            "thousand": self.get("thousands_separator"),
            "symbol": self.get("currency_symbol"),
            "symbolAfter": self.get("symbol_is_after"),
            "precision": self.get("precision"),
        }
        settings['sorter'] = "'moneySorter'"
        settings['sorter_params'] = {}
        settings["editor"] = "'input'"
        return settings

    def get_form_helper_rules(self, form_prefix):
        rules = copy.copy(super().get_form_helper_rules(form_prefix))
        rules['field-' + self.field.get('fieldname') + '-money-format'] = {
            'input_selectors': ['#id_' + form_prefix + '-' + self.field.get('fieldname')],
            'func': 'money-format',
        }
        return rules

    def get_widget(self, context=None, default=None, **kwargs):
        return Input()


class ConditionnalMoneySmartFormat(MoneySmartFormat):
    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["editor"] = "'moneyConditionnalEditor'"
        if 'editor_params' not in settings:
            settings['editor_params'] = {}
        settings['editor_params']['edited_fieldname'] = self.get('fields', default=(None,))[0]
        settings['formatter'] = "'money_conditional'"
        settings['sorter'] = "'moneyConditionalSorter'"
        settings['sorter_params'] = {}
        settings['mutator'] = "'json'"
        settings['mutator_params'] = {}
        settings['footer_data_formatter'] = "'money'"
        settings['footer_data_formatter_params'] = settings.get('formatter_params', {})
        return settings


class CoalesceChoiceSmartFormat(ChoiceSmartFormat):
    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings['formatter'] = "'coalesce'"
        settings['formatter_params'] = {'fields': self.get('fields', target), 'lookup': settings['formatter_params']}
        return settings


class CoalesceMoneySmartFormat(MoneySmartFormat):
    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["editor"] = "'moneyCoalesceEditor'"
        if 'editor_params' not in settings:
            settings['editor_params'] = {}
        settings['editor_params']['edited_fieldname'] = self.get('coalesce', default=(None,))[0]
        settings["formatter"] = "'money_ext_coalesce'"
        return settings


class HtmlSmartFormat(SmartFormat):
    def get_definition(self, target: str = None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["formatter"] = "'html'"
        settings["css_class"] = "smart-view-html-cell"
        return settings


class AnalysisSmartFormat(SmartFormat):
    class Media:
        js = ("smart_view/js/smart-view-analysis.js",)
        css = {
            'all': ('smart_view/css/analysis.css',),
        }

    def get_definition(self, target: str = None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["formatter"] = "'analysis'"
        return settings


class MultiChoiceSmartFormat(SmartFormat):
    class Media:
        js = ("smart_view/js/smart-view-multichoice.js",)

    def get_definition(self, target: str = None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings["formatter"] = "'multichoice'"
        choices = dict(self.get("choices"))
        if callable(choices):
            choices = dict(choices(view_params))
        settings['formatter_params'] = {'lookup': choices}
        return settings

    def get_widget(self, context=None, default=None, **kwargs):
        return MultiChoiceInputWidget(smart_field=self.field)


class SubviewsSmartFormat(SmartFormat):
    def get_definition(self, target=None, view_params: dict = None):
        settings = super().get_definition(target, view_params)
        settings['css_class'] = 'smart-view-vdiv-cell'
        return settings


class ToolsSmartFormat(SmartFormat):
    class Media:
        css = {
            'all': ('smart_view/css/tabulator-column-tools.css',),
        }

    def get_definition(self, target=None, view_params: dict = None):
        if view_params['url_prefix']:
            prefix_list = [view_params['url_prefix']]
        else:
            prefix_list = []
        settings = super().get_definition(target, view_params)
        columns = self.get("columns", target)
        for column in columns:
            column['url'] = reverse(
                column['url_name'],
                args=prefix_list + list(column['url_args'][:-1]) + ['999999999'],
            ).replace('999999999', column['url_args'][-1])
            # assert column['url_args'][-1] == '${id}', _("Last argument for tool definition must be '${id}'")
        settings["columns"] = columns
        return settings


apps.get_app_config('smart_view').register_formats(
    {
        'string': StringSmartFormat,
        'text': TextSmartFormat,
        'conditional_text': ConditionalTextSmartFormat,
        'date': DateSmartFormat,
        'datetime': DatetimeSmartFormat,
        'integer': IntegerSmartFormat,
        'conditional_integer': ConditionalIntegerSmartFormat,
        'choice': ChoiceSmartFormat,
        'coalesce_choice': CoalesceChoiceSmartFormat,
        'conditional_choice': ConditionalChoiceSmartFormat,
        'money': MoneySmartFormat,
        'conditional_money': ConditionnalMoneySmartFormat,
        'boolean': BooleanSmartFormat,
        'multichoice': MultiChoiceSmartFormat,
        'html': HtmlSmartFormat,
        'analysis': AnalysisSmartFormat,
        'subviews': SubviewsSmartFormat,
        'tools': ToolsSmartFormat,
    }
)


class SmartField(metaclass=MediaDefiningClass):
    """
    SmartField 'system' properties :
    - 'format', string, field type (format) see __init__()
    - 'hidden', boolean, self-explanatory
    - 'data' :
        - None => no data (for tools/buttons columns/fields)
        - string => model fieldname
        - QuerySet Expression => to add as computed field in query (via annotate())
        - a callable => called at instanciation then return one of the above ?
    - 'special' :
        - None => nothing
        - 'id' => the field is the "primary key"
        - 'roles' => the field is the "roles field", data must contains comma separated list of role codes (as a string)
        - 'state' => the field is the "state", data must provide the state code
    """

    class Media(forms.Media):
        css = {
            # Empty for now
        }
        # Empty for now

    @property
    def form_media(self):
        return forms.Media(
            {
                'css': {},
                'js': [],
            }
        )

    def __init__(self, format="text", **kwargs):
        if format in sv_app_config.smart_format_registry:
            self.format = sv_app_config.smart_format_registry[format](self)
        else:
            raise ValueError(_("Unknown format for SmartField: {}").format(format))

        # default properties none for now)
        self.properties = {}

        # les champs spéciaux sont cachés par défaut
        if kwargs.get('special') is not None:
            self.properties['hidden'] = True

        self.properties['format'] = format
        self.properties.update(kwargs.copy())

        self.editable = False
        self.smart_format = None

    @property
    def media(self):
        # Add media from SmartFormat instance...
        return forms.Media() + self.format.media

    def get(self, prop_name, context=None, default=None):
        if context is not None:
            if isinstance(context, str):
                keys = reversed(
                    (prop_name,) + tuple(p + "." + prop_name for p in accumulate(context.split("."), lambda a, b: a + "." + b))
                )
                # If prop_name is 'prop' and context like 'c1.c2.c3'
                # keys is now : ('c1.c2.c3.prop', 'c1.c2.prop', 'c1.prop', 'prop')
                # if prop_name == 'title':
                #    print(list(keys), repr(self.properties))
                for key in keys:
                    if key in self.properties:
                        return self.properties[key]
                return default
            else:
                raise RuntimeError(_("context must be a str instance or None, not {}".format(repr(context))))
        else:
            return self.properties.get(prop_name, default)

    def get_annotation(self, request):
        return None

    # def as_column_def(self, context=None, fieldname=None, url_prefix=None, **kwargs):
    def as_column_def(self, context=None, fieldname=None, view_params: dict = None):
        column_settings = {
            "field": fieldname,  # This is the table field (not necessarily identical to model field)
            "title": self.get('title', context),
            "help_text": self.get("help_text", context),
            "hidden": self.get('hidden', context),
            "width": self.get('width', context),
            "min_width": self.get('min_width', context),
            "max_width": self.get('max_width', context),
            "width_grow": self.get('width_grow', context),
            "show_priority": self.get('show_priority', context),
            "header_sort": self.get('header_sort', context),
            'frozen': self.get('frozen', context),
        }
        if self.get("footer_data"):
            column_settings.update({"footer_data": self.get("footer_data")})
            if self.get("footer_data").endswith('_if_ext'):
                column_settings.update(
                    {
                        "footer_data_params": {
                            'data': fieldname,
                            'test': self.get('calc_data_test'),
                            'if_null': self.get('data_if_null'),
                        }
                    }
                )
        column_settings.update(self.format.get_definition(context, view_params))
        if self.get('data_if_null'):
            if 'formatter_params' in column_settings:
                column_settings['formatter_params']['data_if_null'] = self.get('data_if_null')
            else:
                pass
                # print("column with data_if_null but no format")
            # cascade_formatter = column_settings.get('formatter', None)
            # if cascade_formatter is not None:
            #     cascade_formatter = cascade_formatter[1:-1]
            # cascade_formatter_params = column_settings.get('formatter_params', None)
            # column_settings['formatter'] = 'if_null'  # méthode JS et non texte
            # column_settings['formatter_params'] = {
            #     'data_if_null': self.get('data_if_null', context, default=None),
            #     'cascade_formatter': cascade_formatter,
            #     'cascade_formatter_params': cascade_formatter_params,
            # }
        return column_settings

    def update_instance(self, instance, updater, allowed=True):
        logger.error("Not implemented")

    def get_form_helper_rules(self, request, form_prefix=''):
        rules = copy.copy(self.format.get_form_helper_rules(form_prefix))
        # Règle "champs obligatoire" ?
        data = self.get('data', 'form.html')
        if isinstance(data, str):
            # print("  Field:", data, self.get('null'), self.get('db_default'))
            if not self.get('blank', 'form.html'):
                # print(self.get('format'))
                if self.get('format', 'form.html') == 'choice' and self.get('autocomplete', 'form.html'):
                    rules['field-' + self.get('fieldname', 'form.html') + '-mandatory'] = {
                        'input_selectors': ['#id_' + form_prefix + '-' + data],
                        'func': 'mandatory-field',
                        'suffix': '-flexdatalist',
                    }
                else:
                    rules['field-' + self.get('fieldname') + '-mandatory'] = {
                        'input_selectors': ['#id_' + form_prefix + '-' + data],
                        'func': 'mandatory-field',
                        'suffix': '',
                    }

        # champs "affichage conditionnel"
        show_if = self.get('show-if', 'form.html')
        if show_if:
            if show_if.isidentifier():
                rules['field-' + self.get('fieldname', 'form.html') + '-show-if'] = {
                    'input_selectors': ['#id_' + form_prefix + '-' + show_if],
                    'func': 'show-if',
                    'targets': [
                        '#id_' + form_prefix + '-' + self.get('fieldname', 'form.html'),
                        '#label-id_' + form_prefix + '-' + self.get('fieldname', 'form.html') + '-container',
                    ],
                }
            else:  # Preliminary code !!
                rules['field-' + self.get('fieldname', 'form.html') + '-show-if-expr'] = {
                    'input_selectors': ['#id_' + form_prefix + '-' + dep for dep in self.get('show-depends', 'form.html', [])],
                    'func': 'show-if-expr',
                    'targets': [
                        '#id_' + form_prefix + '-' + self.get('fieldname', 'form.html'),
                        '#label-id_' + form_prefix + '-' + self.get('fieldname', 'form.html') + '-container',
                    ],
                    # 'expr': r.as_javascript_function(self.get('show-depends', 'form.html', [])),
                    'expr': self.get('show-if', 'form.html'),
                }

        # Field (smart) copy
        smart_copy = self.get('smart-copy', 'form.html')
        if smart_copy:
            rules['field-' + smart_copy + '-smart-copy-from'] = {
                'input_selectors': ['#id_' + form_prefix + '-' + smart_copy],
                'func': 'smart-copy-from',
                'compute': 'copy',
                'to': 'id_' + form_prefix + '-' + self.get('fieldname', 'form.html'),
                'cascade': self.get('fieldname', 'form.html'),
            }
            rules['field-' + self.get('fieldname', 'form.html') + '-smart-copy-to'] = {
                'input_selectors': ['#id_' + form_prefix + '-' + self.get('fieldname', 'form.html')],
                'func': 'smart-copy-to',
            }

        # Computed fields
        form_data = self.get('data', context='form.html')
        if isinstance(form_data, dict):
            rules['field-' + self.get('fieldname', 'form.html') + '-compute-from'] = {
                'input_selectors': ['#id_' + form_prefix + '-' + form_data['source']],
                'func': 'get-from-list',
                'choices': form_data['choices'](request) if callable(form_data['choices']) else form_data['choices'],
                'to': 'id_' + form_prefix + '-' + self.get('fieldname'),
            }
        elif isinstance(form_data, str):
            r = SmartExpression(form_data)
            if not isinstance(r.tree.body, ast.Name) and self.get('format', 'form.html') == 'money':
                rules['field-' + self.get('fieldname', 'form.html') + '-function-data'] = {
                    'input_selectors': [
                        '#id_' + form_prefix + '-' + dependency for dependency in self.get('depends', 'form.html', [])
                    ],
                    'func': 'expr-function-euros',
                    'to': 'id_' + form_prefix + '-' + self.get('fieldname', 'form.html'),
                    'expr': r.as_javascript_function(self.get('depends', 'form.html', [])),
                }
        return rules

    def api_handle(self, path: list[str], view_params: dict):
        return self.format.api_handle(path, view_params)

    def __repr__(self):
        return f"SmartField object {self.properties}"


class ComputedSmartField(SmartField):
    def __init__(self, *args, **kwargs):
        self.expression = kwargs.get("data", None)
        super().__init__(*args, **kwargs)

    def get_annotation(self, view_attrs):
        if callable(self.expression):
            return self.expression(view_attrs)
        else:
            return self.expression


class ConditionnalSmartField(ComputedSmartField):
    def __init__(self, *args, **kwargs):
        fields_list = kwargs.get('fields', ())
        kwargs['depends'] = list(fields_list)
        group = [Value(',')] * (2 * len(fields_list) - 1)
        group[::2] = [Coalesce(Cast(F(field), CharField()), Value('null')) for field in fields_list]
        if 'flag_field' in kwargs:
            flag_field = kwargs['flag_field']
            flag_expr = Cast(Coalesce(F(flag_field), Value(False)), CharField())
            if '__' in flag_field:
                flag_field_base = flag_field.split('__')[0]
            else:
                flag_field_base = flag_field
            if flag_field_base not in kwargs['depends']:
                kwargs['depends'].append(flag_field_base)
        else:
            flag_expr = Value('true')
        kwargs['data'] = ExpressionWrapper(
            Concat(
                Value('{"flag":'),
                flag_expr,
                Value(',"fields":['),
                *group,
                Value(']}'),
            ),
            CharField(),
        )
        super().__init__(*args, **kwargs)


class ToolsSmartField(SmartField):
    def __init__(self, *args, **kwargs):
        kwargs["format"] = "tools"
        kwargs["data"] = None
        kwargs["max_width"] = 24 * len(kwargs.get("tools", []))
        # TODO: Check if tool in ['open', 'copy', 'delete']
        kwargs["columns"] = [
            {
                'tool': tool['tool'],
                'url_name': tool['url_name'],
                'url_arg_fieldname': tool.get('url_arg_fieldname'),
                'choices': tool.get('choices', {}),
                # 'choice_column': tool.get('choice_column', ''),
                # 'choice_title': tool.get('choice_title', ''),
                # 'choice_lookup': tool.get('choice_lookup', ''),
                # 'choice_url_params': tool.get('choice_url_params', ''),
                'url_args': tool['url_args'],
                'tooltip': tool['tooltip'],
            }
            for tool in kwargs.get('tools', [])
        ]
        super().__init__(*args, **kwargs)

    def as_column_def(self, context=None, fieldname=None, view_params: dict = None):
        settings = super().as_column_def(context, fieldname, view_params)
        for column in settings['columns']:
            for name, choice in column.get('choices', {}).items():
                lookup = choice.get('lookup', {})
                if callable(lookup):
                    choice['lookup'] = choice['lookup'](view_params)
            # if callable(column.get('choice_lookup')):
            #     column['choice_lookup'] = column['choice_lookup'](view_params)
        settings['frozen'] = True
        return settings


class SubviewsSmartField(ComputedSmartField):
    def __init__(self, *args, user=None, **kwargs):
        kwargs['format'] = 'subviews'
        self.user = user
        super().__init__(*args, **kwargs)
