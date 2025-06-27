-- Données statiques
INSERT INTO statut_zone (appellation) VALUES
    ('Actif'),
    ('Inactif');

INSERT INTO statut_entite (appellation) VALUES
    ('Actif'),
    ('Inactif');

INSERT INTO statut_commande (appellation) VALUES
    ('En attente'),
    ('En cours'),
    ('Effectue');

INSERT INTO statut_livreur (appellation) VALUES
    ('Disponible'),
    ('En livraison'),
    ('Inactif');

INSERT INTO statut_livraison (appellation) VALUES
    ('Annulee'),
    ('en cours de livraison'),
    ('livree');

INSERT INTO statut_restaurant (appellation) VALUES
    ('Actif'),
    ('Inactif');

INSERT INTO types_repas (nom) VALUES
    ('Entree'),
    ('Plat'),
    ('Dessert'),
    ('Boisson');

-- Données de test
INSERT INTO clients (email, mot_de_passe, contact, prenom, nom) VALUES
('alice@example.com', 'hashed_password1', '0341234567', 'Alice', 'Rasoanaivo'),
('bob@example.com', 'hashed_password2', '0349876543', 'Bob', 'Rakoto');

INSERT INTO livreurs (nom, contact, position) VALUES
('Tiana Randria', '0321234567', ST_GeogFromText('SRID=4326;POINT(47.5 -18.9)')),
('Nomena Rala', '0327654321', ST_GeogFromText('SRID=4326;POINT(47.6 -18.88)'));

INSERT INTO restaurants (nom, adresse, image, geo_position) VALUES
('Le Gourmet', 'Rue 12, Antananarivo', 'gourmet.png', ST_GeogFromText('SRID=4326;POINT(47.51 -18.91)')),
('Snack Tana', 'Boulevard Tsimisy', 'snack.png', ST_GeogFromText('SRID=4326;POINT(47.52 -18.92)'));

INSERT INTO repas (nom, description, image, type_id, prix) VALUES
('Salade verte', 'Une salade fraîche avec tomates', 'salade.png', 1, 3500),
('Poulet grillé', 'Poulet mariné et grillé', 'poulet.png', 2, 8000),
('Tarte au citron', 'Dessert citronné', 'tarte.png', 3, 4500),
('Jus de mangue', 'Boisson naturelle', 'jus.png', 4, 2500);

INSERT INTO repas_restaurant (restaurant_id, repas_id) VALUES
(1, 1), (1, 2), (1, 4), (2, 3), (2, 4);

INSERT INTO zones (nom, description, zone) VALUES
('Centre Ville', 'Zone centrale de Tana', ST_GeogFromText('SRID=4326;POLYGON((47.5 -18.9, 47.52 -18.9, 47.52 -18.88, 47.5 -18.88, 47.5 -18.9))')),
('Andavamamba', 'Zone Est', ST_GeogFromText('SRID=4326;POLYGON((47.53 -18.91, 47.55 -18.91, 47.55 -18.89, 47.53 -18.89, 47.53 -18.91))'));

INSERT INTO point_de_recuperation (nom, geo_position) VALUES
('Station Analakely', ST_GeogFromText('SRID=4326;POINT(47.505 -18.89)')),
('Marché Isotry', ST_GeogFromText('SRID=4326;POINT(47.54 -18.91)'));

INSERT INTO commandes (client_id, point_recup_id) VALUES
(1, 1),
(2, 2);

INSERT INTO commande_repas (commande_id, repas_id, quantite) VALUES
(1, 2, 1),
(1, 4, 2),
(2, 3, 1);

INSERT INTO disponibilite_repas (repas_id, est_dispo) VALUES
(1, TRUE),
(2, TRUE),
(3, FALSE),
(4, TRUE);

INSERT INTO promotions (repas_id, pourcentage_reduction, date_concerne) VALUES
(2, 15, CURRENT_DATE),
(4, 10, CURRENT_DATE + INTERVAL '1 day');

INSERT INTO livraisons (livreur_id, commande_id) VALUES
(1, 1),
(2, 2);

INSERT INTO zones_restaurant (restaurant_id, zone_id) VALUES
(1, 1),
(2, 2);

INSERT INTO zones_clients (client_id, zone_id) VALUES
(1, 1),
(2, 2);

INSERT INTO zones_livreurs (livreur_id, zone_id) VALUES
(1, 1),
(2, 2);

INSERT INTO entites (nom) VALUES
('Entité A'),
('Entité B');

INSERT INTO historique_statut_zone (zone_id, statut_id) VALUES
(1, 1),
(2, 2);

INSERT INTO historique_statut_entite (entite_id, statut_id) VALUES
(1, 1),
(2, 2);

INSERT INTO reference_zone_entite (zone_id, entite_id) VALUES
(1, 1),
(2, 2);

INSERT INTO historique_statut_commande (commande_id, statut_id) VALUES
(1, 1),
(1, 2),
(2, 3);

INSERT INTO historique_statut_livreur (livreur_id, statut_id) VALUES
(1, 1),
(2, 2);

INSERT INTO historique_statut_livraison (livraison_id, statut_id) VALUES
(1, 2),
(2, 3);

INSERT INTO historique_statut_restaurant (restaurant_id, statut_id) VALUES
(1, 1),
(2, 2);

INSERT INTO historique_zones_recuperation (zone_id, point_recup_id) VALUES
(1, 1),
(2, 2);

INSERT INTO limite_commandes_journalieres (nombre_commandes, date) VALUES
(1, CURRENT_DATE),
(3, CURRENT_DATE + INTERVAL '1 day');
