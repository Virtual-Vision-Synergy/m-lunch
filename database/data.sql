-- insertion.sql
-- Données initiales pour l'application de livraison de repas
-- Tables statiques conservées intactes, autres tables sans accents

-- ======================
-- TABLES STATIQUES (non modifiées)
-- ======================

INSERT INTO core_typerepas (nom) VALUES
('Plat principal'),
('Entrée'),
('Dessert'),
('Boisson'),
('Spécialité malgache');

INSERT INTO core_statutcommande (appellation) VALUES
('En attente'),
('En cours'),
('Livrée'),
('Annulée');

INSERT INTO core_statutlivraison (appellation) VALUES
('En attente'),
('En cours'),
('Effectuée'),
('Annulée');

INSERT INTO core_statutlivreur (appellation) VALUES
('Disponible'),
('En livraison'),
('Inactif');

-- ======================
-- TABLES DYNAMIQUES (sans accents)
-- ======================

INSERT INTO core_statutrestaurant (appellation) VALUES
('Actif'),
('Inactif');

INSERT INTO core_statutzone (appellation) VALUES
('Active'),
('Inactive');

INSERT INTO core_modepaiement (nom) VALUES
('Especes'),
('Carte bancaire'),
('Mobile Money'),
('Virement');

INSERT INTO core_zone (nom, description, zone) VALUES
('Analakely', 'Centre-ville', 'POLYGON((47.5259 -18.9141, 47.5352 -18.9141, 47.5352 -18.9070, 47.5259 -18.9070, 47.5259 -18.9141))'),
('Andravoahangy', 'Zone commerciale', 'POLYGON((47.5330 -18.8950, 47.5430 -18.8950, 47.5430 -18.8880, 47.5330 -18.8880, 47.5330 -18.8950))'),
('Ankorondrano', 'Zone d''affaires', 'POLYGON((47.5210 -18.8830, 47.5310 -18.8830, 47.5310 -18.8750, 47.5210 -18.8750, 47.5210 -18.8830))'),
('Ivandry', 'Zone residentielle', 'POLYGON((47.5390 -18.8730, 47.5480 -18.8730, 47.5480 -18.8650, 47.5390 -18.8650, 47.5390 -18.8730))'),
('Ankadimbahoaka', 'Zone commerciale', 'POLYGON((47.5180 -18.9300, 47.5280 -18.9300, 47.5280 -18.9220, 47.5180 -18.9220, 47.5180 -18.9300))');

INSERT INTO core_client (email, mot_de_passe, contact, prenom, nom, date_inscri) VALUES
('jean.rakoto@example.com', 'pbkdf2_sha256$260000$abc123$def456ghi789=', '+261341234567', 'Jean', 'Rakoto', '2025-01-15 08:30:45'),
('marie.rasoa@example.com', 'pbkdf2_sha256$260000$xyz789$uvw456rst123=', '+261331234568', 'Marie', 'Rasoa', '2025-02-20 12:15:30'),
('pierre.rajaona@example.com', 'pbkdf2_sha256$260000$mno456$pqr789stu123=', '+261321234569', 'Pierre', 'Rajaona', '2025-03-05 14:45:22'),
('aina.rabesoa@example.com', 'pbkdf2_sha256$260000$jkl123$mno456pqr789=', '+261331234570', 'Aina', 'Rabesoa', '2025-03-18 09:20:15'),
('faly.andriamanana@example.com', 'pbkdf2_sha256$260000$def456$ghi789jkl123=', '+261341234571', 'Faly', 'Andriamanana', '2025-04-10 16:40:33'),
('sarah.randria@example.com', 'pbkdf2_sha256$260000$pqr789$stu123vwx456=', '+261331234572', 'Sarah', 'Randria', '2025-05-22 11:25:18'),
('tiana.raharimanana@example.com', 'pbkdf2_sha256$260000$vwx456$yz123abc789=', '+261321234573', 'Tiana', 'Raharimanana', '2025-06-08 17:50:42');

