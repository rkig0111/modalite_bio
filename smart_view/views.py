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
import json
from json import JSONDecodeError


from django.utils import timezone


class DoubleSmartViewMixin:
    """
    Mixin de vue GÉQIP qui présente deux SmartView : La première est la vue principale et la seconde est 'pilotée' par
    la sélection de la première.
    Attributs utilisés :
      * main_smart_view_class : Nom de la classe SmartView principale
      * main_field_name : Nom du chap associé à la SmartView secondaire
      * field_smart_view_class : Nom de la classe SmartView secondaire
      * main_prefix : Préfixe de la smartview principale ('main_table' par défault)
      * field_prefix = Préfixe de la smartview secondaire ('field_table' par défaut)
    """

    template_name = 'dem/smart_view_double.html'
    main_prefix = 'main_table'
    field_prefix = 'field_table'

    def setup(self, request, *args, **kwargs):

        load_filters = {}

        # print("AJA 11")
        super().setup(request, *args, **kwargs)
        if 'url_prefix' in kwargs:
            self.url_prefix = kwargs['url_prefix']
        # A collection of parameters,
        self.view_params = dict(
            {
                'user': request.user,
                'request': request,
                'request_get': request.GET,
                'request_post': request.POST,
                'now': timezone.now(),
                'theme_name': self.theme,
                'user_roles': self._user_roles,
                'user_preferences': self._user_settings,
                'args': args,
            },
            **dict(kwargs),
        )
        if 'filters' in self.request.GET:
            try:
                get_filters = json.loads(self.request.GET['filters'])
                if isinstance(get_filters, list):
                    for get_filter in get_filters:
                        if (
                            isinstance(get_filter, dict)
                            and 'name' in get_filter
                            and get_filter['name'] in self.main_smart_view_class._meta['user_filters']
                            and 'value' in get_filter
                        ):
                            load_filters[get_filter['name']] = get_filter['value']
            except JSONDecodeError:
                pass
        self.main_smart_view = self.main_smart_view_class(
            prefix=self.name.replace('-', '_') + '_' + self.main_prefix,
            view_params=self.view_params,
            load_filters=load_filters,
            request=request,
            appname=self.my_app_name,
            url_prefix=self.url_prefix,
        )
        self.field_smart_view = self.field_smart_view_class(
            prefix=self.name.replace('-', '_') + '_' + self.field_prefix,
            view_params=self.view_params,
            request=request,
            appname=self.my_app_name,
            url_prefix=self.url_prefix,
            manager={
                'fieldname': self.main_field_name,
                'managed_fieldname': self.managed_field_name,
                'smartview': self.main_smart_view,
                'prefix': self.main_smart_view._prefix,
            },
        )

    def get(self, request, **kwargs):
        response = self.main_smart_view.handle()
        if response:
            return response
        response = self.field_smart_view.handle()
        if response:
            return response
        return super().get(request)

    def post(self, request, **kwargs):
        response = self.main_smart_view.handle()
        if response:
            return response
        response = self.field_smart_view.handle()
        if response:
            return response
        return super().post(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_smart_view'] = self.main_smart_view
        context['field_smart_view'] = self.field_smart_view
        context['page_media'] = self.main_smart_view.media + self.field_smart_view.media
        context['title'] = self.title
        return context
