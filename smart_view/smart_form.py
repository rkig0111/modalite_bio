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
import re
from typing import Any, Dict, Optional

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import PermissionDenied, ValidationError
from django.forms import CheckboxSelectMultiple, ModelMultipleChoiceField, MultipleChoiceField
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.forms import CharField, forms
from django.forms.utils import ErrorList
from django.forms import Form
from django.forms import ModelForm
from django.forms.widgets import Input, NullBooleanSelect, Select, TextInput  # noqa


class EurosField(CharField):
    """This is a (Django) **Form** field (not a Django Model field)"""

    def __init__(self, *args, **kwargs):
        if 'max_digits' in kwargs:
            del kwargs['max_digits']
        if 'decimal_places' in kwargs:
            self.decimal_places = kwargs['decimal_places']  # Unused for now
            del kwargs['decimal_places']

        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        if value is not None:
            if not isinstance(value, str):
                value = "{:,}".format(int(float(value))).replace(',', '\u202f') + " €"
            elif value == '':
                value = None
        return value

    def has_changed(self, initial: Optional[Any], data: Optional[Any]) -> bool:
        r = super().has_changed(initial, data)
        return r

    def to_python(self, value: Optional[Any]) -> Optional[str]:
        # TODO: faire les choses dans l'ordre (cf. Django documentation)
        init_value = value
        if value == '':
            value = None
        elif isinstance(value, str):
            # Supprimer les '€' et les espaces de toute sorte + remplacer les éventuelles ',' par des '.'
            value = re.sub("[€\\s]", "", value).replace(",", ".")
            if value == '':
                value = None
            else:
                try:
                    value = int(float(value))
                except ValueError:
                    err = forms.ValidationError(
                        _("La valeur «%(value)s» n'est pas un montant valide"),
                        code='invalid',
                        params={'value': init_value},
                    )
                    raise err

        return value


class MultiChoiceField(MultipleChoiceField):
    """This is a (Django) **Form** field (not a Django Model field)"""

    def __init__(self, *args, **kwargs):
        # AJA : I really don't know why, but 'encoder' and 'decoder' kwargs
        # are not handled by MultipleChoiceField but are provided by form creation factory...
        if 'encoder' in kwargs:
            # print(f"{kwargs['encoder']} {kwargs['decoder']}")
            del kwargs['encoder']
            del kwargs['decoder']
        super().__init__(*args, **kwargs)

    def clean(self, value):
        # The MultiChoiceField original clean method replace a empty list with None
        # This is not the behaviour we need here, so keep the [] and return it
        return value