INSERT INTO core_restaurant (nom, adresse, description, image, geo_position) VALUES
('Le Carnivore', 'Avenue de l''Independance, Analakely', 'Specialiste des viandes grillees et plats malgaches', 'restaurant1.jpg', 'POINT(47.5310 -18.9120)'),
('La Varangue', 'Rue Rainitovo, Ankorondrano', 'Cuisine gastronomique francaise et malgache', 'restaurant2.jpg', 'POINT(47.5260 -18.8800)'),
('Sakamanga', 'Rue Dr Villette, Andravoahangy', 'Cuisine traditionnelle malgache dans un cadre chaleureux', 'restaurant3.jpg', 'POINT(47.5380 -18.8920)'),
('Pizza Mia', 'Rue Ratsimilaho, Ivandry', 'Pizzas artisanales et plats italiens', 'restaurant4.jpg', 'POINT(47.5420 -18.8700)'),
('Le Jardin', 'Avenue Ramanantsoa, Ankadimbahoaka', 'Cuisine fusion et plats vegetariens', 'restaurant5.jpg', 'POINT(47.5220 -18.9250)'),
('Chez Mariette', 'Rue Ravoahangy, Analakely', 'Petit restaurant familial specialise en fruits de mer', 'restaurant6.jpg', 'POINT(47.5290 -18.9100)'),
('Le Bistrot', 'Rue Patrice Lumumba, Ankorondrano', 'Bistrot francais avec terrasse', 'restaurant7.jpg', 'POINT(47.5240 -18.8780)');

INSERT INTO core_commission (restaurant_id, valeur, mis_a_jour_le) VALUES
(1, 10, '2025-01-01 00:00:00'),
(2, 12, '2025-01-01 00:00:00'),
(3, 15, '2025-01-01 00:00:00'),
(4, 10, '2025-01-01 00:00:00'),
(5, 8, '2025-01-01 00:00:00'),
(6, 12, '2025-01-01 00:00:00'),
(7, 10, '2025-01-01 00:00:00');

INSERT INTO core_horaire (restaurant_id, le_jour, horaire_debut, horaire_fin, mis_a_jour_le) VALUES
(1, 0, '11:00:00', '22:00:00', now()), (1, 1, '11:00:00', '22:00:00', now()),
(1, 2, '11:00:00', '22:00:00', now()), (1, 3, '11:00:00', '22:00:00', now()),
(1, 4, '11:00:00', '22:00:00', now()), (1, 5, '11:00:00', '23:00:00', now()),
(1, 6, '11:00:00', '23:00:00', now()),

(2, 0, '12:00:00', '14:30:00', now()), (2, 1, '12:00:00', '14:30:00', now()),
(2, 2, '12:00:00', '14:30:00', now()), (2, 3, '12:00:00', '14:30:00', now()),
(2, 4, '12:00:00', '14:30:00', now()), (2, 5, '12:00:00', '14:30:00', now()),
(2, 0, '19:00:00', '22:30:00', now()), (2, 1, '19:00:00', '22:30:00', now()),
(2, 2, '19:00:00', '22:30:00', now()), (2, 3, '19:00:00', '22:30:00', now()),
(2, 4, '19:00:00', '22:30:00', now()), (2, 5, '19:00:00', '23:00:00', now()),

(3, 0, '10:00:00', '22:00:00', now()), (3, 1, '10:00:00', '22:00:00', now()),
(3, 2, '10:00:00', '22:00:00', now()), (3, 3, '10:00:00', '22:00:00', now()),
(3, 4, '10:00:00', '22:00:00', now()), (3, 5, '10:00:00', '23:00:00', now()),
(3, 6, '10:00:00', '23:00:00', now()),

(4, 0, '11:30:00', '22:30:00', now()), (4, 1, '11:30:00', '22:30:00', now()),
(4, 2, '11:30:00', '22:30:00', now()), (4, 3, '11:30:00', '22:30:00', now()),
(4, 4, '11:30:00', '22:30:00', now()), (4, 5, '11:30:00', '23:30:00', now()),
(4, 6, '11:30:00', '23:30:00', now()),

