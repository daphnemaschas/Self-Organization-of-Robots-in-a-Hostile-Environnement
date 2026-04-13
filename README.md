# Self-Organization of Robots in a Hostile Environment

> **Groupe 5** — Maxence Rossignol, Antoine Yezou, Daphné Maschas

## 1. Présentation du Projet

Ce projet simule une mission de gestion de déchets radioactifs par une flotte d'agents autonomes. L'objectif est d'évacuer la radioactivité d'un environnement divisé en zones de danger croissant en transformant et en déplaçant des déchets vers une zone de stockage sécurisée.

Le système repose sur [Mesa 3.x](https://mesa.readthedocs.io/) (framework de simulation multi-agents) avec une visualisation interactive via [Solara](https://solara.dev/).

## 2. Configuration de l'Environnement

L'espace est une grille 15×10 décomposée en trois zones d'ouest en est :
- **Zone $Z_1$ (Radioactivité faible) :** Point d'apparition des déchets verts.
- **Zone $Z_2$ (Radioactivité moyenne) :** Zone de transit et de transformation intermédiaire.
- **Zone $Z_3$ (Radioactivité haute) :** Contient la "Waste Disposal Zone" à l'extrémité est.

### État Initial

Pour chaque simulation, le nombre de déchets de chaque type est configurable via l'interface (15 par défaut) :
- $N$ déchets **verts** (Valeur radioactive : 1)
- $N$ déchets **jaunes** (Valeur radioactive : 2)
- $N$ déchets **rouges** (Valeur radioactive : 4)

## 3. Protocole et Règles des Robots

Afin de lever les ambiguïtés du sujet, les agents suivent les règles de comportement suivantes :

### Robot Vert (Green Robot)
- **Zone d'évolution :** Strictement limité à la zone $Z_1$.
- **Action de collecte :** Se déplace pour ramasser jusqu'à **2 déchets verts**.
- **Action de transformation :** Une fois 2 déchets en possession, il les fusionne en **1 déchet jaune**.
- **Action de livraison :** Dépose le déchet jaune à la frontière est de $Z_1$ (accessible aux robots jaunes).

### Robot Jaune (Yellow Robot)
- **Zone d'évolution :** Peut circuler dans les zones $Z_1$ et $Z_2$.
- **Action de collecte :** Ramasse jusqu'à **2 déchets jaunes**.
- **Action de transformation :** Une fois 2 déchets en possession, il les fusionne en **1 déchet rouge**.
- **Action de livraison :** Dépose le déchet rouge à la frontière est de $Z_2$ (accessible aux robots rouges).

### Robot Rouge (Red Robot)
- **Zone d'évolution :** Accès total ($Z_1, Z_2, Z_3$).
- **Action de collecte :** Ramasse **1 seul déchet** à la fois (en priorité les rouges).
- **Action finale :** Transporte le déchet rouge vers la "Waste Disposal Zone" en $Z_3$. Une fois déposé, le déchet est considéré comme "traité" et sort du calcul de radioactivité active.

### Communication

Les robots communiquent via un tableau de messages partagé (`message_board`). Lorsqu'un robot vert ou jaune dépose un déchet transformé à la frontière de sa zone, il publie un message `waste_ready` indiquant le type et la position du déchet disponible, afin de signaler aux robots de la zone adjacente qu'un déchet est prêt à être collecté.

## 4. Objectif Global et Métriques

L'objectif est d'optimiser l'organisation collective pour minimiser l'impact radioactif durant la mission.

### Calcul de la Radioactivité Totale

À chaque unité de temps ($step$), la radioactivité totale $R$ est calculée :
$$R_{total} = (1 \times N_{verts}) + (2 \times N_{jaunes}) + (4 \times N_{rouges})$$
*Note : Les déchets dans l'inventaire des robots comptent toujours dans la radioactivité totale.*

### Analyse de Performance

La performance d'une stratégie est évaluée par la **minimisation de l'aire sous la courbe (AUC)** de la radioactivité totale en fonction des steps :
- **Axe X :** Temps (Steps)
- **Axe Y :** Somme totale de radioactivité
- **Critère de succès :** Plus l'aire sous la courbe est faible, plus le système a été efficace à réduire rapidement le danger global.

## 5. Structure du Projet

```
.
├── run.py                          # Point d'entrée — lance le serveur Solara
├── check_start.py                  # Vérifie que le serveur Solara démarre correctement
├── test_logic.py                   # Test de la logique de collecte/transformation
├── pyproject.toml                  # Dépendances (gérées par uv)
├── 5_robot_mission_MAS2026/
│   ├── model.py                    # Modèle RobotMission (grille, règles, collecte de données)
│   ├── agents.py                   # Agents (GreenAgent, YellowAgent, RedAgent)
│   ├── objects.py                  # Objets de l'environnement (Waste, RadioactivitySource, WasteDisposalZone)
│   └── server.py                   # Visualisation Solara (rendu grille + graphiques)
└── data/                           # Logs CSV générés pendant la simulation
```

## 6. Installation et Exécution

### Prérequis
- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets)

### Lancement
```bash
git clone <url-du-dépôt>
cd Self-Organization-of-Robots-in-a-Hostile-Environnement
uv sync
python run.py
```

Le serveur Solara démarre et ouvre une interface web interactive permettant de :
- Configurer le nombre de robots (vert, jaune, rouge) et de déchets initiaux via des sliders.
- Visualiser la grille en temps réel avec les zones colorées, les robots et les déchets.
- Suivre l'évolution des stocks de déchets et de la radioactivité totale via des graphiques.

Les logs de simulation sont sauvegardés automatiquement dans le dossier `data/` tous les 50 steps.
