
# M-LUNCH

Une application web de gestion de livraison de repas 

## Technologies

- **Langage :** Python  
- **Framework :** Django  
- **Base de données :** PostgreSQL avec PostGIS  
- **Librairies supplémentaires :** GDAL (gestion géospatiale)
À noter qu’il est nécessaire d’installer **GDAL** .  
Vous pouvez le faire en téléchargeant l’installateur **OSGeo4W** depuis le lien suivant :  
https://trac.osgeo.org/osgeo4w/wiki/OSGeo4W_fr

Sur cette page, cliquez sur **Installateur OSGeo4W** pour lancer le téléchargement.
Etape d'installation de GDAL : 
osgeo4w-setup.exe > Advanced install > Install from internet > Just me > local package directory (a laisser par defaut) > Direct connection > https://download.osgeo.org > rechercher GDAL  et sur All changer default en install > suivant

---

## Prérequis

- asgiref==3.8.1
- Django==5.2.3
- dotenv==0.9.9
- psycopg2-binary==2.9.10
- python-dotenv==1.1.0
- sqlparse==0.5.3
- tzdata==2025.2


Pour installer les prérequis, run :

```bash
pip install -r requirements.txt

