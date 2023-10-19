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

"""smart_form.py

fr: Un système de classes Django pour gérer facilement les formulaires et tableaux de données, grâce à des bibliothèques javascript
     pour l'instant, seul tabulator.js est supporté pour les tables

     Principales fonctionnalités :
     - Définition des colonnes à partir d'un modèle
     - filtre de base (limite des lignes)
     - Possibilité de 'customiser' les définitions des colonnes (titre, format, alignement...)
     - Gestion des GET (remplissage et mises à jour) automatique
     - Colonne de type 'choice' au niveau navigateur (et non serveur)
     - Gestion des formats (Euro)
     - Format sur plusieurs lignes
     - Colonnes "calculées" (liens FK ou M2M par exemple)
     - Gestion des champs liés à d'autres modèles (ex. rédacteurs) via colonnes calculées
     - Colonnes d'actions (icônes)
     - Mécanisme de gestion fine des droits (par colonne/ligne)

     Attributs pris en compte:
     - field : str, Nom du champ (obligatoire !)
     - title : str, Titre de la colonne,
     - hoz_align : str,
     - min_width : int, largeur minimale en pixels,
     - width_grow : int,
     - show_priority : int (responsive),
     - header_sort : boolean,
     - multi_lines : boolean,
     - formatter : str,
     - formatter_params : dict,

     TODO (pour arriver à ce qui est fait à la main dans GÉQIP):
     - Gestion des filtres
     - Gestion des largeurs/priorité affichage
     - Gestion des éditions (validations, commentaires)

     TODO (plus tard):
     - Gestion des 'locales' (pour Money et Datetime)
"""

from __future__ import annotations

import json
import logging
import operator
from types import new_class
from copy import deepcopy
from itertools import chain
from functools import reduce, partial
from collections.abc import Sequence

from tomlkit.container import Container

from django.apps import apps
from django.urls import reverse
from django.forms import modelform_factory
from django.forms.utils import ErrorList
from django.contrib.contenttypes.fields import GenericRelation
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from xlsxwriter import Workbook

from common.utils import DataWorksheet, HTMLFilter
from document.smart_fields import DocumentsSmartField
from smart_view.smart_expression import SmartExpression
from generic_comment.smart_fields import CommentsSmartField
from smart_view.smart_fields import (
    SmartField,
    BooleanSmartFormat,
    ComputedSmartField,
    ToolsSmartField,
)

from django.db.models import (
    IntegerField,
    BooleanField,
    DateTimeField,
    DateField,
    DecimalField,
    TextField,
    ForeignKey,
)
from django.db.models import F, Q, Exists
from django import forms
from django.forms.widgets import MediaDefiningClass
from django.forms.widgets import HiddenInput
from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

# Avoid circular import
from django.db.models import Field as ModelField

from common.user_settings import get_user_settings, UserSettings
from smart_view.layout import (
    SmartLayoutField,
    SmartLayoutFieldset,
    SmartLayoutFormset,
    SmartLayoutComputedField,
    SmartLayoutHtml,
    SmartLayoutTemplate,
)
from smart_view.smart_form import AutocompleteInputWidget, BaseSmartModelForm, EurosField, MultiChoiceField
from common import config as main_config

logger = logging.getLogger(__name__)


def debug(*args, **kwargs):
    logger.debug(" ".join(map(str, args)))


ALL_FIELDS = "__all__"


def filter_args(filter_description):
    """
    Cette fonction prépare l'appel d'une méthode .filter() d'un
    Manager (ou d'un QuerySet) Django.
    Elle accepte un argument unique (filter_description)
    et retourne un tuple de longueur 2 composé :
     - de la liste des arguments 'positionnels'
     - d'un dict avec les arguments nommés

    Elle s'utilise de la façon suivante :

    fargs = filter_args(filter_description)
    manager...filter(*fargs[0], **fargs[1])...

    Elle gère les cas suivants selon la forme de filter_description:
     Si c'est une chaîne de caractères:
         La considère comme une chaîne encodée en JSON, la décode et applique les règles ci-dessous
     Si c'est un dict
         => considère que ce sont les arguments et qu'il n'y a pas d'arguments positionnels
     Si c'est une expression Q():
         => considère que c'est l'argument unique à passer au filtre
     Si c'est une séquence de longueur 2 et que le second élément est un dict:
         Si le premier élément est un object Q():
             => retourne un seul argument positionnel et tous les arguments nommés
         Si le premier élement est une séquence composée uniquement d'objets Q():
             => retourne toute la séquence comme arguments positionnels et tous les arguments nommés
     Si c'est une séquence et que tous les éléments sont des objets Q:
         => les retourne comme arguments positionnels
    """

    def and_expr(expr):
        # print(">>", expr)
        ops = []
        for key, value in expr.items():
            if key[0] == ':':
                if key == ':or':
                    ops.append(or_expr(value))
                else:
                    logger.warning(_("Unknown tag '{}' in filter expression parsing:".format(key)))
            else:
                ops.append(Q(**{key: value}))
        # print(">>>>", ops)
        if len(ops) == 0:
            return []
        elif len(ops) == 1:
            return [ops[0]]
        else:
            return ops

    def or_expr(expr):
        ops = []
        for value in expr:
            ops.append(Q(*and_expr(value)))
        return reduce(operator.or_, ops)

    if isinstance(filter_description, str):
        filter_description = json.loads(filter_description)

    if isinstance(filter_description, dict):
        return [Q(*and_expr(filter_description))], {}
    elif isinstance(filter_description, Q) or isinstance(filter_description, Exists):
        return [filter_description], {}
    elif isinstance(filter_description, list) or isinstance(filter_description, tuple):
        # print("AJA>>> is list", filter_description)
        if len(filter_description) == 2 and isinstance(filter_description[1], dict):
            if isinstance(filter_description[0], Q) or isinstance(filter_description[0], Exists):
                return filter_description[:1], filter_description[1]
            if (isinstance(filter_description[0], list) or isinstance(filter_description[0], tuple)) and all(
                map(
                    lambda f: isinstance(f, Q) or isinstance(f, Exists),
                    filter_description[0],
                )
            ):
                return filter_description[0], filter_description[1]
        if all(map(lambda f: isinstance(f, Q) or isinstance(f, Exists), filter_description)):
            return filter_description, {}
    raise RuntimeError(
        _("filter_args() argument format doesn't match any possible case (see doc) : {}").format(repr(filter_description))
    )


def tablefield_default(field, **kwargs):
    """A partir d'un champs (de modèle django),
    retourne un smartfield configuré avec les valeurs par défaut (titre, type...)
    """
    if isinstance(field, IntegerField):
        settings = (SmartField, {'format': "integer"})
    elif isinstance(field, DecimalField):
        settings = (SmartField, {'format': "integer"})
    elif isinstance(field, BooleanField):
        settings = (SmartField, {'format': "boolean"})
        if field.null:
            settings[1].update({'tristate': True})
        else:
            settings[1].update({'tristate': False})
    elif isinstance(field, TextField):
        settings = (SmartField, {'format': 'text'})
    elif isinstance(field, DateTimeField):
        settings = (SmartField, {'format': 'datetime'})
    elif isinstance(field, DateField):
        settings = (SmartField, {'format': 'datetime'})
    elif isinstance(field, ForeignKey):
        settings = (
            SmartField,
            {
                'format': 'choice',
                "choices": lambda view_params=None: ((v.pk, str(v)) for v in field.related_model.objects.all()),
            },
        )
    else:
        # Fallback : une colonne texte !
        settings = (SmartField, {'format': 'string'})

    if field.primary_key:
        settings[1]['special'] = 'id'

    settings[1]['title'] = (kwargs.get('title') or field.verbose_name or field.name).capitalize()
    settings[1]['label'] = (kwargs.get('title') or field.verbose_name or field.name).capitalize()
    settings[1]['help_text'] = field.help_text
    settings[1]['db_default'] = field.default
    settings[1]['null'] = field.null
    settings[1]['blank'] = field.blank

    if field.choices:
        settings[1]['format'] = 'choice'
        # ici, on utilise pas de fonction pour la liste de choix, car la source est codée en dur dans le modèle
        # et ne risque donc pas de changer au cours de l'exécution.
        settings[1]['choices'] = dict(field.choices)

    # Ajouter ici les données si field est une clé externe ?
    #  Ou alors on utilise ceci :

    # Comme on crée le SmartView Field à partir du model, on peut indiquer le champ de la base de données
    #  qui porte le même nom
    if not isinstance(field, GenericRelation):
        settings[1]['data'] = field.name

    # lien vers le ModelField (l'objet Python, pas le nom)
    settings[1]['model_field'] = field

    return settings


