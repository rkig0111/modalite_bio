/*
 * Fonction qui détecte si un champ "déclencheur" (classe "subform-trigger")
 * est activé et, si oui, montre le sous-formulaire en question
 *
 * C'est une fonction qui balaye tous les objets. On peut donc ne faire qu'une seule
 * règle.
 *
 * Utilisation :
 *   - Le champ déclencheur doit avoir la classe "subform-trigger" et un id défini ("id_champ" par exemple)
 *   - Le sous-formulaire (ou toute autre partie de la page...) doit avoir la classe "id_champ-subform".
 *   - Le CSS doit définir "display:none;" pour tous les éléments appartenant à la classe "hidden"
 */ 
function subform(fields, rule, init_call) {
    var actions = [];

    //console.debug(fields);

    var fields_l = Object.keys(fields);

    for (var i = 0; i < fields_l.length; i++) {
        var field_n = fields_l[i];

        if (fields[field_n]) {
            actions.push({
                'action': 'classes',
                'selector': '.' + field_n + '-subform',
                'has': null,
                'has_not': 'hidden'
            });
        } else {
            actions.push({
                'action': 'classes',
                'selector': '.' + field_n + '-subform',
                'has': 'hidden',
                'has_not': null
            });
        }
    }
    return actions;
}


function mandatory(fields, rule, init_call) {
    var actions = [];

    fields_keys = Object.keys(fields);

    for (var i = 0; i < fields_keys.length; i++) {
        base_id = fields_keys[i].substring(3);
        if (fields[fields_keys[i]].length < 1) {
            var elt = document.querySelector('label[for=' + fields_keys[i] + ']');
            if (elt === null) {
                elt = document.querySelector('label#' + fields_keys[i] + '-label');
            }
            if (elt === null) {
                var field_name = "<<" + fields_keys[i] + ">>";
            } else {
                var field_name = elt.textContent;
            }

            actions.push({
                'action': 'help',
                'level': 'error',
                'selector': '#' + base_id + '-help',
                'text': 'Le champ "' + field_name + '" est obligatoire',
            });
            actions.push({
                'action': 'classes',
                'selector': '#id_' + base_id,
                'has': 'on_error',
                'has_not': null
            });
        } else {
            actions.push({
                'action': 'classes',
                'selector': '#id_' + base_id,
                'has_not': 'on_error',
                'has': null
            });
        }
    }
    return actions;
}


function form_errors(fields, rule, init_call) {
    var actions = [];
    //console.debug("form_errors called");

    fields_keys = Object.keys(fields);

    for (var i = 0; i < fields_keys.length; i++) {
        //console.debug("  Error on field", fields_keys[i].substring(9));
        error_message = document.getElementById(fields_keys[i]).innerHTML;
        //console.debug("  ", error_message);
        actions.push({
            'action': 'help',
            'level': 'error',
            'selector': '#' + fields_keys[i].substring(9) + '-help',
            'text': error_message,
        });
        actions.push({
            'action': 'classes',
            'selector': '#id_' + fields_keys[i].substring(9),
            'has': 'on_error',
            'has_not': null
        });
    }

    return actions;
}

function form_modified(fields, rule, init_call) {
    var actions = [];

    if (!init_call) {
        actions.push({
            'action': 'help',
            'level': 'info',
            'selector': '#main-help',
            'text': 'Vous avez modifié le formulaire. Pour quitter la page, validez votre saisie ou réinitialisez le formulaire'
        });
        actions.push({
            'action': 'links-lock',
            'text': 'Vous avez modifié le formulaire. Pour quitter la page, validez votre saisie ou réinitialisez le formulaire'
        });
    }

    return actions;
}

