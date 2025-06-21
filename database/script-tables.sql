-- Activer l’extension PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Clients
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    contact TEXT,
    prenom VARCHAR(100),
    nom VARCHAR(100)
);

-- Livreurs
CREATE TABLE livreurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    contact TEXT,
    position GEOGRAPHY(POINT, 4326)
);

-- Types de repas
CREATE TABLE types_repas (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

-- Repas
CREATE TABLE repas (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    description TEXT,
    image TEXT,
    type_id INT REFERENCES types_repas(id),
    prix NUMERIC(10,2) NOT NULL
);

-- Restaurants
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150),
    adresse TEXT,
    image TEXT,
    geo_position GEOGRAPHY(POINT, 4326)
);

-- Zones de livraison
CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    zone GEOGRAPHY(POLYGON, 4326)
);

-- Commandes
CREATE TABLE commandes (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(id),
    cree_le TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Repas par commande
CREATE TABLE commande_repas (
    id SERIAL PRIMARY KEY,
    commande_id INT REFERENCES commandes(id) ON DELETE CASCADE,
    repas_id INT REFERENCES repas(id),
    ajoute_le TIMESTAMP DEFAULT now()
);

-- Disponibilité des repas
CREATE TABLE disponibilite_repas (
    id SERIAL PRIMARY KEY,
    repas_id INT REFERENCES repas(id),
    debut TIMESTAMP,
    fin TIMESTAMP
);

-- Promotions
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    repas_id INT REFERENCES repas(id),
    pourcentage_reduction INT CHECK (pourcentage_reduction BETWEEN 0 AND 100)
);

-- Historique des statuts des commandes
CREATE TABLE historique_statut_commande (
    id SERIAL PRIMARY KEY,
    commande_id INT REFERENCES commandes(id) ON DELETE CASCADE,
    statut VARCHAR(50),
    change_le TIMESTAMP DEFAULT now()
);

-- Historique des statuts des livreurs
CREATE TABLE historique_statut_livreur (
    id SERIAL PRIMARY KEY,
    livreur_id INT REFERENCES livreurs(id),
    statut VARCHAR(50),
    mis_a_jour_le TIMESTAMP DEFAULT now()
);

-- Commandes attribuées aux livreurs
CREATE TABLE livraisons (
    id SERIAL PRIMARY KEY,
    livreur_id INT REFERENCES livreurs(id),
    commande_id INT REFERENCES commandes(id),
    attribue_le TIMESTAMP DEFAULT now()
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
    disponible_depuis TIMESTAMP DEFAULT now()
);

-- Historique des statuts des restaurants
CREATE TABLE historique_statut_restaurant (
    id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES restaurants(id),
    statut VARCHAR(50),
    change_le TIMESTAMP DEFAULT now()
);

-- Limite de commandes par jour
CREATE TABLE limite_commandes_journalieres (
    id SERIAL PRIMARY KEY,
    nombre_commandes INT CHECK (nombre_commandes >= 0),
    date DATE NOT NULL
);
