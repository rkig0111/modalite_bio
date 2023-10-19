==============
Smart Format :
==============

Un objet ``SmartFormat`` est une passerelle entre une valeur (python ou base de données) et
les outils/frameworks/logiciels chargés de faire le lien avec l'utilisateur.

Par exemple, si on a un objet ``date_format`` qui définit un format de date,
la valeur de base doit être un objet datetime python, la configuration (sorte de
définition canonique du format) pourrait être 'dd mmm YY' et il doit permettre :

    - De convertir une date en chaîne de caractères python (avec le respect du format)
    - De convertir une date en chaîne de caractères html (avec le respect du format)
    - Proposer un widget HTML qui affiche et/ou permet de saisir une date avec ce format
    - Proposer une configuration de Tabulator.js qui permet de gérer une date avec ce format
      (c'est à dire un ``formatter``, un ``mutator`` et un ``editor``)
    - Proposer des fonctions pour convertir une date vers un fichier ``pdf`` ou ``LateX``, par exemple.



.. todo::
    l'API actuelle, construite au fur et à mesure du développement est épouvantable
