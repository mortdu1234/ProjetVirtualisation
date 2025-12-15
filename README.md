# ProjetVirtualisation
l'idée de ce projet est de créer un jeu de puissance 4 entre plusieurs container docker.

Pour cela il nous faut :
- une image : pour la gestion des joueurs
- une image : pour la gestion du server

Modélisations du fonctionnement :
- un container server qui gere l'ensemble des parties.
- un container par joueur qui vas gerer un unique joueur

L'idée de la représentation est de :
- faire un matche entre deux joueur d'une meme machine
- faire affronter les deux gagnant et les deux perdant ensemble avec une autre machine

Moyen de communication entre les joueur et le server :
- envois de socket entre les joueurs et le server 

Language de Programmation :
- python

# Initialisation
Lancement du server : écoute en continue sur un port XXXX
Lancerment d'un 
Création d'un server, qui ecoute en continue un port
a chaque fois qu'il recoit un une info sur ce port, rajoute un joueur
joueur : envois message au server sur le port XXXX : "coucou je suis une joueur"
                        le server transmet la connection sur un port privé

Un joueur qui ne joue pas, peut :
    - demander un match : envois un message au server qui renvois la listes des joueurs libre
    - quitter : envois un message au server qui le vire de la liste des joueurs libres

Quand un joueur demande un matche il peut :
    - selectionner un joueur : propose un match contre ce joueur
    - quitter : reviens en mode normal

Quand un joueur recoit une demande de matche il peut :
    - accepter la demande
    - refuser la demande

Quand un joueurs est en matche, il peut :
    - envoyer au server la colone dans laquelle il vas jouer
    - recevoir la grille

# Architecture

ProjetVirtualisation/
│
├── docker-compose.yml
├── README.md
│
├── server/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── server.py
│   ├── game_manager.py
│   ├── game.py
│   └── utils/
│       ├── __init__.py
│       └── protocol.py
│
├── player/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── player.py
│   ├── ai_player.py
│   └── utils/
│       ├── __init__.py
│       └── protocol.py
│
└── shared/
    └── protocol.py

