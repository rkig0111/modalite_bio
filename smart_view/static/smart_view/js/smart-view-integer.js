Tabulator.extendModule("format", "formatters", {
    // integer formatting with coalesce
    integer_ext_coalesce: function(cell, formatterParams, onRendered) {
        var intVal, number, integer, decimal, rgx;
        var add_default_class = false;

        var cell_value = cell.getValue();
        intVal = null;
        for (var i = 0; i < cell_value.length; i++) {
            if (cell_value[i] !== null) {
                intVal = cell_value[i];
                break;
            }
            add_default_class = true;
        }
        if (intVal === null) {
            return '';
        }

        if (isNaN(intVal)) {
            return this.emptyToSpace(this.sanitizeHTML(cell.getValue()));
        }

        var value = intVal;

        if (add_default_class) {
            return '<span class="default-value">' + value + '</span>';
        } else {
            return value;
        }
    },

    integer_conditional: function(cell, formatterParams, onRendered) {
        var intVal, number, integer, decimal, rgx;
        var add_default_class = false;

        var cell_value = cell.getValue();
        intVal = null;
        for (var i = 0; i < cell_value['fields'].length; i++) {
            if (cell_value['fields'][i] !== null) {
                intVal = cell_value['fields'][i];
                break;
            }
            add_default_class = true;
        }
        if (intVal === null) {
            return '';
        }

        if (isNaN(intVal)) {
            return this.emptyToSpace(this.sanitizeHTML(cell.getValue()));
        }

        var value = intVal;

        if (add_default_class) {
            if (cell_value['flag']) {
                cell.getElement().classList.add('default-value');
                cell.getElement().classList.remove('set-value');
                return value;
            } else {
                return '';
                // return '<span class="default-value">' + value + '</span>';
            }
        } else {
            if (cell_value['flag']) {
                cell.getElement().classList.add('set-value');
                cell.getElement().classList.remove('default-value');
                return value;
            } else {
                return '';
                // return value;
            }
        }
    },

});

Tabulator.extendModule("sort", "sorters", {
    integerSorter: function(a, b, aRow, bRow, column,dir, sorterParams) {
        return a - b;
    },
    conditionalIntegerSorter: function(a, b, aRow, bRow, column,dir, sorterParams) {
        let va = 0;
        let vb = 0;

        // a = JSON.parse(a);
        // b = JSON.parse(b);

        if (a.flag === true) {
            for (var i = 0; i < a.fields.length; i++) {
                if (a.fields[i] !== null) {
                    va = a.fields[i];
                    break;
                }
            }
        }
        if (b.flag === true) {
            for (var i = 0; i < b.fields.length; i++) {
                if (b.fields[i] !== null) {
                    vb = b.fields[i];
                    break;
                }
            }
        }
        // console.log("sorter...", a, b, va, vb, a.flag, a['fields']);
        return va - vb;
    },
});

Tabulator.extendModule("edit", "editors", {

    integerCoalesceEditor: function(cell, onRendered, success, cancel, editorParams) {
        //cell - the cell component for the editable cell
        //onRendered - function to call when the editor has been rendered
        //success - function to call to pass the successfuly updated value to Tabulator
        //cancel - function to call to abort the edit and return to a normal cell
        //editorParams - params object passed into the editorParams column definition property

        //create and style editor
        var editor = document.createElement("input");
        editor.style.padding = "3px";
        editor.style.width = "100%";
        editor.style.boxSizing = "border-box";

        var values_list = cell.getValue();

        editor.value = values_list[0];

        //set focus on the select box when the editor is selected (timeout allows for editor to be added to DOM)
        onRendered(function() {
            editor.focus({
                preventScroll: true
            });
            editor.style.height = "100%";
        });

        //when the value has been set, trigger the cell to update
        function successFunc() {
            values_list[0] = parseInt(editor.value);
            success(JSON.stringify(values_list));
        }

        editor.addEventListener("change", successFunc);
        editor.addEventListener("blur", successFunc);

        return editor;
    },

    integerConditionalEditor: function(cell, onRendered, success, cancel, editorParams) {
        //cell - the cell component for the editable cell
        //onRendered - function to call when the editor has been rendered
        //success - function to call to pass the successfuly updated value to Tabulator
        //cancel - function to call to abort the edit and return to a normal cell
        //editorParams - params object passed into the editorParams column definition property

        //create and style editor
        var editor = document.createElement("input");
        editor.style.padding = "3px";
        editor.style.width = "100%";
        editor.style.boxSizing = "border-box";

        var cell_value = cell.getValue();
        var values_list = cell_value['fields'];
        var flag_value = cell_value['flag'];

        editor.value = values_list[0];

        //set focus on the select box when the editor is selected (timeout allows for editor to be added to DOM)
        onRendered(function() {
            editor.focus({
                preventScroll: true
            });
            editor.style.height = "100%";
        });

        //when the value has been set, trigger the cell to update
        function successFunc() {
            values_list[0] = parseInt(editor.value);
            success(JSON.stringify({
                'flag': flag_value,
                'fields': values_list
            }));
        }

        editor.addEventListener("change", successFunc);
        editor.addEventListener("blur", successFunc);

        return editor;
    },

});
