/*

  Rules inputs are fields values. Each should have a 'id' attribute
  A rule is triggered each time one is changed by the user.

    Rule function returns a list of actions, each is a object with
  at least one attribute : 'action'

  Possible actions :
   - 'value' : Change (other) elements values
     * 'selector' : the field id/class
     * 'value' : the value to put in
   - 'classes' : change elements classes
     * 'selector' : the objects which classes will be changed
     * 'has' : classes to add
     * 'has_not' : classes to remove
   - 'help' : Add/remove a (colored) help item in a (dedicaced) window
     * 'text'
     * 'level'
     * 'selector' : the objects where help item will be added
   - 'links-lock' : Lock all links in the page a throw a alert box with a message
     * 'text' : alert message text

   Loop avoidance : None for now.
*/

/* global console, alert, $ */

function expr_function_euros(fields, rule, init_call) {
    "use strict";
    let actions = [];

    let args = [];
    let fields_keys = Object.keys(fields);
    for (let i = 0; i < fields_keys.length; i++) {
        let key = fields_keys[i];
        args.push(parseFloat(fields[key].replace(/[€\s]/g, '').replace(/,/g, '.')));
    }
    // console.debug('func expression');
    // console.debug(rule);
    // console.debug(args);

    let f = Function('args', rule.expr); // jshint ignore:line

    let result = f(args);

    if (isNaN(result)) {
        result = '';
    }

    // console.debug(rule.expr);
    actions.push({
        'action': 'value',
        'selector': '#' + rule.to,
        'value': result,
    });

    return actions;
}

function money_format(fields, rule, init_call) {
    "use strict";
    let actions = [];

    let fields_keys = Object.keys(fields);

    for (let i = 0; i < fields_keys.length; i++) {
        let key = fields_keys[i];
        let value = fields[key];
        // console.debug(key);
        // console.debug(value);
        if ((value) && (value.length > 0)) {
            // récupère les espaces et le '€' et remplace l'éventuelle ',' par un '.'
            value = value.replace(/[€\s]/g, '').replace(/,/g, '.');
            //console.log("Prix value filtered", value);

            let value_number = Number(value);
            //console.log("Prix value number", value_number);

            if (isNaN(value_number)) {
                actions.push({
                    'action': 'classes',
                    'selector': '#' + key,
                    'has': ['on_error'],
                    'has_not': [],
                });
                actions.push({
                    'action': 'help',
                    'selector': '#' + key.substring(3) + '-help',
                    'level': 'error',
                    'text': "« " + fields[key] + " » n'est pas un montant valide",
                });
                //console.log("help on", '#'+key.substring(3)+'-help');
            } else {
                actions.push({
                    'action': 'classes',
                    'selector': '#' + key,
                    'has': [],
                    'has_not': ['on_error'],
                });
                actions.push({
                    'action': 'value',
                    'selector': '#' + key,
                    'value': Math.round(value_number).toLocaleString("fr-FR") + " €",
                });

            }

        } // value.length > 0
        else {
            actions.push({
                'action': 'classes',
                'selector': '#' + key,
                'has': [],
                'has_not': ['on_error'],
            });
        }
    }
    return actions;
}

function show_if(fields, rule, init_call) {
    "use strict";
    let actions = [];

    //console.debug(fields);

    var fields_l = Object.keys(fields);
    var targets = rule.targets;

    for (var i = 0; i < fields_l.length; i++) {
        var field_n = fields_l[i];

        if (fields[field_n]) {
            for (var j = 0; j < targets.length; j++) {
                actions.push({
                    'action': 'classes',
                    'selector': targets[j],
                    'has': null,
                    'has_not': 'hidden'
                });
            }
        } else {
            for (let j = 0; j < targets.length; j++) {
                actions.push({
                    'action': 'classes',
                    'selector': targets[j],
                    'has': 'hidden',
                    'has_not': null
                });
            }
        }
    }
    return actions;
}

function show_if_expr(fields, rule, init_call) {
    "use strict";
    let actions = [];

    let fields_l = Object.keys(fields);
    let targets = rule.targets;

    let args = [];
    let fields_keys = Object.keys(fields);
    for (let i = 0; i < fields_keys.length; i++) {
        let key = fields_keys[i];
        args.push(fields[key]);
    }
    //console.debug('show-if-expr func expression');
    //console.debug(rule);
    //console.debug(args);

    let f = Function('args', rule.expr); // jshint ignore:line

    let result = f(args);
    //console.debug('result=', result);

    //console.warn("Not implemented rule function 'show-if-expr' !");

    if (result) {
        for (var j = 0; j < targets.length; j++) {
            actions.push({
                'action': 'classes',
                'selector': targets[j],
                'has': null,
                'has_not': 'hidden'
            });
        }
    } else {
        for (let j = 0; j < targets.length; j++) {
            actions.push({
                'action': 'classes',
                'selector': targets[j],
                'has': 'hidden',
                'has_not': null
            });
        }
    }
    return actions;
}