(5, 0, '08:00:00', '16:00:00', now()), (5, 1, '08:00:00', '16:00:00', now()),
(5, 2, '08:00:00', '16:00:00', now()), (5, 3, '08:00:00', '16:00:00', now()),
(5, 4, '08:00:00', '16:00:00', now()),

(6, 1, '11:00:00', '22:00:00', now()), (6, 2, '11:00:00', '22:00:00', now()),
(6, 3, '11:00:00', '22:00:00', now()), (6, 4, '11:00:00', '22:00:00', now()),
(6, 5, '11:00:00', '23:00:00', now()), (6, 6, '11:00:00', '23:00:00', now()),

(7, 0, '07:00:00', '22:00:00', now()), (7, 1, '07:00:00', '22:00:00', now()),
(7, 2, '07:00:00', '22:00:00', now()), (7, 3, '07:00:00', '22:00:00', now()),
(7, 4, '07:00:00', '22:00:00', now()), (7, 5, '07:00:00', '23:00:00', now()),
(7, 6, '08:00:00', '22:00:00', now());

INSERT INTO core_horairespecial (restaurant_id, date_concerne, horaire_debut, horaire_fin, mis_a_jour_le) VALUES
(1, '2025-12-25', '18:00:00', '22:00:00', now()),
(2, '2025-12-31', '19:00:00', '01:00:00', now()),
(3, '2025-06-26', '12:00:00', '15:00:00', now()),
(4, '2025-04-20', '12:00:00', '22:00:00', now()),
(5, '2025-05-01', '10:00:00', '15:00:00', now());

INSERT INTO core_pointrecup (nom, geo_position) VALUES
('Analakely - Place de l''Independance', 'POINT(47.5290 -18.9100)'),
('Andravoahangy - Marche couvert', 'POINT(47.5380 -18.8900)'),
('Ankorondrano - Station Jovenna', 'POINT(47.5250 -18.8800)'),
('Ivandry - Centre commercial', 'POINT(47.5420 -18.8700)'),
('Ankadimbahoaka - Parking Shoprite', 'POINT(47.5200 -18.9250)'),
('Analakely - Gare routiere', 'POINT(47.5320 -18.9060)'),
('Ankorondrano - Galerie Zital', 'POINT(47.5230 -18.8750)');

INSERT INTO core_livreur (nom, contact, position, date_inscri) VALUES
('Rabe Andriamalala', '+261331234574', 'POINT(47.5300 -18.9110)', '2025-01-10 09:15:22'),
('Jean Rakotomalala', '+261341234575', 'POINT(47.5370 -18.8910)', '2025-01-15 14:30:45'),
('Marie Rasoanaivo', '+261321234576', 'POINT(47.5240 -18.8790)', '2025-02-05 11:20:33'),
('Paul Randriamampianina', '+261331234577', 'POINT(47.5410 -18.8710)', '2025-02-20 16:45:12'),
('Tiana Raharimalala', '+261341234578', 'POINT(47.5210 -18.9240)', '2025-03-08 08:10:56'),
('Faly Andrianarisoa', '+261331234579', 'POINT(47.5310 -18.9070)', '2025-03-22 13:25:41'),
('Solo Ramaroson', '+261321234580', 'POINT(47.5220 -18.8760)', '2025-04-05 17:50:19');

INSERT INTO core_repas (nom, prix, description, image, type_id) VALUES
('Ravitoto sy henakisoa', 15000, 'Feuilles de manioc pilees avec viande de porc', 'ravitoto.jpg', 1),
('Romazava', 12000, 'Bouillon de viande avec bredes malgaches', 'romazava.jpg', 1),
('Varanga', 18000, 'Viande de zebu mijotee avec legumes', 'varanga.jpg', 1),
('Poulet coco', 14000, 'Poulet cuit dans du lait de coco', 'poulet_coco.jpg', 1),
('Lasopy', 10000, 'Soupe de legumes malgache', 'lasopy.jpg', 1),
('Brochettes de zebu', 8000, 'Brochettes de viande de zebu grillee', 'brochette_zebu.jpg', 1),
('Pizza malgache', 20000, 'Pizza garnie de produits locaux', 'pizza_malgache.jpg', 1),
('Hamburger zebu', 16000, 'Burger avec steak de zebu', 'burger_zebu.jpg', 1),

