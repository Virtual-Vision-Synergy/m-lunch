delete from historique_statut_commande ;
delete from commande_repas ;
delete from commandes ;
delete from statut_commande ;
delete from zones_clients ;
delete from clients ;
delete from zones_restaurant ;
delete from zones ;
delete from repas_restaurant ;
delete from restaurants ;
delete from repas ;
delete from types_repas;

ALTER SEQUENCE historique_statut_commande_id_seq RESTART WITH 1;
ALTER SEQUENCE commande_repas_id_seq RESTART WITH 1;
ALTER SEQUENCE commandes_id_seq RESTART WITH 1;
ALTER SEQUENCE statut_commande_id_seq RESTART WITH 1;
ALTER SEQUENCE zones_clients_id_seq RESTART WITH 1;
ALTER SEQUENCE clients_id_seq RESTART WITH 1;
ALTER SEQUENCE zones_restaurant_id_seq RESTART WITH 1;
ALTER SEQUENCE zones_id_seq RESTART WITH 1;
ALTER SEQUENCE repas_restaurant_id_seq RESTART WITH 1;
ALTER SEQUENCE restaurants_id_seq RESTART WITH 1;
ALTER SEQUENCE repas_id_seq RESTART WITH 1;
ALTER SEQUENCE livreurs_id_seq RESTART WITH 1;
ALTER SEQUENCE types_repas_id_seq RESTART WITH 1;

-- Types de repas (inchangé, universel)
INSERT INTO types_repas (nom) VALUES 
('Burger'), ('Pizza'), ('Sushi'), ('Salade'), ('Pâtes'), 
('Dessert'), ('Boisson'), ('Asiatique'), ('Mexicain'), ('Végétarien'),
('Malagasy'), ('Créole'), ('Fruits de mer');

-- Repas avec spécialités malgaches
INSERT INTO repas (nom, description, type_id, prix) VALUES
('Cheeseburger', 'Burger avec fromage, salade et sauce spéciale', 1, 20000),
('Burger Végétarien', 'Burger aux légumes grillés', 10, 22000),
('Margherita', 'Pizza classique avec tomate et mozzarella', 2, 25000),
('California Roll', 'Sushi au crabe et avocat', 3, 30000),
('Salade César', 'Salade avec poulet grillé et croûtons', 4, 18000),
('Carbonara', 'Pâtes avec sauce à la crème et lardons', 5, 22000),
('Tiramisu', 'Dessert italien au café', 6, 12000),
('THB', 'Biere malgache Three Horses Beer', 7, 5000),
('Pad Thai', 'Nouilles sautées thaïlandaises', 8, 25000),
('Burritos', 'Tortilla garnie de viande et légumes', 9, 20000),
('Romazava', 'Plat traditionnel malgache à base de brèdes', 11, 15000),
('Ravitoto', 'Ravitoto sy henakisoa - Feuilles de manioc pilées avec porc', 11, 18000),
('Lasopy', 'Soupe de légumes malgache', 11, 12000),
('Crevettes grillées', 'Crevettes fraîches de Madagascar', 13, 35000),
('Salade de Fruits tropicaux', 'Mélange de fruits frais de saison', 10, 10000),
('Mokary', 'Beignet malgache', 6, 3000),
('Ranonapango', 'Boisson traditionnelle à base de riz brûlé', 7, 2000),
('Sambos', 'Samoussas malgaches', 12, 4000),
('Achards de légumes', 'Légumes marinés à la malgache', 4, 8000),
('Foie gras de canard', 'Spécialité de Madagascar', 13, 45000);

