# Self-Organization of Robots in a Hostile Environment

## 1. Présentation du Projet
Ce projet simule une mission de gestion de déchets radioactifs par une flotte d'agents autonomes. L'objectif est d'évacuer la radioactivité d'un environnement divisé en zones de danger croissant en transformant et en déplaçant des déchets vers une zone de stockage sécurisée.

## 2. Configuration de l'Environnement
L'espace est décomposé en trois zones d'ouest en est :
- **Zone $Z_1$ (Radioactivité faible) :** Point d'apparition des déchets verts.
- **Zone $Z_2$ (Radioactivité moyenne) :** Zone de transit et de transformation intermédiaire.
- **Zone $Z_3$ (Radioactivité haute) :** Contient la "Waste Disposal Zone" à l'extrémité est.

### État Initial
Pour chaque simulation, le système est initialisé avec un nombre identique de déchets de chaque type pour garantir la comparabilité des résultats :
- $N$ déchets **verts** (Valeur radioactive : 1)
- $N$ déchets **jaunes** (Valeur radioactive : 2)
- $N$ déchets **rouges** (Valeur radioactive : 4)

## 3. Protocole et Règles des Robots
Afin de lever les ambiguïtés du sujet, les agents suivent les règles de comportement suivantes :

### Robot Vert (Green Robot)
- **Zone d'évolution :** Strictement limité à la zone $Z_1$.
- **Action de collecte :** Se déplace pour ramasser jusqu'à **2 déchets verts**.
- **Action de transformation :** Une fois 2 déchets en possession, il les fusionne en **1 déchet jaune**.
- **Action de livraison :** Doit déposer le déchet jaune à la frontière est de $Z_1$ (accessible aux robots jaunes).

### Robot Jaune (Yellow Robot)
- **Zone d'évolution :** Peut circuler dans les zones $Z_1$ et $Z_2$.
- **Action de collecte :** Ramasse jusqu'à **2 déchets jaunes**.
- **Action de transformation :** Une fois 2 déchets en possession, il les fusionne en **1 déchet rouge**.
- **Action de livraison :** Doit déposer le déchet rouge à la frontière est de $Z_2$ (accessible aux robots rouges).

### Robot Rouge (Red Robot)
- **Zone d'évolution :** Accès total ($Z_1, Z_2, Z_3$).
- **Action de collecte :** Ramasse **1 seul déchet** à la fois (en priorité les rouges qui ont le niveau de radioactivité le plus élevé).
- **Action finale :** Transporte le déchet rouge vers la "Waste Disposal Zone" en $Z_3$. Une fois déposé ici, le déchet est considéré comme "traité" et sort du calcul de radioactivité active.

## 4. Objectif Global et Métriques
L'objectif est d'optimiser l'organisation collective pour minimiser l'impact radioactif durant la mission.

### Calcul de la Radioactivité Totale
À chaque unité de temps ($step$), la radioactivité totale $R$ est calculée :
$$R_{total} = (1 \times N_{verts}) + (2 \times N_{jaunes}) + (4 \times N_{rouges})$$
*Note : Les déchets possédés par les robots comptent toujours dans la radioactivité totale de l'environnement.*

### Analyse de Performance
La performance d'une stratégie (ex: avec ou sans communication) est évaluée par la **minimisation de l'aire sous la courbe (AUC)** de la radioactivité totale en fonction des steps :
- **Axe X :** Temps (Steps)
- **Axe Y :** Somme totale de radioactivité
- **Critère de succès :** Plus l'aire sous la courbe est faible, plus le système a été efficace à réduire rapidement le danger global.

## 5. Installation et Exécution
1. Clonez le dépôt.
2. Installez les dépendances : `pip install -r requirements.txt`.
3. Lancez la simulation : `python run.py`.
4. Les graphiques de radioactivité sont générés automatiquement à la fin de l'exécution dans le dossier `/results`.
