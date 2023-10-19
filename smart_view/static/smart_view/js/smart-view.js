/* global Tabulator,alert,$,csrftoken */

/*
  Keybindings to navigate in the table (current_row manager)
  DOES NOT WORK...
*/
Tabulator.extendModule("keybindings", "actions", {
    "selectUpRow": function () {
        'use strict';
        console.log("up !");
        var rows = this.table.getSelectedRows();
        if (rows.length === 1) {
            console.log("up !");
        }
    },
    "selectDownRow": function () {
        'use strict';
        console.log("down !");
        var rows = this.table.getSelectedRows();
    },
});

Tabulator.extendModule("mutator", "mutators", {
    json: function (value, data, type, params, component) {
        //value - original value of the cell
        //data - the data for the row
        //type - the type of mutation occurring  (data|edit)
        //params - the mutatorParams object from the column definition
        //component - when the "type" argument is "edit", this contains the cell component for the edited cell, otherwise it is the column component for the column
        'use strict';
        // console.log("JSON Mutator", value, data, type, component);
        if (value !== undefined) {
            return JSON.parse(value);
        }
    }
});

class SmartView {
    constructor(prefix) {
        this.prefix = prefix;
        this.settings_to_update = {};
        this.settings_update_timeout = null;
    }

    init(tabulator_options, smart_view_options) {
        this.tabulator_options = tabulator_options;
        this.options = smart_view_options;
        this.base_url = smart_view_options.base_url;
        this.row_styler = smart_view_options.row_styler;
        // this.row_tooltip = smart_view_options.row_tooltip;
        var self = this;

        self.current_row = null;
        self.managed_smartviews = [];

        this.tabulator_options.index = this.options.id_field;
        this.tabulator_options.persistenceID = this.prefix;

        // TODO: These don't work...
        this.tabulator_options.keybindings = {
            'selectUpRow': "38",
            'selectDownRow': "40",
        };


        // Function used to store Tabulator persistence data : columns widths & column sort
        // Uses self.update_setiings to avoid bouncing (Tabulator triggers a lot of 'write' events on initialization)
        this.tabulator_options.persistenceWriterFunc = function (id, type, data) {
            //id - tables persistence id
            //type - type of data being persisted ("sort", "filters", "group", "page" or "columns")
            //data - array or object of data

            var settings = {};
            settings[self.options.appname + '.' + id + '.' + type] = data;
            self.update_settings(self, settings);
            // TODO: Pas de gestion des erreurs... Est-ce utile ??
        };
        // Function used to get Tabulator persistence data : columns widths & column sort
        // This information is provided at page initialization (via template) since there is no need to get this data
        // while the page is already displayed AND this is very difficult to handle
        //   (synchronous/classical function should wait for AJAX response...)
        this.tabulator_options.persistenceReaderFunc = function (id, type) {
            //id - tables persistence id
            //type - type of data being persisted ("sort", "filters", "group", "page" or "columns")

            if (self.options.user_settings) {
                return self.options.user_settings[type];
            } else {
                return false;
            }
        };

        // If current_row_manager is active (ie : there is a 'current row' in the table)
        //   This uses/trick 'selection' manager from tabulator
        if (smart_view_options.current_row_manager) {
            //console.log("Row manager is active !");
            this.current_record_element = document.querySelector(`#${this.prefix}-smart-view-menu-bar .current-record`);
            this.records_count_element = document.querySelector(`#${this.prefix}-smart-view-menu-bar .records-count`);

            var button = document.querySelector(`#${this.prefix}-smart-view-menu-bar .first-record`);
            if (button) {
                button.onclick = function (event) {
                    // console.debug("first");
                    self.current_row.getTable().deselectRow();
                    var row = self.tabulator.getRowFromPosition(0, true);
                    self.tabulator.selectRow(row, true);
                    row.scrollTo();
                };
            }
            button = document.querySelector(`#${this.prefix}-smart-view-menu-bar .previous-record`);
            if (button) {
                button.onclick = function (event) {
                    //console.debug("previous");
                    if (self.current_row.getPosition(true) > 0) {
                        self.current_row.getTable().deselectRow();
                        var row = self.tabulator.getRowFromPosition(self.current_row.getPosition(true) - 1, true);
                        self.tabulator.selectRow(row, true);
                        if (row.getPosition() > 0) {
                            row.getPrevRow().scrollTo();
                        } else {
                            row.scrollTo();
                        }
                    }
                };
            }
            button = document.querySelector(`#${this.prefix}-smart-view-menu-bar .next-record`);
            if (button) {
                button.onclick = function (event) {
                    // console.debug("next");
                    if (self.current_row.getPosition(true) < self.tabulator.getRows().length - 1) {
                        self.current_row.getTable().deselectRow();
                        var row = self.tabulator.getRowFromPosition(self.current_row.getPosition(true) + 1, true);
                        self.tabulator.selectRow(row);
                        row.getPrevRow().scrollTo();
                    }
                };
            }
            button = document.querySelector(`#${this.prefix}-smart-view-menu-bar .last-record`);
            if (button) {
                button.onclick = function (event) {
                    // console.debug("last");
                    self.current_row.getTable().deselectRow();
                    var row = self.tabulator.getRowFromPosition(self.tabulator.getRows().length - 1, true);
                    self.tabulator.selectRow(row, true);
                    row.scrollTo();
                };
            }
        }

        for (var i = 0; i < this.tabulator_options.columns.length; i++) {
            //this.tabulator_options.columns[i].editor = "textarea"; // TODO
            //this.tabulator_options.columns[i].editorParams =  {  }; // TODO
            this.tabulator_options.columns[i].editable = function (cell) {
                return self.is_editable(cell, this);
            };
            this.tabulator_options.columns[i].cellEdited = function (cell) {
                return self.cell_edited(cell, this);
            };
        }

        if ('fieldname' in this.row_styler) {
            this.tabulator_options.rowFormatter = function (row, tabulator = this) {
                self.row_formatter(row, tabulator, self.row_styler.fieldname, self.row_styler.styles);
            };
        }

        if (this.options.row_tooltip) {
            //this.tabulator_options.tooltipGenerationMode = 'hover';
            this.tabulator_options.tooltips = function (cell, tabulator = this) {
                return self.options.tooltip_formatter(cell.getData());
            };
        }

        this.tabulator_options.data = [];

        this.tabulator = new Tabulator(`#${this.prefix}-smart-view-table`, this.tabulator_options);
        this.tabulator.smart_view = this;

        this.tabulator.on('cellClick', function (event, cell) {
            return self.cell_click(event, cell, this);
        });

        // L'utilisation d'une fonction intermediaire permettra de récupérer self comme l'objet SmartView
        // 'this' sera l'appelant, c'est à dire le Tabulator (dont le constructeur ne sera pas terminé et donc
        // qui ne sera pas encore référencé par l'objet SmartView)
        this.tabulator.on('tableBuilt', function (tabulator = this) {
            // Prepare 'columns selector'
            self.columns_selector_prepare(tabulator);
        });

        // Select the first row (=set as current row) of table on render complete (only if there is not one yet) :
        if (smart_view_options.current_row_manager) {
            this.tabulator.on('dataLoaded', function (data) {
                if (self.records_count_element) {
                    self.records_count_element.innerText = data.length;
                }
            });
            //console.log("Row manager is active !");
            this.tabulator.on('renderComplete', function () {
                var row_position = 0;
                if ((this.getDataCount()) && (self.current_row === null)) {
                    if (self.options.fragment) {
                        self.destination_row = this.getRow(self.options.fragment);
                        if (self.destination_row) {
                            row_position = self.destination_row.getPosition(true);
                            self.destination_row.scrollTo();
                        }
                    }
                    this.selectRow(this.getRowFromPosition(row_position, true));
                }
            });
            // Avoid unselect a row by clicking on it :
            this.tabulator.on('rowClick', function (event, row) {
                //console.debug("RowClick", row, typeof row.getIndex, self.current_row, row.getTable().getSelectedRows());
                if ((typeof row.getIndex === 'undefined') || (row.getTable().getSelectedRows().length === 0)) {
                    // this click deselected the only selected row => reselect it !
                    row.getTable()
                        .deselectRow(); // just in case ; useful for 'calc' rows (which can be selected but not deselected...)
                    self.current_row.select();
                }
            });
            // local method called when selection (=current row) change :
            this.tabulator.on('rowSelected', function (row) {
                if (typeof row.getIndex === 'function') {
                    self.current_row = row;
                    return self.row_selected(self, row, this);
                }
            });

        } else {
            this.tabulator.on('renderComplete', function () {
                if ((this.getDataCount()) && (self.options.fragment)) {
                    console.debug("Data loaded :", this, self, self.records_count_element, self.options.fragment);
                    self.destination_row = this.getRow(self.options.fragment);
                    console.debug("R: ", this, self.options.fragment, self.destination_row);
                    if (self.destination_row) {
                        this.scrollToRow(self.destination_row, 'center', true).then(function () {
                            // Faire ici un truc pour mettre en évidence la ligne vers laquelle on vient de centrer le tableau !!
                            // Une animation peut-être ?
                        });
                        //self.destination_row.scrollTo();
                    }
                }
            });
            if (self.options.form_fields.length > 0) {
                // console.log("simple form mode for :", self);
                this.tabulator.on('dataLoaded', function (data) {
                    if (data.length === 1) {
                        // console.log("Updating simple form for :", self, data[0]);
                        self.form_update(self, data[0]);
                    }
                });
            }

        }


        $(`#${this.prefix}-smart-view-menu-bar .views-buttons-box .icon-button`).click(function (event) {
            console.log("click on view:", this.dataset.view, self);
            self.show_view(this.dataset.view, this);
        });

        // Liste de tous les éléments HTML5 qui sont utilisés comme filtres pour la table
        this.filters = $(
            `#${this.prefix}-smart-view-filters input, #${this.prefix}-smart-view-filters select, .smart-view-filter-bar input`
        );

        /* Add a event listener to every filter so the table data are
         * reloaded for each change
         */
        for (let i = 0; i < this.filters.length; i++) {
            let filter = this.filters[i];

            filter.addEventListener('change', function (event) {
                self.filters_apply(event, self);
            });
        }

        $(`#${this.prefix}-smart-view-filters-box .smart-view-filter-box i`).css("cursor", "pointer").click(function (event) {
            // console.debug("del filter click !!", self, $(this).parent().attr('data-field'));

            var field_name = $(this).parent().attr('data-field');

            if (self.filters.filter("[name=\"" + field_name + "\"]").is('select')) {
                // Enregistre la valeur dans le stockage local
                //TODO localStorage.setItem('filter-' + field_name, "{}")

                // Met tous les filtres pour ce paramètre sur la même position
                self.filters.filter('select[name="' + field_name + '"]').val("{}");
            } else {
                // Enregistre la valeur dans le stockage local
                //TODO localStorage.setItem('filter-' + field_name, "")

                // Met tous les filtres pour ce paramètre sur la même position
                self.filters.filter('input[name="' + field_name + '"]').val("");
            }

            self.filters_apply(null, self);

            if (window.close_all_menus) {
                window.close_all_menus();
            }
        });

        // If this SmartView has a manager, let's subscribe
        if (this.options.manager) {
            this.options.manager.smart_view.add_managed({
                'smartview': this,
                'fieldname': this.options.manager.manager_fieldname,
                'managed_fieldname': this.options.manager.managed_fieldname
            });
        } else {
            let self = this;
            this.tabulator.on("tableBuilt", function () {
                self.filters_apply(null, self)
            });
        }
    }


