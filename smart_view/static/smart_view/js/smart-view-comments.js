Tabulator.extendModule("format", "formatters", {
    comments: function(cell, formatterParams, onRendered) {
        var html = '';

        var cell_value = cell.getValue();
        if (Array.isArray(cell_value)) {
            // sort comments
            cell_value.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
            console.log('Cell value = ', cell_value);


            cell_value.forEach(comment => {
                var comment_ts = new luxon.DateTime.fromISO(comment.timestamp);
                html += '<div class="smart-view-comment"><span class="comment-header">Le ' + comment_ts.toFormat(
                        'D à t') + ', ' + comment.user_first_name + ' ' + comment.user_last_name +
                    ' :</span>';
                html += '<p>' + comment.text + '<p>';
                html += '</div>'
            });

            return html;
        } else {
            return ('<i class="fa-refresh fa-spin"></i>')
        }
    },
});

 
Tabulator.extendModule("edit", "editors", {
    comments: function(cell, onRendered, success, cancel, editorParams) {
        //cell - the cell component for the editable cell
        //onRendered - function to call when the editor has been rendered
        //success - function to call to pass the successfuly updated value to Tabulator
        //cancel - function to call to abort the edit and return to a normal cell
        //editorParams - params object passed into the editorParams column definition property


        var cell_element = cell.getElement();
        rect = cell_element.getBoundingClientRect();

        // The container
        var box = document.createElement("div");
        box.style.background = "#aaa";
        box.style.padding = "20px";
        box.style['border-radius'] = "10px";
        box.style.position = 'absolute';
        box.style.top = '-40px';
        box.style.left = '-20px';
        box.style['z-index'] = '1000';

        var title_node = document.createElement('span')
        box.appendChild(title_node);
        title_node.style.lineHeight = "10px";
        title_node.innerHTML = "Ajouter un commentaire :"
        //create and style editor
        var editor = document.createElement("textarea");
        box.appendChild(editor);
        editor.style.background = "#fff";
        editor.style.padding = "3px";
        editor.style.width = rect.width + "px";
        editor.style.boxSizing = "border-box";

        var values_list = cell.getValue();

        editor.value = "";

        //set focus on the select box when the editor is selected (timeout allows for editor to be added to DOM)
        onRendered(function() {
            cell_element.style.overflow = 'visible';
            editor.focus({
                preventScroll: true
            });
            editor.style.height = "100%";
        });

        //when the value has been set, trigger the cell to update
        function successFunc() {
            cell_element.style.removeProperty('overflow');
            values_list = {
                'timestamp': luxon.DateTime.now(),
                'add': editor.value
            };
            success(JSON.stringify(values_list));
        }

        editor.addEventListener("change", successFunc);
        editor.addEventListener("blur", successFunc);

        return box;
    },
});