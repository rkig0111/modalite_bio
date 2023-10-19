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
"""
Module pour le layout
"""
from __future__ import annotations

from crispy_forms.layout import Field, LayoutObject, Fieldset
from crispy_forms.utils import TEMPLATE_PACK
from django.template import Template, Context
from django.template.loader import render_to_string


class SmartLayoutFieldset(Fieldset):
    def __init__(self, *args, **kwargs):
        def inner_field_names(fields):
            ret = []
            for f in fields:
                if isinstance(f, str):
                    ret.append(f)
                elif isinstance(f, LayoutObject):
                    ret += inner_field_names(f.fields)
            return ret

        self.level = kwargs.get('level')
        self.html_id = kwargs.get('html_id')

        if 'help_text' in kwargs:
            self.help_text = kwargs.get('help_text')
            kwargs.pop('help_text')
        else:
            self.help_text = None

        children = args[1:]
        self.columns = 1
        for child in children:
            if hasattr(child, 'smart_column'):
                max_col = child.smart_column[0] + child.smart_column[1] - 1
                if max_col > self.columns:
                    self.columns = max_col
        self.grid_template_columns = ' '.join(['auto'] * (self.columns * 2 - 1))
        kwargs['style'] = kwargs.get('style', '') + '; grid-template-columns:{};'.format(self.grid_template_columns)

        super().__init__(*args, **kwargs)

        # Build the list of all included field names
        self.inner_field_names = inner_field_names(self.fields)

    def get_smart_field_names(self):
        smart_field_names = []
        if hasattr(self, 'fields'):
            for field in self.fields:
                if hasattr(field, 'get_smart_field_names') and callable(field.get_smart_field_names):
                    smart_field_names.extend(field.get_smart_field_names())
        return smart_field_names

    def render(
        self,
        form,
        form_style,
        context,
        template_pack=TEMPLATE_PACK,
        extra_context=None,
        **kwargs,
    ):

        show_fieldset = False
        # print('+++ Fieldset +++', repr(self.inner_field_names), end='')
        for fname in self.inner_field_names:
            # print('')
            if fname in form.fields:
                field = form.fields[fname]
                # print('   ', fname, form.initial.get(fname), field.initial, end='')
                if not field.disabled:
                    show_fieldset = True
                    break
                # At this point, field.initial is identical to model field default if form has an instance
                if form.instance.pk is not None and form.initial.get(fname) != field.initial:
                    show_fieldset = True
                    break
                # print(' ==> HIDE', end='')
            else:
                # It's not a ModelField. So let's say, for now, that we need to show it
                # print(fname)
                show_fieldset = True
                break
        # print('\n ++ => SHOW = ', show_fieldset)

        if show_fieldset:
            # Render the fieldset only if there is something in it...
            rendered_fields = self.get_rendered_fields(form, form_style, context, template_pack, **kwargs)
            # TODO : Don't work well if there is only hidden fields (still show an empty fieldset...)
            legend = ""
            local_context = Context(context)
            if hasattr(form, 'instance'):
                local_context['instance'] = form.instance
            if self.legend:
                legend = str(Template(str(self.legend)).render(local_context))

            template = self.get_template_name(template_pack)
            return render_to_string(
                template,
                {
                    "fieldset": self,
                    "legend": legend,
                    "fields": rendered_fields,
                    "form_style": form_style,
                    'message': context.get('message'),
                    'help_text': self.help_text,
                    'html_id': ('id_' + form.prefix + '-fieldset-' + self.html_id) if self.html_id else None,
                },
            )
        else:
            return ''

    def __repr__(self):
        return (
            f"SmartLayoutFieldset(level={self.level}, legend='{self.legend}',"
            f" fields={', '.join(repr(field) for field in self.fields)})"
        )


class SmartLayoutComputedField(LayoutObject):
    template = '%s/layout/computed_field.html'

    def __init__(self, name, **kwargs):
        self.fields = []
        self.smart_field_name = name

        self.row_span = 1
        if 'smart_column' in kwargs:
            # If provided, the smart_column kw argument is a tuple/list (start_column, columns_span). Default is (1,1)
            self.label_column = '{}/{}'.format(kwargs['smart_column'][0] * 2 - 1, kwargs['smart_column'][0] * 2)
            self.field_column = '{}/{}'.format(
                kwargs['smart_column'][0] * 2,
                kwargs['smart_column'][0] * 2 + kwargs['smart_column'][1] * 2 - 1,
            )
            self.smart_column = kwargs['smart_column']
            kwargs.pop('smart_column')
        else:
            self.label_column = 1
            self.field_column = 2
            self.smart_column = (1, 1)
        super().__init__()

    def get_smart_field_names(self):
        return [self.smart_field_name]

    def render(
        self,
        form,
        form_style,
        context,
        template_pack=TEMPLATE_PACK,
        extra_context=None,
        **kwargs,
    ):
        sf = getattr(form.smart_view_class, self.smart_field_name)
        if form.instance and hasattr(form.instance, self.smart_field_name):
            value = getattr(form.instance, self.smart_field_name)
        elif form.initial and self.smart_field_name in form.initial:
            value = form.initial[self.smart_field_name]
        else:
            value = '** AUTO **'
        template = self.get_template_name(template_pack)
        return render_to_string(
            template,
            {
                'field': {
                    'label': sf.get('title', context='form.html'),
                    'help_text': sf.get('help_text', context='form.html'),
                    'value': value,
                    'auto_id': 'id_' + form.prefix + '-' + self.smart_field_name,
                },
                'smart_label_column': self.label_column,
                'smart_field_column': self.field_column,
                'smart_columns': self.smart_column,
                'row_span': self.row_span,
            },
        )


