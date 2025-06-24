import psycopg2
from psycopg2 import extras
from django.conf import settings
from contextlib import contextmanager

# Configuration de la base de données
DB_CONFIG = {
    'dbname': settings.DATABASES['default']['NAME'],
    'user': settings.DATABASES['default']['USER'],
    'password': settings.DATABASES['default']['PASSWORD'],
    'host': settings.DATABASES['default']['HOST'],
    'port': settings.DATABASES['default']['PORT'],
}

@contextmanager
def get_connection():
    """Fournit une connexion PostgreSQL avec gestion contextuelle."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        yield conn
    except psycopg2.Error as e:
        raise ConnectionError(f"Échec de la connexion : {str(e)}")
    finally:
        if conn is not None:
            conn.close()

def execute_query(query, params=None):
    """Exécute une requête SQL (INSERT, UPDATE, DELETE) sans retour de données."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
            conn.commit()
        return True, None
    except psycopg2.errors.UniqueViolation as e:
        return False, e
    except psycopg2.Error as e:
        return False, e

def fetch_query(query, params=None, as_dict=True):
    """Exécute une requête SQL (SELECT) et retourne les résultats."""
    try:
        with get_connection() as conn:
            cursor_factory = extras.DictCursor if as_dict else None
            with conn.cursor(cursor_factory=cursor_factory) as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                if as_dict:
                    return [dict(row) for row in rows], None
                return rows, None
    except psycopg2.Error as e:
        return [], e

def fetch_one(query, params=None, as_dict=True):
    """Exécute une requête SQL et retourne une seule ligne."""
    try:
        with get_connection() as conn:
            cursor_factory = extras.DictCursor if as_dict else None
            with conn.cursor(cursor_factory=cursor_factory) as cur:
                cur.execute(query, params)
                row = cur.fetchone()
            conn.commit()  # Valider la transaction
            if row and as_dict:
                return dict(row), None
            return row, None
    except psycopg2.errors.UniqueViolation as e:
        return None, e
    except psycopg2.Error as e:
        return None, e

def table_exists(table_name):
    """Vérifie si une table existe dans la base de données."""
    query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        )
    """
    result, error = fetch_one(query, (table_name,), as_dict=True)
    if error:
        return False, error
    return result["exists"], None
