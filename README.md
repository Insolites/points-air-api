# points-air-api
API Backend pour Points-Air

## Installation

Pour gérer les paquets et l'installation on utilise
[hatch](https://hatch.pypa.io/latest/).  Installez-le selon les
instructions (le plus facile si vous avez `pipx` c'est simplement
`pipx install hatch`).  Vous pouvez maintenant lancer le serveur de
développement avec:

    hatch run dev

Naviguez à http://127.0.0.1:8092/ (ou l'adresse émise par les messages
sur le console) pour confirmer que ça fonctionne.

## Utilisation

Dans l'API, tout le monde est capable de lire des informations et des
statistiques.  Pour mettre à jour ces informations (augmenter le score
d'une ville ou ajoute des observations d'EEE) il faut une clé API

FIXME: veut-on avoir des comptes d'utilisateur ou tout simplement
passer tous les utilisateurs sous la même clé (puis assigner les
points avec l'emplacement)?

Les scores et les activités sont regroupés par ville.  Pour le moment
la sélection de villes est limité à celles-ci:

- Rimouski
- Repentigny
- Montréal
- Laval
- Gatineau
- Sherbrooke

Les informations et fonctions disponibles sont:

- Localiser l'utilisateur dans une ville
- Localiser les activités les plus proches
- Localiser les observations de EEE les plus proches
- Obtenir les palmarés des obserations selon la ville
- (protégée) Ajouter une observation de EEE

## Activités

## Espèces Exotiques Envahissantes
