
CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(128) NOT NULL,
    contact VARCHAR(50),
    prenom VARCHAR(100),
    nom VARCHAR(100),
    date_inscri TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE statut_commande (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

CREATE TABLE zone (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(100),
    zone VARCHAR(500)
);

CREATE TABLE livreur (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    contact TEXT,
    position VARCHAR(100),
    date_inscri TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE zone_client (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES client(id) ON DELETE CASCADE,
    zone_id INTEGER NOT NULL REFERENCES zone(id) ON DELETE CASCADE,
    UNIQUE (client_id, zone_id)
);

CREATE TABLE zone_livreur (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES zone(id) ON DELETE CASCADE,
    livreur_id INTEGER NOT NULL REFERENCES livreur(id) ON DELETE CASCADE,
    UNIQUE (zone_id, livreur_id)
);

CREATE TABLE point_recup (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    geo_position VARCHAR(100) DEFAULT '0,0'
);

CREATE TABLE mode_paiement (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL
);

CREATE TABLE commande (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES client(id) ON DELETE CASCADE,
    point_recup_id INTEGER NOT NULL REFERENCES point_recup(id) ON DELETE CASCADE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    mode_paiement_id INTEGER REFERENCES mode_paiement(id) ON DELETE SET NULL
);

CREATE TABLE historique_statut_commande (
    id SERIAL PRIMARY KEY,
    commande_id INTEGER NOT NULL REFERENCES commande(id) ON DELETE CASCADE,
    statut_id INTEGER NOT NULL REFERENCES statut_commande(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE statut_restaurant (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

CREATE TABLE restaurant (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(128) NOT NULL,
    adresse TEXT,
    description TEXT,
    image TEXT,
    geo_position VARCHAR(100) DEFAULT '0,0'
);

CREATE TABLE historique_statut_restaurant (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    statut_id INTEGER NOT NULL REFERENCES statut_restaurant(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE type_repas (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

CREATE TABLE repas (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    image TEXT,
    type_id INTEGER NOT NULL REFERENCES type_repas(id) ON DELETE CASCADE,
    prix INTEGER NOT NULL
);

CREATE TABLE disponibilite_repas (
    id SERIAL PRIMARY KEY,
    repas_id INTEGER NOT NULL REFERENCES repas(id) ON DELETE CASCADE,
    est_dispo BOOLEAN DEFAULT TRUE,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE statut_livreur (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

CREATE TABLE historique_statut_livreur (
    id SERIAL PRIMARY KEY,
    livreur_id INTEGER NOT NULL REFERENCES livreur(id) ON DELETE CASCADE,
    statut_id INTEGER NOT NULL REFERENCES statut_livreur(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE statut_zone (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

CREATE TABLE historique_statut_zone (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES zone(id) ON DELETE CASCADE,
    statut_id INTEGER NOT NULL REFERENCES statut_zone(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE statut_livraison (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100)
);

CREATE TABLE livraison (
    id SERIAL PRIMARY KEY,
    livreur_id INTEGER NOT NULL REFERENCES livreur(id) ON DELETE CASCADE,
    commande_id INTEGER NOT NULL REFERENCES commande(id) ON DELETE CASCADE,
    attribue_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE historique_statut_livraison (
    id SERIAL PRIMARY KEY,
    livraison_id INTEGER NOT NULL REFERENCES livraison(id) ON DELETE CASCADE,
    statut_id INTEGER NOT NULL REFERENCES statut_livraison(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE commande_repas (
    id SERIAL PRIMARY KEY,
    commande_id INTEGER NOT NULL REFERENCES commande(id) ON DELETE CASCADE,
    repas_id INTEGER NOT NULL REFERENCES repas(id) ON DELETE CASCADE,
    quantite INTEGER NOT NULL,
    ajoute_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (commande_id, repas_id)
);

CREATE TABLE restaurant_repas (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    repas_id INTEGER NOT NULL REFERENCES repas(id) ON DELETE CASCADE,
    UNIQUE (restaurant_id, repas_id)
);

CREATE TABLE zone_restaurant (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    zone_id INTEGER NOT NULL REFERENCES zone(id) ON DELETE CASCADE,
    UNIQUE (restaurant_id, zone_id)
);

CREATE TABLE commission (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    valeur INTEGER NOT NULL,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE horaire (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    le_jour INTEGER NOT NULL,
    horaire_debut TIME NOT NULL,
    horaire_fin TIME NOT NULL,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE horaire_special (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    date_concerne DATE NOT NULL,
    horaire_debut TIME NOT NULL,
    horaire_fin TIME NOT NULL,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE promotion (
    id SERIAL PRIMARY KEY,
    repas_id INTEGER NOT NULL REFERENCES repas(id) ON DELETE CASCADE,
    pourcentage_reduction INTEGER NOT NULL,
    date_concerne DATE NOT NULL
);

CREATE TABLE limite_commandes_journalieres (
    id SERIAL PRIMARY KEY,
    nombre_commandes INTEGER NOT NULL,
    date DATE NOT NULL
);

CREATE TABLE statut_entite (
    id SERIAL PRIMARY KEY,
    appellation VARCHAR(100) NOT NULL
);

CREATE TABLE entite (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

CREATE TABLE historique_statut_entite (
    id SERIAL PRIMARY KEY,
    entite_id INTEGER NOT NULL REFERENCES entite(id) ON DELETE CASCADE,
    statut_id INTEGER NOT NULL REFERENCES statut_entite(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE reference_zone_entite (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES zone(id) ON DELETE CASCADE,
    entite_id INTEGER NOT NULL REFERENCES entite(id) ON DELETE CASCADE,
    UNIQUE (zone_id, entite_id)
);

CREATE TABLE commande_paiement (
    id SERIAL PRIMARY KEY,
    paiement_id INTEGER NOT NULL REFERENCES mode_paiement(id) ON DELETE CASCADE,
    ajouter_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE historique_zones_recuperation (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES zone(id) ON DELETE CASCADE,
    point_recup_id INTEGER NOT NULL REFERENCES point_recup(id) ON DELETE CASCADE,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE suivis_commande (
    id SERIAL PRIMARY KEY,
    commande_id INTEGER NOT NULL REFERENCES commande(id) ON DELETE CASCADE,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
    statut BOOLEAN DEFAULT FALSE,
    mis_a_jour_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (commande_id, restaurant_id, mis_a_jour_le)
);
