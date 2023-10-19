Tabulator.extendModule("format", "formatters", {
    //currency formatting
    money_ext: function (cell, formatterParams, onRendered) {
        let floatVal, number, integer, decimal, rgx;
        var add_default_class = false;

        if (cell.getValue() !== null) {
            floatVal = parseFloat(cell.getValue());
        } else {
            floatVal = parseFloat(cell.getData()[formatterParams.data_if_null]);
            add_default_class = true;
        }

        var decimalSym = formatterParams.decimal || ".";
        var thousandSym = formatterParams.thousand || ",";
        var symbol = formatterParams.symbol || "";
        var after = !!formatterParams.symbolAfter;
        var precision = typeof formatterParams.precision !== "undefined" ? formatterParams.precision : 2;

        if (isNaN(floatVal)) {
            return this.emptyToSpace(this.sanitizeHTML(cell.getValue()));
        }

        number = precision !== false ? floatVal.toFixed(precision) : floatVal;
        number = String(number).split(".");

        integer = number[0];
        decimal = number.length > 1 ? decimalSym + number[1] : "";

        rgx = /(\d+)(\d{3})/;

        while (rgx.test(integer)) {
            integer = integer.replace(rgx, "$1" + thousandSym + "$2");
        }

        var value = after ? integer + decimal + symbol : symbol + integer + decimal;
        if (add_default_class) {
            return '<span class="default-value">' + value + '</span>';
        } else {
            return value;
        }
    },
    //currency formatting with coalesce
    /*
    money_ext_coalesce: function(cell, formatterParams, onRendered) {
        var floatVal, number, integer, decimal, rgx;
        var add_default_class = false;

        var cell_value = JSON.parse(cell.getValue());
        floatVal = null;
        for (var i = 0; i < cell_value.length; i++) {
            if (cell_value[i] !== null) {
                floatVal = cell_value[i];
                break;
            }
            add_default_class = true;
        }
        if (floatVal === null) {
            return '';
        }
*/
    /*
      if (cell.getValue() !== null) {
        floatVal = parseFloat(cell.getValue());
      } else {
        floatVal = parseFloat(cell.getData()[formatterParams.data_if_null]);
        add_default_class = true;
      }
     */
    /*
            var decimalSym = formatterParams.decimal || ".";
            var thousandSym = formatterParams.thousand || ",";
            var symbol = formatterParams.symbol || "";
            var after = !!formatterParams.symbolAfter;
            var precision = typeof formatterParams.precision !== "undefined" ? formatterParams.precision : 2;

            if (isNaN(floatVal)) {
                return this.emptyToSpace(this.sanitizeHTML(cell.getValue()));
            }

            number = precision !== false ? floatVal.toFixed(precision) : floatVal;
            number = String(number).split(".");

            integer = number[0];
            decimal = number.length > 1 ? decimalSym + number[1] : "";

            rgx = /(\d+)(\d{3})/;

            while (rgx.test(integer)) {
                integer = integer.replace(rgx, "$1" + thousandSym + "$2");
            }

            var value = after ? integer + decimal + symbol : symbol + integer + decimal;
            if (add_default_class) {
                return '<span class="default-value">' + value + '</span>';
            } else {
                return value;
            }
        },
    */
    //currency formatting with coalesce
    money_conditional: function (cell, formatterParams, onRendered) {
        var floatVal, number, integer, decimal, rgx;

        cell.getElement().classList.add('set-value');
        cell.getElement().classList.remove('default-value');

        var cell_value = cell.getValue();
        floatVal = null;
        for (var i = 0; i < cell_value['fields'].length; i++) {
            if (cell_value['fields'][i] !== null) {
                floatVal = cell_value['fields'][i];
                break;
            }
            cell.getElement().classList.add('default-value');
            cell.getElement().classList.remove('set-value');
        }
        if (floatVal === null) {
            return '';
        }

        /*
    if (cell.getValue() !== null) {
      floatVal = parseFloat(cell.getValue());
    } else {
      floatVal = parseFloat(cell.getData()[formatterParams.data_if_null]);
      add_default_class = true;
    }
   */

        var decimalSym = formatterParams.decimal || ".";
        var thousandSym = formatterParams.thousand || ",";
        var symbol = formatterParams.symbol || "";
        var after = !!formatterParams.symbolAfter;
        var precision = typeof formatterParams.precision !== "undefined" ? formatterParams.precision : 2;

        if (isNaN(floatVal)) {
            return this.emptyToSpace(this.sanitizeHTML(cell.getValue()));
        }

        number = precision !== false ? floatVal.toFixed(precision) : floatVal;
        number = String(number).split(".");

        integer = number[0];
        decimal = number.length > 1 ? decimalSym + number[1] : "";

        rgx = /(\d+)(\d{3})/;

        while (rgx.test(integer)) {
            integer = integer.replace(rgx, "$1" + thousandSym + "$2");
        }

        var value = after ? integer + decimal + symbol : symbol + integer + decimal;
        if (cell_value['flag']) {
            return value;
        } else {
            return '';
            // return '<span class="default-value">' + value + '</span>';
        }
    },

});

