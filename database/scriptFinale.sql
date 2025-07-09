-- Script de création de la base de données M-Lunch (généré depuis models.py)
-- Compatible PostgreSQL

-- 1. Tables de statuts
CREATE TABLE core_statutcommande (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

CREATE TABLE core_statutlivraison (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

CREATE TABLE core_statutlivreur (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

CREATE TABLE core_statutrestaurant (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

CREATE TABLE core_statutzone (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

CREATE TABLE core_statutentite (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

-- 2. Modes de paiement
CREATE TABLE core_modepaiement (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL
);

-- 3. Entités
CREATE TABLE core_entite (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

-- 4. Zones
CREATE TABLE core_zone (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(100),
    zone VARCHAR(500)
);

-- 5. Points de récupération
CREATE TABLE core_pointrecup (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    geo_position VARCHAR(100) DEFAULT '0,0'
);

-- 6. Types de repas
CREATE TABLE core_typerepas (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

-- 7. Restaurants
CREATE TABLE core_restaurant (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(128) NOT NULL,
    adresse TEXT,
    description TEXT,
    image TEXT,
    geo_position VARCHAR(100) DEFAULT '0,0',
    date_inscri TIMESTAMP
);

-- 8. Repas
CREATE TABLE core_repas (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    image TEXT,
    type_id INTEGER NOT NULL REFERENCES core_typerepas(id),
    prix INTEGER NOT NULL
);

-- 9. Clients
CREATE TABLE core_client (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(128) NOT NULL,
    contact VARCHAR(50),
    prenom VARCHAR(100),
    nom VARCHAR(100),
    date_inscri TIMESTAMP
);

-- 10. Livreurs
CREATE TABLE core_livreur (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    contact TEXT,
    position VARCHAR(100),
    geo_position VARCHAR(100) DEFAULT '0,0',
    date_inscri TIMESTAMP
);

-- 11. Commandes
CREATE TABLE core_commande (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES core_client(id),
    point_recup_id INTEGER NOT NULL REFERENCES core_pointrecup(id),
    cree_le TIMESTAMP,
    mode_paiement_id INTEGER REFERENCES core_modepaiement(id)
);

-- 12. Historique des statuts de commande
CREATE TABLE core_historiquestatutcommande (
    id SERIAL PRIMARY KEY,
    commande_id INTEGER NOT NULL REFERENCES core_commande(id),
    statut_id INTEGER NOT NULL REFERENCES core_statutcommande(id),
    mis_a_jour_le TIMESTAMP
);

-- 13. Historique des statuts de restaurant
CREATE TABLE core_historiquestatutrestaurant (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES core_restaurant(id),
    statut_id INTEGER NOT NULL REFERENCES core_statutrestaurant(id),
    mis_a_jour_le TIMESTAMP
);

-- 14. Historique des statuts de livreur
CREATE TABLE core_historiquestatutlivreur (
    id SERIAL PRIMARY KEY,
    livreur_id INTEGER NOT NULL REFERENCES core_livreur(id),
    statut_id INTEGER NOT NULL REFERENCES core_statutlivreur(id),
    mis_a_jour_le TIMESTAMP
);

-- 15. Historique des statuts de zone
CREATE TABLE core_historiquestatutzone (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES core_zone(id),
    statut_id INTEGER NOT NULL REFERENCES core_statutzone(id),
    mis_a_jour_le TIMESTAMP
);

-- 16. Historique des statuts de livraison
CREATE TABLE core_historiquestatutlivraison (
    id SERIAL PRIMARY KEY,
    livraison_id INTEGER NOT NULL REFERENCES core_livraison(id),
    statut_id INTEGER NOT NULL REFERENCES core_statutlivraison(id),
    mis_a_jour_le TIMESTAMP
);

-- 17. Historique des statuts d'entité
CREATE TABLE core_historiquestatutentite (
    id SERIAL PRIMARY KEY,
    entite_id INTEGER NOT NULL REFERENCES core_entite(id),
    statut_id INTEGER NOT NULL REFERENCES core_statutentite(id),
    mis_a_jour_le TIMESTAMP
);

-- 18. Livraison
CREATE TABLE core_livraison (
    id SERIAL PRIMARY KEY,
    livreur_id INTEGER NOT NULL REFERENCES core_livreur(id),
    commande_id INTEGER NOT NULL REFERENCES core_commande(id),
    attribue_le TIMESTAMP
);

-- 19. CommandeRepas (détails des commandes)
CREATE TABLE core_commanderepas (
    id SERIAL PRIMARY KEY,
    commande_id INTEGER NOT NULL REFERENCES core_commande(id),
    repas_id INTEGER NOT NULL REFERENCES core_repas(id),
    quantite INTEGER NOT NULL,
    ajoute_le TIMESTAMP,
    UNIQUE (commande_id, repas_id)
);

-- 20. RestaurantRepas (association)
CREATE TABLE core_restaurantrepas (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES core_restaurant(id),
    repas_id INTEGER NOT NULL REFERENCES core_repas(id),
    UNIQUE (restaurant_id, repas_id)
);

-- 21. ZoneRestaurant (association)
CREATE TABLE core_zonerestaurant (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES core_restaurant(id),
    zone_id INTEGER NOT NULL REFERENCES core_zone(id),
    UNIQUE (restaurant_id, zone_id)
);

-- 22. ZoneClient (association)
CREATE TABLE core_zoneclient (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES core_client(id),
    zone_id INTEGER NOT NULL REFERENCES core_zone(id),
    UNIQUE (client_id, zone_id)
);

-- 23. ZoneLivreur (association)
CREATE TABLE core_zonelivreur (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES core_zone(id),
    livreur_id INTEGER NOT NULL REFERENCES core_livreur(id),
    UNIQUE (zone_id, livreur_id)
);

-- 24. Commission
CREATE TABLE core_commission (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES core_restaurant(id),
    valeur INTEGER NOT NULL,
    mis_a_jour_le TIMESTAMP
);

-- 25. Horaire
CREATE TABLE core_horaire (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES core_restaurant(id),
    le_jour INTEGER NOT NULL,
    horaire_debut TIME NOT NULL,
    horaire_fin TIME NOT NULL,
    mis_a_jour_le TIMESTAMP
);

-- 26. Horaire spécial
CREATE TABLE core_horairespecial (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES core_restaurant(id),
    date_concerne DATE NOT NULL,
    horaire_debut TIME NOT NULL,
    horaire_fin TIME NOT NULL,
    mis_a_jour_le TIMESTAMP
);

-- 27. Promotion
CREATE TABLE core_promotion (
    id SERIAL PRIMARY KEY,
    repas_id INTEGER NOT NULL REFERENCES core_repas(id),
    pourcentage_reduction INTEGER NOT NULL,
    date_concerne DATE NOT NULL
);

-- 28. Limite commandes journalières
CREATE TABLE core_limitecommandesjournalieres (
    id SERIAL PRIMARY KEY,
    nombre_commandes INTEGER NOT NULL,
    date DATE NOT NULL
);

-- 29. Disponibilité repas
CREATE TABLE core_disponibiliterepas (
    id SERIAL PRIMARY KEY,
    repas_id INTEGER NOT NULL REFERENCES core_repas(id),
    est_dispo BOOLEAN DEFAULT TRUE,
    mis_a_jour_le TIMESTAMP
);

-- 30. ReferenceZoneEntite
CREATE TABLE core_referencezoneentite (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES core_zone(id),
    entite_id INTEGER NOT NULL REFERENCES core_entite(id),
    UNIQUE (zone_id, entite_id)
);

-- 31. CommandePaiement
CREATE TABLE core_commandepaiement (
    id SERIAL PRIMARY KEY,
    paiement_id INTEGER NOT NULL REFERENCES core_modepaiement(id),
    ajouter_le TIMESTAMP
);

-- 32. HistoriqueZonesRecuperation
CREATE TABLE core_historiquezonesrecuperation (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES core_zone(id),
    point_recup_id INTEGER NOT NULL REFERENCES core_pointrecup(id),
    mis_a_jour_le TIMESTAMP
);

-- 33. SuivisCommande
CREATE TABLE core_suiviscommande (
    id SERIAL PRIMARY KEY,
    commande_id INTEGER NOT NULL REFERENCES core_commande(id),
    restaurant_id INTEGER NOT NULL REFERENCES core_restaurant(id),
    statut BOOLEAN DEFAULT FALSE,
    mis_a_jour_le TIMESTAMP,
    UNIQUE (commande_id, restaurant_id, mis_a_jour_le)
);

-- 34. Admin
CREATE TABLE core_admin (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(128) NOT NULL,
    date_inscri TIMESTAMP
);