-- Restaurants d'Antananarivo
INSERT INTO restaurants (nom,  adresse, geo_position) VALUES
('Burger Queen Tana', 'Avenue de l Indépendance', ST_GeographyFromText('SRID=4326;POINT(47.5252 -18.9100)')),
('Pizza Tana', 'Rue Ratsimilaho', ST_GeographyFromText('SRID=4326;POINT(47.5300 -18.9080)')),
('Sakura Sushi', 'Ambohijatovo', ST_GeographyFromText('SRID=4326;POINT(47.5200 -18.9050)')),
('La Saladerie', 'Isoraka', ST_GeographyFromText('SRID=4326;POINT(47.5150 -18.9070)')),
('Pasta Mia', 'Analakely', ST_GeographyFromText('SRID=4326;POINT(47.5180 -18.9030)')),
('Saveurs d Asie', 'Andraharo', ST_GeographyFromText('SRID=4326;POINT(47.5350 -18.9000)')),
('El Rancho', 'Ankadifotsy', ST_GeographyFromText('SRID=4326;POINT(47.5100 -18.9020)')),
('Chez Mariette', 'Antanimena', ST_GeographyFromText('SRID=4326;POINT(47.5220 -18.9150)')),
('Le Petit Gâteau', 'Faravohitra', ST_GeographyFromText('SRID=4326;POINT(47.5280 -18.9180)')),
('La Varangue', 'Antsahavola', ST_GeographyFromText('SRID=4326;POINT(47.5150 -18.9120)'));

-- Associations repas-restaurants
INSERT INTO repas_restaurant (restaurant_id, repas_id) VALUES
(1, 1), (1, 2), (1, 15), (1, 7), (1, 8),
(2, 3), (2, 12), (2, 5), (2, 13), (2, 7),
(3, 4), (3, 14), (3, 9), (3, 18), (3, 15),
(4, 5), (4, 11), (4, 15), (4, 8), (4, 19),
(5, 6), (5, 13), (5, 7), (5, 8), (5, 15),
(6, 9), (6, 18), (6, 4), (6, 14), (6, 8),
(7, 10), (7, 19), (7, 5), (7, 7), (7, 8),
(8, 11), (8, 12), (8, 13), (8, 15), (8, 17),
(9, 7), (9, 16), (9, 15), (9, 17), (9, 8),
(10, 8), (10, 17), (10, 7), (10, 16), (10, 20);

-- Zones de livraison à Antananarivo
INSERT INTO zones (nom, description, zone) VALUES
('Centre-ville', 'Analakely, Isoraka, Antaninarenina', ST_GeographyFromText('SRID=4326;POLYGON((47.51 -18.91, 47.53 -18.91, 47.53 -18.90, 47.51 -18.90, 47.51 -18.91))')),
('Haute-ville', 'Ambohijatovo, Faravohitra', ST_GeographyFromText('SRID=4326;POLYGON((47.52 -18.92, 47.54 -18.92, 47.54 -18.91, 47.52 -18.91, 47.52 -18.92))')),
('Basse-ville', 'Anosy, Andraharo', ST_GeographyFromText('SRID=4326;POLYGON((47.51 -18.92, 47.53 -18.92, 47.53 -18.93, 47.51 -18.93, 47.51 -18.92))')),
('Ouest', 'Ankadifotsy, Antanimena', ST_GeographyFromText('SRID=4326;POLYGON((47.50 -18.91, 47.51 -18.91, 47.51 -18.92, 47.50 -18.92, 47.50 -18.91))')),
('Est', 'Ankorondrano, Ivandry', ST_GeographyFromText('SRID=4326;POLYGON((47.53 -18.90, 47.55 -18.90, 47.55 -18.91, 47.53 -18.91, 47.53 -18.90))'));

-- Zones desservies par les restaurants
INSERT INTO zones_restaurant (restaurant_id, zone_id) VALUES
(1, 1), (1, 2), (1, 3),
(2, 1), (2, 3), (2, 5),
(3, 1), (3, 4),
(4, 1), (4, 2), (4, 3), (4, 4),
(5, 1), (5, 5),
(6, 1), (6, 2), (6, 4),
(7, 1), (7, 3), (7, 5),
(8, 1), (8, 2),
(9, 1), (9, 2), (9, 3),
(10, 1), (10, 5);