function form_modified(fields, rule, init_call, event) {
    "use strict";
    var actions = [];
    var ignore_as_first = null;

    //console.log("Modified !", fields, rule, event);
    if (event) {
        if (event.target.classList.contains('ignore-first-modification')) {
            ignore_as_first = event.target.id;
        }
    }

    if (ignore_as_first) {
        actions.push({
            'action': 'classes',
            'has': null,
            'has_not': 'ignore-first-modification',
            'selector': ignore_as_first,
        });
    } else if (!init_call) {
        actions.push({
            'action': 'help',
            'level': 'info',
            'selector': '#main-form-help',
            'text': 'Vous avez modifié le formulaire. Pour quitter la page, validez votre saisie ou réinitialisez le formulaire'
        });
        actions.push({
            'action': 'links-lock',
            'text': 'Vous avez modifié le formulaire. Pour quitter la page, validez votre saisie ou réinitialisez le formulaire'
        });
    }

    return actions;
}


function mandatory(fields, rule, init_call) {
    "use strict";
    var actions = [];

    let fields_keys = Object.keys(fields);

    for (var i = 0; i < fields_keys.length; i++) {
        let base_id = fields_keys[i];
        if (fields[fields_keys[i]].length < 1) {
            var elt = document.querySelector('label[for=' + fields_keys[i] + ']');
            if (elt === null) {
                elt = document.querySelector('label#label-' + fields_keys[i]);
            }
            let field_name;
            if (elt === null) {
                field_name = "<<" + fields_keys[i] + ">>";
            } else {
                field_name = elt.textContent;
            }
            actions.push({
                'action': 'help',
                'level': 'error',
                'selector': '#help-' + base_id,
                'text': 'Le champ "' + field_name + '" est obligatoire',
            });
            actions.push({
                'action': 'classes',
                'selector': '#' + base_id + rule.suffix,
                'has': 'on_error',
                'has_not': null
            });
        } else {
            actions.push({
                'action': 'classes',
                'selector': '#' + base_id + rule.suffix,
                'has_not': 'on_error',
                'has': null
            });
        }
    }
    return actions;
}

// Appelée pour toute modification du champ referent (champ "from")
// rule.to contient l'id de la destination
function smart_copy_from(fields, rule, init_call) {
    "use strict";
    var actions = [];

    var elt_to = document.getElementById(rule.to);

    // Appel initial (à l'ouverture du formulaire)
    // On regarde si la destination est différente du calcul
    // Si oui => pas de changement de valeur MAIS ajout de la classe 'hand-modified' à la destination
    // Si non => copie normale
    if (init_call) {
        // console.log("compute...", this)
        let to_value = rule.compute(fields);
        if ((elt_to.value === '') || (elt_to.value === to_value)) {
            // console.debug('*init '+rule.to.substring(3)+' => copyable');
            actions.push({
                'action': 'value',
                'selector': '#' + rule.to,
                'value': to_value,
            });
            actions.push({
                'action': 'help',
                'level': 'info',
                'selector': '#help-' + rule.to,
                'text': 'La valeur est déterminée automatiquement mais vous pouvez saisir manuellement une valeur si vous le souhaitez'
            });
            actions.push({
                'action': 'rule-trigger',
                'rule_id': 'field-' + rule.cascade + '-mandatory',
            });
        } else {
            //console.debug('*init '+rule.to.substring(3)+' => hand-modified');
            actions.push({
                'action': 'classes',
                'selector': '#' + rule.to,
                'has': 'hand-modified',
                'has_not': null,
            });
            actions.push({
                'action': 'help',
                'level': 'info',
                'selector': '#help-' + rule.to,
                'text': 'Vous avez saisi une valeur. Le remplissage automatique est désactivé (videz le champ pour le réactiver)'
            });
        }
    } else {
        if (!elt_to.classList.contains('hand-modified')) {
            let to_value = rule.compute(fields);
            //console.debug('!init '+rule.to.substring(3)+' => set');
            actions.push({
                'action': 'value',
                'selector': '#' + rule.to,
                'value': to_value,
            });
            actions.push({
                'action': 'help',
                'level': 'info',
                'selector': '#help-' + rule.to,
                'text': 'La valeur est déterminée automatiquement mais vous pouvez saisir manuellement une valeur si vous le souhaitez'
            });
            actions.push({
                'action': 'rule-trigger',
                'rule_id': 'field-' + rule.cascade + '-mandatory',
            });
        } else {
            //console.debug('!init '+rule.to.substring(3)+' => locked (do not modify)');
            actions.push({
                'action': 'help',
                'level': 'info',
                'selector': '#help-' + rule.to,
                'text': 'Vous avez saisi une valeur. Le remplissage automatique est désactivé (videz le champ pour le réactiver)'
            });
        }
    }
    return actions;
}

