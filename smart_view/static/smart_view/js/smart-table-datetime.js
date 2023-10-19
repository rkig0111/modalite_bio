/* global Tabulator, luxon */

Tabulator.extendModule("edit", "editors", {

    dateEditor: function(cell, onRendered, success, cancel, editorParams) {
        //cell - the cell component for the editable cell
        //onRendered - function to call when the editor has been rendered
        //success - function to call to pass the successfully updated value to Tabulator
        //cancel - function to call to abort the edit and return to a normal cell
        //editorParams - params object passed into the editorParams column definition property
        "use strict";

        //create and style editor
        let editor = document.createElement("input");

        editor.setAttribute("type", "date");

        //create and style input
        editor.style.padding = "3px";
        editor.style.width = "100%";
        editor.style.boxSizing = "border-box";

        //Set value of editor to the current value of the cell
        editor.value = luxon.DateTime.fromISO(cell.getValue()).toFormat("yyyy-LL-dd");
        //set focus on the select box when the editor is selected (timeout allows for editor to be added to DOM)
        onRendered(function() {
            editor.focus();
            editor.style.css = "100%";
        });

        //when the value has been set, trigger the cell to update
        function successFunc() {
            success(editor.value);
        }

        editor.addEventListener("change", successFunc);
        editor.addEventListener("blur", successFunc);

        //return the editor element
        return editor;
    },

    datetimeEditor: function(cell, onRendered, success, cancel, editorParams) {
        //cell - the cell component for the editable cell
        //onRendered - function to call when the editor has been rendered
        //success - function to call to pass the successfully updated value to Tabulator
        //cancel - function to call to abort the edit and return to a normal cell
        //editorParams - params object passed into the editorParams column definition property
        "use strict";

        //create and style editor
        let editor = document.createElement("input");

        editor.setAttribute("type", "datetime");

        //create and style input
        editor.style.padding = "3px";
        editor.style.width = "100%";
        editor.style.boxSizing = "border-box";

        //Set value of editor to the current value of the cell
        editor.value = luxon.DateTime.fromISO(cell.getValue()).toFormat("yyyy-LL-dd HH:mm:ss");

        //set focus on the select box when the editor is selected (timeout allows for editor to be added to DOM)
        onRendered(function() {
            editor.focus();
            editor.style.css = "100%";
        });

        //when the value has been set, trigger the cell to update
        function successFunc() {
            success(editor.value);
        }

        editor.addEventListener("change", successFunc);
        editor.addEventListener("blur", successFunc);

        //return the editor element
        return editor;
    },

});