def columns_for_model(
    model,
    fields=None,
    exclude=None,
    columns=None,
    tablefield_callback=tablefield_default,
    localized_fields=None,
    labels=None,
    help_texts=None,
    error_messages=None,
    field_classes=None,
    *,
    apply_limit_choices_to=True,
):
    """
    Return a dictionary containing table columns for the given model.

    ``fields`` is an optional list of field names. If provided, return only the
    named fields.

    ``exclude`` is an optional list of field names. If provided, exclude the
    named fields from the returned fields, even if they are listed in the
    ``fields`` argument.

    ``columns`` is a dictionary of model field names mapped to a column.

    ``tablefield_callback`` is a callable that takes a model field and returns
    a form field.

    ``localized_fields`` is a list of names of fields which should be localized.

    ``labels`` is a dictionary of model field names mapped to a label.

    ``help_texts`` is a dictionary of model field names mapped to a help text.

    ``error_messages`` is a dictionary of model field names mapped to a
    dictionary of error messages.

    ``field_classes`` is a dictionary of model field names mapped to a column class.

    ``apply_limit_choices_to`` is a boolean indicating if limit_choices_to
    should be applied to a field's queryset.
    """
    column_dict = {}
    ignored = []
    opts = model._meta
    # Avoid circular import
    from django.db.models import Field as ModelField

    sortable_private_fields = [f for f in opts.private_fields if isinstance(f, ModelField)]
    for f in sorted(chain(opts.concrete_fields, sortable_private_fields, opts.many_to_many)):
        if fields is not None and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue

        kwargs = {}
        if columns and f.name in columns:
            if isinstance(columns[f.name], SmartField):
                kwargs["column"] = columns[f.name]
            elif isinstance(columns[f.name], type) and issubclass(columns[f.name], SmartField):
                kwargs["column"] = columns[f.name]()
            else:
                kwargs = columns[f.name]

        if tablefield_callback is None:
            tablefield = f.tablefield(**kwargs)
        elif not callable(tablefield_callback):
            raise TypeError("tablefield_callback must be a function or callable")
        else:
            tablefield = tablefield_callback(f, **kwargs)

        if tablefield:
            if apply_limit_choices_to:
                # TODO: Choices
                # apply_limit_choices_to_to_formfield(tablefield)
                pass
            column_dict[f.name] = tablefield
        else:
            ignored.append(f.name)

    if fields:
        column_dict = {f: column_dict.get(f) for f in fields if (not exclude or f not in exclude) and f not in ignored}

    return column_dict


