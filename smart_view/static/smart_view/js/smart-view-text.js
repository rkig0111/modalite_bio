Tabulator.extendModule("format", "formatters", {
    text_conditional: function(cell, formatterParams, onRendered) {
        var intVal, number, integer, decimal, rgx;
        var add_default_class = false;

        var cell_value = cell.getValue();
        txtVal = null;
        for (var i = 0; i < cell_value['fields'].length; i++) {
            if (cell_value['fields'][i] !== null) {
                txtVal = cell_value['fields'][i];
                break;
            }
            add_default_class = true;
        }
        if (txtVal === null) {
            return '';
        }

        var value = txtVal;

        if (add_default_class) {
            cell.getElement().classList.add('default-value');
        } else {
            cell.getElement().classList.add('set-value');
        }
        return value;
    },
});


Tabulator.extendModule("edit", "editors", {

    textConditionalEditor: function(cell, onRendered, success, cancel, editorParams) {
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
            values_list[0] = editor.value;
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