function format_prix(fields, rule, init_call) {
    var actions = [];
    var keys = Object.keys(fields);
    for (var i = 0; i < keys.length; i++) {
        var key = keys[i];
        var value = fields[key];

        if (value.length > 0) {
            // récupère les espaces et le '€' et remplace l'éventuelle ',' par un '.'
            value = value.replace(/[€\s]/g, '').replace(/,/g, '.');
            //console.log("Prix value filtered", value);

            value_number = Number(value)
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


function existant(fields, rule, init_call) {
    var actions = [];

    if (fields.id_cause == 'RE') {
        actions.push({
            'action': 'help',
            'level': 'info',
            'selector': '#materiel_existant-help',
            'text': "Précisez ici quel est le matériel à remplacer (N° inventaire)",
        });
        actions.push({
            'action': 'classes',
            'selector': '.existant-row',
            'has': null,
            'has_not': 'hidden'
        });
    } else if (fields.id_cause == 'EV') {
        actions.push({
            'action': 'help',
            'level': 'info',
            'selector': '#materiel_existant-help',
            'text': "Précisez ici quel est le matériel à faire évoluer (N° inventaire)",
        });
        actions.push({
            'action': 'classes',
            'selector': '.existant-row',
            'has': null,
            'has_not': 'hidden'
        });
    } else {
        actions.push({
            'action': 'classes',
            'selector': '.existant-row',
            'has': 'hidden',
            'has_not': null
        });
    }

    return actions;
}

function denomination(fields, rule, init_call) {
    var actions = [];

    if (fields.id_nom_projet.length < 1) {
        actions.push({
            'action': 'help',
            'level': 'error',
            'selector': '#nom_projet-help',
            'text': 'Le champs "Dénomination" est obligatoire',
        });
        actions.push({
            'action': 'classes',
            'selector': '#id_nom_projet',
            'has': 'on_error',
            'has_not': null
        });
    } else {
        actions.push({
            'action': 'classes',
            'selector': '#id_nom_projet',
            'has': null,
            'has_not': 'on_error'
        });
    }

    return actions;
}


function code_uf(fields, rule, init_call) {
    var actions = [];

    if (fields.id_uf.length < 1) {
        actions.push({
            'action': 'help',
            'level': 'error',
            'selector': '#uf-help',
            'text': 'Le champs "UF" est obligatoire',
        });
        actions.push({
            'action': 'classes',
            'selector': '#id_uf',
            'has': 'on_error',
            'has_not': null
        });
    } else {
        actions.push({
            'action': 'classes',
            'selector': '#id_uf',
            'has': null,
            'has_not': 'on_error'
        });
    }

    return actions;
}


function cause(fields, rule, init_call) {
    var actions = [];

    if (fields.id_cause == "RE") {
        actions.push({
            'action': 'help',
            'level': 'info',
            'selector': '#cause-help',
            'text': "Remplacement : L'équipement remplacera un autre, plus ancien, qui sera retiré du service",
        });
    } else if (fields.id_cause == "AQ") {
        actions.push({
            'action': 'help',
            'level': 'info',
            'selector': '#cause-help',
            'text': "Augmentation de Quantité : L'équipement viendra en complément du parc de matériel du même type dans le service",
        });
    } else if (fields.id_cause == "EV") {
        actions.push({
            'action': 'help',
            'level': 'info',
            'selector': '#cause-help',
            'text': "Evolution : La demande vise à faire évoluer un équipement existant",
        });
    } else if (fields.id_cause == "TN") {
        actions.push({
            'action': 'help',
            'level': 'info',
            'selector': '#cause-help',
            'text': "Technique Nouvelle : L'équipement sera utilisé pour mettre en œuvre une technique nouvelle au sein du service",
        });
    } else if (fields.id_cause == "RA") {
        actions.push({
            'action': 'help',
            'level': 'info',
            'selector': '#cause-help',
            'text': "Rachat fin de marhé : Rachat d'un équipement suite à l'arrivée du terme d'un marché de location (LOA), de Mise à disposition (MAD) ou d'un crédit bail",
        });
    }
    return actions;
}


function argum_justif(fields, rule, init_call) {
    var actions = [];

    var arg_length = 0;

    //console.debug(fields);
    var keys = Object.keys(fields);
    for (var i = 0; i < keys.length; i++) {
        var key = keys[i];
        if (fields[key] === false) {} else if (fields[key] === true) {
            arg_length += 10
        } else {
            arg_length += fields[key].length
        }
    }

    if (arg_length < 10) {
        actions.push({
            'action': 'help',
            'level': 'warning',
            'selector': '#argumentaire-help',
            'text': "L\'argumentation semble pour l'instant insuffisante, ce qui réduit les chances d'obtenir un avis favorable lors des arbitrages.",
        });
    }

    return actions;
}

function precisions_arg(fields, rule, init_call) {
    var actions = [];

    //console.debug(fields);

    if (fields.precisions_arg) {
        actions.push({
            'action': 'classes',
            'selector': '#precisions_arg-sf',
            'has': null,
            'has_not': 'hidden'
        });
    } else {
        actions.push({
            'action': 'classes',
            'selector': '#precisions_arg-sf',
            'has': 'hidden',
            'has_not': null
        });
    }

    return actions;
}

function calcul_enveloppe(in_fields) {
    if (in_fields.id_prix_unitaire == '')
        return '';
    else {
        var r = Math.round(Number(in_fields.id_quantite) * Number(in_fields.id_prix_unitaire.replace(/[€\s]/g, '').replace(/,/g,
            '.')));
        if (isNaN(r)) {
            return '';
        } else {
            return r.toLocaleString("fr-FR") + " €"
        }

    }
    //return (Math.round(in_fields.id_quantite.replace(/[^0-9,.]/g,"").replace(/,/g,".")) * Math.round(in_fields.id_prix_unitaire.replace(/[^0-9,.]/g,"").replace(/,/g,"."))).toLocaleString("fr-FR") + " €";
}

// copy function :
// in_fields is a object with only 1 property
function copy(in_fields) {
    fname = Object.keys(in_fields);
    return in_fields[fname[0]];
}

function clean_name(name) {
    return name.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s/g, '').toLowerCase();
}

function make_email(in_fields) {
    return clean_name(in_fields.id_last_name) + '.' + clean_name(in_fields.id_first_name) + '@chu-amiens.fr';
}

function make_username(in_fields) {
    return clean_name(in_fields.id_last_name).substring(0, 6) + clean_name(in_fields.id_first_name).substring(0, 2);
}

// Appelée pour toute modification du champ referent (champ "from")
// rule.to contient l'id de la destination
function from_fields(fields, rule, init_call) {
    var actions = [];

    var elt_to = document.getElementById(rule.to);

    // Appel initial (à l'ouverture du formulaire)
    // On regarde si la destination est différente du calcul
    // Si oui => pas de changement de valeur MAIS ajout de la classe 'hand-modified' à la destination
    // Si non => copie normale
    if (init_call) {
        to_value = rule.compute(fields);
        if ((elt_to.value == '') || (elt_to.value == to_value)) {
            //console.debug('*init '+rule.to.substring(3)+' => copyable');
            actions.push({
                'action': 'value',
                'selector': '#' + rule.to,
                'value': to_value,
            });
            actions.push({
                'action': 'help',
                'level': 'info',
                'selector': '#' + rule.to.substring(3) + '-help',
                'text': 'La valeur est déterminée automatiquement mais vous pouvez saisir manuellement une valeur si vous le souhaitez'
            });
            actions.push({
                'action': 'rule-trigger',
                'rule_id': 'obligatoires',
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
                'selector': '#' + rule.to.substring(3) + '-help',
                'text': 'Vous avez saisi une valeur. Le remplissage automatique est désactivé (videz le champ pour le réactiver)'
            });
        }
    } else {
        if (!elt_to.classList.contains('hand-modified')) {
            to_value = rule.compute(fields);
            //console.debug('!init '+rule.to.substring(3)+' => set');
            actions.push({
                'action': 'value',
                'selector': '#' + rule.to,
                'value': to_value,
            });
            actions.push({
                'action': 'help',
                'level': 'info',
                'selector': '#' + rule.to.substring(3) + '-help',
                'text': 'La valeur est déterminée automatiquement mais vous pouvez saisir manuellement une valeur si vous le souhaitez'
            });
            actions.push({
                'action': 'rule-trigger',
                'rule_id': 'obligatoires',
            });
        } else {
            //console.debug('!init '+rule.to.substring(3)+' => locked (do not modify)');
            actions.push({
                'action': 'help',
                'level': 'info',
                'selector': '#' + rule.to.substring(3) + '-help',
                'text': 'Vous avez saisi une valeur. Le remplissage automatique est désactivé (videz le champ pour le réactiver)'
            });
        }
    }
    return actions;
}

// Appelée pour toute modification du champ destination (champ "to")
function to_field(fields, rule, init_call) {
    var actions = [];

    var targets = Object.keys(fields);

    for (var i = 0; i < targets.length; i++) {
        target = targets[i];
        if (!init_call)
            if (fields[target] != '') {
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
            }
        else {
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
    return actions;
}

/*
 * Fonction appelée pour synchroniser le champ caché "id_uf" avec le
 * flexdatalist créé sur le champ texte visible "dyn_uf"
 * */
function test_uf(fields, rule, init_call) {
    var actions = [];

    // console.log("test_uf...");

    if (init_call) {
        // récupère l'UF depuis le champs caché "uf"
        var elt = document.getElementById("id_uf");

        $('#id_dyn_uf').flexdatalist('value', elt.value);

        // Simule la saisie dans le champs "structure"
        actions.push({
            action: 'rule-trigger',
            rule_id: 'obligatoires',
        });

    } else {
        // console.log("test_uf... on update...", $('#id_dyn_uf').val());
        actions.push({
            'action': 'value',
            'selector': '#id_uf',
            'value': fields.id_dyn_uf,
        });
    }

    // console.log("test_uf... on update...", $('#id_dyn_uf').val(), data.valid_ufs);

    var uf_id = parseInt($('#id_dyn_uf').val());

    if (data.valid_ufs.indexOf(uf_id) >= 0) {

        var elt = document.getElementById("nom_service");
        if (elt) {
            elt.innerText = data.services[data.ufs[data.uf_id[uf_id]]['service__code']]['nom'];
            // console.debug("Set nom service:", data.services[data.ufs[data.uf_id[uf_id]]['service__code']]['nom']);
        }
        elt = document.getElementById("nom_pole");
        if (elt) {
            elt.innerText = data.poles[data.ufs[data.uf_id[uf_id]]['pole__code']]['nom'];
            // console.debug("Set nom pole:", data.poles[data.ufs[data.uf_id[uf_id]]['pole__code']]['nom']);
        }
        elt = document.getElementById("nom_organisation");
        if (elt) {
            elt.innerText = data.organisations[data.ufs[data.uf_id[uf_id]]['etablissement__code']]['nom'];
            // console.debug("Set nom etablissement:", data.organisations[data.ufs[data.uf_id[uf_id]]['etablissement__code']]['nom']);
        }

        actions.push({
            action: 'classes',
            selector: '#id_dyn_uf-flexdatalist',
            has: [],
            has_not: ['on_error'],
        });
    } else {
        var elt = document.getElementById("nom_service");
        if (elt) {
            elt.innerHTML = "&nbsp;";
        }
        elt = document.getElementById("nom_pole");
        if (elt) {
            elt.innerHTML = "&nbsp;";
        }
        elt = document.getElementById("nom_organisation");
        if (elt) {
            elt.innerHTML = "&nbsp;";
        }

        actions.push({
            action: 'classes',
            selector: '#id_dyn_uf-flexdatalist',
            has: ['on_error'],
            has_not: [],
        });

        if ($('#id_dyn_uf').val().length > 0) {
            actions.push({
                'action': 'value',
                'selector': '#id_uf',
                'value': '',
            });
            actions.push({
                action: 'help',
                selector: '#dyn_uf-help',
                level: 'error',
                text: "L'UF saisie n'est pas valide",
            });
        }
    }
    return actions;
}


common_rules = {
    // Modification de formulaire : bloque les liens simples et fait une alerte si tentative de sortie de la page
    'form_modified': {
        'input_selectors': ['input'],
        'func': form_modified,
    },
    // Gestion des erreurs de formulaire (affiche les erreurs retournées par Django exactement sur le champ concerné)
    'form_errors': {
        'input_selectors': ['.form-error'],
        'func': form_errors,
    },
    // Champs obligatoires (mettre en évidence en temps réel)
    'obligatoires': {
        //'input_selectors':['.required'],
        'input_selectors': ['#id_nom_projet', '#id_referent', '#id_uf', "#id_libelle", "#id_dyn_uf", "#id_username",
            "#id_password1", '#id_password2'
        ],
        'func': mandatory,
    },
    // Sous-formulaires (montrer / cacher)
    'subforms': {
        'input_selectors': ['.subform-trigger'],
        'func': subform
    },
};

demande_rules = {
    // Affiche le champs 'matériel concerné' pour un remplacement ou une évolution
    'materiel_existant': {
        'input_selectors': ['#id_cause'],
        'func': existant
    },
    // Longueur de l'argumentation (alerter si trop court)
    'argum_justif': {
        'input_selectors': ['.arg-detail', '#id_autre_argumentaire'],
        'func': argum_justif
    },
    // Cause (explique le choix)
    'cause': {
        'input_selectors': ['#id_cause'],
        'func': cause
    },
    // Reformate le prix unitaire (entier, espaces, euro)
    // Cette règle doit être avant les règles de copie (from/to)
    'prix_unit': {
        'input_selectors': '#id_prix_unitaire',
        'func': format_prix
    },
    // Reformate le montant total (entier, espaces, euro)
    // Cette règle doit être avant les règles de copie (from/to)
    'prix_projet': {
        'input_selectors': '#id_montant',
        'func': format_prix
    },

    // Pour chaque champs calculé/copié en semi-auto, il faut DEUX règles :
    //  Une règle 'from_fields' avec le nom de la source, etc.
    // contact auto from referent
    'from_referent': {
        'input_selectors': ['#id_referent'],
        'func': from_fields,
        'compute': copy,
        'to': 'id_contact',
    },
    // referent to contact auto
    'to_contact': {
        'input_selectors': ['#id_contact'],
        'func': to_field,
        'cascade': 'from_referent',
    },

    // From
    'from_libelle': {
        'input_selectors': ['#id_libelle'],
        'func': from_fields,
        'compute': copy,
        'to': 'id_nom_projet',
    },
    // To
    'to_nom_projet': {
        'input_selectors': ['#id_nom_projet'],
        'func': to_field,
        'cascade': 'from_libelle',
    },

    // Calcul enveloppe
    // From
    'from_qte_pu': {
        'input_selectors': ['#id_quantite', '#id_prix_unitaire'],
        'func': from_fields,
        'compute': calcul_enveloppe,
        'to': 'id_montant',
    },
    // To
    'to_enveloppe': {
        'input_selectors': ['#id_montant'],
        'func': to_field,
        'cascade': 'from_qte_pu',
    },

    // UF AUTO
    'uf': {
        'input_selectors': ['#id_dyn_uf'],
        'func': test_uf,
    },
};

signup_rules = {
    // Username (formulaire signup)
    'from_name_u': {
        'input_selectors': ['#id_first_name', '#id_last_name'],
        'func': from_fields,
        'compute': make_username,
        'to': 'id_username',
    },
    'to_username': {
        'input_selectors': ['#id_username'],
        'func': to_field,
        'cascade': 'from_name_u',
    },

    // Email (formulaire signup)
    'from_name': {
        'input_selectors': ['#id_first_name', '#id_last_name'],
        'func': from_fields,
        'compute': make_email,
        'to': 'id_email',
    },
    'to_email': {
        'input_selectors': ['#id_email'],
        'func': to_field,
        'cascade': 'from_name',
    },

};