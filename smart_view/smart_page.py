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
# Create your views here.
from __future__ import annotations

import json
import logging
from copy import copy, deepcopy
import collections.abc
from itertools import chain
from json import JSONDecodeError

# from pprint import pprint
from warnings import warn

from crispy_forms.layout import Div
from django.forms.utils import ErrorDict
from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from common import config
from common.base_views import BiomAidViewMixinMetaclass
from common.views import BiomAidViewMixin
from smart_view.layout import SmartLayoutButton
from smart_view.smart_view import smart_view_factory

logger = logging.getLogger(__name__)


def deep_update(src, updater):
    src = deepcopy(src)
    for k, v in updater.items():
        if isinstance(v, collections.abc.Mapping):
            src[k] = deep_update(src.get(k, {}), v)
        else:
            src[k] = v
    return src


class SmartPageMetaclass(BiomAidViewMixinMetaclass):
    def __new__(mcs: type, name: str, bases: tuple, attrs: dict):

        if name != 'SmartPage' and 'name' not in attrs:
            raise RuntimeError(_("La SpartPage '{}' n'a pas d'attribut 'name' !").format(name))

        # -------------------------------------------------------------
        # Dynamic SmartView handling
        if 'smart_view_class' not in attrs:
            if 'smart_view_config' in attrs:

                if isinstance(attrs['smart_view_config'], str):
                    cfg = None
                    smart_views = config.get('smart_views', [])
                    for smart_view in smart_views:
                        if smart_view.get('name') == attrs['smart_view_config']:
                            cfg = smart_view
                            break
                else:
                    cfg = attrs['smart_view_config']

                if cfg:
                    # print('  Building it from config...')
                    try:
                        attrs['smart_view_class'] = smart_view_factory(name + 'SmartView', cfg)
                    except ValueError as the_error:
                        # except FileExistsError as the_error:
                        logger.warning(
                            f'Error building SmartView for {name} : « {the_error} ». SmartPage content will not be displayed.'
                        )
                else:
                    logger.warning(
                        f'Error building SmartView for {name} : '
                        '« No valid configuration provided ». SmartPage content will not be displayed.'
                    )
            else:
                raise RuntimeError(
                    _("A SmartPage must have either a smart_view_class attribute" " or a smart_view_config that defines one")
                )

        # -------------------------------------------------------------

        smart_modes = {}
        # This is NOT a true MRO scan but works for now
        for base in reversed(list(bases)):
            for class_ in reversed(list(base.__mro__)):
                if hasattr(class_, 'smart_modes'):
                    smart_modes = class_.smart_modes
                elif hasattr(class_, 'smart_modes__update'):
                    smart_modes = deep_update(smart_modes, class_.smart_modes__update)
        if 'smart_modes' in attrs:
            smart_modes = attrs['smart_modes']
        elif 'smart_modes__update' in attrs:
            smart_modes = deep_update(smart_modes, attrs['smart_modes__update'])
        attrs['smart_modes'] = smart_modes

        if name != 'SmartPage':
            if 'smart_view_class' in attrs:
                if set(attrs['smart_modes'].keys()) != {None}:
                    form_class = attrs['smart_view_class'].get_form_class()
                    if not isinstance(form_class, type):
                        warn(
                            _("SmartView '{}' used in SmartPage {} should have a defined form").format(
                                repr(attrs['smart_view_class']), name
                            )
                        )
                        # TODO: If the SmartPage _do_ use forms (look into smart_modes), ensure that it is defined
            else:
                warn(_("SmartPage {} should have a smart_view_class attribute").format(name))

        new_class = super().__new__(mcs, name, bases, attrs)

        if (
            hasattr(new_class, 'smart_modes')
            and new_class.smart_view_class is not None
            and new_class.smart_view_class._meta['form_helper'].layout is not None
        ):
            form_helpers = {}
            for mode_name, mode_def in new_class.smart_modes.items():
                # Since we only modify Layout root properties, let's go for a shallow copy for now
                form_helpers[mode_name] = deepcopy(new_class.smart_view_class._meta['form_helper'])
                button_box = Div(css_class="form-buttons-box")
                for button_def in mode_def.get('buttons', []):
                    button_box.append(
                        SmartLayoutButton(
                            button_def.get('type', 'submit'),
                            button_def.get('value', 'record'),
                            button_def.get('label', 'Envoyer'),
                            message=button_def.get('message', ''),
                            redirect=new_class.get_url_name(button_def.get('redirect', None)),
                            redirect_params=button_def.get('redirect_params', '{}'),
                            redirect_url_params=button_def.get('redirect_url_params', ''),
                        )
                    )
                form_helpers[mode_name].layout.append(button_box)

                # la SmartPage se charge d'inclure les Media nécessaires, donc pas besoin de les mettre dans le <form></form>
                form_helpers[mode_name].include_media = False
            new_class.form_helpers = form_helpers

        return new_class