-- Clients malgaches
INSERT INTO clients (email, mot_de_passe, contact, prenom, nom, date_inscri) VALUES
('rabe@example.mg', 'password1', '+261340102030', 'Jean', 'Rabe', '2023-01-15 10:30:00'),
('rasoa@example.mg', 'password2', '+261340203040', 'Marie', 'Rasoa', '2023-02-20 14:15:00'),
('randria@example.mg', 'password3', '+261340304050', 'Pierre', 'Randria', '2023-03-05 09:00:00'),
('raharison@example.mg', 'password4', '+261340405060', 'Sophie', 'Raharison', '2023-04-10 16:45:00'),
('rakoto@example.mg', 'password5', '+261340506070', 'Thomas', 'Rakoto', '2023-05-15 11:20:00'),
('ravao@example.mg', 'password6', '+261340607080', 'Laura', 'Ravao', '2023-06-20 13:10:00'),
('randriana@example.mg', 'password7', '+261340708090', 'Nicolas', 'Randriana', '2023-07-05 17:30:00'),
('ramanana@example.mg', 'password8', '+261340809100', 'Emma', 'Ramanana', '2023-08-10 10:00:00'),
('ramaroson@example.mg', 'password9', '+261340910110', 'Alexandre', 'Ramaroson', '2023-09-15 15:45:00'),
('randriami@example.mg', 'password10', '+261341011120', 'Camille', 'Randriami', '2023-10-20 12:00:00'),
('razafy@example.mg', 'password11', '+261341112130', 'Antoine', 'Razafy', '2023-11-05 14:30:00'),
('rasolof@example.mg', 'password12', '+261341213140', 'Julie', 'Rasolof', '2023-12-10 09:15:00'),
('rajaona@example.mg', 'password13', '+261341314150', 'David', 'Rajaona', '2024-01-15 16:00:00'),
('rakotobe@example.mg', 'password14', '+261341415160', 'Sarah', 'Rakotobe', '2024-02-20 11:45:00'),
('randrian@example.mg', 'password15', '+261341516170', 'Paul', 'Randrian', '2024-03-05 13:20:00');

-- Zones préférées des clients
INSERT INTO zones_clients (client_id, zone_id) VALUES
(1, 1), (1, 2),
(2, 1),
(3, 3), (3, 5),
(4, 1), (4, 4),
(5, 2),
(6, 1), (6, 3),
(7, 5),
(8, 1), (8, 2), (8, 3),
(9, 4),
(10, 1),
(11, 2), (11, 5),
(12, 1), (12, 3),
(13, 4),
(14, 1),
(15, 2), (15, 3);

-- Statuts de commande (inchangé)
INSERT INTO statut_commande (appellation) VALUES
('En attente'), ('En préparation'), ('Prête'), ('En livraison'), ('Livrée'), ('Annulée');

-- Commandes récentes
INSERT INTO commandes (client_id, cree_le) VALUES
(1, '2024-04-01 12:30:00'),
(2, '2024-04-01 13:15:00'),
(3, '2024-04-01 18:45:00'),
(4, '2024-04-02 11:20:00'),
(5, '2024-04-02 12:45:00'),
(6, '2024-04-02 19:30:00'),
(7, '2024-04-03 10:15:00'),
(8, '2024-04-03 13:00:00'),
(9, '2024-04-03 20:00:00'),
(10, '2024-04-04 12:30:00'),
(11, '2024-04-04 14:45:00'),
(12, '2024-04-04 19:15:00'),
(13, '2024-04-05 11:00:00'),
(14, '2024-04-05 13:30:00'),
(15, '2024-04-05 18:45:00'),
(1, '2024-04-06 12:15:00'),
(2, '2024-04-06 14:30:00'),
(3, '2024-04-06 20:00:00'),
(4, '2024-04-07 11:45:00'),
(5, '2024-04-07 13:15:00');

-- Détails des commandes
INSERT INTO commande_repas (commande_id, repas_id, quantite) VALUES
(1, 11, 2), (1, 17, 2),
(2, 12, 1), (2, 7, 1),
(3, 14, 3), (3, 8, 2),
(4, 5, 1), (4, 15, 1),
(5, 6, 2), (5, 7, 1),
(6, 10, 2), (6, 19, 1),
(7, 2, 1), (7, 11, 1),
(8, 12, 1), (8, 13, 1),
(9, 14, 2), (9, 18, 1),
(10, 11, 1), (10, 5, 1),
(11, 16, 2), (11, 17, 2),
(12, 1, 1), (12, 2, 1),
(13, 3, 2), (13, 12, 1),
(14, 4, 1), (14, 14, 1),
(15, 5, 2), (15, 11, 1),
(16, 6, 1), (16, 13, 1),
(17, 7, 2), (17, 16, 1),
(18, 8, 1), (18, 17, 2),
(19, 9, 2), (19, 18, 1),
(20, 10, 1), (20, 19, 1);

