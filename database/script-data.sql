-- CLIENT
CREATE TABLE core_client (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(128) NOT NULL,
    contact VARCHAR(50),
    prenom VARCHAR(100),
    nom VARCHAR(100),
    date_inscri TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- STATUT COMMANDE
CREATE TABLE core_statutcommande (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

-- ZONE
CREATE TABLE core_zone (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(100),
    zone VARCHAR(500)
);

-- ZONE CLIENT
CREATE TABLE core_zoneclient (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES core_client(id) ON DELETE CASCADE,
    zone_id INTEGER REFERENCES core_zone(id) ON DELETE CASCADE,
    UNIQUE (client_id, zone_id)
);

-- STATUT LIVREUR
CREATE TABLE core_statutlivreur (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

-- LIVREUR
CREATE TABLE core_livreur (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    contact TEXT,
    position VARCHAR(100),
    date_inscri TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ZONE LIVREUR
CREATE TABLE core_zonelivreur (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES core_zone(id) ON DELETE CASCADE,
    livreur_id INTEGER REFERENCES core_livreur(id) ON DELETE CASCADE,
    UNIQUE (zone_id, livreur_id)
);

-- POINT DE RECUP
CREATE TABLE core_pointrecup (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    geo_position VARCHAR(100) DEFAULT '0,0'
);

-- MODE PAIEMENT
CREATE TABLE core_modepaiement (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
);

-- COMMANDE
CREATE TABLE core_commande (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES core_client(id) ON DELETE CASCADE,
    point_recup_id INTEGER REFERENCES core_pointrecup(id) ON DELETE CASCADE,
    cree_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    mode_paiement_id INTEGER REFERENCES core_modepaiement(id) ON DELETE SET NULL
);

-- HISTORIQUE STATUT COMMANDE
CREATE TABLE core_historiquestatutcommande (
    id SERIAL PRIMARY KEY,
    commande_id INTEGER REFERENCES core_commande(id) ON DELETE CASCADE,
    statut_id INTEGER REFERENCES core_statutcommande(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- STATUT RESTAURANT
CREATE TABLE core_statutrestaurant (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

-- RESTAURANT
CREATE TABLE core_restaurant (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) UNIQUE NOT NULL,
    adresse TEXT,
    description TEXT,
    image TEXT,
    geo_position VARCHAR(100) DEFAULT '0,0'
);

-- HISTORIQUE STATUT RESTAURANT
CREATE TABLE core_historiquestatutrestaurant (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES core_restaurant(id) ON DELETE CASCADE,
    statut_id INTEGER REFERENCES core_statutrestaurant(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- TYPE DE REPAS
CREATE TABLE core_typerepas (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

-- REPAS
CREATE TABLE core_repas (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    image TEXT,
    type_id INTEGER REFERENCES core_typerepas(id) ON DELETE CASCADE,
    prix INTEGER NOT NULL
);

-- DISPONIBILITE REPAS
CREATE TABLE core_disponibiliterepas (
    id SERIAL PRIMARY KEY,
    repas_id INTEGER REFERENCES core_repas(id) ON DELETE CASCADE,
    est_dispo BOOLEAN DEFAULT TRUE,
    mis_a_jour_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- HISTORIQUE STATUT LIVREUR
CREATE TABLE core_historiquestatutlivreur (
    id SERIAL PRIMARY KEY,
    livreur_id INTEGER REFERENCES core_livreur(id) ON DELETE CASCADE,
    statut_id INTEGER REFERENCES core_statutlivreur(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- STATUT ZONE
CREATE TABLE core_statutzone (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

-- HISTORIQUE STATUT ZONE
CREATE TABLE core_historiquestatutzone (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES core_zone(id) ON DELETE CASCADE,
    statut_id INTEGER REFERENCES core_statutzone(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- STATUT LIVRAISON
CREATE TABLE core_statutlivraison (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

-- LIVRAISON
CREATE TABLE core_livraison (
    id SERIAL PRIMARY KEY,
    livreur_id INTEGER REFERENCES core_livreur(id) ON DELETE CASCADE,
    commande_id INTEGER REFERENCES core_commande(id) ON DELETE CASCADE,
    attribue_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- HISTORIQUE STATUT LIVRAISON
CREATE TABLE core_historiquestatutlivraison (
    id SERIAL PRIMARY KEY,
    livraison_id INTEGER REFERENCES core_livraison(id) ON DELETE CASCADE,
    statut_id INTEGER REFERENCES core_statutlivraison(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- COMMANDE REPAS
CREATE TABLE core_commanderepas (
    id SERIAL PRIMARY KEY,
    commande_id INTEGER REFERENCES core_commande(id) ON DELETE CASCADE,
    repas_id INTEGER REFERENCES core_repas(id) ON DELETE CASCADE,
    quantite INTEGER NOT NULL,
    ajoute_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (commande_id, repas_id)
);

-- RESTAURANT REPAS
CREATE TABLE core_restaurantrepas (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES core_restaurant(id) ON DELETE CASCADE,
    repas_id INTEGER REFERENCES core_repas(id) ON DELETE CASCADE,
    UNIQUE (restaurant_id, repas_id)
);

-- ZONE RESTAURANT
CREATE TABLE core_zonerestaurant (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES core_restaurant(id) ON DELETE CASCADE,
    zone_id INTEGER REFERENCES core_zone(id) ON DELETE CASCADE,
    UNIQUE (restaurant_id, zone_id)
);

-- COMMISSION
CREATE TABLE core_commission (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES core_restaurant(id) ON DELETE CASCADE,
    valeur INTEGER NOT NULL,
    mis_a_jour_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- HORAIRE
CREATE TABLE core_horaire (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES core_restaurant(id) ON DELETE CASCADE,
    le_jour INTEGER NOT NULL,
    horaire_debut TIME NOT NULL,
    horaire_fin TIME NOT NULL,
    mis_a_jour_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- HORAIRE SPECIAL
CREATE TABLE core_horairespecial (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES core_restaurant(id) ON DELETE CASCADE,
    date_concerne DATE NOT NULL,
    horaire_debut TIME NOT NULL,
    horaire_fin TIME NOT NULL,
    mis_a_jour_le TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- PROMOTION
CREATE TABLE core_promotion (
    id SERIAL PRIMARY KEY,
    repas_id INTEGER REFERENCES core_repas(id) ON DELETE CASCADE,
    pourcentage_reduction INTEGER NOT NULL,
    date_concerne DATE NOT NULL
);

-- LIMITE COMMANDES JOURNALIERES
CREATE TABLE core_limitecommandesjournalieres (
    id SERIAL PRIMARY KEY,
    nombre_commandes INTEGER NOT NULL,
    date DATE NOT NULL
);