('Samoussa', 3000, 'Beignets triangulaires farcis', 'samoussa.jpg', 2),
('Nem', 3500, 'Rouleaux de printemps frits', 'nem.jpg', 2),
('Salade malgache', 7000, 'Salade de legumes frais', 'salade_malgache.jpg', 2),
('Soupe de crevettes', 9000, 'Soupe a base de crevettes fraiches', 'soupe_crevette.jpg', 2),

('Mofo gasy', 2000, 'Petits gateaux de riz', 'mofo_gasy.jpg', 3),
('Koba', 3000, 'Gateau a base de banane et cacahuetes', 'koba.jpg', 3),
('Bonbon coco', 2500, 'Confiserie a base de noix de coco', 'bonbon_coco.jpg', 3),
('Glace artisanale', 5000, 'Glace faite maison parfum vanille', 'glace_vanille.jpg', 3),

('THB Pilsener', 4000, 'Biere locale', 'thb_pilsener.jpg', 4),
('Ranona', 2000, 'Jus de canne a sucre', 'ranona.jpg', 4),
('Jus de litchi', 3500, 'Jus de fruit frais', 'jus_litchi.jpg', 4),
('Eau minerale', 1500, 'Eau en bouteille', 'eau.jpg', 4),

('Akoho sy voanio', 13000, 'Poulet au coco', 'akoho_voanio.jpg', 5),
('Vary amin''anana', 10000, 'Riz aux bredes', 'vary_anana.jpg', 5),
('Kitoza', 9000, 'Viande sechee de zebu', 'kitoza.jpg', 5),
('Ravitoto voatabia', 16000, 'Ravitoto avec tomate', 'ravitoto_voatabia.jpg', 5);

-- DISPONIBILITE REPAS
INSERT INTO core_disponibiliterepas (repas_id, est_dispo, mis_a_jour_le) VALUES
(1, TRUE, now()), (2, TRUE, now()), (3, TRUE, now()), (4, TRUE, now()), (5, TRUE, now()), (6, TRUE, now()),
(7, TRUE, now()), (8, TRUE, now()), (9, TRUE, now()), (10, TRUE, now()), (11, TRUE, now()), (12, TRUE, now()),
(13, TRUE, now()), (14, TRUE, now()), (15, TRUE, now()), (16, TRUE, now()), (17, TRUE, now()), (18, TRUE, now()),
(19, TRUE, now()), (20, TRUE, now()), (21, TRUE, now()), (22, TRUE, now()), (23, TRUE, now()), (24, TRUE, now());

INSERT INTO core_restaurantrepas (restaurant_id, repas_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 6), (1, 21), (1, 22), (1, 23), (1, 24), (1, 17), (1, 19),
(2, 3), (2, 4), (2, 5), (2, 7), (2, 8), (2, 11), (2, 12), (2, 16), (2, 17), (2, 19), (2, 20),
(3, 1), (3, 2), (3, 5), (3, 6), (3, 9), (3, 10), (3, 13), (3, 14), (3, 15), (3, 18), (3, 19), (3, 21), (3, 22), (3, 24),
(4, 7), (4, 8), (4, 9), (4, 10), (4, 11), (4, 16), (4, 17), (4, 19), (4, 20),
(5, 4), (5, 5), (5, 7), (5, 8), (5, 11), (5, 12), (5, 16), (5, 19), (5, 20),
(6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 12), (6, 17), (6, 19), (6, 20), (6, 21), (6, 22), (6, 24),
(7, 3), (7, 4), (7, 5), (7, 7), (7, 8), (7, 11), (7, 12), (7, 16), (7, 17), (7, 19), (7, 20);