// Appelée pour toute modification du champ destination (champ "to")
function smart_copy_to(fields, rule, init_call) {
    "use strict";
    let actions = [];

    let targets = Object.keys(fields);

    for (var i = 0; i < targets.length; i++) {
        let target = targets[i];
        if (!init_call) {
            if (fields[target] !== '') {
                // console.debug('!'+target.substring(3)+' => hand-modified');
                actions.push({
                    'action': 'classes',
                    'selector': '#' + target,
                    'has': 'hand-modified',
                    'has_not': null,
                });
                actions.push({
                    'action': 'rule-trigger',
                    'rule_id': rule.cascade,
                });
            } else {
                // console.debug('!init contact => cleaned => copy');
                actions.push({
                    'action': 'classes',
                    'selector': '#' + target,
                    'has': null,
                    'has_not': 'hand-modified',
                });
                actions.push({
                    'action': 'rule-trigger',
                    'rule_id': rule.cascade,
                });
            }
        }
    }
    return actions;
}

function get_from_list(fields, rule, init_call) {
    "use strict";
    let actions = [];

    let targets = Object.keys(fields);

    for (let i = 0; i < targets.length; i++) {
        let target = targets[i];
        let field = fields[i];

        //console.log("get_from_list called on", target, field, rule, document.getElementById(target).value);
        actions.push({
            'action': 'value',
            'value': rule.choices[document.getElementById(target).value] || "&nbsp;",
            'selector': '#' + rule.to,
        });
    }

    return actions;
}


// copy function :
// in_fields is a object with only 1 property
function field_copy(in_fields) {
    "use strict";
    let fname = Object.keys(in_fields);
    return in_fields[fname[0]];
}


class FormHelper {

    constructor(form, rules, options) {
        "use strict";

        function handler(form, rule, elements, options) {
            return function (event) {
                self.helper_cb(form, rule, elements, options, false, event);
            };
        }

        this.rules = rules;
        this.form = form;
        this.options = Object.assign(options, {
            'debug': false,
            'help_container_id': 'help',
        });
        let self = this;

        if (typeof (form) === 'string') {
            form = document.querySelector(form);
        }

        let rules_keys = Object.keys(rules);
        for (let i = 0; i < rules_keys.length; i++) {
            let rule = rules[rules_keys[i]];
            rule.id = rules_keys[i];

            if ('compute' in rule) {
                // console.log("  Rule:", rule.compute);
                rule.compute = this.compute_functions[rule.compute];
            }

            var elements = this.get_elements(form, rule.input_selectors);
            if (options.debug) {
                console.debug('inputs:', elements);
            }
            // Apply the rule once (at launch)
            if (elements.length > 0) {
                this.helper_cb(form, rule, elements, options, true, null);
            }

            for (var k = 0; k < elements.length; k++) {
                if (options.debug) {
                    console.debug(elements[k]);
                }

                elements[k].addEventListener('change', handler(form, rule, elements, options));
            }
        }
    }


    helper_functions = {
        'form-modified': form_modified,
        'expr-function-euros': expr_function_euros,
        'mandatory-field': mandatory,
        'show-if': show_if,
        'show-if-expr': show_if_expr,
        'smart-copy-from': smart_copy_from,
        'smart-copy-to': smart_copy_to,
        'get-from-list': get_from_list,
        'money-format': money_format,
    }

    compute_functions = {
        'copy': field_copy,
    }

