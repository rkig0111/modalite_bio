Tabulator.extendModule("format", "formatters", {
    analysis: function(cell, formatterParams, onRendered) {

        var cell_value = cell.getValue();
        //console.log('Analyse cell value = ', cell_value);
        if (Array.isArray(cell_value.anomalies)) {
            var html = '<div class="analysis"><ul>';
            // sort comments
            // cell_value.sort((a,b) => a.timestamp.localeCompare(b.timestamp));
            // console.log('Analyse cell value = ', cell_value);
            cell_value.anomalies.forEach(anomaly => {
                if (true) {
                    //html += '<div class="smart-view-document">';
                    // <span class="document-header">Le '+document_ts.format('D MMM YYYY à H:mm')+', '+document.user_first_name+' '+document.user_last_name+' :</span>
                    html += '<li class="message level-'+anomaly.level+'">' + anomaly.message + '</li>'
                }
            });

            html += '</ul></div>'
            return html;
        } else {
            return ('<div class="analysis">&varnothing;</div>')
        }
    },
});