class SmartInputWidgetMixin:
    """For future use"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MoneyInputWidget(SmartInputWidgetMixin, Input):
    class Media(forms.Media):
        js = ('smart_view/js/money.js',)
        css = {'all': ('smart_view/css/jquery.flexdatalist.min.css',)}


class AutocompleteInputWidget(SmartInputWidgetMixin, Input):
    template_name = 'smart_view/autocomplete_widget.html'

    class Media(forms.Media):
        js = ('smart_view/js/jquery.flexdatalist.min.js',)
        css = {'all': ('smart_view/css/jquery.flexdatalist.min.css',)}

    def __init__(self, smart_field=None):
        super().__init__()
        self.smart_field = smart_field
        # self.attrs['list'] = 'list__{}'.format(self.smart_field.get('fieldname'))

    def get_context(self, name: str, value: Any, attrs: Optional[dict]) -> Dict[str, Any]:
        context = super().get_context(name, value, attrs)
        if attrs.get('disabled', False):
            lookup = self.smart_field.get("lookup", context='form.html')
            if callable(lookup):
                lookup = dict(lookup(view_params={}))
            if isinstance(lookup, dict):
                context['display_value'] = lookup[value]
        return context

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super().render(name, value, attrs=attrs, renderer=renderer)
        if attrs.get('disabled', False):
            return text_html

        choices = self.smart_field.get("choices", context='form.html')
        if callable(choices):
            choices = dict(choices(view_params=dict({'user': self._request.user})))

        # Ensure that everything in choices is a string (for html...)
        if isinstance(choices, dict):
            choices = {str(k): str(v) for k, v in choices.items()}
        elif isinstance(choices, list) or isinstance(choices, tuple):
            choices = {str(k): str(v) for k, v in choices}

        if self.smart_field.get('null'):
            # The '' value will be converted to None by form save() function
            # choices[None] = _("-- Indéfini --")
            choices[''] = _("-- Indéfini --")

        # print(f"render {name} {value} {choices.get(value, '')}")
        # data_list = '<datalist id="list__{}">'.format(self.smart_field.get('fieldname', name))
        # for item_value, item_display in choices.items():
        #     data_list += '<option value="{}">{}</option>'.format(item_value, item_display)
        # data_list += '</datalist>'
        script = """<script>
        $('#id_{}').flexdatalist({{
         minLength: 0,
         url: '{url}',
         focusFirstResult: true,
         searchContain: true,
         cache:false,
         selectionRequired: true,
         valueProperty: 'value',
         originalValue: "{value}",
         noResultsText: \"Pas de résultat trouvé pour '{{keyword}}'\"
        }}).on('change:flexdatalist', function(event, set, options) {{
         // Simule le "onChange" sur le champ original
         var event = new CustomEvent('change');
         this.dispatchEvent(event);
        }}).on('init:flexdatalist', function(event1, data)
         {{var event = new CustomEvent('change');
         event1.target.classList.add('ignore-first-modification');
         event1.target.value = "{value}";
         event1.target.nextSibling.value = "{value_label}";
         this.dispatchEvent(event);}});
        </script>""".format(
            name,
            url=self.url + 'get_flexdatalist_choices/',
            value=value,
            value_label=choices.get(str(value), ''),
        )
        return text_html + script


class MultiChoiceInputWidget(SmartInputWidgetMixin, CheckboxSelectMultiple):
    class Media(forms.Media):
        pass

    def __init__(self, smart_field=None):
        # widgets = [CheckboxInput(), CheckboxInput()]
        super().__init__(attrs={'class': 'smart-multichoices'})
        self.smart_field = smart_field
        # print(f"MultiChoice.__init__({smart_field})")

    def format_value(self, value):
        return [cx[0] for cx in self.choices if cx[0] in value]


class SmartFormMixin:
    user_roles = ()
    form_role = ()

    class Media:
        css = {
            "all": ("smart_view/css/smart-view-form.css",),
        }
        js = ("smart_view/js/form-helper.js",)

    def __init__(self, *args, **kwargs):
        # self._smart_fields_dict = {}
        if 'user_roles' in kwargs:
            self.user_roles = kwargs['user_roles']
            kwargs.pop('user_roles')
        if 'url' in kwargs:
            self.url = kwargs['url']
            kwargs.pop('url')
        super().__init__(*args, **kwargs)

    @property
    def media(self):
        """"""
        # Collect media from columns...
        media = forms.Media(self.Media)
        # TODO: restrict to smartfields used in the form // Warning, no subforms at this time !!
        if hasattr(self, '_smart_fields_dict'):
            # print("Media 1:", self.Media)
            # print("Media:", self._smart_fields_dict)
            for fieldname in self._smart_fields_dict.keys():
                # print("  field", fieldname)
                media += self._smart_fields_dict[fieldname].form_media

        # And the widgets
        for field in self.fields.values():  # noqa
            media += field.widget.media

            # print("  media", self._smart_fields_dict[fieldname].form_media)
        # if self._meta.form_layout:
        #     media += forms.Media(SmartViewBaseForm.Media)
        # print('returning Media:', media)
        return media

    def clean(self):
        if isinstance(self, ModelForm):
            # Ensure current user can write all fields of the form
            # This is a 'hard' security since form should be built to avoid this case
            errors = {}
            if self.instance.pk is None:
                # Creating a new object in the database...

                # Two step validation :
                # Step 1 : Can the user create a record ?
                allowed = set(self.smart_view_class._meta['permissions']['create'])
                if not (allowed & set(self.user_roles)):
                    raise ValidationError(_("Vous n'avez pas les droits suffisants pour créer un élément"))

                # Step 2 : Check every fields (similar code than with 'update',
                # but instance state is None and roles are user_roles not instance roles)
                permissions = self.smart_view_class._meta['permissions']['write'].get(None, {})
                for fieldname in self.changed_data:
                    can_update = False
                    for role in self.user_roles:
                        if permissions.get(role, {}).get(fieldname, False):
                            can_update = True
                            break
                    if not can_update:
                        errors[fieldname] = _("Vous n'avez pas les droits suffisants pour ajouter ce champ.")
            else:
                # Check fields for updating a existing object OR creating a new one in the database
                permissions = self.smart_view_class._meta['permissions']['write'].get(self.instance_state, {})

                for fieldname in self.changed_data:
                    can_update = False
                    for role in self.instance_roles:
                        if permissions.get(role, {}).get(fieldname, False):
                            can_update = True
                            break
                    if not can_update:
                        errors[fieldname] = _("Vous n'avez pas les droits suffisants pour modifier ce champ.")

            # Check for mandatory smart_fields
            # Do not handle model mandatory (not null, not blank...) because Django already take care of that
            for smart_field_name, smart_field in self.smart_view_class._meta['smartfields_dict'].items():
                needed = not smart_field.get('blank', context='form.html', default=True) and smart_field_name in self.cleaned_data
                if needed:
                    if self.cleaned_data.get(smart_field_name) is None or self.cleaned_data.get(smart_field_name) == '':
                        errors[smart_field_name] = _("Ce champ est obligatoire")

            if errors:
                raise ValidationError(errors)
        return super().clean()

    def api_handle(self, path: list[str], request: HttpRequest):
        return JsonResponse({'error': 1, 'message': _("API object not found : {}").format(path[0])})

    def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        "Output HTML. Used by as_table(), as_ul(), as_p()."
        # Errors that should be displayed above all fields.

        # Cette version d'_html_output() est destinée à remplacer celle d'origine de BaseForm pour la rendre plus configurable
        # et notamment récupérer des infos dans la configuration des champs de la SmartView

        top_errors = self.non_field_errors().copy()
        output, hidden_fields = [], []

        for name, field in self.fields.items():
            html_class_attr = ''
            bf = self[name]
            bf_errors = self.error_class(bf.errors)
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([_('(Hidden field %(name)s) %(error)s') % {'name': name, 'error': str(e)} for e in bf_errors])
                hidden_fields.append(str(bf))
            else:
                if self.instance_state is None:
                    roles = self.user_roles
                else:
                    roles = self.instance_roles

                instance_permissions = self.smart_view_class._meta['permissions'].get('write', {}).get(self.instance_state, {})
                read_only = True
                if not self.read_only:
                    for role in roles:
                        if instance_permissions.get(role, {}).get(name):
                            read_only = False
                            break

                # Create a 'class="..."' attribute if the row should have any
                # CSS classes applied.
                css_classes = bf.css_classes(['test-sv-class'] + (['read-only'] if read_only else []))
                if css_classes:
                    html_class_attr = ' class="%s"' % css_classes

                if errors_on_separate_row and bf_errors:
                    output.append(error_row % str(bf_errors))

                if bf.label:
                    label = conditional_escape(bf.label)
                    label = bf.label_tag(label) or ''
                else:
                    label = ''

                if field.help_text:
                    help_text = help_text_html % field.help_text
                else:
                    help_text = ''

                # Don't know how to handle ModelMultipleChoiceField (m2m)... So avoid it for now
                if read_only and isinstance(bf.field.widget, Select) and not isinstance(bf.field, ModelMultipleChoiceField):
                    widget = bf.as_widget(widget=TextInput(), attrs={'readonly': read_only})
                else:
                    widget = bf.as_widget(attrs={'readonly': read_only})

                output.append(
                    normal_row
                    % {
                        'errors': bf_errors,
                        'label': label,
                        'field': widget,
                        'help_text': help_text,
                        'html_class_attr': html_class_attr,
                        'css_classes': css_classes,
                        'field_name': bf.html_name,
                    }
                )

        if top_errors:
            output.insert(0, error_row % top_errors)

        if hidden_fields:  # Insert any hidden fields in the last row.
            str_hidden = ''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                if not last_row.endswith(row_ender):
                    # This can happen in the as_p() case (and possibly others
                    # that users write): if there are only top errors, we may
                    # not be able to conscript the last row for our purposes,
                    # so insert a new, empty row.
                    last_row = normal_row % {
                        'errors': '',
                        'label': '',
                        'field': '',
                        'help_text': '',
                        'html_class_attr': html_class_attr,
                        'css_classes': '',
                        'field_name': '',
                    }
                    output.append(last_row)
                output[-1] = last_row[: -len(row_ender)] + str_hidden + row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        return mark_safe('\n'.join(output))


class BaseSmartForm(SmartFormMixin, Form):
    pass


class BaseSmartModelForm(SmartFormMixin, ModelForm):
    def __init__(
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
        request=None,
        choices=None,
        user_roles=(),
        url=None,
    ):
        # noinspection PyArgumentList
        super().__init__(
            data=data,
            files=files,
            auto_id=auto_id,
            prefix=prefix,
            initial=initial,
            error_class=error_class,
            label_suffix=label_suffix,
            empty_permitted=empty_permitted,
            use_required_attribute=use_required_attribute,
            renderer=renderer,
            instance=instance,
            url=url,
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

        # Restrict possibles choices for given fields
        self.choices = choices or {}

        # Current user
        if request is not None:
            self.user = request.user

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

        # Indique aux widgets AutocompleteWidget quel est l'utilisateur
        # pour permettre le calcul dynamique des listes de choix
        # Little trick : We set attributes of the widget so it's easy to fetch this information at layout rendering

        # Compute this form permissions
        permissions = self.smart_view_class._meta['permissions']['write'][instance_state]
        form_permissions = {}
        for role in set(self.user_roles) | set(self.instance_roles):
            for fieldname, fieldname_permission in permissions.get(role, {}).items():
                if fieldname in form_permissions:
                    # Temporary crude priority permissions rule ==> max !
                    form_permissions[fieldname] = max(fieldname_permission, form_permissions[fieldname])
                else:
                    form_permissions[fieldname] = fieldname_permission

        # Scan fields and adjust properties if needed
        for fname, field in self.fields.items():
            field.label = self._smart_fields_dict[fname].get('title', 'form.html')
            field.help_text = self._smart_fields_dict[fname].get('help_text', 'form.html')
            # field.model_default = self._smart_fields_dict[fname].get('default', 'form.html')
            if self.read_only or not form_permissions.get(fname, False):
                field.disabled = True
            else:
                # Set field choices accordingly to current view/request
                field_choices = self._smart_fields_dict[fname].get('choices', 'form.html')
                if callable(field_choices):
                    field_choices = field_choices(view_params={'user': request.user, 'now': timezone.now()})
                if field_choices:
                    if isinstance(field_choices, dict):
                        field_choices = list(field_choices.items())
                    else:
                        field_choices = list(field_choices)

                if fname in self.choices:
                    # limit choices to those provided in the request
                    field_choices = [
                        choice
                        for choice in field_choices
                        if choice is not None
                        and choice[0] is not None
                        and (choice[0] in self.choices[fname] or str(choice[0]) in self.choices[fname])
                    ]

                if field_choices and field_choices[0] is not None and self._smart_fields_dict[fname].get('null', 'form.html'):
                    field_choices.insert(0, (None, '-+- Indéterminé -+-'))

                if field_choices:
                    field_choices.sort(key=lambda a: a[1])

                field.choices = field_choices
                if not isinstance(field.widget, NullBooleanSelect):
                    field.widget.choices = field_choices or []

                if self.choices and fname in self.choices and field.choices is not None:
                    match len(field.choices):
                        case 0:
                            raise PermissionDenied(
                                _("Vous ne pouvez pas afficher ce formulaire (droits insuffisants). {}.").format(
                                    self.choices[fname]
                                )
                            )
                        case 1:
                            # Do not disable the field as it prevent form to send a value, even if mandatory :-(
                            # field.disabled = True

                            # Ensure the pre-filled value is the only possible one (useful if the input is hidden)
                            field.initial = field.choices[0][0]

                # For autocomplete widget, a API url is also needed
                if isinstance(field.widget, AutocompleteInputWidget):
                    field.widget.url = self.url + str(fname) + '/'
                    field.widget._request = request