    // A function to debounce settings storage via AJAX
    // Start a timeout for every call and aggregate multiple calls within this timeout
    update_settings(self, settings) {
        // Restart timeout
        if (self.settings_update_timeout) {
            clearTimeout(self.settings_update_timeout);
        }
        // Aggregate/update pending settings
        Object.assign(self.settings_to_update, settings);
        // start a new timeout, with AJAX POST when finished
        self.settings_update_timeout = setTimeout(
            () => {
                // End of timeOut reached => send a POST AJAX request to store pending settings into user's preferences
                $.ajax(
                    self.options.settings_url, {
                    method: 'POST',
                    context: self,
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: {
                        settings: JSON.stringify(self.settings_to_update)
                    }
                }
                ).done(function () {
                    // Success => reset locally stored / pending settings
                    self.settings_to_update = {};
                });
            },
            // One full second seems efficient enought
            1000
        );
    }

    show_view(view, button) {
        // console.log('id=', this, `${this.prefix}-smart-view-${view}`, button);
        var view_elt = document.getElementById(`${this.prefix}-smart-view-${view}`);
        if (this.options.view_switch_mode === 'radio') {
            //TODO...
            // Hide all...
        }
        if (view_elt.style.display !== 'none') {
            view_elt.style.display = 'none';
            button.classList.remove('selected');
        } else {
            view_elt.style.display = 'block';
            button.classList.add('selected');
        }
    }

