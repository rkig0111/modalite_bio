var smart_view_checkbox_fmt = function (cell, formatterParams, onRendered) {
    "use strict";
    if (cell._cell.value === null) {
        return "<i class=\"fa-regular fa-circle\"></i>";
    }
    else if (cell._cell.value == 0) {
        return "<i class=\"fa-regular fa-circle-xmark\"></i>";
    }
    else {
        return "<i class=\"fa-regular fa-circle-check\"></i>";
    }
};