class SmartLayoutField(Field):
    def __init__(self, *args, **kwargs):
        self.row_span = 1
        self.smart_field_name = args[0]
        if 'smart_column' in kwargs:
            # If provided, the smart_column kw argument is a tuple/list (start_column, columns_span). Default is (1,1)
            self.label_column = '{}/{}'.format(kwargs['smart_column'][0] * 2 - 1, kwargs['smart_column'][0] * 2)
            self.field_column = '{}/{}'.format(
                kwargs['smart_column'][0] * 2,
                kwargs['smart_column'][0] * 2 + kwargs['smart_column'][1] * 2 - 1,
            )
            self.smart_column = kwargs['smart_column']
            kwargs.pop('smart_column')
        else:
            self.label_column = 1
            self.field_column = 2
            self.smart_column = (1, 1)
        if 'smart_field' in kwargs:
            self.smart_field = kwargs.get('smart_field')
            kwargs.pop('smart_field')
        if 'view_roles' in kwargs:
            self.view_roles = kwargs.get('view_roles')
            kwargs.pop('view_roles')
        else:
            self.view_roles = None

        super().__init__(*args, **kwargs)

    def get_smart_field_names(self):
        return self.fields

    def render(
        self,
        form,
        form_style,
        context,
        template_pack=TEMPLATE_PACK,
        extra_context=None,
        **kwargs,
    ):

        # If the current user can't view the field, just return an empty string
        if self.view_roles is not None and hasattr(form, 'user_roles') and not (set(self.view_roles) & set(form.user_roles)):
            return ''

        context['smart_label_column'] = self.label_column
        context['smart_field_column'] = self.field_column
        context['row_span'] = self.row_span

        return super().render(
            form,
            form_style,
            context,
            template_pack=template_pack,
            extra_context=extra_context,
            **kwargs,
        )

    def __repr__(self):
        return f"SmartLayoutField('{self.smart_field_name}')"


class SmartLayoutHtml(LayoutObject):
    def __init__(self, html, style, level):
        self.fields = []
        super().__init__()
        self.style = style
        self.html = html

    def render(
        self,
        form,
        form_style,
        context,
        template_pack=TEMPLATE_PACK,
        extra_context=None,
        **kwargs,
    ):
        local_context = Context(context)
        if hasattr(form, 'instance'):
            local_context['instance'] = form.instance

        return '<div style="{}">'.format(self.style) + Template(str(self.html)).render(local_context) + '</div>'


class SmartLayoutTemplate(LayoutObject):
    def __init__(self, template_name, style, level):
        self.fields = []
        super().__init__()
        self.style = style
        self.template = template_name

    def render(
        self,
        form,
        form_style,
        context,
        template_pack=TEMPLATE_PACK,
        extra_context=None,
        **kwargs,
    ):
        local_context = Context(context)
        if hasattr(form, 'instance'):
            local_context['instance'] = form.instance
        template = self.get_template_name(template_pack)

        return '<div style="{}">'.format(self.style) + render_to_string(template, context.flatten()) + '</div>'


class SmartLayoutButton(LayoutObject):

    template = '%s/layout/button.html'

    def __init__(
        self,
        button_type,
        value,
        label=None,
        message='',
        redirect='',
        redirect_params='{}',
        redirect_url_params='',
        **kwargs,  # NOQA
    ):
        self.fields = []
        self.type = button_type
        self.value = value
        self.message = message
        self.redirect = redirect
        self.base_redirect_params = redirect_params
        self.base_redirect_url_params = redirect_url_params
        self.label = label or value.capitalize()
        super().__init__()

    def render(
        self,
        form,
        form_style,
        context,
        template_pack=TEMPLATE_PACK,
        extra_context=None,
        **kwargs,
    ):

        self.value = Template(str(self.value)).render(context)
        template = self.get_template_name(template_pack)

        self.redirect_params = Template(str(self.base_redirect_params)).render(context)
        self.redirect_url_params = self.base_redirect_url_params
        if callable(self.redirect_url_params):
            self.redirect_url_params = self.redirect_url_params(
                {'request': context['request'], 'request_get': context['request'].GET}
            )
        context.update({'button': self})
        return render_to_string(template, context.flatten())


class SmartLayoutFormset(LayoutObject):

    template = '%s/layout/inline_formset.html'

    def __init__(self, *args, **kwargs):
        self.smart_field_name = args[0]
        self.fields = args
        self.value = None
        self.smart_column = kwargs.get('smart_column', (1, 1))
        self.row_span = 1
        self.initial = kwargs.get('initial')
        self.template = kwargs.get('subform_template', self.template)
        self.smart_field = kwargs['smart_field']
        self.formset_class = self.smart_field.get_formset()
        super().__init__()

    def render(
        self,
        form,
        form_style,
        context,
        template_pack=TEMPLATE_PACK,
        extra_context=None,
        **kwargs,
    ):
        # AJA: Je ne sais pas à quoi sert cette ligne => provisoirement mise en commentaire.
        # self.value = Template(str(self.value)).render(context)

        formset = context.get('formsets', {}).get(self.fields[0])

        r = ''
        if formset:
            context['formset'] = formset
        else:
            initial = self.initial
            if callable(initial):
                initial = initial(**context.flatten())
            context['formset'] = self.formset_class(instance=form.instance, initial=initial)
            subform_template = self.get_template_name(template_pack)
            r += Template('{{formset.management_form}}').render(context)
            rindex = len(context['formset']) - context['formset'].extra
            index = 0
            for form in context['formset']:
                context['form_rindex'] = rindex
                context['form_index'] = index
                context['form'] = form
                r += render_to_string(subform_template, context.flatten())
                rindex -= 1
                index += 1
        return r