    cell_click(event, cell, tabulator) {
        //console.log("cell click:", event, cell, tabulator, this, cell.getColumn());

        var col_definition = cell.getColumn().getDefinition();
        console.debug("cell_click()");

        if (col_definition.editor === null) {

            event.stopPropagation();

            //console.log("chekbox !:", event, cell, tabulator, this);
            // Si la case est un checkbox et est éditable => changer l'état !
            if (this.is_editable(cell)) {
                console.debug("cell_click + is_editable");
                if (col_definition.editorParams.tristate === true) {
                    console.debug("cell_click + is_editable + tristate", cell.getValue());
                    cell.setValue({
                        null: 1,
                        true: false,
                        false: null,
                        1: 0,
                        0: null
                    }[cell.getValue()]);
                } else {
                    console.debug("cell_click + is_editable + NON tristate", cell.getValue());
                    cell.setValue({
                        null: 1,
                        true: false,
                        false: true,
                        1: 0,
                        0: 1
                    }[cell.getValue()]);
                }
            }
            // cell_edited() est appelé automatiquement, ce qui entraîne la mise à jour de la base !
        }
    }

    add_managed(managed) {
        // console.debug("Add managed this=", this);
        this.managed_smartviews.push(managed);
    }

    form_update(self, data) {
        // Update form
        for (var i in self.options.form_fields) {
            var field_name = self.options.form_fields[i];
            var elt = document.getElementById(self.prefix + '-smart-view-form-' + field_name);
            console.debug("  form field:", field_name, elt);
            elt.value = data[field_name];
        }
    }

