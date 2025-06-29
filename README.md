# M-LUNCH

Une application web de gestion de livraison de repas

## Installation et démarrage rapide

1. **Créer un environnement virtuel Python**

Sous Windows :
```bash
python -m venv .venv
.venv\Scripts\activate
```
Sous Linux/Mac :
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

3. **Appliquer les migrations (base de données)**

```bash
python manage.py makemigrations mlunch.core
python manage.py migrate
```

4. **Lancer le serveur de développement**

```bash
python manage.py runserver
```

## Notes supplémentaires
- Assurez-vous d'avoir Python 3.8 ou supérieur installé.
- Les migrations concernent principalement l'app `mlunch.core`.
- Pour initialiser la base avec des données, vous pouvez utiliser les scripts SQL dans le dossier `database/` si besoin.
- Pour toute erreur liée à l'environnement, vérifiez que l'environnement virtuel est bien activé.