INSERT INTO core_commande (client_id, point_recup_id, cree_le, mode_paiement_id) VALUES
(1, 1, '2025-06-01 12:30:45', 1),
(2, 2, '2025-06-01 13:15:22', 2),
(3, 3, '2025-06-02 11:45:33', 3),
(4, 4, '2025-06-02 14:20:15', 1),
(5, 5, '2025-06-03 12:10:42', 2),
(6, 6, '2025-06-03 13:25:18', 3),
(7, 7, '2025-06-04 11:30:56', 1),
(1, 1, '2025-06-04 13:45:27', 2),
(2, 2, '2025-06-05 12:15:39', 3),
(3, 3, '2025-06-05 14:30:12', 1),
(4, 4, '2025-06-06 12:40:48', 2),
(5, 5, '2025-06-06 13:55:23', 3),
(6, 6, '2025-06-07 11:20:17', 1),
(7, 7, '2025-06-07 14:10:35', 2),
(1, 1, '2025-06-08 12:50:42', 3);

INSERT INTO core_commanderepas (commande_id, repas_id, quantite, ajoute_le) VALUES
(1, 1, 2, '2025-06-01 12:31:00'), (1, 17, 2, '2025-06-01 12:31:05'), (1, 13, 3, '2025-06-01 12:31:10'),
(2, 3, 1, '2025-06-01 13:16:00'), (2, 19, 1, '2025-06-01 13:16:05'), (2, 15, 2, '2025-06-01 13:16:10'),
(3, 7, 1, '2025-06-02 11:46:00'), (3, 9, 3, '2025-06-02 11:46:05'), (3, 20, 2, '2025-06-02 11:46:10'),
(4, 2, 2, '2025-06-02 14:21:00'), (4, 18, 2, '2025-06-02 14:21:05'), (4, 14, 1, '2025-06-02 14:21:10'),
(5, 4, 1, '2025-06-03 12:11:00'), (5, 6, 4, '2025-06-03 12:11:05'), (5, 17, 2, '2025-06-03 12:11:10'),
(6, 8, 2, '2025-06-03 13:26:00'), (6, 10, 2, '2025-06-03 13:26:05'), (6, 16, 1, '2025-06-03 13:26:10'),
(7, 5, 1, '2025-06-04 11:31:00'), (7, 12, 1, '2025-06-04 11:31:05'), (7, 19, 1, '2025-06-04 11:31:10'),
(8, 21, 1, '2025-06-04 13:46:00'), (8, 22, 1, '2025-06-04 13:46:05'), (8, 18, 2, '2025-06-04 13:46:10'),
(9, 23, 2, '2025-06-05 12:16:00'), (9, 24, 1, '2025-06-05 12:16:05'), (9, 17, 1, '2025-06-05 12:16:10'),
(10, 1, 1, '2025-06-05 14:31:00'), (10, 2, 1, '2025-06-05 14:31:05'), (10, 13, 2, '2025-06-05 14:31:10'),
(11, 3, 1, '2025-06-06 12:41:00'), (11, 4, 1, '2025-06-06 12:41:05'), (11, 20, 2, '2025-06-06 12:41:10'),
(12, 7, 1, '2025-06-06 13:56:00'), (12, 8, 1, '2025-06-06 13:56:05'), (12, 16, 1, '2025-06-06 13:56:10'),
(13, 5, 1, '2025-06-07 11:21:00'), (13, 6, 2, '2025-06-07 11:21:05'), (13, 17, 1, '2025-06-07 11:21:10'),
(14, 9, 3, '2025-06-07 14:11:00'), (14, 10, 2, '2025-06-07 14:11:05'), (14, 19, 1, '2025-06-07 14:11:10'),
(15, 21, 1, '2025-06-08 12:51:00'), (15, 22, 1, '2025-06-08 12:51:05'), (15, 18, 2, '2025-06-08 12:51:10');

