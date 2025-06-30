-- Status tables data
INSERT INTO core_statutcommande (appellation) VALUES
('En attente'), ('En cours'), ('Livree');

INSERT INTO core_statutlivraison (appellation) VALUES
('Effectuee'), ('En cours'), ('Annulee');

INSERT INTO core_statutlivreur (appellation) VALUES
('Disponible'), ('En livraison'), ('Inactif');

INSERT INTO core_statutrestaurant (appellation) VALUES
('Actif'), ('Inactif');

INSERT INTO core_statutzone (appellation) VALUES
('Active'), ('Inactive');

-- Meal types
INSERT INTO core_typerepas (nom) VALUES
('Plat principal'), ('Entrée'), ('Dessert'), ('Boisson'), ('Spécialité malgache');

-- Zones
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

-- Zone-Restaurant
INSERT INTO core_zonerestaurant (zone_id, restaurant_id) VALUES
(1, 1), (1, 4), (2, 2), (3, 3), (4, 5), (5, 2);

-- Restaurant status
INSERT INTO core_historiquestatutrestaurant (restaurant_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2025-06-29 10:00:00'),
(2, 1, '2025-06-29 09:30:00'),
(3, 1, '2025-06-29 11:00:00'),
(4, 2, '2025-06-29 22:00:00'),
(5, 1, '2025-06-29 08:45:00');

-- Meals
INSERT INTO core_repas (nom, prix, description, image, type_id) VALUES
('Ravitoto sy Hena-kisoa', 12000, 'Plat traditionnel malgache à base de feuilles de manioc et de porc', 'ravitoto.jpg', 5),
('Romazava', 10000, 'Bouillon de viande de zébu aux brèdes', 'romazava.jpg', 5),
('Burger Gasy', 15000, 'Burger avec steak de zébu', 'burger_gasy.jpg', 1),
('Mofo Gasy', 4000, 'Gâteau traditionnel malgache', 'mofo_gasy.jpg', 3),
('Pizza Fruits de Mer', 22000, 'Pizza aux fruits de mer frais', 'pizza_mer.jpg', 1),
('THB', 5000, 'Bière locale Three Horses Beer', 'thb.jpg', 4),
('Salade Malagasy', 8000, 'Salade fraîche aux légumes locaux', 'salade_malagasy.jpg', 2);

-- Restaurant-Meal
INSERT INTO core_restaurantrepas (restaurant_id, repas_id) VALUES
(1, 1), (1, 2), (1, 6),
(2, 1), (2, 2), (2, 4), (2, 6),
(3, 3), (3, 5), (3, 7), (3, 6),
(4, 3), (4, 4), (4, 6),
(5, 5), (5, 7), (5, 6);

-- Pickup points (sans adresse)
INSERT INTO core_pointrecup (nom) VALUES
('Analakely Centre'),
('Andravoahangy Marche'),
('Station Jovenna'),
('Shoprite'),
('Ivandry Centre');

-- Clients
INSERT INTO core_client (email, mot_de_passe, contact, prenom, nom, date_inscri) VALUES
('rakoto@example.com', '123456', '+261341234567', 'Jean', 'Rakoto', '2025-06-01 14:23:45'),
('rasoa@example.com', '123456', '+261331234568', 'Marie', 'Rasoa', '2025-06-05 09:12:36'),
('rajaona@example.com', 'pbkdf2_sha256$...hWXqp4EVu...', '+261321234569', 'Pierre', 'Rajaona', '2025-06-10 16:45:23'),
('aina@example.com', 'pbkdf2_sha256$...JDJJv1KB...', '+261331234570', 'Aina', 'Rabesoa', '2025-06-12 11:34:12'),
('faly@example.com', 'pbkdf2_sha256$...WpueB3uK...', '+261341234571', 'Faly', 'Andriamanana', '2025-06-15 08:23:56');

-- Zone-Client
INSERT INTO core_zoneclient (client_id, zone_id) VALUES
(1, 1), (1, 3), (2, 2), (3, 4), (4, 5), (5, 1);

-- Livreurs
INSERT INTO core_livreur (nom, contact, position, date_inscri) VALUES
('Rabe', '+261331234572', 'POINT(47.5300 -18.9100)', '2025-05-15 09:45:12'),
('Nirina', '+261341234573', 'POINT(47.5350 -18.8920)', '2025-05-20 14:23:45'),
('Mamy', '+261321234574', 'POINT(47.5250 -18.8810)', '2025-05-25 10:34:56'),
('Solo', '+261331234575', 'POINT(47.5420 -18.8710)', '2025-05-28 08:12:23');

-- Livreurs statut
INSERT INTO core_historiquestatutlivreur (livreur_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2025-06-29 08:00:00'),
(2, 2, '2025-06-29 12:15:00'),
(3, 1, '2025-06-29 09:30:00'),
(4, 3, '2025-06-29 16:45:00');

-- Commandes
INSERT INTO core_commande (client_id, point_recup_id, cree_le) VALUES
(1, 1, '2025-06-29 12:30:45'),
(2, 2, '2025-06-29 13:15:23'),
(3, 3, '2025-06-29 14:45:12'),
(4, 4, '2025-06-29 15:20:56'),
(5, 1, '2025-06-29 16:10:34');

-- Historique commandes
INSERT INTO core_historiquestatutcommande (commande_id, statut_id, mis_a_jour_le) VALUES
(1, 2, '2025-06-29 12:35:45'),
(2, 3, '2025-06-29 13:20:23'),
(3, 1, '2025-06-29 14:45:12'),
(4, 1, '2025-06-29 15:40:56'),
(5, 2, '2025-06-29 16:15:34');

-- Détails des commandes (sans prix_unitaire)
INSERT INTO core_commanderepas (commande_id, repas_id, quantite) VALUES
(1, 1, 2), (1, 6, 2),
(2, 2, 1), (2, 4, 2),
(3, 3, 2), (3, 6, 3),
(4, 5, 1), (4, 7, 1),
(5, 1, 1), (5, 2, 1), (5, 6, 2);

-- Livraisons
INSERT INTO core_livraison (commande_id, livreur_id, attribue_le) VALUES
(1, 1, '2025-06-29 12:40:00'),
(2, 2, '2025-06-29 13:25:00'),
(3, 3, '2025-06-29 15:45:00');

-- Statut livraison
INSERT INTO core_historiquestatutlivraison (livraison_id, statut_id, mis_a_jour_le) VALUES
(1, 2, '2025-06-29 12:55:00'),
(2, 2, '2025-06-29 13:40:00'),
(3, 3, '2025-06-29 16:20:00');

-- Statut des zones
INSERT INTO core_historiquestatutzone (zone_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2025-06-01 08:00:00'),
(2, 1, '2025-06-01 08:00:00'),
(3, 1, '2025-06-01 08:00:00'),
(4, 1, '2025-06-01 08:00:00'),
(5, 1, '2025-06-01 08:00:00');

-- Horaire régulier pour chaque restaurant (lundi à samedi, 8h à 20h)
INSERT INTO core_horaire (restaurant_id, le_jour, horaire_debut, horaire_fin, mis_a_jour_le) VALUES
-- Le Carnivore
(1, 0, '08:00', '20:00', now()), (1, 1, '08:00', '20:00', now()), (1, 2, '08:00', '20:00', now()),
(1, 3, '08:00', '20:00', now()), (1, 4, '08:00', '20:00', now()), (1, 5, '08:00', '20:00', now()),

-- Sakamanga
(2, 0, '09:00', '21:00', now()), (2, 1, '09:00', '21:00', now()), (2, 2, '09:00', '21:00', now()),
(2, 3, '09:00', '21:00', now()), (2, 4, '09:00', '21:00', now()), (2, 5, '09:00', '21:00', now()),

-- La Varangue
(3, 0, '10:00', '22:00', now()), (3, 1, '10:00', '22:00', now()), (3, 2, '10:00', '22:00', now()),
(3, 3, '10:00', '22:00', now()), (3, 4, '10:00', '22:00', now()), (3, 5, '10:00', '22:00', now()),

-- Café de la Gare
(4, 0, '07:00', '19:00', now()), (4, 1, '07:00', '19:00', now()), (4, 2, '07:00', '19:00', now()),
(4, 3, '07:00', '19:00', now()), (4, 4, '07:00', '19:00', now()), (4, 5, '07:00', '19:00', now()),

-- Pizza Paradiso
(5, 0, '11:00', '23:00', now()), (5, 1, '11:00', '23:00', now()), (5, 2, '11:00', '23:00', now()),
(5, 3, '11:00', '23:00', now()), (5, 4, '11:00', '23:00', now()), (5, 5, '11:00', '23:00', now());
