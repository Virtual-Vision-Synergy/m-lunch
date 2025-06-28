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


-- Insertion dans clients
INSERT INTO clients (email, mot_de_passe, contact, prenom, nom) VALUES
    ('jean.dupont@example.com', 'motdepasse123', '+33 6 12 34 56 78', 'Jean', 'Dupont'),
    ('marie.martin@example.com', 'securepass456', '+33 6 98 76 54 32', 'Marie', 'Martin');

-- Insertion dans livreurs
INSERT INTO livreurs (nom, contact, position) VALUES
    ('Paul Durand', '+33 6 45 67 89 01', ST_GeomFromText('POINT(-73.935242 40.730610)', 4326)),
    ('Sophie Lefevre', '+33 6 23 45 67 89', ST_GeomFromText('POINT(-73.987654 40.712345)', 4326));


-- Insertion dans statut_zone
INSERT INTO statut_zone (appellation) VALUES
    ('Actif'),
    ('Inactif');

-- Insertion dans statut_entite
INSERT INTO statut_entite (appellation) VALUES
    ('Ouvert'),
    ('Fermé');

-- Insertion dans statut_commande
INSERT INTO statut_commande (appellation) VALUES
    ('En attente'),
    ('Confirmée');

-- Insertion dans statut_livreur
INSERT INTO statut_livreur (appellation) VALUES
    ('Disponible'),
    ('En livraison');
INSERT INTO statut_livreur (appellation) VALUES ('Quitte');

-- Insertion dans statut_livraison
INSERT INTO statut_livraison (appellation) VALUES
    ('En cours'),
    ('Livrée');
INSERT INTO statut_livraison (appellation) VALUES
    ('Annulee');

-- Insertion dans statut_restaurant
INSERT INTO statut_restaurant (appellation) VALUES
    ('Opérationnel'),
    ('En maintenance');
-- Insertion dans types_repas
INSERT INTO types_repas (nom) VALUES
    ('Snack'),
    ('Dessert');

-- Insertion dans statut_repas
INSERT INTO statut_repas (appellation) VALUES
    ('Disponible'),
    ('Indisponible'),
    ('Retiré du menu');

INSERT INTO types_repas (nom) VALUES
    ('Petit-déjeuner'),
    ('Déjeuner'),
    ('Dîner'),
    ('Collation'),
    ('Goûter');
INSERT INTO restaurants (nom, adresse, image, geo_position)
VALUES
('La Varangue', '17 Rue Printsy Ratsimamanga, Antananarivo 101', 'https://exemple.com/images/varangue.jpg', ST_GeogFromText('SRID=4326;POINT(47.5162 -18.8792)')),

('KUDeTA Urban Club', 'Rue des écoles, Isoraka, Antananarivo', 'https://exemple.com/images/kudeta.jpg', ST_GeogFromText('SRID=4326;POINT(47.5183 -18.9121)')),

('Le Carnivore', 'Rue Ravelojaona, Antanimena, Antananarivo', 'https://exemple.com/images/carnivore.jpg', ST_GeogFromText('SRID=4326;POINT(47.5168 -18.8943)')),

('Le Rossini', 'Ambatonakanga, Antananarivo', 'https://exemple.com/images/rossini.jpg', ST_GeogFromText('SRID=4326;POINT(47.5179 -18.9060)')),

('Café de la Gare', 'Soarano, Gare de Tana, Antananarivo', 'https://exemple.com/images/soarano.jpg', ST_GeogFromText('SRID=4326;POINT(47.5150 -18.9052)')),

('Le Buffet du Jardin', 'Jardin dAmbohijatovo, Antananarivo', 'https://exemple.com/images/buffet.jpg', ST_GeogFromText('SRID=4326;POINT(47.5190 -18.9065)')),

('Nerone Ristorante', 'Ankorondrano, Antananarivo', 'https://exemple.com/images/nerone.jpg', ST_GeogFromText('SRID=4326;POINT(47.5312 -18.8815)')),

('La Table dEugène', 'Ivandry, Antananarivo', 'https://exemple.com/images/eugene.jpg', ST_GeogFromText('SRID=4326;POINT(47.5400 -18.8750)')),

('Pavé Antaninarenina', 'Rue Ravelojaona, Antaninarenina, Antananarivo', 'https://exemple.com/images/pave.jpg', ST_GeogFromText('SRID=4326;POINT(47.5170 -18.9075)')),

('Villa Vanille', 'Ambohijatovo, Antananarivo', 'https://exemple.com/images/vanille.jpg', ST_GeogFromText('SRID=4326;POINT(47.5185 -18.9050)'));