    row_selected(self, row, tabulator) {
        // console.debug("row_selected", row.getData());

        // Update managed SmartViews
        for (var i = 0; i < self.managed_smartviews.length; i++) {
            if (self.managed_smartviews[i].last_manage_value !== row.getData()[self.managed_smartviews[i].fieldname]) {

                // To avoid useless managment (kind of workaround...)
                self.managed_smartviews[i].last_manage_value = row.getData()[self.managed_smartviews[i].fieldname];
                var managed_smartview = self.managed_smartviews[i];

                // console.debug("Update managed...", managed_smartview, row.getData()[managed_smartview.fieldname]);
                var filter = {};
                filter[managed_smartview.managed_fieldname] = managed_smartview.last_manage_value;
                managed_smartview.smartview.filters_apply(null, managed_smartview.smartview, filter);
            }
        }

        // Update form (if any)
        self.form_update(self, row.getData());

        // Update rows navigator
        // console.debug("Row selected :", row.getPosition(true));
        if (self.current_record_element) {
            self.current_record_element.innerText = 1 + row.getPosition(true);
        }
    }

    is_editable(cell, tabulator) {
        var fieldname;
        var definition = cell.getColumn().getDefinition();
        if (definition.editorParams && definition.editorParams.edited_fieldname) {
            fieldname = definition.editorParams.edited_fieldname;
        } else {
            fieldname = cell.getField();
        }
        // console.log("AJA:", fieldname);
        var roles = cell.getRow().getData()[this.options.roles_field];
        if (roles) {
            roles = roles.split(',');
        }
        var state = cell.getData()[this.options.state_field];
        //console.log("is editable:", cell, tabulator, this, cell.getColumn(), fieldname, roles, state);

        var p_level = this.options.permissions;

        /*
        if (this.options.current_row_manager) {
            cell.getTable().deselectRow();
            cell.getRow().select();
        }
        */


        //console.log("p_level:", p_level);
        if (p_level.write) {
            p_level = p_level.write;
        } else {
            return false;
        }
        //console.log("p_level:", p_level);
        if (p_level[state]) {
            p_level = p_level[state];
        } else {
            return false;
        }
        //console.log("p_level:", p_level);
        for (var i = 0; i < roles.length; i++) {
            var role = roles[i];
            if (p_level[role] && p_level[role][fieldname]) {
                return true;
            }
        }

        return false;
    }

