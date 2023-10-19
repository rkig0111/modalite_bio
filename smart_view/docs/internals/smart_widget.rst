================
Smart Widget :
================

Un SmartWidget est une classe Python qui génère un objet graphique à la demande. Il est prévu pour être affiché
sur une page HTML, particulièrement dans un environnement Django.

Il possède les caractéristiques suivantes :

- Il gère ses 'media' (au sens de Django, c'est à dire les fichiers de style CSS et les scripts JS).
- Il peut être hiérarchique (un widget peut être composé d'autres widgets)
- Il peut être créé soit de façon classique / statique, dans le code, par héritage d'autres classes Widget ou
  par création dynamique "au vol".
- Il a un mode de fonctionnement très déclaratif : Un widget est paramétrique et son code est exécuté à chaque rendu
  d'une vue Django pour créer une représentation graphique.
- Il peut être 'actif' au sens http car il a une porte d'entrée et peut donc recevoir des requêtes et les
  traiter [partie non implémentée, à finaliser...]
