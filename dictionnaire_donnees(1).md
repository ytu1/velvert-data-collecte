# Dictionnaire de données — Vel'Vert

Vel'Vert exploite une flotte de vélos électriques en libre-service. Ce document décrit les données du projet, et la façon dont le modèle évoluera au fil du parcours.

**Version** : Phase 0 (S39) · **Dernière mise à jour** : avant le démarrage de la promo

---

## 1. État actuel du modèle

### Table `stations`

Liste des stations de la flotte et leur état de remplissage.

| Colonne | Type | Description | Contrainte |
|---|---|---|---|
| `station_id` | INTEGER | Identifiant unique de la station | Clé primaire |
| `nom_station` | TEXT | Nom de la station (ex : `Republique`) | |
| `velos_disponibles` | INTEGER | Nombre de vélos actuellement disponibles | |
| `capacite_totale` | INTEGER | Nombre total d'emplacements de la station | |

**Alimentée par** : `script_collecte_velos.py`, à partir de l'export CSV hebdomadaire.

### Table `trajets`

Locations enregistrées par l'application.

| Colonne | Type | Description | Contrainte |
|---|---|---|---|
| `trajet_id` | INTEGER | Identifiant unique du trajet | Clé primaire |
| `station_depart_id` | INTEGER | Station d'où part le trajet | Référence `stations.station_id` |
| `duree_minutes` | INTEGER | Durée de la location en minutes | |
| `date_trajet` | DATE | Date du trajet | |

> Introduite en S39 (mercredi), pour les exercices de requêtage.

---

## 2. Format de l'export CSV

Le fichier `export_stations.csv`, reçu chaque semaine du système de stations, utilise **exactement les mêmes noms de colonnes que la table** `stations` :

```
station_id,nom_station,velos_disponibles,capacite_totale
```

> **Point de vigilance** : c'est le seul contrat entre le fichier source et la base. Si l'un des deux change sans l'autre, la collecte casse. C'est précisément ce que travaille le brief « Environnement & Collecte ».

---

## 3. Indicateurs dérivés

Ces valeurs ne sont pas stockées : elles se calculent au moment de l'analyse.

| Indicateur | Calcul | Usage métier |
|---|---|---|
| `taux_remplissage` | `velos_disponibles / capacite_totale` | Repérer les stations en tension (seuil usuel : 20 %) |

> **Pourquoi un seuil relatif et non absolu** : 6 vélos dans une station de 10 emplacements (60 %) n'a rien à voir avec 6 vélos dans une station de 40 (15 %). Un seuil en valeur absolue traiterait les deux cas de la même façon. Cette nuance est volontairement mise en jeu dans les exercices.

---

## 4. Feuille de route du modèle

Le modèle ci-dessus est **délibérément incomplet**. Chaque manque est un exercice à venir : les apprenants feront évoluer la base plutôt que de la recevoir déjà finie. C'est le mécanisme central du parcours — *faire évoluer une source existante* — et non une simplification.

### Phase 1 — La source évolue

| Évolution prévue | Ce que ça fait travailler |
|---|---|
| Durées de trajet négatives ou disproportionnées | Détection et traitement des valeurs aberrantes |
| Coordonnées de géolocalisation manquantes | Traitement des valeurs manquantes |
| Renommage de colonnes côté source | Mise à jour du script de collecte |
| Ajout d'une colonne à `stations` | `ALTER TABLE`, rechargement des données |

### Phase 2 — Sources multiples et données semi-structurées

| Évolution prévue | Ce que ça fait travailler |
|---|---|
| Flux JSON depuis une API | Collecte de données non structurées |
| Table `zones_urbaines`, reliée à `stations` | Modélisation Merise, clés étrangères |
| Table `stations_recharge` | Relations entre tables, jointures |
| Vues SQL de synthèse | CTE, agrégations, optimisation |

### Phase 3 — Consolidation

| Évolution prévue | Ce que ça fait travailler |
|---|---|
| Pipeline de collecte automatisé | Orchestration, ETL/ELT |
| Modélisation en étoile | Entrepôt de données, modélisation décisionnelle |

### Ce qui est volontairement absent aujourd'hui

- **Pas de clé étrangère déclarée** entre `trajets.station_depart_id` et `stations.station_id`. La relation existe dans les faits, mais elle sera formalisée en Phase 2, au moment de la modélisation.
- **Pas de table `zones_urbaines`**, alors que le besoin métier existe déjà (analyse de rentabilité par zone). Elle arrive en Phase 2.
- **Pas de données de facturation** dans `trajets`. Elles arrivent avec l'analyse de chiffre d'affaires.
- **Pas de valeurs manquantes ni aberrantes** dans le jeu Phase 0 : les données sont propres, pour que les premiers exercices portent sur la syntaxe et non sur le nettoyage. Le désordre arrive en Phase 1, quand ils sauront quoi en faire.

---

## 5. Jeu de données Phase 0

Volontairement réduit et lisible : à ce stade, un apprenant doit pouvoir vérifier de tête si le résultat d'une requête est correct.

**`stations` — 5 lignes**

| id | nom | dispo | capacité | taux |
|---|---|---|---|---|
| 1 | Republique | 2 | 20 | 10 % |
| 2 | Bastille | 15 | 18 | 83 % |
| 3 | Nation | 1 | 15 | 7 % |
| 4 | Chatelet | 8 | 25 | 32 % |
| 5 | Bercy | 6 | 10 | 60 % |

> Bercy est le cas piège : 6 vélos, c'est peu en valeur absolue, mais la station est bien remplie. Un filtre sur seuil absolu la fait apparaître à tort.

**`trajets` — 12 lignes**, durées de 6 à 55 minutes, réparties sur 4 jours (21 au 24 septembre 2026). Les extrêmes sont volontaires : ils rendent les requêtes de détection d'anomalies non triviales.

> Ce volume ne permet pas d'analyse statistique sérieuse — c'est assumé. Un export plus large sera fourni en Phase 1, au moment où moyenne, médiane et écart-type auront un sens.
