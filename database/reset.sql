-- Disable triggers temporarily to avoid foreign key constraint issues
SET session_replication_role = 'replica';

-- Delete data from all tables in the correct order (child tables first)
TRUNCATE TABLE core_historiquestatutzone CASCADE;
TRUNCATE TABLE core_historiquestatutrestaurant CASCADE;
TRUNCATE TABLE core_historiquestatutlivreur CASCADE;
TRUNCATE TABLE core_historiquestatutlivraison CASCADE;
TRUNCATE TABLE core_historiquestatutcommande CASCADE;
TRUNCATE TABLE core_promotion CASCADE;
TRUNCATE TABLE core_commanderepas CASCADE;
TRUNCATE TABLE core_livraison CASCADE;
TRUNCATE TABLE core_commande CASCADE;
TRUNCATE TABLE core_zoneclient CASCADE;
TRUNCATE TABLE core_zonerestaurant CASCADE;
TRUNCATE TABLE core_restaurantrepas CASCADE;
TRUNCATE TABLE core_repas CASCADE;
TRUNCATE TABLE core_typerepas CASCADE;
TRUNCATE TABLE core_livreur CASCADE;
TRUNCATE TABLE core_client CASCADE;
TRUNCATE TABLE core_pointrecup CASCADE;
TRUNCATE TABLE core_restaurant CASCADE;
TRUNCATE TABLE core_zone CASCADE;
TRUNCATE TABLE core_statutcommande CASCADE;
TRUNCATE TABLE core_statutlivraison CASCADE;
TRUNCATE TABLE core_statutlivreur CASCADE;
TRUNCATE TABLE core_statutrestaurant CASCADE;
TRUNCATE TABLE core_statutzone CASCADE;

-- Reset sequences (auto-increment counters) manually for each table
SELECT setval(pg_get_serial_sequence('core_client', 'id'), COALESCE(MAX(id), 1), false) FROM core_client;
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

-- Re-enable triggers
SET session_replication_role = 'origin';