class SmartPage(BiomAidViewMixin, TemplateView, metaclass=SmartPageMetaclass):
    """
    Une SmartPage est une View (classe) qui permet de générer plusieurs vues (ou plus exactement plusieurs URLs)
    pour travailler sur un modèle unique, sur la base d'une SmartView principale (avec son modèle)
    Notamment, la SmartPage donne par défaut des vues pour :
    - Ajouter un élément au modèle
    - Modifier un élément du modèle
    - Voir un élément du modèle
    - Copier un élément du modèle (pour en créer un nouveau avec certains champs identiques)
    - Supprimer un élément du modèle
    - Voir (tableau / Smartview) des éléments du modèle

    Toutes ces opérations peuvent être configurées et en particulier tenir compte des rôles et des droits de l'utilisateur et
    être limités aux contraintes données par la SmartView (par exemple objets dans un état donné)
    ou être configurées vue par vue.

    Les vues générées seront nommée (pour utilisation de reverse() ou du tag {% url %}) sous la forme :
    appname-name-mode
    où :
      - appname est le nom de l'application (autodétecté)
      - name est le nom de la page, fourni dans l'attribut de classe 'name'
      - le nom du mode (celle décrite avec le mode 'None' a pour nom 'appname-name' tout simplement

    """

    name = '__undefined__'
    application = None
    smart_view_class = None

    header_message = None
    view_filters = None
    record_ok_message = _("Element {pk} enregistré")
    deleted_done_message = _("L'élément {pk} a été supprimé.")
    no_grant_to_delete_record_message = _("Vous n'avez pas les droits suffisants pour supprimer l'élément {pk}.")
    try_to_delete_wthout_confirm_message = _("L'élément {pk} ne peut être supprimé sans passer par le formulaire de confirmation")
    smart_modes = {
        # L'entrée None décrit le comportement par défaut (sans vue) car la page est aussi une vue !
        None: {
            'view': 'list',  # lister les objets du modèle est la vue par défaut
        },
        'create': {
            'view': 'create',  # Facultatif car c'est la vue par défaut si le nom est 'create"
            'title': _("Ajouter un élément"),
            'buttons': (
                {
                    'type': 'submit',
                    'label': _("Enregistrer et ajouter un autre élément"),
                    'value': 'record',
                    'redirect': 'create',  # Attention : Redirection vers le mode None (mode par défaut)
                    'redirect_url_params': lambda vp: vp['request_get'].urlencode(),
                },
                {
                    'type': 'submit',
                    'label': _("Ajouter et retour à la liste"),
                    'value': 'record-then-list',
                    'message': _("<br><br>Vous allez être redirigé vers la liste"),
                    'redirect': None,  # Attention : Redirection vers le mode None (mode par défaut)
                },
                {
                    'type': 'reset',
                    'label': _("Réinitialiser le formulaire"),
                    'redirect_url_params': lambda vp: vp['request_get'].urlencode(),
                },
            ),
        },
        'update': {
            'args': (('pk', 'int'),),
            'title': _("Modifier un élément"),
            'buttons': (
                {
                    'type': 'submit',
                    'label': _("Enregistrer et continuer à modifier"),
                    'value': 'record-then-update',
                    'message': '',
                    # 'redirect': None,  # Attention : Redirection vers le mode None (mode par défaut)
                    'redirect': 'update',  # Attention : Redirection vers le mode None (mode par défaut)
                    'redirect_params': '{%load l10n%}{"pk":{{pk|unlocalize}}}',
                },
                {
                    'type': 'submit',
                    'label': _("Enregistrer et retour à la liste"),
                    'value': 'record-then-list',
                    'message': _("<br><br>Vous allez être redirigé vers la liste"),
                    'redirect': None,  # Attention : Redirection vers le mode None (mode par défaut)
                },
                {
                    'type': 'reset',
                    'label': _("Réinitialiser le formulaire"),
                },
            ),
        },
        'copy': {
            'title': _("Copier un élément"),
            'args': (('pk', 'int'),),
            'exclude': (),
            'next': 'create',  # Par défaut, l'action après avoir copié le contenu d'une instance, c'est d'en créer une nouvelle
            'buttons': (
                {
                    'type': 'submit',
                    'label': _("Enregistrer"),
                    'value': 'record-then-list',
                    'message': _("<br>Vous allez être redirigé vers..."),
                    'redirect': None,  # Attention : Redirection vers le mode None (mode par défaut)
                },
                {
                    'type': 'reset',
                    'label': _("Réinitialiser le formulaire"),
                },
            ),
        },
        'view': {
            'args': (('pk', 'int'),),
        },
        'ask-delete': {
            'title': _("Supprimer un élément"),
            'view': 'view',
            'args': (('pk', 'int'),),
            'next': 'delete',
            'buttons': (
                {
                    'type': 'submit',
                    'label': _("Confirmer la suppression"),
                    'value': 'delete',
                    'message': _("<br>Vous allez être redirigé vers le tableau."),
                    'redirect': None,  # Attention : Redirection vers le mode None (mode par défaut)
                },
            ),
        },
        'delete': {
            'args': (('pk', 'int'),),
            'view': 'view',
            # Back to the default view after delete
            'next': None,
        },
    }
    template_name = 'smart_view/smart_page.html'
    prefix = 'table'
    # Le mode par défaut de la page
    mode = None

    # Nom du champ 'identifiant' présenté à l'utilisateur
    user_key_field = 'pk'

    @classmethod
    def get_url_patterns(cls):
        urlpatterns = []
        full_name = cls.name
        url_base = cls.name + '/'
        urlpatterns.append(
            path(
                url_base + '_api/<path:api_path>/',
                cls.as_view(),
                name=full_name + '-api',
            )
        )
        for mode_name, mode_definition in cls.smart_modes.items():
            assert isinstance(mode_definition, dict)
            kwargs_pattern = ''.join(
                '<{}:{}>/'.format(kwarg_def.get('type', 'str'), kwarg)
                for kwarg, kwarg_def in mode_definition.get('kwargs', {}).items()
            )
            if mode_name is None:
                urlpatterns.append(path(url_base + kwargs_pattern, cls.as_view(), name=full_name))
            else:
                if not mode_definition.get('args', None):
                    urlpatterns.append(
                        path(
                            url_base + mode_name + '/' + kwargs_pattern,
                            cls.as_view(mode=mode_name),
                            name=full_name + '-' + mode_name,
                        )
                    )
                else:
                    args = mode_definition.get('args', ())
                    args_str = '/'.join(['<' + (arg[1] + ':' if len(arg) == 2 else '') + arg[0] + '>' for arg in args])
                    urlpatterns.append(
                        path(
                            url_base + mode_name + '/' + args_str + '/',
                            cls.as_view(mode=mode_name),
                            name=full_name + '-' + mode_name,
                        )
                    )
        return urlpatterns

    @classmethod
    def get_url_name(cls, mode='__UNSPECIFIED__'):
        # Petite astuce pour éviter d'utiliser None lorsque le mode n'est pas précisé (car None signifie 'mode par défaut'...)
        if mode == '__UNSPECIFIED__':
            mode = cls.mode
        url_name = cls.application + ':' + cls.name
        if mode:
            url_name += '-' + mode
        return url_name

    def dispatch(self, request, *args, **kwargs):

        # Test for permission BEFORE instancing SmartViews
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return self.handle_no_permission()

        load_filters = {}

        for param, value in self.request.GET.items():
            if param != 'from' and param != 'filters':
                try:
                    load_filters[param] = {param: int(value)}
                except ValueError:
                    pass

        if 'filters' in self.request.GET:
            try:
                get_filters = json.loads(self.request.GET['filters'])
                if isinstance(get_filters, list):
                    for get_filter in get_filters:
                        if (
                            isinstance(get_filter, dict)
                            and 'name' in get_filter
                            and get_filter['name'] in self.smart_view_class._meta['user_filters']
                            and 'value' in get_filter
                        ):
                            load_filters[get_filter['name']] = get_filter['value']
            except JSONDecodeError:
                pass

        if hasattr(self, 'view_filters') and self.view_filters:
            view_filters = self.view_filters(request, *args, **kwargs)
        else:
            view_filters = None

        if self.smart_view_class is not None:
            self.main_smart_view = self.smart_view_class(
                prefix=self.name.replace('-', '_') + '_' + self.prefix,
                view_params=self.view_params,
                request=request,
                appname=self.my_app_name,
                view_filters=view_filters,
                load_filters=load_filters,
                url_prefix=self.url_prefix,
            )
            # Liste de toutes les SmartView gérés par cette page
            self._smart_views = {
                self.main_smart_view._prefix: self.main_smart_view,
            }
        else:
            self.main_smart_view = None
            self._smart_views = {}

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        # Try API first
        if 'api_path' in kwargs:
            path = kwargs['api_path'].split('/')
            if path[0] in self._smart_views:
                return self._smart_views[path[0]].api_handle(path[1:], self.view_params)
            else:
                return JsonResponse(
                    {
                        'error': 1,
                        'message': _("Unkown API path: {}").format(kwargs['api_path']),
                    }
                )

        # Essaye d'abord de voir si la requête n'est pas destinée à un objet SmartView de la page
        for smart_view in self._smart_views.values():
            response = smart_view.handle()
            # Si c'est le cas, on s'arrête là et on renvoie la réponse fournie par l'objet SmartView
            if isinstance(response, HttpResponse):
                return response

        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        # Essaye d'abord de voir si la requête n'est pas destinée à un objet SmartView de la page
        for smart_view in self._smart_views.values():
            response = smart_view.handle()
            # Si c'est le cas, on s'arrête là et on renvoie la réponse fournie par l'objet SmartView
            if isinstance(response, HttpResponse):
                return response

        mode_definition = self.smart_modes[self.mode]

        # Par défaut, pas de message (mais pas d'erreur non plus => message est une `str`)
        message = ""

        # Par défaut, pas de redirection après traitement du POST
        redirect_after = None
        redirect_after_params = None
        redirect_after_url_params = None

        # Par défaut, pas d'instance concernée
        instance = None
        instance_state = None
        instance_roles = ()

        # L'action à faire est définie dans la définition du mode ou est le nom du mode (par défaut)
        action = mode_definition.get('action', self.mode)

        main_form = None
        if action in ('create', 'update'):
            if action == 'update':
                (
                    instance,
                    instance_state,
                    instance_roles,
                ) = self.main_smart_view.get_record(self.view_params, kwargs['pk'])
            main_form = self.main_smart_view.get_form_class()(
                request.POST,
                request.FILES,
                prefix=self.main_smart_view._prefix,
                instance=instance,
                instance_state=instance_state,
                instance_roles=instance_roles,
                user_roles=self._user_roles,
                request=request,
                url=self.reverse(self.get_url_name(None)) + '_api/' + self.main_smart_view._prefix + '/',
            )
            if main_form.is_valid():
                main_form.save()

                # Used for subforms/formsets
                instance = main_form.instance

                # TODO: This message should be customizable !!

                # équivalent de record_to_dict() mais en ajoutant les champs non éditables
                record_dict = {
                    f.name: f.value_from_object(instance)
                    for f in chain(
                        instance._meta.concrete_fields,
                        instance._meta.private_fields,
                        instance._meta.many_to_many,
                    )
                }

                params = dict(**record_dict, pk=main_form.instance.pk)
                message = self.record_ok_message.format(**params)
                main_form = None  # Pour éviter de renvoyer un formulaire pré-rempli

                subforms = [
                    sfc(
                        request.POST,
                        request.FILES,
                        instance=instance,
                        initial=sfc.smart_field_class.formset_initial(user=request.user),
                        form_kwargs={'user': request.user},
                    )
                    for sfc in self.main_smart_view.get_subforms_classes()
                ]
                # Warning ! These form can also be Formsets !
                for form in subforms:
                    if form.is_valid():
                        # print("form:", repr(form), repr(form.model), repr(form.instance), repr(form.extra_forms))
                        form.save()
                    else:
                        # print("Errors:", form.errors)
                        # There is only subforms (inline formset) errors... What to do with that ???
                        # TODO:...
                        ...
            else:
                message = main_form.errors
                # If there is errors, do not event try to validate/save subforms...
                # Maybe redirect toward a 'modify' view with subforms errors highlighed ?
                # This mean subform can block main form record ?
                # for fieldname in main_form.errors:
                #     print("field error", fieldname)

        elif action == 'delete':
            # S'assurer que l'utilisateur a bien confirmé la suppression
            if 'form_action' in request.POST and request.POST.get('form_action') == 'delete':
                (
                    instance,
                    instance_state,
                    instance_roles,
                ) = self.main_smart_view.get_record(self.view_params, kwargs['pk'])
                # équivalent de record_to_dict() mais en ajoutant les champs non éditables
                record_dict = {
                    f.name: f.value_from_object(instance)
                    for f in chain(
                        instance._meta.concrete_fields,
                        instance._meta.private_fields,
                        instance._meta.many_to_many,
                    )
                }
                params = dict(**record_dict, pk=instance.pk)

                print(
                    "Trying to delete:",
                    instance,
                    instance_state,
                    instance_roles,
                    set(self.main_smart_view._meta['permissions'].get('delete', {}).get(instance_state, set())),
                )
                if set(self.main_smart_view._meta['permissions'].get('delete', {}).get(instance_state, set())) & set(
                    instance_roles
                ):
                    instance.delete()
                    # TODO: This message should be customizable !!
                    message = self.deleted_done_message.format(**params)
                else:
                    # TODO: This message should be customizable !!
                    message = self.no_grant_to_delete_record_message.format(**params)
            else:
                (
                    instance,
                    instance_state,
                    instance_roles,
                ) = self.main_smart_view.get_record(self.view_params, kwargs['pk'])
                # équivalent de record_to_dict() mais en ajoutant les champs non éditables
                record_dict = {
                    f.name: f.value_from_object(instance)
                    for f in chain(
                        instance._meta.concrete_fields,
                        instance._meta.private_fields,
                        instance._meta.many_to_many,
                    )
                }
                params = dict(**record_dict, pk=instance.pk)
                # TODO: This message should be customizable !!
                message = self.try_to_delete_wthout_confirm_message.format(**params)
        else:
            logger.warning(_("Unknown action/mode '{}' for POST method for view '{}'").format(self.mode, self.name))

        # Ajoute le message du bouton à la fin du texte si c'est une chaîne de cractère. Sinon, c'est que c'est une erreur et
        #   cela n'a pas d'intérêt
        if isinstance(message, str):  # Ce n'est pas une erreur !
            message += str(request.POST[request.POST['form_action'] + '-message'])
            redirect_after = request.POST[request.POST['form_action'] + '-redirect']
            redirect_after_params = json.loads(request.POST.get(request.POST['form_action'] + '-redirect_params', '{}'))
            redirect_after_url_params = request.POST.get(request.POST['form_action'] + '-redirect_url_params', '')

        if message:
            kwargs['message'] = message
        if main_form:
            kwargs['smart_view_form'] = main_form
        if redirect_after:
            kwargs['redirect_after'] = redirect_after
        if redirect_after_params:
            kwargs['redirect_after_params'] = redirect_after_params
        if redirect_after_url_params:
            kwargs['redirect_after_url_params'] = redirect_after_url_params

        return self.get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mode_definition = self.smart_modes[self.mode]

        # Try to get initial values from URL query string
        initial = {}
        if 'initial' in self.view_params['request_get']:
            try:
                initial = json.loads(self.request.GET['initial'])
            except JSONDecodeError:
                logger.warning(_("Form initial value is not correct JSON: '{}'.").format(self.request.GET['initial']))
            if not isinstance(initial, dict):
                initial = {}
                logger.warning(_("Form initial value is not a dict': {}'.").format(self.request.GET['initial']))

        # Try to get choices values from URL query string
        choices = {}
        if 'choices' in self.request.GET:
            try:
                choices = json.loads(self.request.GET['choices'])
            except JSONDecodeError:
                logger.warning(_("Form 'choices' value is not correct JSON: '{}'.").format(self.request.GET['choices']))
            if not isinstance(choices, dict):
                choices = {}
                logger.warning(_("Form initial value is not a dict': {}'.").format(self.request.GET['choices']))

        view_mode = mode_definition.get('view', self.mode)
        context['title'] = mode_definition.get('title', context['title'])

        context['args'] = [kwargs[arg[0]] for arg in mode_definition.get('args', ())]

        params = self.request
        if callable(self.header_message):
            context['header_message'] = self.header_message(params)
        else:
            context['header_message'] = self.header_message

        # Si la page ne procure pas de message, essayer de voir ce que propose la SmartView principale
        if context['header_message'] is None and self.main_smart_view:
            if callable(self.main_smart_view._meta['help_text']):
                context['header_message'] = self.main_smart_view._meta['help_text'](params)
            else:
                context['header_message'] = self.main_smart_view._meta['help_text']

        if context['header_message'] is None:
            context['header_message'] = ""

        context['redirect_after_message'] = kwargs.get('redirect_after')

        if hasattr(self, 'form_helpers'):
            context['smart_view_form_helper'] = copy(self.form_helpers.get(self.mode))
        else:
            context['smart_view_form_helper'] = None

        # If there is no form post message (error, recorded ack...) then check if there is a default form message
        if not context.get('message') and self.main_smart_view._meta['form_message']:
            message = self.main_smart_view._meta['form_message']
            if callable(message):
                message = message(self.view_params)
            context['message'] = message

        next_mode = mode_definition.get('next', self.mode)
        next_kwargs = {kwarg: kwargs.get(kwarg) for kwarg in self.smart_modes.get(next_mode).get('kwargs', {}).keys()}
        if next_mode in ('update', 'view', 'delete', 'ask-delete'):
            context['smart_view_form_helper'].form_action = self.reverse(
                self.get_url_name(next_mode),
                kwargs=dict(next_kwargs, **{'pk': kwargs['pk']}),
            )
        elif next_mode is not None and context['smart_view_form_helper'] is not None:
            context['smart_view_form_helper'].form_action = self.reverse(self.get_url_name(next_mode), kwargs=next_kwargs)

        if self.mode in ('create', 'update', 'copy', 'view', 'ask-delete'):
            if 'pk' in kwargs:
                (
                    instance,
                    instance_state,
                    instance_roles,
                ) = self.main_smart_view.get_record(self.view_params, kwargs['pk'])
            else:
                instance, instance_state, instance_roles = None, None, ()

            if mode_definition.get('next'):
                context['url_name'] = self.get_url_name(mode_definition.get('next'))
            else:
                context['url_name'] = self.get_url_name(self.mode)

            if self.mode == 'copy':
                initial = dict(initial, **{'id': None})
                if self.main_smart_view._meta['fields_to_copy']:
                    for fieldname in self.main_smart_view._meta['fields_to_copy']:
                        initial[fieldname] = getattr(instance, fieldname)
                if self.main_smart_view._meta['initial_on_copy'] and isinstance(
                    self.main_smart_view._meta['initial_on_copy'], dict
                ):
                    initial = dict(initial, **self.main_smart_view._meta['initial_on_copy'])
                    # initial = dict(initial, **self.main_smart_view._meta['initial_on_copy'])
                instance = None
                instance_roles = ()
                instance_state = None
                del context['args']

            if next_mode == 'create':
                # We are about to create a new record
                #   so get initial values from SmartView settings/SmartFields
                for field in self.main_smart_view._meta['smartfields_dict'].keys():
                    field_initial = getattr(self.main_smart_view, field).get('initial')
                    if callable(field_initial):
                        field_initial = field_initial(self.view_params)
                    if field_initial is not None:
                        initial[field] = field_initial
                        # print("  Initial:", field, "=>", field_initial)

            if 'smart_view_form' in kwargs:
                # Le formulaire déjà rempli est fourni dans les arguments
                #   Il vient de la methode post, par exemple dans le cas d'enregistrement qui a échoué (il contient les erreurs)
                context['smart_view_form'] = kwargs['smart_view_form']
            else:
                # Sinon, on crée un formulaire vide, rempli éventuellement avec l'instance récupérée
                context['smart_view_form'] = self.main_smart_view.get_form_class()(
                    prefix=self.main_smart_view._prefix,
                    initial=initial,
                    instance=instance,
                    read_only=True if view_mode == 'view' else False,
                    instance_state=instance_state,
                    instance_roles=instance_roles,
                    user_roles=self._user_roles,
                    request=self.request,
                    choices=choices,
                    url=self.reverse(self.get_url_name(None)) + '_api/' + self.main_smart_view._prefix + '/',
                )

            # -------------------------------------------------------------------------------------------------
            # Global form rules
            # -------------------------------------------------------------------------------------------------

            context['smart_view_form_helper_js_rules'] = {
                'global-form-modified': {
                    'input_selectors': ['input', 'select', 'textarea'],
                    'func': 'form-modified',
                },
            }
            for rule_name, rule_in in (self.smart_view_class._meta['form_rules'] or {}).items():
                rule = {
                    'func': rule_in['func'],
                    'expr': rule_in['expr'],
                    'input_selectors': [
                        '#id_' + context['smart_view_form'].prefix + '-' + dependency for dependency in rule_in.get('depends', [])
                    ],
                    'targets': ['#id_' + context['smart_view_form'].prefix + '-' + dependency for dependency in rule_in['targets']],
                }
                context['smart_view_form_helper_js_rules']['form-' + rule_name] = rule

            # -------------------------------------------------------------------------------------------------

            # Ajoute les règles de form-helper JS
            if context.get('smart_view_form_helper'):
                for smart_field_name in self.main_smart_view._meta['smartfields_dict'].keys():
                    context['smart_view_form_helper_js_rules'].update(
                        self.main_smart_view._meta['smartfields_dict'][smart_field_name].get_form_helper_rules(
                            self.request, form_prefix=self.main_smart_view._prefix
                        )
                    )
                context['smart_view_form_helper'].form_id = 'smart_view_form-' + context['smart_view_form'].prefix

        else:  # Fallback to basic SmartView mode
            context['smart_view'] = self.main_smart_view

        if isinstance(context.get('message'), ErrorDict):
            data = context.get('message').as_data()
            context['message'] = (
                _("Des erreurs ont empêché l'enregistrement&nbsp;:")
                + '<ul><li>'
                + '</li><li>'.join(
                    [
                        self.main_smart_view._meta['smartfields_dict'][field].get('title', context='html.form')
                        + '&nbsp;:<ul><li>'
                        + '</li><li>'.join([str(error.args[0]) for error in errors])
                        + '</li></ul>'
                        for field, errors in data.items()
                    ]
                )
                + '</li></ul>'
            )

        return context