class SmartViewMetaclass(MediaDefiningClass):
    """Collect SmartFields declared on the base classes. (code took from DeclarativeFieldsMetaclass...)"""

    def meta_setting_update(self, initial, update):
        if initial is None:
            initial = (SmartField, {})

        if isinstance(update, tuple) and issubclass(update[0], SmartField) and isinstance(update[1], dict):
            initial[1].update(update[1])
            return update[0], initial[1]
        elif isinstance(update, dict):
            initial[1].update(update)
            return deepcopy(initial)
        else:
            raise RuntimeError(_("Setting update : bad type : {}").format(repr(update)))

    def __new__(mcls: type, name: str, bases: tuple, attrs: dict):
        """Fonction appelée pour créer la classe "name"
        mcls est la métaclasse (class)
        name est le nom de la classe à créer (str)
        bases sont les classes parentes de la classe à créer (liste de classes)
        attrs sont les attributs de la classe à créer (dict)
        """

        _meta = dict()

        # print("Step 0 "+"-"*100+"\n", name)
        # pprint(_meta)

        # Step 1 - Inheritance

        if len(bases) == 1:
            for base in reversed(bases[0].__mro__):
                if hasattr(base, "_meta") and isinstance(base._meta, dict):
                    for attr in base._meta:
                        if not attr.startswith("_"):
                            _meta[attr] = deepcopy(base._meta[attr])
        else:
            NotImplementedError("Multiple heritance non implemented yet for SmartView")

        # A ce point, le _meta est exactement l'héritage, c'est à dire ce qu'il serait
        # sans aucune altération via Meta ou définition de nouveaux attributs

        # print("Step 1 (Inheritance done)"+"-"*90+"\n", name)
        # pprint(_meta)

        # Step 2 - Try to get configuration from model (if any)

        if 'Meta' in attrs and attrs["Meta"].__dict__.get("model", None):
            model = attrs["Meta"].__dict__.get("model", None)
            model_fields = attrs["Meta"].__dict__.get("model_fields", ALL_FIELDS)
            model_exclude_fields = attrs["Meta"].__dict__.get("model_exclude_fields", [])
            model_all_fields = []

            # print("    model detected ! fields=")
            # pprint(model_fields)

            opts = model._meta

            # Liste des champs "privés" du modèle
            sortable_private_fields = [f for f in opts.private_fields if isinstance(f, ModelField)]

            # On balaye tous les champs du modèle (concrets, privés et many2many)
            for f in sorted(chain(opts.concrete_fields, sortable_private_fields, opts.many_to_many)):
                # print("  >  (Model)field", f.name)
                if (model_fields != ALL_FIELDS and f.name in model_fields) or (
                    model_fields == ALL_FIELDS and f.name not in model_exclude_fields
                ):
                    # Création de la colonne !
                    model_all_fields.append(f.name)
                    # print(" (Model)  Raw columns settings for field", f.name, "...")

                    _meta['settings'] = dict(_meta['settings'], **{f.name: tablefield_default(f)})

                    # _meta.settings[f.name]['data'] = f.name

                    # print(" (Model)   ", _meta.settings[f.name])

            # Update fields with model fields
            if model_fields == ALL_FIELDS:
                _meta["fields"] = model_all_fields
            else:
                _meta['fields'] += list(_meta['fields']) + list(model_fields)

            _meta['permissions'] = {}

        # Step 3 : Update the setting with declared fields in the class body (only to add smartfields)

        for key, value in list(attrs.items()):
            # print("  attr.value", value)
            # print("    is_tuple", isinstance(value, tuple))
            # Si l'un des attributs de la classe à créer a la bonne forme :
            if (
                isinstance(value, tuple)
                and len(value) == 2
                and isinstance(value[0], type)
                and issubclass(value[0], SmartField)
                and isinstance(value[1], dict)
            ):
                # On l'ajoute à la liste des colonnes "déclarées"

                # current_columns.append((key, value))
                _meta['fields'] = list(_meta['fields']) + [key]
                _meta['settings'] = dict(_meta['settings'], **{key: value})

                # On le supprime de la liste des attributs (il ne sera donc pas un attribut de la classe une fois créée)
                attrs.pop(key)

        # print("Step 3 (added fields from attributes)"+"-"*100+"\n", name)
        # pprint(_meta)

        # Step 4 : Update using Meta class
        if 'Meta' in attrs and isinstance(attrs['Meta'], type):
            for attr_name in dir(attrs['Meta']):
                if attr_name == 'settings':
                    if 'settings' not in _meta:
                        _meta['settings'] = deepcopy(attrs['Meta'].settings)
                    else:
                        for s_name, setting in attrs['Meta'].settings.items():
                            # print('setting:', name, setting)
                            _meta['settings'] = dict(
                                _meta['settings'],
                                **{s_name: mcls.meta_setting_update(mcls, _meta['settings'].get(s_name), setting)},
                            )
                elif attr_name[:2] != "__":
                    # if attr_name not in _meta:
                    #     _meta[attr_name] = copy(getattr(attrs["Meta"], attr_name))
                    # else:
                    if attr_name.endswith("__add"):
                        _meta[attr_name[: -len("__add")]] += getattr(attrs["Meta"], attr_name)
                    elif attr_name.endswith("__remove"):
                        if attr_name[: -len("__remove")] in _meta:
                            if isinstance(_meta[attr_name[: -len("__remove")]], tuple) or isinstance(
                                _meta[attr_name[: -len("__remove")]], list
                            ):
                                wlist = list(_meta[attr_name[: -len("__remove")]])
                                if isinstance(_meta[attr_name[: -len("__remove")]][0], str):
                                    for welt in getattr(attrs["Meta"], attr_name):
                                        try:
                                            wlist.remove(welt)
                                        except ValueError:
                                            logger.warning(
                                                _(
                                                    "Trying to remove inexistent value {welt} while building class "
                                                    "{cls} wich does not exist in {attr_name} = {wlist}"
                                                ).format(
                                                    welt=welt,
                                                    wlist=wlist,
                                                    attr_name=attr_name[: -len("__remove")],
                                                    cls=name,
                                                )
                                            )
                                elif (
                                    isinstance(_meta[attr_name[: -len("__remove")]][0], dict)
                                    and 'name' in _meta[attr_name[: -len("__remove")]][0]
                                ):
                                    for welt in getattr(attrs["Meta"], attr_name):
                                        for element in wlist:
                                            if 'name' in element and element['name'] == welt:
                                                wlist.remove(element)
                                                break
                                # print(attr_name[: -len("__remove")], ":", _meta[attr_name[: -len("__remove")]], "==>", wlist)
                                _meta[attr_name[: -len("__remove")]] = tuple(wlist)
                            elif isinstance(_meta[attr_name[: -len("__remove")]], dict) or isinstance(
                                _meta[attr_name[: -len("__remove")]], dict
                            ):
                                wdict = dict(_meta[attr_name[: -len("__remove")]])
                                for welt in getattr(attrs["Meta"], attr_name):
                                    del wdict[welt]
                                _meta[attr_name[: -len("__remove")]] = dict(wdict)
                            else:
                                raise RuntimeWarning(_("Unhandled Meta: {}").format(attr_name))
                        else:
                            raise RuntimeError(
                                _("{} Meta attribute found but no {} !").format(attr_name, _meta[attr_name[: -len("__remove")]])
                            )
                    elif attr_name.endswith("__update"):
                        _meta[attr_name[: -len("__update")]].update(getattr(attrs["Meta"], attr_name))
                    else:  # default : replace
                        _meta[attr_name] = deepcopy(getattr(attrs["Meta"], attr_name))

            # print("Step 4 (updated via Meta class)"+"-"*80+"\n", name)
            # pprint(_meta)

        # No default primary key
        _meta['id_field'] = None

        # No default roles field
        _meta['roles_field'] = None

        # No default state field
        _meta['state_field'] = None

        # No update timestamp field
        _meta['update_timestamps'] = []

        # Step 5 : Get config defined settings (and update class ones)

        config_settings = main_config.get(name, {})
        if config_settings:
            # print(f"{name}:")
            for k, v in config_settings.items():
                if k in _meta['fields']:
                    for src, dest_f in {
                        'hidden': lambda v: {'hidden': bool(v)},
                        'null': lambda v: {'null': bool(v)},
                        'default': lambda v: {'default': v},
                        'label': lambda v: {'title': v},
                        'help_text': lambda v: {'help_text': v},
                    }.items():
                        if v.get(src) is not None:
                            _meta['settings'][k][1].update(dest_f(v.get(src)))
                    # print(f"  {k}: {v} {_meta['settings'][k]}")

        # Step 6 : Create real SmartField

        # Créer les instances des champs

        if _meta['model'] is not None:
            # Si le modèle n'est pas défini, c'est une classe abstraite (inutilisable) et il
            # ne faut donc pas créer les instances des champs (ce serait inutile)
            dependencies = {}
            smartfields = []
            for smartfield_name in _meta['fields']:
                settings = _meta['settings'].get(smartfield_name, None)
                if settings is None:
                    logger.warning(
                        _(
                            "While creating class {class_name}, no settings for"
                            " smartfield {smartfield_name} were found ; fallback to SmartField(**{{}})"
                        ).format(class_name=name, smartfield_name=smartfield_name)
                    )
                    settings = (SmartField, {})

                smartfield = settings[0](**dict(settings[1], **{"fieldname": smartfield_name}))

                smartfields.append(smartfield)
                attrs[smartfield_name] = smartfield

                if settings[1].get('special', None) == 'id':
                    _meta["id_field"] = smartfield_name
                    # debug("pk =", name, smartfield_name)
                elif settings[1].get('special', None) == 'roles':
                    _meta["roles_field"] = smartfield_name
                elif settings[1].get('special', None) == 'state':
                    _meta["state_field"] = smartfield_name
                    # debug(name, "Roles field:", smartfield_name)
                if smartfield.get("depends", default=None):
                    dependencies[smartfield_name] = smartfield.get("depends")
                    # print(smartfield_name, "depends on", dependencies[smartfield_name])

                # Ici, on recherche si un champ est 'auto_now'. Si c'est le cas, il faudra le mettre dans la liste des
                # champs à sauver à chaque modification d'un enregistrement (pour qu'il puisse jouer son rôle)
                model_field = settings[1].get('model_field')
                if model_field and hasattr(model_field, 'auto_now') and model_field.auto_now:
                    # print(smartfield_name, settings[1].get('model_field'))
                    _meta['update_timestamps'].append(smartfield_name)

            # Gestion des dépendances entre fields --------------------------------------------------------------------------------
            touched = True
            alterers = {}

            while touched:
                touched = False
                for altered, dependency in dependencies.items():
                    for l_alterer in dependency:
                        if l_alterer in alterers:
                            if altered not in alterers[l_alterer]:
                                alterers[l_alterer].append(altered)
                                touched = True
                        else:
                            alterers[l_alterer] = [altered]
                            touched = True
                        for alterer in alterers.keys():
                            if l_alterer in alterers[alterer] and altered not in alterers[alterer]:
                                alterers[alterer].append(altered)
                                touched = True

            # print("AJA> alterers:")
            # from pprint import pprint
            # pprint(alterers)

            for alterer, altered in alterers.items():
                attrs[alterer].alters = deepcopy(altered)
                # if alterer == 'montant_unitaire_expert_metier':
                #     print("AJA>    Alters:", attrs[alterer].alters, dir(attrs[alterer]))

            # Fin gestion des dépendances entre fields ----------------------------------------------------------------------------

            # attrs["_smartfields"] = smartfields
            _meta["smartfields"] = smartfields
            _meta["smartfields_dict"] = {smartfield.get('fieldname'): smartfield for smartfield in smartfields}

            # print("Step 6 "+"-"*100+"\n  attrs:")
            # pprint(attrs)

            # Step 6.5 : Get 'real' data fields => bound directly to the table database (Django Model)
            try:
                if _meta['fields']:
                    _meta['data_fields'] = [
                        attrs[column].get('data')
                        for column in _meta['fields']
                        if attrs[column].get('data') and isinstance(attrs[column].get('data'), str)
                    ]
                else:
                    _meta["data_fields"] = []
            except KeyError as ke:
                raise RuntimeError(
                    _("Champ non trouvé dans la SmartView {} : '{}' n'est pas dans {}").format(name, ke.args[0], list(attrs.keys()))
                )

            # _meta['data_fields'] = attrs["_data_fields"]

            # print("Step 6.5 (_meta.data_fields created)"+"-"*80+"\n  _meta.data_fields:")
            # pprint(_meta.data_fields)

            # Step 6.5 : Build queryset function

            # from django.db.models import Value

            annotations_fields = {
                k: v.get_annotation for k, v in _meta["smartfields_dict"].items() if isinstance(v, ComputedSmartField)
            }

            defined = set(_meta['data_fields'])
            for sfn, sfd in _meta['smartfields_dict'].items():
                if isinstance(sfd, ComputedSmartField):
                    if set(sfd.get('depends', default=[])) <= defined:
                        annotations_fields[sfn] = sfd.get_annotation
                        defined.add(sfn)
                    else:
                        raise RuntimeError(
                            _(
                                "While defining class {}, impossible to add computed field {}, which depends on {}"
                                " and only {} are defined"
                            ).format(name, sfn, repr(sfd.get('depends')), repr(defined))
                        )

            # print("\nClass:", name, ":")
            # for sfn, sfo in _meta['smartfields_dict'].items():
            #     if sfn not in annotations_fields:
            #         print("Field:     ", sfn)
            #     else:
            #         print("Annotation:", sfn, repr(sfo.get('depends')))

            def queryset(view_params: dict):
                return (
                    _meta['model']
                    .objects.using(_meta['database'])
                    .annotate(**{k: v(view_params) for k, v in annotations_fields.items()})
                )

            _meta['queryset'] = queryset

            # All fieldnames that should be passed to values() Queryset method to mimic a values() without arg
            _meta['values_fields'] = _meta['data_fields'] + list(annotations_fields.keys())

        # Step 7 : Process filters

        filters = {}
        menu_filters = []
        bar_filters = []
        for filtname, filter_i in _meta['user_filters'].items():
            mfilter = dict(deepcopy(filter_i))
            if "label" not in mfilter:
                # No label set : Let's try to get one
                if "fieldname" in mfilter and mfilter["fieldname"] in attrs:
                    # from a column (by fieldname)
                    mfilter["label"] = attrs[mfilter["fieldname"]].get("title")
                elif name in attrs:
                    # from a column (by name)
                    mfilter["fieldname"] = filtname
                    mfilter["label"] = attrs[mfilter["fieldname"]].get("title")
                else:
                    # fallback
                    mfilter["label"] = filtname.capitalize()
            if mfilter["type"] == "select":
                if "choices" in mfilter:
                    if (
                        callable(mfilter["choices"])
                        or isinstance(mfilter["choices"], list)
                        or isinstance(mfilter["choices"], tuple)
                    ):
                        pass  # Use choices as provided
                    elif mfilter['choices'] == '__STYLES__':
                        choices = [{'label': _("Tous"), 'value': json.dumps({})}]
                        for key, value in _meta['row_styler']['styles'].items():
                            if isinstance(key, tuple):
                                choices.append(
                                    {
                                        'label': value[1].replace('<br>', ', '),
                                        'value': json.dumps({_meta['row_styler']['fieldname'] + '__in': key}),
                                        'style': value[0],
                                    }
                                )
                            else:
                                choices.append(
                                    {
                                        'label': value[1].replace('<br>', ', '),
                                        'value': json.dumps({_meta['row_styler']['fieldname']: key}),
                                        'style': value[0],
                                    }
                                )
                        mfilter["choices"] = choices
                    elif isinstance(mfilter["choices"], dict):
                        # ensure there is a fieldname key
                        mfilter['choices']['fieldname'] = mfilter['choices'].get('fieldname', filtname)
                        mfilter['fieldname'] = mfilter['choices'].get('fieldname', filtname)

                        m_label_expr = mfilter["choices"].get('label', mfilter['choices'].get('fieldname', filtname))
                        if isinstance(m_label_expr, str):
                            expr = SmartExpression(m_label_expr)
                            m_label_expr = expr.as_django_orm()({})

                        m_sort_expr = mfilter["choices"].get('sort', None)
                        if m_sort_expr is None:
                            m_sort_expr = m_label_expr

                        choices = (
                            lambda view_params, base_filter_args=(), base_filter_kwargs=dict(), manager=_meta[
                                'model'
                            ].objects, mf=mfilter.copy(), label_expr=deepcopy(m_label_expr), sort_expr=deepcopy(
                                m_sort_expr
                            ), add_null=attrs[
                                mfilter['choices']['fieldname'].split('__')[0]
                            ].get(
                                "null"
                            ), **kwargs: [
                                {"label": _("Tout"), "value": "{}"}
                            ]
                            + [
                                {
                                    "label": obj["label"],
                                    "value": json.dumps({mf["choices"]["fieldname"]: obj['smart_view_filter_id']}),
                                }
                                for obj in manager.filter(*base_filter_args, **base_filter_kwargs)
                                .filter(*mf["choices"].get("subfilter", []))
                                .order_by()
                                .distinct()
                                .values(
                                    smart_view_filter_id=F(mf["choices"]["fieldname"]),
                                    label=label_expr,
                                )
                                .order_by(sort_expr)
                            ]
                            + (
                                [
                                    {
                                        'label': _("-- Défini --"),
                                        'value': '{{{}__isnull:false}}'.format(mf['fieldname']),
                                    },
                                    {
                                        'label': _("-- Indéfini --"),
                                        'value': '{{{}__isnull:true}}'.format(mf['fieldname']),
                                    },
                                ]
                                if add_null
                                else []
                            )
                        )
                        # if attrs[mfilter['fieldname'])].get("null"):
                        #     choices.append()
                        mfilter["choices"] = choices
                    else:
                        raise RuntimeError(
                            "Filter choices must be callable, a sequence or a dict, not {}".format(repr(mfilter["choices"]))
                        )
                else:
                    # On a juste le nom du filtre (éventuellement du champs)
                    # et il faut deviner la liste de choix d'après le modèle
                    if "fieldname" not in mfilter:
                        mfilter["fieldname"] = filtname
                    smartfield = attrs[mfilter["fieldname"]]
                    choices = [{"label": _("Tout"), "value": "{}"}]
                    if smartfield.get("choices", default=[]):
                        sf_choices = smartfield.get("choices")
                        add_null = smartfield.get('null')
                        if callable(sf_choices):
                            # print(repr(filter_i))
                            choices = (
                                lambda view_params=None, mf=mfilter.copy(), sfc=sf_choices, add_null=add_null, **kwargs: [
                                    {'label': _("Tout"), 'value': '{}'}
                                ]
                                + [
                                    {
                                        "label": c[1],
                                        "value": json.dumps({mf["fieldname"]: c[0]}),
                                    }
                                    for c in dict(sfc(view_params)).items()
                                ]
                                + (
                                    [
                                        {
                                            'label': _("-- Défini --"),
                                            'value': '{"' + mf["fieldname"] + '__isnull":false}',
                                        },
                                        {
                                            'label': _("-- Indéfini --"),
                                            'value': '{"' + mf["fieldname"] + '__isnull":true}',
                                        },
                                    ]
                                    if add_null
                                    else []
                                )
                            )
                        else:
                            sf_choices = deepcopy(sf_choices)
                            # print(sf_choices)
                            choices = (
                                lambda view_params=None, mf=mfilter.copy(), sfc=sf_choices, add_null=add_null, **kwargs: [
                                    {'label': _("Tout"), 'value': '{}'}
                                ]
                                + [
                                    {
                                        "label": c[1],
                                        "value": json.dumps({mf["fieldname"]: c[0]}),
                                    }
                                    for c in dict(sfc).items()
                                ]
                                + (
                                    [
                                        {
                                            'label': _("-- Défini --"),
                                            'value': '{"' + mf["fieldname"] + '__isnull":false}',
                                        },
                                        {
                                            'label': _("-- Indéfini --"),
                                            'value': '{"' + mf["fieldname"] + '__isnull":true}',
                                        },
                                    ]
                                    if add_null
                                    else []
                                )
                            )
                    elif isinstance(smartfield.format, BooleanSmartFormat):
                        choices += [
                            {
                                "label": _("Oui"),
                                "value": json.dumps({mfilter["fieldname"]: True}),
                            },
                            {
                                "label": _("Non"),
                                "value": json.dumps({mfilter["fieldname"]: False}),
                            },
                        ]
                        if smartfield.get('null'):
                            choices += [
                                {
                                    "label": _("-- Défini --"),
                                    "value": json.dumps({mfilter["fieldname"] + "__isnull": False}),
                                },
                                {
                                    "label": _("-- Indéfini --"),
                                    "value": json.dumps({mfilter["fieldname"] + "__isnull": True}),
                                },
                            ]
                    else:
                        raise AttributeError(
                            _("No choices given and no way to create one for filter '{}' ").format(mfilter["fieldname"])
                        )
                    mfilter["choices"] = choices
            elif mfilter["type"] == "contains":
                if isinstance(mfilter.get('fieldname'), str):
                    mfilter['fieldnames'] = (mfilter['fieldname'],)
            else:
                raise AttributeError(_("Unknown filter type: {}").format(mfilter["type"]))

            filters[filtname] = mfilter
            if mfilter.get('position') == 'bar':
                bar_filters.append(filtname)
            else:
                menu_filters.append(filtname)

        _meta["user_filters"] = filters
        _meta["menu_user_filters"] = menu_filters
        _meta["bar_user_filters"] = bar_filters

        # step 8 : Process form layout

        # Comment ça marche :
        # La mise en page est une chaîne de caractères multilignes (qui pourrait être issue d'un fichier texte)
        # Elle utilise l'indentation (comme python) pour définir le niveau d'imbrication des composants
        # Un fieldsets est représenté par une ligne commençant par '#' puis le titre du fieldset (tag 'legend')
        #   puis ses enfants, avec une indentation
        # Un champ est représenté par une chaîne de caractères entre '<' et '>', sans espaces
        # On peut mettre plusieurs champs sur une seule ligne, séparés par des espaces
        # Chaque champ occupe deux colonnes de la grille (une pour le 'label' et une pour le 'field')
        #   TODO: Voir si un autre mode est possible (smartphone, avec le label au dessus du champ, par exemple)
        # Les '-' dans le nom du champ sont ignorés. Un champ '<--->' est juste un vide qui occupe deux colonnes
        # Si le nom d'un champ comporte un '+', il s'étend en largeur :
        #   <--fieldname--+----> : Champ sur 4 colonnes : 1 pour le label et 3 pour le field lui-même
        # Il ne peut y avoir qu'un seul nom entre '<' et '>' : <--f1-f2--> est le champ 'f1-f2' et <--f1-+--f2-> est illégal

        def layout_parse_objects(objects_line, sublines, level=0, siblings=[]):
            """
            objects_line est SANS indentation
            sublines est une liste des lignes AVEC indentation
            """
            # print("        Parse object: '{}', {}".format(objects_line, repr(sublines)))
            subforms = []

            if objects_line.startswith('#'):
                children, subforms_p = layout_parse_lines(sublines, level=level + 1)
                subforms.extend(subforms_p)
                # print("    Fieldset legend='{}', contents={}".format(objects_line[2:], children))
                objects_line_parts = objects_line.split(' ', maxsplit=1)
                return (
                    [
                        SmartLayoutFieldset(
                            objects_line_parts[1] if len(objects_line_parts) > 1 else '',
                            *children,
                            css_class='level-' + str(level),
                            style='grid-column:1/last-column',
                            level=level,
                            html_id=objects_line_parts[0][1:] or None,
                        )
                    ],
                    subforms,
                )
            elif objects_line.startswith('§'):
                if sublines:
                    raise AttributeError(
                        _(
                            "Form Layout lines for html code cannot have children (probable indentation error) : {}".format(
                                objects_line
                            )
                        )
                    )
                return (
                    [
                        SmartLayoutHtml(
                            objects_line[1:],
                            style='grid-column:1/last-column',
                            level=level,
                        )
                    ],
                    subforms,
                )
            elif objects_line.startswith('$'):
                if sublines:
                    raise AttributeError(
                        _(
                            "Form Layout lines for template cannot have children (probable indentation error) : {}".format(
                                objects_line
                            )
                        )
                    )
                return (
                    [
                        SmartLayoutTemplate(
                            objects_line[1:],
                            style='grid-column:1/last-column',
                            level=level,
                        )
                    ],
                    subforms,
                )
            elif objects_line.startswith('<'):
                if sublines:
                    raise AttributeError(
                        _(
                            "Form Layout lines with fields cannot have children (probable indentation error) : {}".format(
                                objects_line
                            )
                        )
                    )
                fields = objects_line.split()
                column = 1
                objects = []
                for field_def in fields:
                    if field_def:
                        if field_def[0] == '<' and field_def[-1] == '>':
                            field_def = field_def[1:-1]
                            field_def_splitted = sorted(
                                [f.strip('-') for f in field_def.split('+')],
                                reverse=True,
                            )
                            colspan = len(field_def_splitted)
                            if any([len(s) for s in field_def_splitted[1:]]):
                                raise AttributeError("Bad field definition: {}".format(field_def))
                            field_def = field_def_splitted[0]
                            if field_def not in _meta['fields']:
                                raise AttributeError(
                                    _("In {} form_layout, field_def {} not in the SmartView (not in {})").format(
                                        name, field_def, str(_meta['fields'])
                                    )
                                )
                            smart_field = _meta['smartfields_dict'][field_def]
                            extends_sibling = False
                            for sibling in siblings:
                                if (
                                    sibling.smart_field_name == field_def
                                    and sibling.smart_column[0] == column
                                    and sibling.smart_column[1] == colspan
                                ):
                                    sibling.row_span += 1
                                    extends_sibling = True
                            if not extends_sibling:
                                if isinstance(smart_field, CommentsSmartField):
                                    objects.append(
                                        SmartLayoutFormset(
                                            field_def,
                                            smart_column=(column, colspan),
                                            subform_template=smart_field.subform_template,
                                            formset_model=smart_field.formset_model,
                                            initial=smart_field.formset_initial,
                                            smart_field=smart_field,
                                        )
                                    )
                                    subforms.append(smart_field)
                                elif isinstance(smart_field, DocumentsSmartField):
                                    colspan = 1
                                    objects.append(
                                        SmartLayoutFormset(
                                            field_def,
                                            smart_column=(column, colspan),
                                            subform_template=smart_field.subform_template,
                                            formset_model=smart_field.formset_model,
                                            initial=smart_field.formset_initial,
                                            smart_field=smart_field,
                                        )
                                    )
                                    subforms.append(smart_field)
                                elif isinstance(smart_field, ComputedSmartField):
                                    objects.append(
                                        SmartLayoutComputedField(
                                            field_def,
                                            smart_column=(column, colspan),
                                            smart_field=smart_field,
                                        )
                                    )
                                else:
                                    objects.append(
                                        SmartLayoutField(
                                            field_def,
                                            smart_column=(column, colspan),
                                            smart_field=smart_field,
                                        )
                                    )
                            column += colspan
                        else:
                            raise AttributeError(_("In {} form_layout, incorrect fieldname in layout '{}'").format(name, field_def))
                return objects, subforms
            else:
                raise AttributeError(_("Error TODO message"))

        def layout_parse_lines(lines, level=1):
            """Implémentation récursive de la lecture du layout
            C'est loin d'être la plus efficiente, mais c'est plus simple à comprendre et donc à modifier/améliorer
            et comme ce n'est exécuté qu'une seule fois au lancement de Django, l'efficience et moins importante
            """
            subforms = []

            root_indent = None
            objects = []

            objects_line = None
            sublines = []

            for line in lines:
                data_line = line.lstrip(' ')
                if data_line:
                    indent = len(line) - len(data_line)
                    if root_indent is None:
                        # Première ligne non vide = indentation de base pour cet objet
                        root_indent = indent
                    indent = indent - root_indent

                    if indent == 0:
                        if objects_line is not None:
                            # There was a object => parse & record it !
                            objects_p, subforms_p = layout_parse_objects(objects_line, sublines, level, objects)
                            objects.extend(objects_p)
                            subforms.extend(subforms_p)
                            sublines = []
                        objects_line = data_line

                    else:
                        if objects_line is not None:
                            sublines.append(line)
                        else:
                            raise AttributeError(
                                _("Error while parsing form layout : incorrect indenting for line '{}' ").format(data_line)
                            )

            if objects_line is not None:
                objects_p, subforms_p = layout_parse_objects(objects_line, sublines, level, objects)
                objects.extend(objects_p)
                subforms.extend(subforms_p)

            return objects, subforms

        _meta['form_layout'] = main_config.get(name + '.form_layout', _meta.get('form_layout'))
        form_layout_definition = _meta['form_layout']
        _meta['form_helper'] = FormHelper()
        _meta['form_helper'].template_pack = 'geqip'
        _meta['form_helper'].form_class = 'smart-view-form'

        if isinstance(form_layout_definition, str):
            pl = layout_parse_lines(form_layout_definition.splitlines())
            _meta['form_helper'].layout = pl[0][0]
            _meta['subforms'] = [smart_field.get_formset() for smart_field in pl[1]]

        attrs["_meta"] = _meta

        # Step 8 : Some checking...

        # TODO

        # Step 9 : At last, create the class

        new_class = super().__new__(mcls, name, bases, attrs)

        # Build main form class
        new_class.build_form_class()

        return new_class


