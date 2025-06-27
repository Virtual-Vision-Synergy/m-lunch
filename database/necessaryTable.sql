
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
    ('Actif'),
    ('Inactif');
-- Insertion dans statut_commande
INSERT INTO statut_commande (appellation) VALUES
    ('En attente'),
    ('En cours');
    ('Effectue')
-- Insertion dans statut_livreur
INSERT INTO statut_livreur (appellation) VALUES
    ('Disponible'),
    ('En livraison'),
    ('Inactif');
-- Insertion dans statut_livraison
INSERT INTO statut_livraison (appellation) VALUES
    ('Annulee'),
    ('en cours de livraison'),
    ('livree');
-- Insertion dans statut_restaurant
INSERT INTO statut_restaurant (appellation) VALUES
    ('Actif'),
    ('Inactif');
-- Insertion dans types_repas
INSERT INTO types_repas (nom) VALUES
    ('Entree'),
    ('Plat'),
    ('Dessert'),
    ('Boisson');

-- Insertion dans statut_repas
INSERT INTO statut_repas (appellation) VALUES
    ('Disponible'),
    ('Indisponible');