-- Statuts des commandes
INSERT INTO historique_statut_commande (commande_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-04-01 12:30:00'),
(2, 1, '2024-04-01 13:15:00'),
(3, 1, '2024-04-01 18:45:00'),
(4, 1, '2024-04-02 11:20:00'),
(5, 1, '2024-04-02 12:45:00'),
(6, 1, '2024-04-02 19:30:00'),
(7, 1, '2024-04-03 10:15:00'),
(8, 1, '2024-04-03 13:00:00'),
(9, 1, '2024-04-03 20:00:00'),
(10, 1, '2024-04-04 12:30:00'),
(11, 2, '2024-04-04 14:45:00'),
(12, 3, '2024-04-04 19:15:00'),
(13, 4, '2024-04-05 11:00:00'),
(14, 5, '2024-04-05 13:30:00'),
(15, 6, '2024-04-05 18:45:00'),
(16, 2, '2024-04-06 12:15:00'),
(17, 3, '2024-04-06 14:30:00'),
(18, 4, '2024-04-06 20:00:00'),
(19, 5, '2024-04-07 11:45:00'),
(20, 6, '2024-04-07 13:15:00');

-- Livreurs
INSERT INTO livreurs (nom, contact, position, date_inscri) VALUES
('Rakoto', '+261320123456', ST_GeographyFromText('SRID=4326;POINT(47.5150 -18.9080)'), '2023-01-10 08:00:00'),
('Rasoa', '+261320234567', ST_GeographyFromText('SRID=4326;POINT(47.5250 -18.9050)'), '2023-02-15 09:30:00'),
('Randria', '+261320345678', ST_GeographyFromText('SRID=4326;POINT(47.5200 -18.9150)'), '2023-03-20 10:45:00'),
('Razafy', '+261320456789', ST_GeographyFromText('SRID=4326;POINT(47.5300 -18.9100)'), '2023-04-25 11:15:00'),
('Raharison', '+261320567890', ST_GeographyFromText('SRID=4326;POINT(47.5100 -18.9000)'), '2023-05-30 14:20:00');

-- Statuts livreur
INSERT INTO statut_livreur (appellation) VALUES
('Disponible'), ('En livraison'), ('Indisponible'), ('En pause');

-- Historique statut livreur
INSERT INTO historique_statut_livreur (livreur_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-04-01 08:00:00'),
(2, 1, '2024-04-01 09:00:00'),
(3, 1, '2024-04-01 10:00:00'),
(4, 1, '2024-04-01 11:00:00'),
(5, 1, '2024-04-01 12:00:00');

-- Points de récupération
INSERT INTO point_de_recuperation (nom, geo_position) VALUES
('Point Analakely', ST_GeographyFromText('SRID=4326;POINT(47.5180 -18.9030)')),
('Point Isoraka', ST_GeographyFromText('SRID=4326;POINT(47.5150 -18.9070)')),
('Point Ambohijatovo', ST_GeographyFromText('SRID=4326;POINT(47.5200 -18.9050)')),
('Point Ankorondrano', ST_GeographyFromText('SRID=4326;POINT(47.5350 -18.9000)')),
('Point Antanimena', ST_GeographyFromText('SRID=4326;POINT(47.5220 -18.9150)'));

-- Historique zones récupération
INSERT INTO historique_zones_recuperation (zone_id, point_recup_id, mis_a_jour_le) VALUES
(1, 1, '2024-01-01 00:00:00'),
(1, 2, '2024-01-01 00:00:00'),
(2, 3, '2024-01-01 00:00:00'),
(3, 4, '2024-01-01 00:00:00'),
(4, 5, '2024-01-01 00:00:00');

-- Statuts zone
INSERT INTO statut_zone (appellation) VALUES
('Active'), ('Inactive'), ('En maintenance');

-- Historique statut zone
INSERT INTO historique_statut_zone (zone_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-01-01 00:00:00'),
(2, 1, '2024-01-01 00:00:00'),
(3, 1, '2024-01-01 00:00:00'),
(4, 1, '2024-01-01 00:00:00'),
(5, 1, '2024-01-01 00:00:00');

-- Entités
INSERT INTO entites (nom) VALUES
('Restaurant'), ('Livreur'), ('Client'), ('Zone de livraison'), ('Commande');

-- Statuts entité
INSERT INTO statut_entite (appellation) VALUES
('Actif'), ('Inactif'), ('Suspendu'), ('En vérification');

-- Historique statut entité
INSERT INTO historique_statut_entite (entite_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-01-01 00:00:00'),
(2, 1, '2024-01-01 00:00:00'),
(3, 1, '2024-01-01 00:00:00'),
(4, 1, '2024-01-01 00:00:00'),
(5, 1, '2024-01-01 00:00:00');

-- Référence zone entité
INSERT INTO reference_zone_entite (zone_id, entite_id) VALUES
(1, 1), (1, 2), (1, 3),
(2, 1), (2, 2), (2, 3),
(3, 1), (3, 2), (3, 3),
(4, 1), (4, 2), (4, 3),
(5, 1), (5, 2), (5, 3);

-- Modes de paiement
INSERT INTO mode_de_paiement (nom) VALUES
('Espèces'), ('Mobile Money'), ('Carte bancaire'), ('Virement');

-- Commande paiement
INSERT INTO commande_paiement (paiement_id, ajouter_le) VALUES
(1, '2024-04-01 12:30:00'),
(2, '2024-04-01 13:15:00'),
(3, '2024-04-01 18:45:00'),
(1, '2024-04-02 11:20:00'),
(2, '2024-04-02 12:45:00'),
(3, '2024-04-02 19:30:00'),
(4, '2024-04-03 10:15:00'),
(1, '2024-04-03 13:00:00'),
(2, '2024-04-03 20:00:00'),
(3, '2024-04-04 12:30:00'),
(4, '2024-04-04 14:45:00'),
(1, '2024-04-04 19:15:00'),
(2, '2024-04-05 11:00:00'),
(3, '2024-04-05 13:30:00'),
(4, '2024-04-05 18:45:00'),
(1, '2024-04-06 12:15:00'),
(2, '2024-04-06 14:30:00'),
(3, '2024-04-06 20:00:00'),
(4, '2024-04-07 11:45:00'),
(1, '2024-04-07 13:15:00');

-- Disponibilité des repas
INSERT INTO disponibilite_repas (repas_id, est_dispo, mis_a_jour_le) VALUES
(1, TRUE, '2024-04-01 00:00:00'),
(2, TRUE, '2024-04-01 00:00:00'),
(3, TRUE, '2024-04-01 00:00:00'),
(4, TRUE, '2024-04-01 00:00:00'),
(5, TRUE, '2024-04-01 00:00:00'),
(6, TRUE, '2024-04-01 00:00:00'),
(7, TRUE, '2024-04-01 00:00:00'),
(8, TRUE, '2024-04-01 00:00:00'),
(9, TRUE, '2024-04-01 00:00:00'),
(10, TRUE, '2024-04-01 00:00:00'),
(11, TRUE, '2024-04-01 00:00:00'),
(12, TRUE, '2024-04-01 00:00:00'),
(13, TRUE, '2024-04-01 00:00:00'),
(14, TRUE, '2024-04-01 00:00:00'),
(15, TRUE, '2024-04-01 00:00:00'),
(16, TRUE, '2024-04-01 00:00:00'),
(17, TRUE, '2024-04-01 00:00:00'),
(18, TRUE, '2024-04-01 00:00:00'),
(19, TRUE, '2024-04-01 00:00:00'),
(20, TRUE, '2024-04-01 00:00:00');

-- Promotions
INSERT INTO promotions (repas_id, pourcentage_reduction, date_concerne) VALUES
(1, 10, '2024-04-15'),
(3, 15, '2024-04-16'),
(5, 20, '2024-04-17'),
(7, 10, '2024-04-18'),
(9, 15, '2024-04-19'),
(11, 20, '2024-04-20'),
(13, 10, '2024-04-21'),
(15, 15, '2024-04-22'),
(17, 20, '2024-04-23'),
(19, 10, '2024-04-24');

-- Statuts livraison
INSERT INTO statut_livraison (appellation) VALUES
('Attribuée'), ('En cours'), ('Livrée'), ('Retardée'), ('Annulée');

-- Livraisons
INSERT INTO livraisons (livreur_id, commande_id, attribue_le) VALUES
(1, 1, '2024-04-01 12:45:00'),
(2, 2, '2024-04-01 13:30:00'),
(3, 3, '2024-04-01 19:00:00'),
(4, 4, '2024-04-02 11:35:00'),
(5, 5, '2024-04-02 13:00:00'),
(1, 6, '2024-04-02 19:45:00'),
(2, 7, '2024-04-03 10:30:00'),
(3, 8, '2024-04-03 13:15:00'),
(4, 9, '2024-04-03 20:15:00'),
(5, 10, '2024-04-04 12:45:00'),
(1, 11, '2024-04-04 15:00:00'),
(2, 12, '2024-04-04 19:30:00'),
(3, 13, '2024-04-05 11:15:00'),
(4, 14, '2024-04-05 13:45:00'),
(5, 15, '2024-04-05 19:00:00'),
(1, 16, '2024-04-06 12:30:00'),
(2, 17, '2024-04-06 14:45:00'),
(3, 18, '2024-04-06 20:15:00'),
(4, 19, '2024-04-07 12:00:00'),
(5, 20, '2024-04-07 13:30:00');

-- Historique statut livraison
INSERT INTO historique_statut_livraison (livraison_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-04-01 12:45:00'),
(2, 1, '2024-04-01 13:30:00'),
(3, 1, '2024-04-01 19:00:00'),
(4, 1, '2024-04-02 11:35:00'),
(5, 1, '2024-04-02 13:00:00'),
(6, 1, '2024-04-02 19:45:00'),
(7, 1, '2024-04-03 10:30:00'),
(8, 1, '2024-04-03 13:15:00'),
(9, 1, '2024-04-03 20:15:00'),
(10, 1, '2024-04-04 12:45:00'),
(11, 2, '2024-04-04 15:00:00'),
(12, 3, '2024-04-04 19:30:00'),
(13, 2, '2024-04-05 11:15:00'),
(14, 3, '2024-04-05 13:45:00'),
(15, 5, '2024-04-05 19:00:00'),
(16, 2, '2024-04-06 12:30:00'),
(17, 3, '2024-04-06 14:45:00'),
(18, 2, '2024-04-06 20:15:00'),
(19, 3, '2024-04-07 12:00:00'),
(20, 5, '2024-04-07 13:30:00');

-- Zones livreurs
INSERT INTO zones_livreurs (livreur_id, zone_id, mis_a_jour_le) VALUES
(1, 1, '2024-01-01 00:00:00'),
(1, 2, '2024-01-01 00:00:00'),
(2, 1, '2024-01-01 00:00:00'),
(2, 3, '2024-01-01 00:00:00'),
(3, 2, '2024-01-01 00:00:00'),
(3, 4, '2024-01-01 00:00:00'),
(4, 3, '2024-01-01 00:00:00'),
(4, 5, '2024-01-01 00:00:00'),
(5, 1, '2024-01-01 00:00:00'),
(5, 5, '2024-01-01 00:00:00');

-- Statuts restaurant
INSERT INTO statut_restaurant (appellation) VALUES
('Ouvert'), ('Fermé'), ('En congé'), ('Complet');

-- Historique statut restaurant
INSERT INTO historique_statut_restaurant (restaurant_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-04-01 08:00:00'),
(2, 1, '2024-04-01 08:00:00'),
(3, 1, '2024-04-01 08:00:00'),
(4, 1, '2024-04-01 08:00:00'),
(5, 1, '2024-04-01 08:00:00'),
(6, 1, '2024-04-01 08:00:00'),
(7, 1, '2024-04-01 08:00:00'),
(8, 1, '2024-04-01 08:00:00'),
(9, 1, '2024-04-01 08:00:00'),
(10, 1, '2024-04-01 08:00:00');

-- Commissions
INSERT INTO commissions (restaurant_id, valeur, mis_a_jour_le) VALUES
(1, 15, '2024-01-01 00:00:00'),
(2, 15, '2024-01-01 00:00:00'),
(3, 20, '2024-01-01 00:00:00'),
(4, 15, '2024-01-01 00:00:00'),
(5, 10, '2024-01-01 00:00:00'),
(6, 20, '2024-01-01 00:00:00'),
(7, 15, '2024-01-01 00:00:00'),
(8, 10, '2024-01-01 00:00:00'),
(9, 15, '2024-01-01 00:00:00'),
(10, 20, '2024-01-01 00:00:00');

-- Limite commandes journalières
INSERT INTO limite_commandes_journalieres (nombre_commandes, date) VALUES
(100, '2024-04-01'),
(100, '2024-04-02'),
(100, '2024-04-03'),
(100, '2024-04-04'),
(100, '2024-04-05'),
(100, '2024-04-06'),
(100, '2024-04-07'),
(100, '2024-04-08'),
(100, '2024-04-09'),
(100, '2024-04-10');

-- Horaires réguliers
INSERT INTO horaire (restaurant_id, le_jour, horaire_debut, horaire_fin) VALUES
-- Burger Queen Tana (1)
(1, 1, '08:00:00', '20:00:00'),
(1, 2, '08:00:00', '20:00:00'),
(1, 3, '08:00:00', '20:00:00'),
(1, 4, '08:00:00', '20:00:00'),
(1, 5, '08:00:00', '20:00:00'),
(1, 6, '09:00:00', '18:00:00'),
(1, 7, '10:00:00', '15:00:00'),

-- Pizza Tana (2)
(2, 1, '07:00:00', '22:00:00'),
(2, 2, '07:00:00', '22:00:00'),
(2, 3, '07:00:00', '22:00:00'),
(2, 4, '07:00:00', '22:00:00'),
(2, 5, '07:00:00', '22:00:00'),
(2, 6, '08:00:00', '23:00:00'),
(2, 7, '08:00:00', '22:00:00'),

-- Sakura Sushi (3)
(3, 1, '06:00:00', '20:00:00'),
(3, 2, '06:00:00', '20:00:00'),
(3, 3, '06:00:00', '20:00:00'),
(3, 4, '06:00:00', '20:00:00'),
(3, 5, '06:00:00', '20:00:00'),
(3, 6, '07:00:00', '19:00:00'),
(3, 7, '08:00:00', '18:00:00'),

-- La Saladerie (4)
(4, 1, '05:00:00', '18:00:00'),
(4, 2, '05:00:00', '18:00:00'),
(4, 3, '05:00:00', '18:00:00'),
(4, 4, '05:00:00', '18:00:00'),
(4, 5, '05:00:00', '18:00:00'),
(4, 6, '06:00:00', '16:00:00'),
(4, 7, '07:00:00', '15:00:00'),

-- Pasta Mia (5)
(5, 1, '08:00:00', '20:00:00'),
(5, 2, '08:00:00', '20:00:00'),
(5, 3, '08:00:00', '20:00:00'),
(5, 4, '08:00:00', '20:00:00'),
(5, 5, '08:00:00', '20:00:00'),
(5, 6, '09:00:00', '19:00:00'),
(5, 7, '10:00:00', '18:00:00');

-- Horaires spéciaux (pour jours fériés)
INSERT INTO horaire_special (restaurant_id, date_concerne, horaire_debut, horaire_fin) VALUES
(1, '2024-04-08', '10:00:00', '16:00:00'), -- Lundi de Pâques
(2, '2024-04-08', '10:00:00', '18:00:00'),
(3, '2024-04-08', '09:00:00', '17:00:00'),
(4, '2024-04-08', '08:00:00', '15:00:00'),
(5, '2024-04-08', '09:00:00', '16:00:00'),
(1, '2024-05-01', '11:00:00', '15:00:00'), -- Fête du Travail
(2, '2024-05-01', '12:00:00', '18:00:00'),
(3, '2024-05-01', '10:00:00', '16:00:00'),
(4, '2024-05-01', '09:00:00', '14:00:00'),
(5, '2024-05-01', '10:00:00', '15:00:00');