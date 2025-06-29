-- Status tables data
INSERT INTO core_statutcommande (nom) VALUES
('En attente'), ('Confirmée'), ('Préparation'), ('Prête'), ('Annulée');

INSERT INTO core_statutlivraison (nom) VALUES
('Attribuée'), ('En cours'), ('Livrée'), ('Annulée');

INSERT INTO core_statutlivreur (nom) VALUES
('Disponible'), ('En livraison'), ('Indisponible');

INSERT INTO core_statutrestaurant (nom) VALUES
('Ouvert'), ('Fermé'), ('En pause');

INSERT INTO core_statutzone (nom) VALUES
('Active'), ('Inactive'), ('Temporairement désactivée');

-- Meal types
INSERT INTO core_typerepas (nom) VALUES
('Plat principal'), ('Entrée'), ('Dessert'), ('Boisson'), ('Spécialité malgache');

-- Zones (with PostGIS data for Antananarivo districts)
INSERT INTO core_zone (nom, description, zone) VALUES
('Analakely', 'Centre-ville', 'POLYGON((47.5259 -18.9141, 47.5352 -18.9141, 47.5352 -18.9070, 47.5259 -18.9070, 47.5259 -18.9141))'),
('Andravoahangy', 'Zone commerciale', 'POLYGON((47.5330 -18.8950, 47.5430 -18.8950, 47.5430 -18.8880, 47.5330 -18.8880, 47.5330 -18.8950))'),
('Ankorondrano', 'Zone d''affaires', 'POLYGON((47.5210 -18.8830, 47.5310 -18.8830, 47.5310 -18.8750, 47.5210 -18.8750, 47.5210 -18.8830))'),
('Ivandry', 'Zone résidentielle', 'POLYGON((47.5390 -18.8730, 47.5480 -18.8730, 47.5480 -18.8650, 47.5390 -18.8650, 47.5390 -18.8730))'),
('Ankadimbahoaka', 'Zone commerciale', 'POLYGON((47.5180 -18.9300, 47.5280 -18.9300, 47.5280 -18.9220, 47.5180 -18.9220, 47.5180 -18.9300))');

-- Restaurants
INSERT INTO core_restaurant (nom, adresse, image, geo_position) VALUES
('Le Carnivore', 'Avenue de l''Indépendance, Analakely', 'carnivore.jpg', 'POINT(47.5310 -18.9120)'),
('Sakamanga', 'Rue Pasteur Raseta, Andravoahangy', 'sakamanga.jpg', 'POINT(47.5380 -18.8920)'),
('La Varangue', 'Rue Rainitovo, Ankorondrano', 'varangue.jpg', 'POINT(47.5260 -18.8800)'),
('Café de la Gare', 'Avenue de Madagascar, Soarano', 'cafe_gare.jpg', 'POINT(47.5320 -18.9060)'),
('Pizza Paradiso', 'Rue Ratsimilaho, Ivandry', 'pizza_paradiso.jpg', 'POINT(47.5420 -18.8700)');

-- Zone-Restaurant associations
INSERT INTO core_zonerestaurant (zone_id, restaurant_id) VALUES
(1, 1), (1, 4), (2, 2), (3, 3), (4, 5), (5, 2);

