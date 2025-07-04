-- Script de reset pour M-Lunch - Antananarivo, Madagascar
-- PostgreSQL + PostGIS

-- Nettoyage des données existantes (en ordre inverse des dépendances)
DELETE FROM core_commanderepas;
DELETE FROM core_historiquestatutlivraison;
DELETE FROM core_livraison;
DELETE FROM core_historiquestatutcommande;
DELETE FROM core_commande;
DELETE FROM core_zoneclient;
DELETE FROM core_zonelivreur;
DELETE FROM core_zonerestaurant;
DELETE FROM core_restaurantrepas;
DELETE FROM core_promotion;
DELETE FROM core_horairespecial;
DELETE FROM core_horaire;
DELETE FROM core_commission;
DELETE FROM core_historiquestatutrestaurant;
DELETE FROM core_historiquestatutlivreur;
DELETE FROM core_historiquestatutzone;
DELETE FROM core_repas;
DELETE FROM core_typerepas;
DELETE FROM core_restaurant;
DELETE FROM core_livreur;
DELETE FROM core_client;
DELETE FROM core_pointrecup;
DELETE FROM core_zone;
DELETE FROM core_limitecommandesjournalieres;
DELETE FROM core_modepaiement;
DELETE FROM core_statutcommande;
DELETE FROM core_statutlivraison;
DELETE FROM core_statutlivreur;
DELETE FROM core_statutrestaurant;
DELETE FROM core_statutzone;

-- Réinitialisation des séquences
ALTER SEQUENCE core_client_id_seq RESTART WITH 1;
ALTER SEQUENCE core_zone_id_seq RESTART WITH 1;
ALTER SEQUENCE core_pointrecup_id_seq RESTART WITH 1;
ALTER SEQUENCE core_restaurant_id_seq RESTART WITH 1;
ALTER SEQUENCE core_typerepas_id_seq RESTART WITH 1;
ALTER SEQUENCE core_repas_id_seq RESTART WITH 1;
ALTER SEQUENCE core_livreur_id_seq RESTART WITH 1;
ALTER SEQUENCE core_modepaiement_id_seq RESTART WITH 1;
ALTER SEQUENCE core_commande_id_seq RESTART WITH 1;
ALTER SEQUENCE core_livraison_id_seq RESTART WITH 1;
ALTER SEQUENCE core_statutcommande_id_seq RESTART WITH 1;
ALTER SEQUENCE core_statutlivraison_id_seq RESTART WITH 1;
ALTER SEQUENCE core_statutlivreur_id_seq RESTART WITH 1;
ALTER SEQUENCE core_statutrestaurant_id_seq RESTART WITH 1;
ALTER SEQUENCE core_statutzone_id_seq RESTART WITH 1;
ALTER SEQUENCE core_commission_id_seq RESTART WITH 1;
ALTER SEQUENCE core_horaire_id_seq RESTART WITH 1;
ALTER SEQUENCE core_horairespecial_id_seq RESTART WITH 1;
ALTER SEQUENCE core_promotion_id_seq RESTART WITH 1;
ALTER SEQUENCE core_limitecommandesjournalieres_id_seq RESTART WITH 1;
ALTER SEQUENCE core_historiquestatutcommande_id_seq RESTART WITH 1;
ALTER SEQUENCE core_historiquestatutlivraison_id_seq RESTART WITH 1;
ALTER SEQUENCE core_historiquestatutlivreur_id_seq RESTART WITH 1;
ALTER SEQUENCE core_historiquestatutrestaurant_id_seq RESTART WITH 1;
ALTER SEQUENCE core_historiquestatutzone_id_seq RESTART WITH 1;

COMMIT;
