/*
  global Tabulator
 */

Tabulator.extendModule("format", "formatters", {

    multichoice: function (cell, formatterParams, onRendered) {
        "use strict";

        // console.log("formatterParams:", formatterParams);
        var value = '';

        try {
            var cell_value = JSON.parse(cell.getValue());
        } catch (valeur) {
            console.log(valeur);
            var cell_value = (String)(cell.getValue());
        }
        for (const val in formatterParams.lookup) {
            if (cell_value.includes(val)) {
                value += formatterParams.lookup[val] + ', ';
            }
        }
        if (value) {
            return value.slice(0, -2);
        } else {
            return value;
        }
    },

});
