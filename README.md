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
statistiques.  Pour ajouter des observations d'EEE, il faut
s'authentifier avec un compte d'utilisateur.

FIXME: authentification à déterminer (de préférence passwordless)

Les scores et les activités sont regroupés par ville.  Pour le moment
la sélection de villes est limité à celles-ci:

- Rimouski
- Repentigny
- Sainte-Adèle
- Montréal
- Laval
- Gatineau
- Sherbrooke

Les informations et fonctions disponibles sont:

- Localiser l'utilisateur dans une ville
- Localiser les activités les plus proches selon des critéres (type
  d'activité, météo, etc)
- Localiser les observations de EEE les plus proches
- Obtenir les palmarés des observations selon la ville
- Obtenir les contributions de l'utilisateur
- (protégée) Planifier une activité
- (protégée) Confirmer une activité
- (protégée) Ajouter une observation de EEE avec ou sans photo

## Activités

Les villes sont cotées selon les activités confirmées sur leur
territoire, et ce, peu importe le lieu de résidence de l'utilisateur.
Nous voulons non seulement encourager une mode de vie active chez les
citoyens mais aussi l'aménagement d'infrastructures chez les villes.
Nous voulons aussi encourager les gens de s'activer près de chez eux,
pour augmenter le score de leur propre ville.

Pour avoir un crédit il faut non seulement planifier une activité mais
aussi l'avoir fait dans le délai prévu.  L'application mobile se
servira de l'emplacement de l'utilisateur pour confirmer sa présence
à l'endroit planifié.

FIXME: veut-on aussi permettre le téléversement de fichiers GPX ou des
connections avec des applications dont Strava, RideWithGPS, etc?

## Espèces Exotiques Envahissantes

Puisqu'il n'est pas vraiment souhaitable d'avoir des EEE sur son
territoire, on n'augmente pas le score de sa ville en les signalant.

Puisque les activités prises en charge sont terrestres de nature,
seulement les EEE terrestres sont concernés, c'est à dire les catégories suivantes dans [la liste Sentinelle](https://www.donneesquebec.ca/recherche/dataset/especes-exotiques-envahissantes/resource/ac4aeddf-13ed-4d80-9ca3-28ca9ed77b14):

- Plantes de milieux terrestres
- Plantes émergentes
- Insectes
- Oiseaux et mammifères
