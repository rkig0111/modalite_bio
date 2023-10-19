from django.utils.translation import gettext as _

from smart_view.smart_widget import HtmlMediaDefiningClass, HtmlWidget


class SmartTableMetaclass(HtmlMediaDefiningClass):
    def __new__(mcls: type, name: str, bases: tuple, attrs: dict):
        new_class = super().__new__(mcls, name, bases, attrs)

        if name != 'SmartTable':
            if attrs['smart_view_class'] is not None:
                # print("Building SmartTable {}...".format(name))
                pass
            else:
                raise RuntimeError(_("SmartTable subclasses ('{}') must have a smart_view_class attribute").format(name))

        return new_class


# class SmartTable(HtmlWidget):
class SmartTable(HtmlWidget, metaclass=SmartTableMetaclass):
    class Media:
        css = {
            "all": (
                "smart_view/css/tabulator.min.css",
                "smart_view/css/smart-table.css",
            ),
        }
        js = (
            "smart_view/js/tabulator.min.js",
            "smart_view/js/get-coockie.js",
            "smart_view/js/smart-view.js",
        )

    template_name = 'smart_view/smart_table.html'
    smart_view_class = None
    columns = tuple()
    selectable_columns = tuple()
    user_filters = tuple()
    PARAMS_ADD = ('options',)
    _template_mapping_add = {
        'options': lambda self, kwargs: self.params['options'],
    }

    def column_definition(self, colname):
        base_definition = getattr(self.smart_view_class, colname).as_column_def(fieldname=colname, view_params=self.params)
        definition = {'field': colname}
        definition['title'] = base_definition.get('title', colname)
        return definition

    def params_process(self):
        columns = [self.column_definition(col) for col in self.columns]
        self.params['options'] = {
            'height': '100%',
            'layout': 'fitDataFill',
            'movableColumns': True,
            'persistence': {'columns': ['width'], 'sort': True},
            'columnDefaults': {
                'vertAlign': 'middle',
            },
            'columns': columns,
        }
