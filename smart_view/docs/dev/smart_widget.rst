================
Smart Widget :
================

L'utilisation d'un widget se fait en X étapes :

- La classe est créée soit via le code python, soit par le biais de la `factory` qui est une méthode classe
  pour chaque Widget. La `factory` permet de créer dynamiquement, **au lancement de Django seulement**,
  (par exemple à partir d'un fichier de configuration) des classes de Widget.
- L'objet python widget est créé à partir de sa classe. **Méthode `__init__()`**
- La structure du widget est finalisée (ou créée si elle est dynamique). **Méthode setup()**.
- Les différents paramètres internes sont calculés, dans le widget et dans ses enfants (propagation) :
  **Méthode `parameters_process()`**. Le widget principal (*top level*) ne devrait prendre comme paramètres entrants
  que les paramètres de vue standards (utilisateur, requête, GET, POST, rôles de l'utilisateur,
  préférences de l'utilisateur, heure courante, etc.)
- Le contexte de rendu est créé à partir des paramètres transmis et/ou calculés et d'un *mapping* des variables.
  **Méthode `_get_context_data()`**. Il n'est normalement pas nécessaire de surcharger cette méthode.
- Enfin, le rendu final utilise le template et la liste des différents enfants, dont les différents contextes ont
  été calculés lors de l'étape précédente, pour générer le code HTML final. **Méthode `as_html()`**. Il n'est normalement pas nécessaire de surcharger cette méthode.

Idéalement, un widget doit être complètement déclaratif : La seule méthode qui devrait être surchargée est
`params_process()`. A terme, cette méthode pourra être totalement être défini avec une fonction déclarée
(à l'aide d'un objet SmartExpression venant, par exemple, d'un fichier de configuration ou d'une chaîne de
caractères).

Conception d'un widget statique
--------------------------------

Un widget statique est un widget dont la structure (arborescence des sous-widgets) est complètement
définie, quelles que soient les valeurs des paramètres (params). Il est donc défini complètement dans le
code et/ou dans les fichiers de configuration.

Conception d'un widget dynamique
---------------------------------

Un widget dynamique est un widget dont la structure (arborescence des sous-widgets) est calculée
en fonction des valeurs de paramètres de vue.

Conception d'un widget passif
------------------------------

Un widget passif est un widget qui, une fois rendu (calcul de la chaîne HTML et des dépendances JS et CSS) n'a plus
besoin d'interaction entre la page et le serveur. Il peut tout de même contenir du code JS qui donne une impression de
dynamisme, mais sans requête HTTP vers le serveur pour, par exemple, récupérer des données. Si un widget utilise l'API
data de BiomAid pour récupérer des données, il est considéré comme passif car il n'a pas besoin de l'instantiation de
la version python pour fonctionner.

Il n'a pas besoin d'être instancié en mode `'api'`

Conception d'un widget actif
-----------------------------

Un widget actif est un widget dont
