-- Activer l’extension PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Clients
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    contact TEXT,
    prenom VARCHAR(100),
    nom VARCHAR(100),
    date_inscri TIMESTAMP DEFAULT now()
);

-- Livreurs
CREATE TABLE livreurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    contact TEXT,
    position GEOGRAPHY(POINT, 4326),
    date_inscri TIMESTAMP DEFAULT now()
);

-- Types de repas
CREATE TABLE types_repas (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

-- Repas
CREATE TABLE repas (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    image TEXT,
    type_id INT REFERENCES types_repas(id),
    prix INTEGER NOT NULL
);

-- Restaurants
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    adresse TEXT,
    description TEXT,
    image TEXT,
    geo_position GEOGRAPHY(POINT, 4326)
);

-- Horaires réguliers
CREATE TABLE horaire (
    id SERIAL PRIMARY KEY,
    restaurant_id  INT REFERENCES restaurants(id) ON DELETE CASCADE,
    le_jour INT CHECK (le_jour BETWEEN 1 AND 7),
    horaire_debut TIME,
    horaire_fin TIME,
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

-- Horaires exceptionnels
CREATE TABLE horaire_special (
    id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES restaurants(id) ON DELETE CASCADE,
    date_concerne DATE NOT NULL,
    horaire_debut TIME,
    horaire_fin TIME,
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

-- Commissions
CREATE TABLE commissions (
    id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES restaurants(id) ON DELETE CASCADE,
    valeur INT NOT NULL,
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

-- Statuts
CREATE TABLE statut_zone (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100) NOT NULL
);

CREATE TABLE statut_entite (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100) NOT NULL
);

CREATE TABLE statut_commande (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100) NOT NULL
);

CREATE TABLE statut_livreur (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100) NOT NULL
);

CREATE TABLE statut_livraison (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100) NOT NULL
);

CREATE TABLE statut_restaurant (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100) NOT NULL
);

-- Zones de livraison
CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description VARCHAR(100),
    zone GEOGRAPHY(POLYGON, 4326)
);

CREATE TABLE point_de_recuperation (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    geo_position GEOGRAPHY(POINT, 4326)
);

-- Modes de paiement
CREATE TABLE mode_de_paiement (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL
);

CREATE TABLE commande_paiement (
    id SERIAL PRIMARY KEY,
    paiement_id INT REFERENCES mode_de_paiement(id),
    ajouter_le TIMESTAMP DEFAULT now()
);

CREATE TABLE historique_zones_recuperation (
    id SERIAL PRIMARY KEY,
    zone_id  INT REFERENCES zones(id) ON DELETE CASCADE,
    point_recup_id INT REFERENCES point_de_recuperation(id),
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

CREATE TABLE historique_statut_zone (
    id SERIAL PRIMARY KEY,
    zone_id INT REFERENCES zones(id) ON DELETE CASCADE,
    statut_id INT REFERENCES statut_zone(id),
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

CREATE TABLE entites (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

CREATE TABLE historique_statut_entite (
    id SERIAL PRIMARY KEY,
    entite_id INT REFERENCES entites(id) ON DELETE CASCADE,
    statut_id INT REFERENCES statut_entite(id),
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

CREATE TABLE reference_zone_entite (
    id SERIAL PRIMARY KEY,
    zone_id INT REFERENCES zones(id),
    entite_id INT REFERENCES entites(id)
);

-- Commandes
CREATE TABLE commandes (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(id),
    point_recup_id INT REFERENCES point_de_recuperation(id),
    cree_le TIMESTAMP DEFAULT now()
);

-- Repas par commande
CREATE TABLE commande_repas (
    id SERIAL PRIMARY KEY,
    commande_id INT REFERENCES commandes(id) ON DELETE CASCADE,
    repas_id INT REFERENCES repas(id),
    quantite INT NOT NULL,
    ajoute_le TIMESTAMP DEFAULT now()
);

-- Disponibilité des repas
CREATE TABLE disponibilite_repas (
    id SERIAL PRIMARY KEY,
    repas_id INT REFERENCES repas(id),
    est_dispo BOOLEAN DEFAULT TRUE,
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

-- Promotions
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    repas_id INT REFERENCES repas(id),
    pourcentage_reduction INT CHECK (pourcentage_reduction BETWEEN 0 AND 100),
    date_concerne DATE NOT NULL
);

-- Historique des statuts des commandes
CREATE TABLE historique_statut_commande (
    id SERIAL PRIMARY KEY,
    commande_id INT REFERENCES commandes(id) ON DELETE CASCADE,
    statut_id INT REFERENCES statut_commande(id),
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

-- Historique des statuts des livreurs
CREATE TABLE historique_statut_livreur (
    id SERIAL PRIMARY KEY,
    livreur_id INT REFERENCES livreurs(id),
    statut_id INT REFERENCES statut_livreur(id),
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

-- Commandes attribuées aux livreurs
CREATE TABLE livraisons (
    id SERIAL PRIMARY KEY,
    livreur_id INT REFERENCES livreurs(id),
    commande_id INT REFERENCES commandes(id),
    attribue_le TIMESTAMP DEFAULT now()
);

-- Historique des statuts des livraisons
CREATE TABLE historique_statut_livraison (
    id SERIAL PRIMARY KEY,
    livraison_id INT REFERENCES livraisons(id),
    statut_id INT REFERENCES statut_livraison(id),
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

-- Repas proposés par un restaurant
CREATE TABLE repas_restaurant (
    id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES restaurants(id),
    repas_id INT REFERENCES repas(id)
);

-- Zones desservies par un restaurant
CREATE TABLE zones_restaurant (
    id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES restaurants(id),
    zone_id INT REFERENCES zones(id)
);

-- Zones préférées des clients
CREATE TABLE zones_clients (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(id),
    zone_id INT REFERENCES zones(id)
);

-- Zones couvertes par un livreur
CREATE TABLE zones_livreurs (
    id SERIAL PRIMARY KEY,
    livreur_id INT REFERENCES livreurs(id),
    zone_id INT REFERENCES zones(id),
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

-- Historique des statuts des restaurants
CREATE TABLE historique_statut_restaurant (
    id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES restaurants(id),
    statut_id INT REFERENCES statut_restaurant(id),
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

-- Limite de commandes par jour
CREATE TABLE limite_commandes_journalieres (
    id SERIAL PRIMARY KEY,
    nombre_commandes INT NOT NULL,
    date DATE NOT NULL
);
