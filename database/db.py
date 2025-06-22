# database/db.py

import psycopg2
from psycopg2 import sql, extras
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration base de données
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'mlunch'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
}

def get_connection():
    """Établit une connexion PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"[Erreur de connexion] {e}")
        return None


def execute_query(query, params=None):
    """
    Exécute une requête SQL (INSERT, UPDATE, DELETE).
    Ne retourne pas de résultat.
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
        return True
    except Exception as e:
        print(f"[Erreur d'exécution] {e}")
        return False
    finally:
        conn.close()


def fetch_query(query, params=None):
    """
    Exécute une requête SQL (SELECT) et retourne les résultats sous forme de liste de dictionnaires.
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"[Erreur de récupération] {e}")
        return []
    finally:
        conn.close()


def fetch_one(query, params=None):
    """
    Exécute une requête SQL et retourne une seule ligne sous forme de dictionnaire.
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None
    except Exception as e:
        print(f"[Erreur fetch_one] {e}")
        return None
    finally:
        conn.close()


def table_exists(table_name):
    """Vérifie si une table existe dans la base de données."""
    query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        );
    """
    result = fetch_one(query, (table_name,))
    return result["exists"] if result else False
