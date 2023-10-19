============
Smart Form :
============

La classe SmartForm est une sous-classe de la classe ModelForm de Django.

Cela signifie qu'un SmartForm se comporte globalement comme un ModelForm Django
(cf. `documentation <https://docs.djangoproject.com/fr/4.0/topics/forms/modelforms/>`_ Django) :

- Instancié sans paramètre, il crée un formulaire vide (pour créer une nouvelle entrée dans la base)
- Instancié avec une requête (request.POST le plus souvent), il crée un formulaire liée à une nouvelle instance d'un
  objet de la base. L'utilisation de la méthode `save()` créera effectivement ce nouvel objet dans la base.
- Instancié avec un objet de la base (`instance=...`), il crée un formulaire lié à cet objet
- Instancié avec un objet de la base **et** un requête, il permet de préparer la modification d'un objet de la base.
  Cette modification sera effective après l'appel de la méthode `save()`.

La classe SmartForm apporte les fonctionnalités supplémentaires suivantes :

- Mise en page rapide via un gabarit texte simple
- Widgets sophistiqués (dates avec calendrier, listes de choix avec recherche et AJAX...)
- Gestion des droits définis dans la SmartView
- Champs calculés (stockés dans la base ou non)
- Possibilité de montrer ou de cacher (dynamiquement) un champs ou même une section entière en fonction de la valeur
  d'un autre champs
- Utilisation des étiquettes et textes d'aide de la SmartView associée.

Création d'une classe SmartForm
===============================

Pour l'instant, chaque SmartView crée sa propre classe SmartForm lors de l'initialisation de Django.

Cela signifie que les informations nécessaires à la création de la classe SmartForm doivent être
fournis directement dans la classe `Meta` de la SmartView. Au 07/07/2022, le seul attribut à donner est
l'attribut `form_layout` qui donne le gabarit du formulaire.

Syntaxe de `form_layout`:
----------------------------

C'est une chaîne de caractère multilignes (il est conseillé d'utiliser le triple quote ou le triple double quote).

Les règles utilisées sont :

- Le formulaire est disposé sur une grille (en lignes et en colonnes)
- Chaque ligne de la chaîne de caractères correspond à une ligne du formulaire
- L'indentation compte : Chaque niveau d'indentation implique la création d'un "sous-formulaire".
  Le premier niveau d'indentation est neutralisé (on peut commencer à n'importe quel niveau et pas uniquement à
  la colonne 0 (pour rester aligné avec le code Python).
- Les espaces (hors indentation) sont ignorés
- Une ligne qui commence par un `#` est un titre de section (ou de sous-section)
- Il est possible d'utiliser des variables dans les titres, en encadrant la variable entre `{{` et `}}`.
  La seule variable accessible est `instance` pour l'instant (on utilise un champ avec `{{ instance.comment }}`,
  par exemple. Cela n'a de sens que pour les champs non modifiables.
- Un champ prend normalement 2 colonnes : Une pour le titre (l'étiquette) et une pour le champ lui-même.
- Un champ est défini par son nom (identifiant défini dans la SmartView) encadré par `<` et `>` (*l'espace de champ*).
  Par exemple : `<comment>`.
- Le caractère `-` dans l'espace de champ (avant ou après un nom de champ) est ignoré. Ainsi : `<comment>`, `<--comment>`, `<comment-->
  et `<-comment->` seront interprétés exactement de la même manière.
- S'il y a un `+` dans l'espace de champ, cela rallonge de deux colonnes la taille du champ sur la grille.
  Ainsi `<comment---+--->` consommera 4 colonnes : 1 pour le titre et 3 pour le champ lui-même.
- Si un champ est trouvé, à la même position, sur 2 lignes successives, il consommera 2 lignes de la grille. Attention,
  comme la grille est 'élastique', cela ne sera visible que s'il y a d'autres champs, non dupliqués, sur ces lignes.


Propriétés des champs de la SmartView utilisées
===============================================

**title** Titre du champ (étiquette)

**help_text** Texte d'aide (à destination de l'utilisateur) pour ce champ.

**initial** Valeur de remplissage initiale, pour un nouvel objet. Cette valeur sera écrasée par la valeur
éventuellement fournie à la création du formulaire (typiquement une valeur fournie via la requête HTTP).

**choices** ezfzefzef
 efzefzef ef zef zefzef

**show-if** Détermine si un champ (entier : titre + champ de saisie) doit être affiché ou non.

**hidden** Si cette propriété vaut `True`, le champs ne sera jamais affiché (mais fera néanmoins partie du formulaire).

**data** efzefze


+-----------------------------+----------------+-----------------+----------------+------------------------+------------+------------------------------------------------+
| Droits (selon rôle et état) | Champ          | Choix           | Valeur fournie | Affichage              | Enregistré | Exemple                                        |
+=============================+================+=================+================+========================+============+================================================+
| Oui                         | Texte / Nombre | Non défini      | Oui            | Texte, valeur initiale | Oui        | Tous les champs classiques                     |
|                             |                |                 |                |                        |            |                                                |
+-----------------------------+----------------+-----------------+----------------+------------------------+------------+------------------------------------------------+
| Non                         | Texte / Nombre | Sans objet      | Oui            | R/O                    |     Non    | Champ en lecture seule lors d'une modification |
+-----------------------------+----------------+-----------------+----------------+------------------------+------------+------------------------------------------------+
| Oui                         | Texte / Nombre | Oui (plus de 1) | Oui            | Choix                  | Oui        | Texte / nombre à choisir dans une liste,       |
|                             |                |                 |                |                        |            | typiquement un code (discipline, rôle...)      |
+-----------------------------+----------------+-----------------+----------------+------------------------+------------+------------------------------------------------+
| Oui                         | Texte / Nombre | Oui (1 seul)    | Oui            | R/O                    | Oui        |                                                |
+-----------------------------+----------------+-----------------+----------------+------------------------+------------+------------------------------------------------+
|                             |                |                 |                |                        |            |                                                |
+-----------------------------+----------------+-----------------+----------------+------------------------+------------+------------------------------------------------+
|                             |                |                 |                |                        |            |                                                |
+-----------------------------+----------------+-----------------+----------------+------------------------+------------+------------------------------------------------+