-- Restaurant status history
INSERT INTO core_historiquestatutrestaurant (restaurant_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2025-06-29 10:00:00'),
(2, 1, '2025-06-29 09:30:00'),
(3, 1, '2025-06-29 11:00:00'),
(4, 2, '2025-06-29 22:00:00'),
(5, 1, '2025-06-29 08:45:00');

-- Meals
INSERT INTO core_repas (nom, prix, description, image, est_dispo, type_id) VALUES
('Ravitoto sy Hena-kisoa', 12000, 'Plat traditionnel malgache à base de feuilles de manioc et de porc', 'ravitoto.jpg', true, 5),
('Romazava', 10000, 'Bouillon de viande de zébu aux brèdes', 'romazava.jpg', true, 5),
('Burger Gasy', 15000, 'Burger avec steak de zébu', 'burger_gasy.jpg', true, 1),
('Mofo Gasy', 4000, 'Gâteau traditionnel malgache', 'mofo_gasy.jpg', true, 3),
('Pizza Fruits de Mer', 22000, 'Pizza aux fruits de mer frais', 'pizza_mer.jpg', true, 1),
('THB', 5000, 'Bière locale Three Horses Beer', 'thb.jpg', true, 4),
('Salade Malagasy', 8000, 'Salade fraîche aux légumes locaux', 'salade_malagasy.jpg', true, 2);

-- Restaurant-Meal associations
INSERT INTO core_restaurantrepas (restaurant_id, repas_id, disponible) VALUES
(1, 1, true), (1, 2, true), (1, 6, true),
(2, 1, true), (2, 2, true), (2, 4, true), (2, 6, true),
(3, 3, true), (3, 5, true), (3, 7, true), (3, 6, true),
(4, 3, true), (4, 4, true), (4, 6, true),
(5, 5, true), (5, 7, true), (5, 6, true);

-- Pickup points
INSERT INTO core_pointrecup (nom, adresse) VALUES
('Analakely Centre', 'Avenue de l''Indépendance, Analakely'),
('Andravoahangy Marché', 'Rue Ratsimilaho, Andravoahangy'),
('Station Jovenna', 'Boulevard de l''Europe, Ankorondrano'),
('Shoprite', 'Route des Hydrocarbures, Ankorondrano'),
('Ivandry Centre', 'Rue du Dr Raharinosy, Ivandry');

-- Clients
INSERT INTO core_client (email, mot_de_passe, contact, prenom, nom, date_inscri) VALUES
('rakoto@example.com', 'pbkdf2_sha256$390000$XnzqLtCx7GDUctg3ui4h8A$3s2ncf+3+A43lnTn9lFaX7eMU89B9YMzOMUQhZxk5QI=', '+261341234567', 'Jean', 'Rakoto', '2025-06-01 14:23:45'),
('rasoa@example.com', 'pbkdf2_sha256$390000$ihQyPQarFczumo5S1HNmKR$4D4suFGC9JlI74DwXS+BMfYE5o+tuUqm5c7t9y7LvNM=', '+261331234568', 'Marie', 'Rasoa', '2025-06-05 09:12:36'),
('rajaona@example.com', 'pbkdf2_sha256$390000$QQbnXP9HCOm6m9qiV7MzCU$hWXqp4EVuGO2lDw66MUZMLmXRhbj/jyHld11mZMw2wM=', '+261321234569', 'Pierre', 'Rajaona', '2025-06-10 16:45:23'),
('aina@example.com', 'pbkdf2_sha256$390000$GhXpDvQCyNaxr7D4WHUtos$JDJJv1KByhP1yV9gXEep45POQZI2BGfvqs0yvXLi4qw=', '+261331234570', 'Aina', 'Rabesoa', '2025-06-12 11:34:12'),
('faly@example.com', 'pbkdf2_sha256$390000$Ax8vy2CAZlbzhBEp4JA9gC$WpueB3uKs7ZwhWwBsLQuSlIIp2pJjbYJKzSdHIM9TaA=', '+261341234571', 'Faly', 'Andriamanana', '2025-06-15 08:23:56');

-- Zone-Client associations
INSERT INTO core_zoneclient (client_id, zone_id) VALUES
(1, 1), (1, 3), (2, 2), (3, 4), (4, 5), (5, 1);

-- Deliverers
INSERT INTO core_livreur (nom, contact, position, date_inscri) VALUES
('Rabe', '+261331234572', 'POINT(47.5300 -18.9100)', '2025-05-15 09:45:12'),
('Nirina', '+261341234573', 'POINT(47.5350 -18.8920)', '2025-05-20 14:23:45'),
('Mamy', '+261321234574', 'POINT(47.5250 -18.8810)', '2025-05-25 10:34:56'),
('Solo', '+261331234575', 'POINT(47.5420 -18.8710)', '2025-05-28 08:12:23');

-- Deliverer status history
INSERT INTO core_historiquestatutlivreur (livreur_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2025-06-29 08:00:00'),
(2, 2, '2025-06-29 12:15:00'),
(3, 1, '2025-06-29 09:30:00'),
(4, 3, '2025-06-29 16:45:00');

-- Orders
INSERT INTO core_commande (client_id, point_recup_id, cree_le) VALUES
(1, 1, '2025-06-29 12:30:45'),
(2, 2, '2025-06-29 13:15:23'),
(3, 3, '2025-06-29 14:45:12'),
(4, 4, '2025-06-29 15:20:56'),
(5, 1, '2025-06-29 16:10:34');

-- Order statuses
INSERT INTO core_historiquestatutcommande (commande_id, statut_id, mis_a_jour_le) VALUES
(1, 2, '2025-06-29 12:35:45'),
(2, 3, '2025-06-29 13:20:23'),
(3, 1, '2025-06-29 14:45:12'),
(4, 4, '2025-06-29 15:40:56'),
(5, 2, '2025-06-29 16:15:34');

-- Order details
INSERT INTO core_commanderepas (commande_id, repas_id, quantite, prix_unitaire) VALUES
(1, 1, 2, 12000),
(1, 6, 2, 5000),
(2, 2, 1, 10000),
(2, 4, 2, 4000),
(3, 3, 2, 15000),
(3, 6, 3, 5000),
(4, 5, 1, 22000),
(4, 7, 1, 8000),
(5, 1, 1, 12000),
(5, 2, 1, 10000),
(5, 6, 2, 5000);

-- Deliveries
INSERT INTO core_livraison (commande_id, livreur_id, attribue_le) VALUES
(1, 1, '2025-06-29 12:40:00'),
(2, 2, '2025-06-29 13:25:00'),
(3, 3, '2025-06-29 15:45:00');

-- Delivery statuses
INSERT INTO core_historiquestatutlivraison (livraison_id, statut_id, mis_a_jour_le) VALUES
(1, 2, '2025-06-29 12:55:00'),
(2, 2, '2025-06-29 13:40:00'),
(3, 3, '2025-06-29 16:20:00');

-- Promotions
INSERT INTO core_promotion (repas_id, pourcentage_reduction, date_debut, date_fin) VALUES
(1, 15, '2025-06-25', '2025-07-05'),
(3, 10, '2025-06-28', '2025-07-10'),
(5, 20, '2025-07-01', '2025-07-15');

-- Zone status history
INSERT INTO core_historiquestatutzone (zone_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2025-06-01 08:00:00'),
(2, 1, '2025-06-01 08:00:00'),
(3, 1, '2025-06-01 08:00:00'),
(4, 1, '2025-06-01 08:00:00'),
(5, 1, '2025-06-01 08:00:00');