    cell_edited(cell, tabulator) {
        document.getElementsByTagName('html')[0].classList.add("busy");
        var self = this; // SmartView
        //console.log("has been edited:", cell, tabulator, this);
        var record = {
            where: {},
            set: {}
        };
        //console.log(this);
        record.where[this.options.id_field] = cell.getData()[this.options.id_field];
        var definition = cell.getColumn().getDefinition();
        if (definition.editorParams && definition.editorParams.edited_fieldname) {
            // Assume que si on a edited_fieldname, la valeur est une chaîne JSON dont il faut prendre le premier élément. Bof.
            record.set[definition.editorParams.edited_fieldname] = cell.getValue().fields[0];
        } else {
            record.set[cell.getField()] = cell.getValue();
        }
        cell.restoreOldValue();
        $.ajax(this.base_url, {
            method: 'POST',
            context: cell,
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                smart_view_prefix: this.prefix,
                update: JSON.stringify(record)
            }
        }).done(
            function (data) {
                if (data.error) {
                    alert("La cellule ne peut pas être mise à jour.\n\nErreur : " + data.error.message);
                } else {
                    for (const updatedRow of data.updated) {
                        let update = {};
                        let id = -1;
                        //update[self.options.id_field] = cell.getData()[self.options.id_field];
                        for (let fieldname in updatedRow) {
                            if (fieldname == '_row_id') {
                                id = updatedRow._row_id
                            } else
                                if (updatedRow.hasOwnProperty(fieldname)) {
                                    update[fieldname] = updatedRow[fieldname];
                                }
                        }
                        let row = this.getTable().getRow(id);
                        // Avoid updating row which id is not in the table
                        if (row) {
                            row.update(update);
                        }

                        //console.debug("id", id, "update", update);
                        //this.getRow().reformat();
                    }
                }
                document.getElementsByTagName('html')[0].classList.remove("busy");
            }
        ).fail(
            function (data) {
                document.getElementsByTagName('html')[0].classList.remove("busy");
                alert("La cellule ne peut pas être mise à jour.\n\nErreur renvoyée par le serveur.");
            }
        );
    }

    columns_selector_prepare(tabulator) {
        // Système de sélection des colonnes à afficher dans le tableau
        var prefix = this.prefix;
        var self = this;
        var column_selectors = document.querySelectorAll(`#${prefix}-columns-selector input`);
        var responsive_base = {};

        function show_column_update(cb) {
            let id = self.options.appname + '.' + 'tabulator-' + prefix + '.show-column.' + cb.name;
            let settings = {};
            if (cb.checked) {
                tabulator.showColumn(cb.name);
                settings[id] = true;
            } else {
                var col = tabulator.getColumn(cb.name);
                col.hide();
                settings[id] = false;
            }
            self.update_settings(self, settings);
            tabulator.redraw();
        }
        for (let i = 0; i < column_selectors.length; i++) {
            let cb = column_selectors[i];
            let col = tabulator.getColumn(cb.name);
            if (col) {
                var definition = col.getDefinition();
                var id = self.options.appname + '.' + 'tabulator-' + prefix + '.show-column.' + cb.name;
                if (self.options.user_settings && self.options.user_settings['show-column'] && self.options.user_settings[
                    'show-column'][cb.name] === false) {
                    cb.checked = false;
                } else {
                    cb.checked = true;
                }

                // L'utilisation de .onchange() évite d'enregistrer plusieurs fois la callback
                cb.onchange = function (event) {
                    var cb = event.target;
                    show_column_update(cb);
                };
                show_column_update(cb);
            }
        }
    }

    row_formatter(row, tabulator, fieldname, styles) {
        var data = row.getData();

        if (data[fieldname] in styles) {
            row.getElement().style.cssText = styles[data[fieldname]][0];
        }
    }

    filter_value(smartview, filter) {
        let filter_value = $(filter).val();
        if ($(filter[0]).is('input') && filter[0].type === "text") {
            if (filter_value !== "") {
                if (filter[0].attributes['data-fieldname'].value.substring(0, 1) !== '[') {
                    filter_value = '{"' + filter[0].attributes['data-fieldname'].value + '__icontains":"' +
                        filter_value + '"}';
                } else {
                    var str_value = filter_value;
                    var fields = JSON.parse(filter[0].attributes['data-fieldname'].value);
                    filter_value = '{":or":[';
                    // console.debug("fields =>", fields);
                    for (var i = 0; i < fields.length; i++) {
                        var field = fields[i];
                        filter_value += '{"' + field + '__icontains": "' + str_value + '"},';
                    }
                    filter_value = filter_value.substr(0, filter_value.length - 1) + ']}';
                    // console.debug("  string =>", filter_value);
                }
            } else {
                filter_value = '{}';
            }
        } else if ($(filter[0]).is('input') && filter[0].type === "radio") {
            // console.log("radio filter", this);
            if (filter[0].checked) {
                filter_value = filter[0].value;
            } else {
                filter_value = "{}";
            }
        }
        console.debug(filter, filter_value);
        return filter_value;
    }

    /*
      Fonction qui est appelée au chargement de la page et à chaque fois qu'un filtre est modifié par l'utilisateur.

      Cette fonction vérifie la cohérence entre les différents filtres (TODO), met à jour le stockage local pour mémoriser l'état des filtres (TODO)
      et (re)charge les données dans le tableau.
     */
    filters_apply(event, smartview, base_filter = {}) {
        // console.debug("filters_apply...", event, smartview);

        var query = smartview.base_url;
        var filters_kw = base_filter;
        var filters_full = {};

        smartview.filters.each(function (filter) {
            var filter_box = $(
                `#${smartview.prefix}-smart-view-filters-box .smart-view-filter-box[data-field="${this.attributes['name'].value}"]`
            );
            var filter_value = $(this).val();
            var filter_label = $(
                `#${smartview.prefix}-smart-view-filters label[name="${this.attributes['name'].value}"]`).html();

            if ($(this).is('select')) {
                if (filter_value !== "{}") {
                    // console.debug(filter_box);
                    // console.debug("filter", this.attributes['name'].value, "val:", filter_value, "label:", "text_value");

                    filter_box.find('.filter-text').html(filter_label + ' : <b>' + $(
                        `#${smartview.prefix}-smart-view-filters select[name="` + this.attributes['name']
                            .value + '"] option[value=\'' + filter_value + '\']').html() + '</b>');
                    filter_box.show();
                } else {
                    filter_box.hide();
                }

            } else if ($(this).is('input') && this.type === "text") {
                if (filter_value !== "") {
                    filter_box.find('.filter-text').html(filter_label + ' : <b> "' + filter_value + '</b>"');
                    filter_box.show();

                    if (this.attributes['data-fieldname'].value.substring(0, 1) !== '[') {
                        filter_value = '{"' + this.attributes['data-fieldname'].value + '__icontains":"' +
                            filter_value + '"}';
                    } else {
                        var str_value = filter_value;
                        var fields = JSON.parse(this.attributes['data-fieldname'].value);
                        filter_value = '{":or":[';
                        // console.debug("fields =>", fields);
                        for (var i = 0; i < fields.length; i++) {
                            var field = fields[i];
                            filter_value += '{"' + field + '__icontains": "' + str_value + '"},';
                        }
                        filter_value = filter_value.substr(0, filter_value.length - 1) + ']}';
                        // console.debug("  string =>", filter_value);
                    }

                } else {
                    filter_box.hide();
                    filter_value = "{}";
                }
            } else if ($(this).is('input') && this.type === "radio") {
                // console.log("radio filter", this);
                if (this.checked) {
                    filter_value = "{}";
                    filter_value = this.value;
                } else {
                    filter_value = "{}";
                }
            } else {
                console.warn("Unable to handle filter input", this);
            }
            filter_value = JSON.parse(filter_value);
            if (Object.keys(filter_value).length !== 0) {
                filters_full[this.attributes['name'].value] = filter_value;
            }
            Object.assign(filters_kw, filter_value);
        });
        var settings = {};
        settings[smartview.options.appname + '.tabulator-' + smartview.prefix + '.filters'] = filters_full;
        smartview.update_settings(smartview, settings);
        smartview.tabulator.setData(query + '?smart_view_prefix=' + smartview.prefix + '&filters=' + encodeURIComponent(JSON
            .stringify(filters_kw)));
    }

    export_url(smartview, id) {
        let filters_kw = {};
        smartview.filters.each(function (filter) {
            let filter_value = smartview.filter_value(smartview, $(this));
            console.debug('f=', filter_value);
            filter_value = JSON.parse(filter_value);
            Object.assign(filters_kw, filter_value);
        });
        return smartview.base_url + "?smart_view_prefix=" + smartview.prefix + '&filters=' + encodeURIComponent(JSON
            .stringify(filters_kw)) + "&export=" + id;
    }

    tool_delete_fmt(self, cell, formatterParams, onRendered) {
        var p_level = self.options.permissions;

        if (p_level['delete']) {
            p_level = p_level['delete'];
        } else {
            return;
        }
        var state = cell.getRow().getData()[self.options.state_field];
        if (p_level[state]) {
            p_level = p_level[state];
        } else {
            return;
        }
        var roles = cell.getRow().getData()[self.options.roles_field];
        if (roles) {
            roles = roles.split(',');
        }

        const common_roles = roles.filter(value => p_level.includes(value));

        if (common_roles.length) {
            return "<i class=\"fa-regular fa-trash-can fa-lg\"></i>";
        }
        /*
            for (var i = 0 ; i < roles.length ; i++) {
              var role = roles[i];
              if (p_level[role]) {
                return "<i class=\"fa fa-trash fa-lg\"></i>";
              }
            } */
    }

    tool_open_fmt(self, cell, formatterParams, onRendered) {
        if (cell.getRow().getData()[self.options.roles_field].split(',').includes('OWN')) {
            return "<i class=\"fa-regular fa-edit fa-lg\"></i>";
        } else {
            return "<i class=\"fa-regular fa-eye fa-lg\"></i>";
        }
    }

    tool_copy_fmt(self, cell, formatterParams, onRendered) {
        // TODO: Test if I can (read this row/instance and) create a new row/instance
        return "<i class=\"fa-regular fa-clone fa-lg\"></i>";
    }

    checkbox_fmt(self, cell, formatterParams, onRendered) {
        if (cell.getValue() === null) {
            return "<i class=\"fa-regular fa-circle fa-lg\"></i>";
        }
        else if (!cell.getValue()) {
            return "<i class=\"fa-solid fa-xmark fa-lg\"></i>";
        }
        else {
            return "<i class=\"fa-solid fa-check fa-lg\"></i>";
        }
    }

    if_null_fmt(self, cell, formatterParams, onRendered) {
        //console.log(cell.getValue());
        if (cell.getValue() !== null) {
            /*if (formatterParams.cascade_formatter) {
              var formatter = Tabulator.prototype.moduleBindings.format.prototype.formatters[formatterParams.cascade_formatter];
              if (formatter) {
                return formatter(cell, formatterParams.cascade_formatter_params, onRendered);
              } else {
                return cell.getValue();
              }
            } else { */
            return cell.getValue();
            /*} */
        } else {
            //console.log("-->", formatterParams.data_if_null);
            var value = cell.getData()[formatterParams.data_if_null];
            return '<span class="default-value">' + value + '</span>';
        }
    }

    if_null_calc(value, data, calcParams) { }
}
