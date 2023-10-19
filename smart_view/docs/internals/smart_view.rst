=============
Smart View :
=============

Une SmartView est une classe Python qui, en quelque sorte, "étend" un modèle
Django en lui ajoutant :

- Des champs calculés
- Une gestion des permissions
- Des formats
- Des filtres

Une SmartView est aussi en mesure de générer des objets graphiques (html) :

- Tableau (éditable)
- Formulaire

La SmartView fournit aussi les méthodes HTTP pour gérer les requêtes nécessaires au bon fonctionnement
de ces objets graphiques

Les champs calculés :
=====================

Un champs calculé est un champs qui est ajouté à chaque enregistrement. Il est calculé à partir :

- Des autres champs du modèle (y compris, éventuellement, d'autres champs calculés)
- De certains paramètres de la requête (utilisateur, date courante, etc.)

.. note::
    Techniquement, un champs calculé est une `annotation` de Django. Pour l'instant, cela se fait par le biais d'une
    expression Django mais à l'avenir, un gestionnaire d'expression (donné sous forme d'une chaîne de caractères)
    est envisagé. Cela permettra notamment de créer des champs calculés dans les SmartViews à partir de fichiers
    de configuration (voir le chapitre sur la `factory` de SmartView).


La gestion des permissions :
============================

La gestion des permissions s'appuie sur deux notions :

- Les rôles
- L'état d'un enregistrement

...à rédiger...

.. note::
    Les champs calculés et la gestion des permissions pourraient un jour être intégrés dans un module dédié,
    nommé `overoly`.

Les formats :
=============

Voir chapitre dédié.

Les filtres :
=============

...à rédiger...

Les tableaux éditables :
========================

...à rédiger...

Les formulaires :
=================

...à rédiger...
