/*
  global Tabulator
 */

Tabulator.extendModule("format", "formatters", {

    coalesce: function (cell, formatterParams, onRendered) {
        "use strict";
        var intVal, number, integer, decimal, rgx;
        var add_default_class = false;

        // console.log("formatterParams:", formatterParams);

        var cell_value = cell.getValue();
        var row_data = cell.getData();

        var fields = formatterParams.fields;

        let idxVal = null;
        if (cell_value) {
            idxVal = cell_value;
        } else {
            for (var i = 0; i < fields.length; i++) {
                if (row_data[fields[i]] !== null) {
                    idxVal = row_data[fields[i]];
                    break;
                }
            }
            add_default_class = true;
        }

        var value = formatterParams.lookup[idxVal];

        if (add_default_class) {
            cell.getElement().classList.add('default-value');
            cell.getElement().classList.remove('set-value');
        } else {
            cell.getElement().classList.remove('default-value');
            cell.getElement().classList.add('set-value');
        }
        return value;
    },

});
