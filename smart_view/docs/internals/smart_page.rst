========================
Smart Page :
========================

Une SmartPage est une View (classe) qui permet de générer plusieurs vues (ou plus exactement plusieurs URLs)
pour travailler sur un modèle unique, sur la base d'une SmartView principale (avec son modèle)
Notamment, la SmartPage donne par défaut des vues pour :

- Ajouter un élément au modèle
- Modifier un élément du modèle
- Voir un élément du modèle
- Copier un élément du modèle (pour en créer un nouveau avec certains champs identiques)
- Supprimer un élément du modèle
- Voir (tableau / Smartview) des éléments du modèle

Toutes ces opérations peuvent être configurées et en particulier tenir compte des rôles et des droits de l'utilisateur et
être limités aux contraintes données par la SmartView (par exemple objets dans un état donné)
ou être configurées vue par vue.

Les vues générées seront nommées (pour utilisation de reverse() ou du tag {% url %}) sous la forme :
appname:name-mode
où :

- appname est le nom de l'application (autodétecté)
- name est le nom de la page, fourni dans l'attribut de classe 'name'
- le nom du mode (celle décrite avec le mode 'None' a pour nom 'appname-name' tout simplement

Les différents modes sont :

:None: Une vue (dans un tableau) de la SmartView, avec un menu, des filtres, etc.
:'create': Un formulaire pour ajouter un nouvel élément dans la table
:'copy': Copie d'un élément de la table (ouvre un formulaire pour créer un nouvel élément mais avec certaines données
    pré-saisies depuis l'élément à copier.
:'modify': Un formulaire pour modifier un élément déjà dans la table
:'ask_delete': Un formulaire simple (affichage en lecture seule + boutons) pour demander à
    l'utilisateur une confirmation avant de supprimer un objet
:'delete': Suppression effective d'un élément.
