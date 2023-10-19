/* global Tabulator, luxon, console, alert, $ */

Tabulator.extendModule("format", "formatters", {
    documents: function (cell, formatterParams, onRendered) {
        "use strict";

        let html = '';

        var cell_value = cell.getValue();

        if (typeof(cell_value)==='string')
        { cell_value = JSON.parse(cell_value); }

        if (Array.isArray(cell_value)) {
            // sort comments
            // cell_value.sort((a,b) => a.timestamp.localeCompare(b.timestamp));
            // console.log('Document cell value = ', cell_value);
            cell_value.forEach(document => {
                if (document.timestamp) {
                    var document_ts = new luxon.DateTime.fromISO(document.timestamp);
                    html += '<div class="smart-view-document">';
                    // <span class="document-header">Le '+document_ts.format('D MMM YYYY à H:mm')+', '+document.user_first_name+' '+document.user_last_name+' :</span>
                    html += '<p><b>' + formatterParams.choices[document.type] + '</b> : <a href="' + formatterParams.media_url +
                        document.link + '" onclick="window.open(this.href); return false;">' + document
                            .filename + '</a><br>' + document.description + '<p>';
                    html += '</div>';
                }
            });

            return html;
        } else {
            return ('<i class="fa-refresh fa-spin"></i>');
        }
    },
});
