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

-- Reset sequences (auto-increment counters)
ALTER SEQUENCE core_client_id_seq RESTART WITH 1;
ALTER SEQUENCE core_commande_id_seq RESTART WITH 1;
ALTER SEQUENCE core_commanderepas_id_seq RESTART WITH 1;
ALTER SEQUENCE core_historiquestatutcommande_id_seq RESTART WITH 1;
ALTER SEQUENCE core_historiquestatutlivraison_id_seq RESTART WITH 1;
ALTER SEQUENCE core_historiquestatutlivreur_id_seq RESTART WITH 1;
ALTER SEQUENCE core_historiquestatutrestaurant_id_seq RESTART WITH 1;
ALTER SEQUENCE core_historiquestatutzone_id_seq RESTART WITH 1;
ALTER SEQUENCE core_livraison_id_seq RESTART WITH 1;
ALTER SEQUENCE core_livreur_id_seq RESTART WITH 1;
ALTER SEQUENCE core_pointrecup_id_seq RESTART WITH 1;
ALTER SEQUENCE core_promotion_id_seq RESTART WITH 1;
ALTER SEQUENCE core_repas_id_seq RESTART WITH 1;
ALTER SEQUENCE core_restaurant_id_seq RESTART WITH 1;
ALTER SEQUENCE core_restaurantrepas_id_seq RESTART WITH 1;
ALTER SEQUENCE core_statutcommande_id_seq RESTART WITH 1;
ALTER SEQUENCE core_statutlivraison_id_seq RESTART WITH 1;
ALTER SEQUENCE core_statutlivreur_id_seq RESTART WITH 1;
ALTER SEQUENCE core_statutrestaurant_id_seq RESTART WITH 1;
ALTER SEQUENCE core_statutzone_id_seq RESTART WITH 1;
ALTER SEQUENCE core_typerepas_id_seq RESTART WITH 1;
ALTER SEQUENCE core_zone_id_seq RESTART WITH 1;
ALTER SEQUENCE core_zoneclient_id_seq RESTART WITH 1;
ALTER SEQUENCE core_zonerestaurant_id_seq RESTART WITH 1;

-- Re-enable triggers
SET session_replication_role = 'origin';