INSERT INTO core_livraison (commande_id, livreur_id, attribue_le) VALUES
(1, 1, '2025-06-01 12:40:00'),
(2, 2, '2025-06-01 13:25:00'),
(3, 3, '2025-06-02 12:00:00'),
(4, 4, '2025-06-02 14:30:00'),
(5, 5, '2025-06-03 12:20:00'),
(6, 6, '2025-06-03 13:35:00'),
(7, 1, '2025-06-04 11:40:00'),
(8, 2, '2025-06-04 13:55:00'),
(9, 4, '2025-06-05 12:25:00'),
(10, 5, '2025-06-05 14:40:00'),
(11, 6, '2025-06-06 12:50:00'),
(12, 1, '2025-06-06 14:05:00'),
(13, 2, '2025-06-07 11:30:00'),
(14, 4, '2025-06-07 14:20:00'),
(15, 5, '2025-06-08 13:00:00');

INSERT INTO core_historiquestatutcommande (commande_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2025-06-01 12:31:00'), (1, 2, '2025-06-01 12:40:00'), (1, 3, '2025-06-01 13:15:00'),
(2, 1, '2025-06-01 13:16:00'), (2, 2, '2025-06-01 13:25:00'), (2, 3, '2025-06-01 14:00:00'),
(3, 1, '2025-06-02 11:46:00'), (3, 2, '2025-06-02 12:00:00'), (3, 3, '2025-06-02 12:45:00'),
(4, 1, '2025-06-02 14:21:00'), (4, 2, '2025-06-02 14:30:00'), (4, 3, '2025-06-02 15:15:00'),
(5, 1, '2025-06-03 12:11:00'), (5, 2, '2025-06-03 12:20:00'), (5, 3, '2025-06-03 13:05:00'),
(6, 1, '2025-06-03 13:26:00'), (6, 2, '2025-06-03 13:35:00'), (6, 3, '2025-06-03 14:20:00'),
(7, 1, '2025-06-04 11:31:00'), (7, 2, '2025-06-04 11:40:00'), (7, 3, '2025-06-04 12:25:00'),
(8, 1, '2025-06-04 13:46:00'), (8, 2, '2025-06-04 13:55:00'), (8, 3, '2025-06-04 14:40:00'),
(9, 1, '2025-06-05 12:16:00'), (9, 2, '2025-06-05 12:25:00'), (9, 3, '2025-06-05 13:10:00'),
(10, 1, '2025-06-05 14:31:00'), (10, 2, '2025-06-05 14:40:00'), (10, 3, '2025-06-05 15:25:00'),
(11, 1, '2025-06-06 12:41:00'), (11, 2, '2025-06-06 12:50:00'), (11, 3, '2025-06-06 13:35:00'),
(12, 1, '2025-06-06 13:56:00'), (12, 2, '2025-06-06 14:05:00'), (12, 3, '2025-06-06 14:50:00'),
(13, 1, '2025-06-07 11:21:00'), (13, 2, '2025-06-07 11:30:00'), (13, 3, '2025-06-07 12:15:00'),
(14, 1, '2025-06-07 14:11:00'), (14, 2, '2025-06-07 14:20:00'), (14, 3, '2025-06-07 15:05:00'),
(15, 1, '2025-06-08 12:51:00'), (15, 2, '2025-06-08 13:00:00'), (15, 3, '2025-06-08 13:45:00');

INSERT INTO core_historiquestatutlivraison (livraison_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2025-06-01 12:40:00'), (1, 2, '2025-06-01 12:45:00'), (1, 3, '2025-06-01 13:15:00'),
(2, 1, '2025-06-01 13:25:00'), (2, 2, '2025-06-01 13:30:00'), (2, 3, '2025-06-01 14:00:00'),
(3, 1, '2025-06-02 12:00:00'), (3, 2, '2025-06-02 12:05:00'), (3, 3, '2025-06-02 12:45:00'),
(4, 1, '2025-06-02 14:30:00'), (4, 2, '2025-06-02 14:35:00'), (4, 3, '2025-06-02 15:15:00'),
(5, 1, '2025-06-03 12:20:00'), (5, 2, '2025-06-03 12:25:00'), (5, 3, '2025-06-03 13:05:00'),
(6, 1, '2025-06-03 13:35:00'), (6, 2, '2025-06-03 13:40:00'), (6, 3, '2025-06-03 14:20:00'),
(7, 1, '2025-06-04 11:40:00'), (7, 2, '2025-06-04 11:45:00'), (7, 3, '2025-06-04 12:25:00'),
(8, 1, '2025-06-04 13:55:00'), (8, 2, '2025-06-04 14:00:00'), (8, 3, '2025-06-04 14:40:00'),
(9, 1, '2025-06-05 12:25:00'), (9, 2, '2025-06-05 12:30:00'), (9, 3, '2025-06-05 13:10:00'),
(10, 1, '2025-06-05 14:40:00'), (10, 2, '2025-06-05 14:45:00'), (10, 3, '2025-06-05 15:25:00'),
(11, 1, '2025-06-06 12:50:00'), (11, 2, '2025-06-06 12:55:00'), (11, 3, '2025-06-06 13:35:00'),
(12, 1, '2025-06-06 14:05:00'), (12, 2, '2025-06-06 14:10:00'), (12, 3, '2025-06-06 14:50:00'),
(13, 1, '2025-06-07 11:30:00'), (13, 2, '2025-06-07 11:35:00'), (13, 3, '2025-06-07 12:15:00'),
(14, 1, '2025-06-07 14:20:00'), (14, 2, '2025-06-07 14:25:00'), (14, 3, '2025-06-07 15:05:00'),
(15, 1, '2025-06-08 13:00:00'), (15, 2, '2025-06-08 13:05:00'), (15, 3, '2025-06-08 13:45:00');

INSERT INTO core_historiquestatutrestaurant (restaurant_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2025-01-01 00:00:00'),
(2, 1, '2025-01-01 00:00:00'),
(3, 1, '2025-01-01 00:00:00'),
(4, 1, '2025-01-01 00:00:00'),
(5, 1, '2025-01-01 00:00:00'),
(6, 1, '2025-01-01 00:00:00'),
(7, 1, '2025-01-01 00:00:00');

INSERT INTO core_historiquestatutzone (zone_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2025-01-01 00:00:00'),
(2, 1, '2025-01-01 00:00:00'),
(3, 1, '2025-01-01 00:00:00'),
(4, 1, '2025-01-01 00:00:00'),
(5, 1, '2025-01-01 00:00:00');

INSERT INTO core_zoneclient (client_id, zone_id) VALUES
(1, 1), (1, 3),
(2, 2), (2, 4),
(3, 3), (3, 5),
(4, 4),
(5, 5),
(6, 1), (6, 2),
(7, 3), (7, 4);

INSERT INTO core_zonelivreur (zone_id, livreur_id) VALUES
(1, 1), (1, 6),
(2, 2), (2, 6),
(3, 3), (3, 7),
(4, 4), (4, 7),
(5, 5);

INSERT INTO core_zonerestaurant (restaurant_id, zone_id) VALUES
(1, 1),
(2, 3),
(3, 2),
(4, 4),
(5, 5),
(6, 1),
(7, 3);

INSERT INTO core_promotion (repas_id, pourcentage_reduction, date_concerne) VALUES
(1, 20, '2025-06-26'),
(2, 15, '2025-06-26'),
(17, 10, '2025-06-26'),
(7, 25, '2025-12-25'),
(8, 20, '2025-12-25'),
(16, 15, '2025-12-25'),
(4, 10, '2025-05-01'),
(6, 15, '2025-05-01'),
(19, 10, '2025-05-01');

INSERT INTO core_limitecommandesjournalieres (nombre_commandes, date) VALUES
(50, '2025-06-26'),
(30, '2025-12-25'),
(40, '2025-12-31'),
(35, '2025-05-01');