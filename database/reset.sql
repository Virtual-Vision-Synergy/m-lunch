-- 1. Désactiver les triggers (désactive les contraintes FK)
SET session_replication_role = 'replica';

-- 2. Vider toutes les tables dépendantes en respectant l'ordre (enfants → parents)
TRUNCATE TABLE
    core_historiquestatutzone,
    core_historiquestatutrestaurant,
    core_historiquestatutlivreur,
    core_historiquestatutlivraison,
    core_historiquestatutcommande,
    core_promotion,
    core_commanderepas,
    core_livraison,
    core_commande,
    core_zoneclient,
    core_zonerestaurant,
    core_restaurantrepas,
    core_repas,
    core_typerepas,
    core_livreur,
    core_client,
    core_pointrecup,
    core_restaurant,
    core_zone,
    core_statutcommande,
    core_statutlivraison,
    core_statutlivreur,
    core_statutrestaurant,
    core_statutzone
RESTART IDENTITY CASCADE;

-- 3. Réinitialiser manuellement les séquences (utile si RESTART IDENTITY ne suffit pas)

-- Exemple : reset de la séquence de core_client
SELECT setval(pg_get_serial_sequence('core_client', 'id'), COALESCE(MAX(id), 1), false) FROM core_client;

-- (répété pour chaque table ayant une colonne ID auto-incrémentée)
SELECT setval(pg_get_serial_sequence('core_livreur', 'id'), COALESCE(MAX(id), 1), false) FROM core_livreur;
SELECT setval(pg_get_serial_sequence('core_commande', 'id'), COALESCE(MAX(id), 1), false) FROM core_commande;
SELECT setval(pg_get_serial_sequence('core_livraison', 'id'), COALESCE(MAX(id), 1), false) FROM core_livraison;
SELECT setval(pg_get_serial_sequence('core_repas', 'id'), COALESCE(MAX(id), 1), false) FROM core_repas;
SELECT setval(pg_get_serial_sequence('core_restaurant', 'id'), COALESCE(MAX(id), 1), false) FROM core_restaurant;
SELECT setval(pg_get_serial_sequence('core_zone', 'id'), COALESCE(MAX(id), 1), false) FROM core_zone;
SELECT setval(pg_get_serial_sequence('core_pointrecup', 'id'), COALESCE(MAX(id), 1), false) FROM core_pointrecup;
SELECT setval(pg_get_serial_sequence('core_statutcommande', 'id'), COALESCE(MAX(id), 1), false) FROM core_statutcommande;
SELECT setval(pg_get_serial_sequence('core_statutlivraison', 'id'), COALESCE(MAX(id), 1), false) FROM core_statutlivraison;
SELECT setval(pg_get_serial_sequence('core_statutlivreur', 'id'), COALESCE(MAX(id), 1), false) FROM core_statutlivreur;
SELECT setval(pg_get_serial_sequence('core_statutrestaurant', 'id'), COALESCE(MAX(id), 1), false) FROM core_statutrestaurant;
SELECT setval(pg_get_serial_sequence('core_statutzone', 'id'), COALESCE(MAX(id), 1), false) FROM core_statutzone;
SELECT setval(pg_get_serial_sequence('core_historiquestatutzone', 'id'), COALESCE(MAX(id), 1), false) FROM core_historiquestatutzone;
SELECT setval(pg_get_serial_sequence('core_historiquestatutrestaurant', 'id'), COALESCE(MAX(id), 1), false) FROM core_historiquestatutrestaurant;
SELECT setval(pg_get_serial_sequence('core_historiquestatutlivreur', 'id'), COALESCE(MAX(id), 1), false) FROM core_historiquestatutlivreur;
SELECT setval(pg_get_serial_sequence('core_historiquestatutlivraison', 'id'), COALESCE(MAX(id), 1), false) FROM core_historiquestatutlivraison;
SELECT setval(pg_get_serial_sequence('core_historiquestatutcommande', 'id'), COALESCE(MAX(id), 1), false) FROM core_historiquestatutcommande;
SELECT setval(pg_get_serial_sequence('core_promotion', 'id'), COALESCE(MAX(id), 1), false) FROM core_promotion;
SELECT setval(pg_get_serial_sequence('core_commanderepas', 'id'), COALESCE(MAX(id), 1), false) FROM core_commanderepas;
SELECT setval(pg_get_serial_sequence('core_zoneclient', 'id'), COALESCE(MAX(id), 1), false) FROM core_zoneclient;
SELECT setval(pg_get_serial_sequence('core_zonerestaurant', 'id'), COALESCE(MAX(id), 1), false) FROM core_zonerestaurant;
SELECT setval(pg_get_serial_sequence('core_restaurantrepas', 'id'), COALESCE(MAX(id), 1), false) FROM core_restaurantrepas;
SELECT setval(pg_get_serial_sequence('core_typerepas', 'id'), COALESCE(MAX(id), 1), false) FROM core_typerepas;

-- 4. Réactiver les contraintes (FK, triggers, etc.)
SET session_replication_role = 'origin';