Tabulator.extendModule("columnCalcs", "calculations", {
    'sum_if_ext': function (values, data, calcParams) {
        //values - array of column values
        //data - all table data
        //calcParams - params passed from the column definition object
        var value_column = calcParams['data']; //'enveloppe_allouee';
        var if_null_column = calcParams['if_null'] //'montant_arbitrage';
        var test_column = calcParams['test']; //'gel';

        var sum = 0;
        data.forEach(function (row_data) {
            if (row_data[test_column]) {
                if (row_data[value_column] !== null)
                    sum += parseFloat(row_data[value_column]);
                else if (row_data[if_null_column] !== null)
                    sum += parseFloat(row_data[if_null_column]);
            }
        });
        return sum;
    },

    'sum_conditional': function (values, data, calcParams) {
        //values - array of column values
        //data - all table data
        //calcParams - params passed from the column definition object
        var value_column = calcParams['data']; //'enveloppe_allouee';
        var if_null_column = calcParams['if_null'] //'montant_arbitrage';
        var test_column = calcParams['test']; //'gel';

        var sum = 0;

        values.forEach(function (cell_value_raw) {
            var cell_value = cell_value_raw;
            if (cell_value['flag']) {
                var values = cell_value['fields'];
                sum += parseFloat(values.find(el => el !== null));
            }
            /*            if (row_data[test_column]) {
                            if (row_data[value_column] !== null)
                                sum += parseFloat(row_data[value_column]);
                            else if (row_data[if_null_column] !== null)
                                sum += parseFloat(row_data[if_null_column]);
                        } */
        });
        return sum;
    },

});

Tabulator.extendModule("edit", "editors", {

    moneyCoalesceEditor: function (cell, onRendered, success, cancel, editorParams) {
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
        onRendered(function () {
            editor.focus({
                preventScroll: true
            });
            editor.style.height = "100%";
        });

        //when the value has been set, trigger the cell to update
        function successFunc() {
            values_list[0] = parseFloat(editor.value);
            console.log("Success:", editor.value, values_list);
            success(JSON.stringify(values_list));
        }

        editor.addEventListener("change", successFunc);
        editor.addEventListener("blur", successFunc);

        return editor;
    },

    moneyConditionnalEditor: function (cell, onRendered, success, cancel, editorParams) {
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
        onRendered(function () {
            editor.focus({
                preventScroll: true
            });
            editor.style.height = "100%";
        });

        //when the value has been set, trigger the cell to update
        function successFunc() {
            values_list[0] = parseFloat(editor.value);
            //console.log("Success:", editor.value, values_list);
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

Tabulator.extendModule('sort', 'sorters', {
    moneySorter: function (a, b, aRow, bRow, column, dir, sorterParams) {
        return a - b;
    },

    moneyConditionalSorter: function (a, b, aRow, bRow, column, dir, sorterParams) {
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