    /*
     * Méthode qui est appelée à chaque modification. Elle collecte les
     *   valeurs des champs, appelle la fonction de la règle et
     *   répercute le résultat de la règle sur la page (via le DOM)
     */
    helper_cb(form, rule, elements, options, init_call, event) {
        "use strict";
        if (options.debug) {
            console.debug(rule.func, elements, event);
        }
        var my_vars = {};
        for (var i = 0; i < elements.length; i++) {
            var element = elements[i];
            if (element.type === 'checkbox') {
                my_vars[element.id] = element.checked;
            } else {
                // Get input value
                my_vars[element.id] = element.value;
            }
        }

        let func = this.helper_functions[rule.func];

        if (func !== undefined) {

            let responses = func(my_vars, rule, init_call, event);
            if (options.debug) {
                console.debug("Results from rule " + rule.id);
                console.debug(responses);
            }

            let altered_nodes = [];

            // Remove previous messages from this rule
            let items = document.querySelectorAll(".help-msg");
            for (let i = 0; i < items.length; i++) {
                if (items[i].getAttribute("data-rule") === rule.id) {
                    altered_nodes.push(items[i].parentNode);
                    items[i].parentNode.removeChild(items[i]);
                }
            }

            // Apply rules response to the DOM
            for (let i = 0; i < responses.length; i++) {
                let response = responses[i];

                // Change value
                if (response.action === 'value') {
                    var node_list = form.querySelectorAll(response.selector);
                    for (var j = 0; j < node_list.length; j++) {
                        var node = node_list[j];
                        if ((node.tagName === 'INPUT') || (node.tagName === 'SELECT')) {
                            node.value = response.value;
                        } else if (node.tagName === 'SPAN') {
                            node.innerHTML = response.value;
                        }
                    }
                }
                // Locks every links on the page
                else if (response.action === 'links-lock') {
                    $("a").off("click");
                    $('a').on('click', response, function (e) {
                        if (e.target.onclick === null) {
                            // Ne s'applique que pour les liens "normaux" (sans onclick défini)
                            e.preventDefault();
                            alert(e.data.text);
                        }
                    });
                }
                // Change classes
                else if (response.action === 'classes') {
                    let node_list = form.querySelectorAll(response.selector);
                    for (let j = 0; j < node_list.length; j++) {
                        let classes = node_list[j].classList;

                        let has_not = response.has_not;
                        if (typeof (response.has_not) === 'string') {
                            has_not = [response.has_not];
                        }
                        if (has_not) {
                            for (let k = 0; k < has_not.length; k++) {
                                classes.remove(has_not[k]);
                            }
                        }
                        let has = response.has;
                        if (typeof (response.has) === 'string') {
                            has = [response.has];
                        }
                        if (has) {
                            for (let k = 0; k < has.length; k++) {
                                classes.add(has[k]);
                            }
                        }
                    }
                }
                // Add/replace help messages
                else if (response.action === 'help') {
                    var parents = document.querySelectorAll(response.selector);
                    if (options.debug) {
                        console.debug("parents:", parents);
                    }
                    if (parents.length < 1) {
                        console.warn("Rule " + rule.id + " returns a help message (selector = '" + response.selector +
                            "' which do not match !");
                    }
                    for (let j = 0; j < parents.length; j++) {
                        let parent = parents[j];
                        //console.debug("parent", parent);
                        let item = document.createElement("div");
                        item.setAttribute("data-rule", rule.id);
                        item.classList.add("help-msg");
                        item.classList.add("help-" + response.level);
                        item.textContent = response.text;
                        //TODO: insert at the right place to keep messages sorted by level
                        parent.appendChild(item);
                        altered_nodes.push(parent);
                    }
                }
                // Trigger a rule (last action !!)
                else if (response.action === 'rule-trigger') {
                    let rule = this.rules[response.rule_id];
                    //console.debug("trigering rule", response.rule_id, rule);
                    if (rule) {
                        let elements = this.get_elements(form, rule.input_selectors);
                        this.helper_cb(form, rule, elements, options, false, null);
                    } else {
                        console.warn("Rule not found :", response.rule_id);
                    }
                } else {
                    console.warn("Rule " + response.rule_id + " returns unknown action: " + response.action);
                }
            }

            // Compute highest level
            for (i = 0; i < altered_nodes.length; i++) {
                var highest_level = 0;
                var parent = altered_nodes[i];
                // console.log("altered node (bubble)", parent);

                for (let k = 0; k < parent.children.length; k++) {
                    var child = parent.children[k];
                    if (child.classList.contains('help-error')) {
                        highest_level = 3;
                    } else if (child.classList.contains('help-warning') && (highest_level <= 2)) {
                        highest_level = 2;
                    } else if (child.classList.contains('help-info') && (highest_level <= 1)) {
                        highest_level = 1;
                    }
                }
                // console.log("level", highest_level);

                var grandparent = parent.parentElement;
                // console.debug("gparent", grandparent.classList);
                if (highest_level >= 3) {
                    grandparent.classList.add("error");
                } else if (highest_level >= 2) {
                    grandparent.classList.remove("error");
                    grandparent.classList.add("warning");
                } else if (highest_level >= 1) {
                    grandparent.classList.remove("error");
                    grandparent.classList.remove("warning");
                    grandparent.classList.add("info");
                } else {
                    grandparent.classList.remove("error");
                    grandparent.classList.remove("warning");
                    grandparent.classList.remove("info");
                }
            }
        } else {
            console.warn("Unrecognised function name:", rule.func, rule);
        }
    }

    // Method that get elements from a selector _or_ a list of selectors
    get_elements(form, selectors) {
        "use strict";
        var isels;
        if (typeof (selectors) === 'string') {
            isels = [selectors];
        } else {
            isels = selectors;
        }
        var elements = [];
        for (var j = 0; j < isels.length; j++) {
            var node_list = form.querySelectorAll(isels[j]);
            for (var k = 0; k < node_list.length; k++) {
                elements.push(node_list[k]);
            }
        }
        return elements;
    }
}