# Les quelques fonctions ci-dessous dont le nom commence par '_form_' sont destinées à être des méthodes de la classe
# du formulaire, créée dynamiquement par get_form_class
# TODO: Utiliser une métaclasse pour créer intelligemment cette classe lors
#  de l'import (une fois pour toute et non à chaque requête)
#  En fait, il en faudrait sans doute plusieurs (classes) : Une par mode de la SmartPage...


def _form__init__(
    self,
    data=None,
    files=None,
    auto_id='id_%s',
    prefix=None,
    initial=None,
    error_class=ErrorList,
    label_suffix=None,
    empty_permitted=False,
    instance=None,
    instance_state=None,
    instance_roles=(),
    use_required_attribute=None,
    renderer=None,
    read_only=False,
    user_roles=(),
    request=None,
):
    # noinspection PyArgumentList
    super(self.__class__, self).__init__(
        data=data,
        files=files,
        auto_id=auto_id,
        prefix=prefix,
        initial=initial,
        error_class=error_class,
        label_suffix=label_suffix,
        empty_permitted=empty_permitted,
        instance=instance,
        use_required_attribute=use_required_attribute,
        renderer=renderer,
    )

    # Si ce paramètre est vrai, le formulaire généré n'en sera pas vraiment un mais plutôt un affichage des données contenues
    #   dans le formulaire, sans possibilité d'édition, mais avec le format et la mise en page du formulaire
    self.read_only = read_only

    # Rôles de l'utilisateur. Attention, il s'agit des rôles 'génériques' et non des rôles liés spécifiquement à une instance,
    #   qui doivent être passés ailleurs... Voir la notion de rôle 'potentiel' à creuser...
    # Ces rôles génériques sont utilisés pour le formulaire vide ou copié (create)
    self.user_roles = user_roles

    # Liste des rôles pour l'instance avec laquelle le formulaire est lié
    self.instance_roles = instance_roles

    # Etat de l'instance avec laquelle le formulaire est lié
    self.instance_state = instance_state

    # Utilisateur en cours
    self.user = request.user

    self.helper = FormHelper()
    self.helper.add_input(Submit('submit', 'Submit'))

    # Indique aux widgets AutocompleteWidget quel est l'utilisateur
    # pour permettre le calcul dynamique des listes de choix
    for field in self.fields.values():
        if isinstance(field.widget, AutocompleteInputWidget):
            field.widget._request = request


