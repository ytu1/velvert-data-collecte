"""
Script de collecte : importe les donnees des stations Vel'Vert depuis un
export CSV vers la base de donnees de test.

Contexte : l'export hebdomadaire du systeme de stations est recu sous forme
de fichier CSV (export_stations.csv). Ce script lit ce fichier et insere
(ou met a jour, s'il existe deja) chaque station dans la table `stations`
de la base de donnees.

Voir dictionnaire_donnees.md pour le detail des colonnes attendues.
"""

import pandas as pd
import psycopg2

# --- Connexion a la base de donnees de test ---
# Ces informations te sont communiquees par ton formateur au demarrage du brief.
# Remplace les 5 valeurs ci-dessous avant de lancer le script.
DB_HOST = "A_COMPLETER"
DB_PORT = 5432
DB_NAME = "A_COMPLETER"
DB_USER = "A_COMPLETER"
DB_PASSWORD = "A_COMPLETER"


def charger_export(chemin_csv):
    """Charge l'export CSV des stations dans un DataFrame pandas."""
    return pd.read_csv(chemin_csv)


def inserer_stations(df, conn):
    """Insere ou met a jour chaque station dans la table `stations`."""
    cur = conn.cursor()
    for _, ligne in df.iterrows():
        cur.execute(
            """
            INSERT INTO stations (station_id, nom_station, velos_disponibles, capacite_totale)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (station_id) DO UPDATE SET
                nom_station = EXCLUDED.nom_station,
                velos_disponibles = EXCLUDED.velos_disponibles,
                capacite_totale = EXCLUDED.capacite_totale;
            """,
            (
                int(ligne["station_id"]),
                ligne["nom"],
                int(ligne["velos_disponibles"]),
                int(ligne["capacite_totale"]),
            ),
        )
    conn.commit()
    cur.close()


if __name__ == "__main__":
    print("Lecture de l'export...")
    df = charger_export("export_stations.csv")
    print(f"{len(df)} stations trouvees dans l'export.")

    print("Connexion a la base de donnees...")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

    print("Import des stations...")
    inserer_stations(df, conn)

    conn.close()
    print("Import termine.")