# def _form_save(self):
#     # print("My form_save !")
#     # TODO: Stuff to do before saving the instance into the database...
#
#     # A little trick to allow using super() with a dynamically added method
#     super(self.__class__, self).save()


# def _form_render(self):
#     # print("Render :", self.smart_view_class, self.prefix)
#     fields, html = self.as_fieldset(self.smart_view_class._meta.form_layout)
#     # TODO : insert needed fields as hidden ones
#     # print(fields)
#     return html


class SmartView(metaclass=SmartViewMetaclass):
    """SmartView est une classe permettant d'utiliser facilement des tables dynamiques, en utilisant
    la bibliothèque javascript 'tabulator.js' avec Django

    Elle s'utilise comme un Form

    Les informations pour la gestion des colonnes sont de deux natures :
    - La liste des colonnes à inclure dans le tableau
    - Les options associées à ces colonnes

    Ces deux types d'informations peuvent être gérés **séparément** lors des héritages

    Des colonnes peuvent être créées :
    - Par une classe associée à un modèle : Dans ce cas, le modèle et les attributs 'fields' et 'exclude' définissent les
       colonnes à créer suivant la même logique que les Form de Django
    - Par déclaration explicites dans la définition d'une classe (même logique pour les Form, mais la syntaxe est différente :
        chaque colonne est un tuple de 2 éléments :
            - la classe de la colonne
            - les réglages (settings) de la colonne
    - Par modification de la liste des colonnes héritées :
        - Utilisation des attributs 'columns' (liste des noms des colonnes à garder de l'ancêtre) et 'columns_remove' (garder
           toutes les colonnes de l'ancêtre sauf celles de la liste) de Meta
        - Ajout de colonnes par déclaration directe

    Pour les réglages :
    - les créations de colonnes sont toujours associées à des réglages de base (création par le modèle ou par les déclarations)
    - Il est toujours possible de les modifier via les attributs 'settings_update' ou 'settings_set' de la classe Meta

    Liste des classes et réglages de colonnes :
        - cf. ci-dessus (classe SmartField et descendants)

    Principe de fonctionnement :
        - Les métaclasses tiennent à jour quelques attributs :
            - '_columns' qui est une liste des colonnes (instances)
            - '_columns_definitions' qui est une liste des *définitions* des colonnes : tuples (class, settings)
    """

    class Media:
        css = {
            "all": (
                "smart_view/css/tabulator.min.css",
                "smart_view/css/smart-view.css",
            ),
        }
        js = (
            "smart_view/js/tabulator.min.js",
            "smart_view/js/get-coockie.js",
            "smart_view/js/smart-view.js",
        )

    class Meta:
        # Basic view settings
        database = 'default'
        model = None
        model_fields = ALL_FIELDS

        help_text = None
        fields = ()  # Could be a set instead of a list ?
        settings = {}

        # Common view settings
        base_filter = None
        user_filters = {}
        exports = {}
        permissions = None
        menu_left = ()
        menu_right = ()
        views = ('table',)
        default_view = None  # So, the first in the list is the default

        # Si True, active la gestion d'une ligne courante dans le tableau (et/ou d'un enregistrement courant)
        current_row_manager = False

        # Fields to initialize on copy:
        initial_on_copy = None
        fields_to_copy = None

        # For table type view
        columns = []
        selectable_columns = []
        row_styler = None

        # For form type view
        form_class = None
        form_layout = None
        form_rules = None
        form_message = None
        form_helper = FormHelper()
        # UNUSED : computed from layout : form_fields = []

    @classmethod
    def _form_class_populate_ns(cls, form_class_ns):
        """
        Complète le NameSpace de la classe Form nouvellement crée
        cf. types.new_class() pour la doc
        """
        form_class_ns['smart_view_class'] = cls
        form_class_ns['Media'] = BaseSmartModelForm.Media
        form_class_ns['_smart_fields_dict'] = cls._meta['smartfields_dict']

        return form_class_ns

    @classmethod
    def build_form_class(cls, exclude=()):
        # print(f"SmartView.build_form_class for {cls}")
        # TODO : Get labels, help_texts & widgets from SmartView class & configuration
        field_classes = {}

        if cls._meta['form_layout'] is None:
            return

        exclude = list(exclude)
        form_fields = cls._meta['data_fields']
        help_texts = {}
        widgets = {
            'id': HiddenInput(),
            # 'num_marche': TextInput(attrs={'class': 'left toto'}),
        }
        labels = {}
        for field_name in form_fields:
            smartfield = cls._meta['smartfields_dict'][field_name]
            labels[field_name] = smartfield.get('title', context='form.html')
            help_texts[field_name] = smartfield.get('help_text', context='form.html')

            if smartfield.get('hidden', context='form.html'):
                widgets[field_name] = HiddenInput()
            else:
                widget = smartfield.format.get_widget(context='form.html')
                if widget:
                    widgets[field_name] = widget
                # print(labels, help_texts)
            model_field = cls._meta['model']._meta.get_field(smartfield.get('fieldname'))
            # print(smartfield.get('fieldname'), model_field.editable)
            if not model_field.editable:
                exclude.append(smartfield.get('fieldname'))
            if smartfield.get('format') == 'money':
                field_classes[field_name] = EurosField
            elif smartfield.get('format') == 'multichoice':
                field_classes[field_name] = MultiChoiceField

        form_class = new_class(
            'SmartViewForm',
            (
                modelform_factory(
                    cls._meta['model'],
                    form=BaseSmartModelForm,
                    fields=form_fields,
                    exclude=exclude,  # Temporaire : Tous les champs du modèle
                    widgets=widgets,
                    labels=labels,
                    help_texts=help_texts,
                    field_classes=field_classes,
                ),
            ),
            exec_body=cls._form_class_populate_ns,
        )
        cls._meta['form_class'] = form_class

    @classmethod
    def get_form_class(cls, exclude=()):
        return cls._meta['form_class']

    @classmethod
    def get_subforms_classes(cls):
        return cls._meta['subforms']

    def __init__(
        self,
        prefix=None,
        view_params: dict = dict(),
        request=None,
        view_filters=None,
        manager=None,
        url=".",
        load_filters={},
        **kwargs,
    ):
        self._prefix = prefix or ''
        self._view_params = view_params

        # if field_smartviews is None:
        #     field_smartviews = {}
        for name, value in kwargs.items():
            self._meta[name] = value

        self._url_prefix = self._view_params['url_prefix']
        if self._url_prefix:
            self._reverse_base = {'url_prefix': self._view_params['url_prefix']}
        else:
            self._reverse_base = {}
        if self._meta['base_filter'] is not None:
            if not isinstance(self._meta['base_filter'], dict) and callable(self._meta['base_filter']):
                base_filter = self._meta['base_filter'](self, view_params)
            else:
                base_filter = self._meta['base_filter']
            self.base_filter_args = filter_args(base_filter)
        else:
            self.base_filter_args = filter_args({})

        self.url = url
        self.request = view_params['request']
        # self.field_smartviews = field_smartviews
        self.manager = manager

        self.user_settings = (
            get_user_settings(self._view_params['user'], self._meta['appname'] + '.tabulator-' + self._prefix).get(
                self._meta['appname'] + '.tabulator-' + self._prefix, {}
            )
            or {}
        )

        if view_filters is not None:
            if callable(view_filters):
                view_filters = view_filters(self, self.request)
            self.view_filters = filter_args(view_filters)
        else:
            self.view_filters = filter_args({})

        # Filtres à activer au chargement de la page = à la création de l'HTML mais que l'utilisateur peut modifier
        self.load_filters = load_filters

    @property
    def media(self):
        """"""
        # Collect media from columns...
        media = forms.Media(self.Media)
        for smartfield in self._meta['smartfields']:
            media += smartfield.media
        # if self._meta.form_layout:
        #     media += forms.Media(SmartViewBaseForm.Media)
        return media

    def get_columns_names(self):
        if self._meta['columns'] is not None:
            return self._meta['columns']
        else:
            return self._meta['smartfields_names']

    def columns_as_def(self, **kwargs):
        # print(self._meta.columns, self.get_columns_names())
        return [
            getattr(self, column_name).as_column_def(fieldname=column_name, **kwargs) for column_name in self.get_columns_names()
        ]

    # def as_form(self):
    #     widget, fields = smart_widget_factory(self, self._meta.form_layout)
    #     if widget is not None:
    #         return {'html': widget.render(), 'fields': list(fields)}
    #     else:
    #         return {'html': "", 'fields': []}

    # def as_form_html(self, data=None, initial=None, instance=None):
    #     html = self.get_form_class()(data, initial=initial, instance=instance).as_ul()
    #     return html

    def as_html(self):
        """"""
        template = get_template('smart_view/smart_view.html')
        # print("AJA columns_def", self.columns_as_def())

        user_filters = {}
        for filter_name, u_filter in self._meta['user_filters'].items():
            # Create a temporary copy of user filter
            u1_filter = deepcopy(dict(u_filter))

            # If needed, restrict choices to accessible records
            if 'choices' in u1_filter and callable(u1_filter['choices']):
                u1_filter['choices'] = u1_filter['choices'](
                    self._view_params,
                    base_filter_args=self.base_filter_args[0],
                    base_filter_kwargs=self.base_filter_args[1],
                    manager=self.get_base_queryset(self._view_params),
                )
            user_filters[filter_name] = u1_filter

        # form = self.as_form()

        def filter_update(name, filter):
            """Adapte un filtre pour tenir compte des filtres de l'URL ou des préférences"""
            value = None
            if name in self.load_filters:
                value = self.load_filters[name]
                json_value = json.dumps(value)
            elif name in self.user_settings.get('filters', {}):
                value = self.user_settings['filters'][name]
                json_value = json.dumps(value)
            if value is not None:
                if filter['type'] == 'select':
                    choices = []
                    for choice in filter['choices']:
                        if value == choice.get('code') or json_value == choice['value'] or value == choice['label']:
                            choice['selected'] = True
                        choices.append(choice)
                    filter['choices'] = choices
            return filter

        columns = self.columns_as_def(context='table.tabulator', view_params=self._view_params)
        columns_visible = [column['field'] for column in columns if not column.get('hidden', False)]

        context = {
            'url_prefix': self._view_params['url_prefix'],
            'prefix': self._prefix,
            'views': self._meta['views'],
            # 'form': form,
            'id_field': self._meta['id_field'],
            # le passage par un dict() ci-dessous permet de ne pas envoyer des dict dans le gestionnaire de templates
            # qui ne les reconnait pas...
            'menu_left': [dict(entry) for entry in self._meta['menu_left']],
            'menu_right': [dict(entry) for entry in self._meta['menu_right']],
            'columns': columns,
            'selectable_columns': [
                {
                    'id': col_name,
                    'title': getattr(self, col_name).properties.get('title', ""),
                }
                for col_name in self._meta['selectable_columns']
                if col_name in columns_visible
            ],
            # 'user_filters': user_filters,
            'menu_user_filters': {
                filter_name: filter_update(filter_name, user_filters[filter_name])
                for filter_name in self._meta['menu_user_filters']
            },
            'bar_user_filters': {
                filter_name: filter_update(filter_name, user_filters[filter_name]) for filter_name in self._meta['bar_user_filters']
            },
            'exports': dict(self._meta['exports']),
            'query_base': self.url + "?smart_view_prefix=" + self._prefix,
            'smart_view_options': {
                'base_url': self.url,  # + "?smart_view_prefix=" + self.prefix,
                'settings_url': reverse('common:api_user_settings', kwargs=self._reverse_base),
                'appname': self._meta['appname'],
                # TODO : Handle Anonymous User case.
                'user_settings': self.user_settings,
                'id_field': self._meta['id_field'],
                'roles_field': self._meta['roles_field'],
                'state_field': self._meta['state_field'],
                'permissions': dict(self._meta['permissions']),
                'current_row_manager': self._meta['current_row_manager'],
                # 'form_fields': form['fields'],
                'form_fields': [],
            },
            # TODO :
            # 'secondary_smartviews': self.field_smartviews
            # [{'fieldname': fsv['fieldname'], 'smartview': fsv['smartview']} for fsv in self.field_smartviews],
            'manager': self.manager,
        }

        # On construit ici deux dictionnaires :
        # - Un premier qui servira dans le code JS à déterminer la couleur des lignes (en éclatant les listes d'état
        #    spécifiées par 'row_styler' pour avoir 1 seul état par entrée du dictionnaire)
        # - Un second qui maitient une entrée par style et qui sert à afficher la légende
        if 'row_styler' in self._meta and self._meta['row_styler'] is not None:
            styles = {}
            context['legend'] = {}
            for states, style in self._meta['row_styler']['styles'].items():
                if isinstance(states, frozenset) or isinstance(states, tuple):
                    styles.update({state: style for state in states})
                    context['legend']['/'.join(states)] = style
                else:
                    styles[states] = style
                    context['legend'][states] = style
            # print("AJA> ", styles)
            context['smart_view_options']['row_styler'] = {
                'fieldname': self._meta['row_styler']['fieldname'],
                'styles': styles,
            }
        else:
            context['smart_view_options']['row_styler'] = {}
            context['legend'] = None

        if 'table_row_tooltip' in self._meta:
            context['smart_view_options']['row_tooltip'] = dict(self._meta['table_row_tooltip'])
            context['smart_view_tooltip_formatter'] = "\n".join(
                [
                    "* "
                    + getattr(self, column).properties.get('title', column.capitalize())
                    + " : ${{data.{column}}}".format(column=column)
                    for column in self._meta['table_row_tooltip']['columns']
                ]
            )
        return template.render(context=context)

    def get_base_queryset(self, view_attrs, skip_base_filter=False):
        """Retourne le Queryset qui correspond à la définition de base de la SmartView.
        C'est à dire :
        - Les champs de base (depuis le modèle)
        - Les champs calculés (annotations)
        - Le filtre de base de la SmartView

        Tout ce qui concerne la request n'est pas pris en compte :
        - Filtre de vue
        - Filtre utilisateur
        - tout le reste :-)

        La requête est tout de même nécessaire comme paramètre, car elle est utilisée pour les champs calculés (comme les rôles)

        si skip_base_filter est vrai, le filtre de base n'est pas appliqué
        (utile pour les mises à jour qui ne répondent plus au filtre de base après modification)
        """

        # view_attrs = {
        #     'request': request,
        #     'now': now(),
        #     'user': request.user,
        # }

        # print(self._meta['queryset'](view_attrs))

        # annotation_fields = [sf for sf in self._meta['columns'] if getattr(self, sf).get_annotation(view_attrs)]
        # queryset = (
        #     self._meta['model']
        #     .objects.using(self._meta['database'])
        #     .annotate(**{sf: getattr(self, sf).get_annotation(self._view_params) for sf in annotation_fields})
        # )

        queryset = self._meta['queryset'](view_attrs)

        read_permissions = self._meta['permissions'].get('read', {}).keys()
        if len(read_permissions):  # TODO : Comportement par défaut = lecture autorisée pour tous. Sans doute à revoir...
            queryset = queryset.filter(reduce(lambda a, b: a | b, [Q(roles__contains=k) for k in read_permissions]))

        if skip_base_filter:
            return queryset.distinct()
        else:
            return queryset.filter(*self.base_filter_args[0], **self.base_filter_args[1]).distinct()

    def get_record(self, view_attrs, pk):
        # 1 - Get state and roles for this row
        pkf = self._meta['id_field']
        qs = (
            self.get_base_queryset(view_attrs, skip_base_filter=True)
            .filter(**{pkf: pk})
            .annotate(
                **{
                    sf: getattr(self, sf).get_annotation(self._view_params)
                    for sf in [self._meta['state_field'], self._meta['roles_field']]
                    if getattr(self, sf).get_annotation(self._view_params)
                }
            )
        )
        if qs.exists():
            tmp = qs.values(*[self._meta['state_field'], self._meta['roles_field']])[0]
        else:
            raise RuntimeError("Record not found ! SmartView={}, pk={}".format(repr(self), pk))
        row_state = tmp[self._meta['state_field']]
        row_roles = tmp[self._meta['roles_field']].split(",")
        return qs.get(), row_state, row_roles

    def update(self, request, updater):
        """Méthode qui réalise effectivement la modification dans la base ET retourne le résultat de cette demande de modification
        qui peut éventuellement être une erreur (droits insuffisants, type de données, etc.)

        La vérification des droits est refaite à chaque requête (on ne fait pas confiance à javascript)

        Si des champs (calculés dans la base) ont des dépendances, ils sont également mis à jour.

        Tous les champs modifiés par la modification sont retournés dans la réponse : Ceux de la base (directement modifiés ou
          parce que c'était des dépendances) et ceux calculés 'au vol' dans le cadre de la SmartView.
        """
        # TODO: Multiple rows update ?

        # 1 - Get state and roles for this row
        # pkf = self._meta.id_field
        # qs = (
        #     self._meta.model.objects.filter(**{pkf: updater["where"][pkf]})
        #     .annotate(
        #         **{
        #             sf: getattr(self, sf).get_annotation(request)
        #             for sf in [self._meta.state_field, self._meta.roles_field]
        #             if getattr(self, sf).get_annotation(request)
        #         }
        #     )
        #     .values(*[self._meta.state_field, self._meta.roles_field])[0]
        # )
        # row_state = qs[self._meta.state_field]
        # row_roles = qs[self._meta.roles_field].split(",")

        # Primary Key Field name
        pkf = self._meta['id_field']

        record, row_state, row_roles = self.get_record(self._view_params, updater["where"][pkf])

        # 2 - Check writing permission for theses columns
        perms = self._meta['permissions']
        # --> perms is now the whole permissions dict

        if not perms.get("write", False):
            return {"error": {"message": _("Cet enregistrement ne peut pas être modifié")}}
        perms = perms.get("write", False)
        # --> perms is now the write permissions dict (still depends on state and role)

        if not perms.get(row_state, False):
            return {"error": {"message": _("Cet enregistrement ne peut pas être modifié dans cet état")}}
        perms = perms.get(row_state, False)
        # --> perms is now the write and state permissions dict (still depends on role)

        allowed_fields = set()
        for role in row_roles:
            if perms.get(role, False):
                # At least this very role is allowed to modufy this record ; let's continue
                allowed_fields = allowed_fields.union({fieldname for fieldname, allowed in perms.get(role, {}).items() if allowed})
        if not allowed_fields:
            return {"error": {"message": _("Vos droits ne permettent pas de modifier cet enregistrement")}}

        # 3 - Update the row(s)

        # record = self._meta.model.objects.filter(**{pkf: updater["where"][pkf]}).get()

        # Liste des champs qui vont devoir être sauvés dans la base : champs modifiés et dépendances
        fields_to_save = []

        # Liste de champs qui vont devoir être retournés dans la réponse : champs modifiés dans la base et champs calculés 'au vol'
        smartfields_to_read = []

        for name, value in updater["set"].items():
            # print("  AJA> update:", name, value, allowed_fields, getattr(self, name).get('title', 'table.html'))

            if name not in allowed_fields:
                return {
                    "error": {
                        "message": _("Vos droits ne permettent pas de modifier le champ '{}' de cet enregistrement").format(
                            getattr(self, name).get('title', 'table.html')
                        )
                    }
                }

            if name in self._meta['data_fields']:
                smartfields_to_read.append(name)
            if hasattr(getattr(self, name), "alters"):
                # print("  AJA>  alters...", getattr(self, name).alters)
                for f in getattr(self, name).alters:
                    if getattr(self, f).get('data') is not None:
                        smartfields_to_read.append(f)

            # Vérifie que le champs existe dans la smartview et est bien lié à la base
            if isinstance(getattr(self, name).get('data'), str):
                # Modification effective de l'enregistrement...

                model_fieldname = getattr(self, name).get('data')
                # Cas particulier de la FK
                if isinstance(getattr(self._meta['model'], model_fieldname).field, ForeignKey):
                    if value == 'null':
                        setattr(record, model_fieldname, None)
                    elif value != '':
                        setattr(
                            record,
                            model_fieldname,
                            getattr(self._meta['model'], model_fieldname).field.related_model.objects.get(pk=int(value)),
                        )
                    # if value = '' ==> do nothing (returned by tabulator.js if user click out of the list)
                # Cas des valeurs numériques (une chaîne vide peut signifier 'null')
                elif any(
                    [
                        isinstance(getattr(self._meta['model'], model_fieldname).field, klass)
                        for klass in (DecimalField, IntegerField)
                    ]
                ):
                    if value is None or value == "":
                        setattr(record, model_fieldname, None)
                    else:
                        try:
                            setattr(record, model_fieldname, float(value))
                        except ValueError as err:
                            return {
                                'error': {
                                    'message': _("La valeur '{}' ne peut pas être convertie en nombre. ({})").format(value, err)
                                }
                            }
                # Cas des dates (une chaîne vide peut signifier 'null')
                elif any(
                    [isinstance(getattr(self._meta['model'], model_fieldname).field, klass) for klass in (DateField, DateTimeField)]
                ):
                    if value is None or value == "":
                        setattr(record, model_fieldname, None)
                    else:
                        try:
                            setattr(record, model_fieldname, value)
                        except ValueError as err:
                            return {
                                'error': {
                                    'message': _("La valeur '{}' ne peut pas être convertie en date(heure). ({})").format(
                                        value, err
                                    )
                                }
                            }
                # Cas 'normal'
                else:
                    setattr(record, model_fieldname, value)

                # Il faut évidemment sauvgarder cette modification
                fields_to_save.append(model_fieldname)

                # ajoute les champs qui dépendent de lui dans les listes de champs 'dépendants' (calculés à l'enregistrement)
                if hasattr(getattr(self, name), "alters"):
                    # print("  AJA>  alters...", getattr(self, name).alters)
                    for f in getattr(self, name).alters:
                        if isinstance(getattr(self, f).get('data'), str):
                            fields_to_save.append(getattr(self, f).get('data'))
                            # print("  which is a model_fieldname:", repr(getattr(self, f).get('data')))

                # On ajoute aussi les champs 'timestamp' s'il y en a
                fields_to_save += self._meta['update_timestamps']
                smartfields_to_read += self._meta['update_timestamps']

            else:
                # Si on arrive ici, c'est que le champ à modifier n'est pas un champ d'enregistrement
                smart_field = getattr(self, name)
                smart_field.update_instance(request, record, name, updater, allowed=bool(name in allowed_fields))

        try:
            record.save(update_fields=fields_to_save)
        except ValidationError as err:
            return {"error": {"message": str(err)}}
        except ValueError as err:
            return {"error": {"message": str(err)}}

        qs_list = []
        # 4.1 - Get _all_ updated fields in this row/record (updated field AND altered ones)
        record_queryset = (
            self.get_base_queryset(self._view_params, skip_base_filter=True)
            .filter(**{pkf: updater["where"][pkf]})
            .values(*smartfields_to_read, _row_id=F(pkf))
        )
        qs_list.append(record_queryset)

        # 4.2 - Get _all_ updated fields in other rows/records
        for sf in smartfields_to_read:
            for other_rows_desc in getattr(self, sf).get('alter_rows', '', []):
                # same_field_value = (
                #     self.get_base_queryset(self._view_params, skip_base_filter=True)
                #     .filter(pk=updater['where'][pkf])
                #     .values_list(other_rows_desc['same_field'])[0]
                # )
                # print(f"{sf=}, {other_rows_desc=}, {same_field_value=}")
                qs_list.append(
                    self.get_base_queryset(self._view_params, skip_base_filter=False)
                    .filter(
                        **{
                            other_rows_desc['same_field']: self.get_base_queryset(self._view_params, skip_base_filter=True)
                            .filter(pk=updater['where'][pkf])
                            .values_list(other_rows_desc['same_field'])[0]
                        }
                    )
                    .values(*other_rows_desc['fields'], _row_id=F(pkf))
                )

        # 5 - Return them
        return {"updated": reduce(lambda a, b: a + list(b), qs_list, [])}

    def export_xlsx(self, export, queryset, view_params):
        def boolean_to_excel(value):
            return {True: _("Oui"), False: _("Non")}.get(value, None)

        def html_to_excel(value):
            return HTMLFilter.convert_html_to_text(value or '')

        def choice_to_excel(choices, value):
            try:
                ret = choices[value]
            except KeyError:
                ret = choices[str(value)]
            return ret

        def conditional_to_excel(value):
            return next((item for item in json.loads(value)['fields'] if item is not None), None)

        def analysis_to_excel(value):
            # analysis = json.loads(value)
            analysis = value or {}
            if 'anomalies' in analysis and isinstance(analysis['anomalies'], list):
                return '\n'.join([str(anomaly['level']) + ' - ' + anomaly['message'] for anomaly in analysis['anomalies']])
            else:
                return 'ø'

        user_prefs = UserSettings(view_params['user'])[self._meta['appname']]['tabulator-' + self._prefix]
        columns = []
        formats = {}
        converters = {}
        for column in user_prefs['columns']:
            if (
                'field' in column
                and user_prefs.get('show-column', {col: True for col in self._meta['columns']}).get(column['field'], True)
                and not getattr(self, column['field']).get("hidden")
                and not isinstance(getattr(self, column['field']), ToolsSmartField)
            ):
                columns.append(column['field'])
                smart_field = getattr(self, column['field'])
                formats[column['field']] = {
                    'title': smart_field.get('title', 'xlsx', default=str(column['field'])),
                    'width': (column.get('width') or 60) / 6,  # Valeur totalement arbitraire...
                    'cell': {'text_h_align': {'left': 1, 'center': 2, 'right': 3}.get(smart_field.get('hoz_align', 'xlsx'))},
                }
                # print(smart_field.get('format'))
                if smart_field.get('format') == 'money':
                    formats[column['field']]['cell']['num_format'] = '# ##0,00 €'
                elif smart_field.get('format') == 'boolean':
                    converters[column['field']] = boolean_to_excel
                elif smart_field.get('format') == 'datetime':
                    formats[column['field']]['cell']['num_format'] = 'dd/mm/yyyy'
                elif smart_field.get('format') == 'html':
                    converters[column['field']] = html_to_excel
                elif smart_field.get('format') == 'conditional_integer':
                    converters[column['field']] = conditional_to_excel
                elif smart_field.get('format') == 'conditional_money':
                    converters[column['field']] = conditional_to_excel
                    formats[column['field']]['cell']['num_format'] = '# ##0,00 €'
                elif smart_field.get('format') == 'choice':
                    lookup = smart_field.get('choices')
                    if callable(lookup):
                        lookup = lookup(view_params)
                    lookup = dict(lookup)
                    lookup.update({None: None})
                    converters[column['field']] = partial(choice_to_excel, lookup)
                elif smart_field.get('format') == 'analysis':
                    converters[column['field']] = analysis_to_excel

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = "attachment; filename={}".format(export.get("filename", "file"))
        wb = Workbook(response, {'remove_timezone': True})
        wd = DataWorksheet(wb, _("Feuille"), formats, converters)
        wd.prepare().put_query_set(queryset).finalize()

        wb.close()

        return response

    def api_handle(self, path: list[str], view_params: dict):
        if hasattr(self, path[0]):
            return getattr(self, path[0]).api_handle(path[1:], view_params)
        else:
            return JsonResponse(
                {
                    'error': 1,
                    'message': _("API object (SmartField from {}) not found : {}").format(self._meta['name'], path[0]),
                }
            )

    def handle(self):
        """Méthode qui gère les requêtes en provenance de la vue lorsque la page a déjà été affichée
        Ce sont toutes les requêtes JSON (demande du contenu du tableau, mise à jour des champs) et d'exports
        """
        # TODO: Add "dynamic" filters data
        # print("AJA>", request.POST, request.POST.get('smart_view_prefix'), self.prefix in request.POST.get('smart_view_prefix',
        # []))

        request = self._view_params['request']

        if self._prefix in request.POST.get('smart_view_prefix', ()):
            if request.POST.get('update'):
                # Update via JSON (pour le tableau)
                # print("AJA3", request.POST.get('update'))
                return JsonResponse(self.update(request, json.loads(request.POST.get('update'))))
            # elif 'create' in request.POST.get('smart_view_action', ()):
            #     print('Create !', request.POST)
            #
            #     return {'message':_("Hello !")}
            # elif 'update' in request.POST.get('smart_view_action', ()):
            #     print('Update !', request.POST)
            # elif 'delete' in request.POST.get('smart_view_action', ()):
            #     print('Delete !', request.POST)
        elif request.GET and request.GET.get("smart_view_prefix") == self._prefix:
            # print("AJA1", request.GET)
            # This request is for me !
            if request.GET.get("update"):
                return JsonResponse(self.update(request, json.loads(request.GET.get("update"))))
            else:
                # Demande de contenu pour JSON ou export => calcul QuerySet avec le contenu du tableau
                user_filters = filter_args(request.GET.get("filters", "{}"))
                # print("AJA>>>", user_filters)

                # annotation_fields = [sf for sf in self._meta['columns'] if getattr(self, sf).get_annotation(self._view_params)]
                # print("Annotations :", annotation_fields)

                query_set = (
                    self.get_base_queryset(self._view_params)
                    .filter(*self.view_filters[0], **self.view_filters[1])
                    .filter(*user_filters[0], **user_filters[1])
                )

                # fields = list(self._meta['data_fields']) + list(annotation_fields)
                # print("All :", fields)

                if request.GET.get("export") in self._meta['exports']:
                    export = self._meta['exports'][request.GET.get("export")]
                    # view_params = dict(user=request.user)
                    if export.get("engine") == "xlsx":
                        return self.export_xlsx(export, query_set, self._view_params)
                    else:
                        raise RuntimeError(_("Unknown export engine: {}").format(export.get("engine")))
                else:
                    return JsonResponse({"data": list(query_set.values(*self._meta['values_fields']))})
        # Renvoyer None indique à l'appelant (la vue) que la requête n'a pas été traitée

    def __str__(self):
        return self.as_html()


def smart_view_factory(name: str, config: dict):
    """
    A factory that returns a SmartView class from a configuration dictionary
    (read, for example, from a configuration file).

    Parameters
    ----------
    name : Name of the created class (please use CamelCase format)
    config : Dictionary which describe the SmartView class to build

    Returns
    -------
    a SmartView class, built from given configuration
    """

    attrs = {}

    # print(f"\nBuilding SmartView {name}:")
    # pprint(config)

    meta_class = type('Meta', (), {})

    try:
        model_name = config.get('model')
        if model_name is None:
            raise ValueError(_("No model provided"))
        elif (
            not isinstance(model_name, Sequence)
            or not len(model_name) == 2
            or not isinstance(model_name[0], str)
            or not isinstance(model_name[1], str)
        ):
            raise ValueError(_("Model must be given as a sequence of 2 strings (application_name, model_name)"))
        else:
            meta_class.model = apps.get_model(*model_name)
    except LookupError as l_err:  # The model does not exist
        raise ValueError(l_err)

    # The columns list
    meta_class.columns = tuple(config.get('columns', []).value)

    # The exports menu
    meta_class.exports = dict(config.get('exports')) or {}

    # The selectable columns menu entry
    meta_class.selectable_columns = config.get('selectable_columns', [])
    if isinstance(meta_class.selectable_columns, Container):
        meta_class.selectable_columns = meta_class.selectable_columns.value

    # User filters
    meta_class.user_filters = config.get('user_filters', {})
    if isinstance(meta_class.user_filters, Container):
        meta_class.user_filters = meta_class.user_filters.value
        # print(type(meta_class.user_filters))
    # pprint(meta_class.user_filters)

    # fields Settings
    meta_class.settings = config.get('settings', {})
    if isinstance(meta_class.settings, Container):
        meta_class.settings = meta_class.settings.value

    # New (computed) fields
    for new_field_name, new_field_def in config.get('add_field', {}).items():
        field_def = dict(new_field_def)
        # print(f"defining {new_field_name} : {field_def}")
        if 'data' in field_def and isinstance(field_def['data'], str):
            expression = SmartExpression(field_def['data'])
            # print(f"{expression.as_django_orm()}")
            field_def['data'] = expression.as_django_orm()
        attrs[new_field_name] = (ComputedSmartField, field_def)

    try:
        attrs['Meta'] = meta_class
        smart_view_class = type(name, (SmartView,), attrs)
    except RuntimeError as rt_err:
        # except FileNotFoundError as rt_err:
        raise ValueError(f"RuntimeError : {str(rt_err)}")

    return smart_view_class
