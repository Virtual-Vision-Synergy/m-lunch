-- Script d'insertion des données de test pour M-Lunch - Antananarivo, Madagascar
-- PostgreSQL + PostGIS

-- 1. Statuts
INSERT INTO core_statutcommande (appellation) VALUES
('En attente'),
('Confirmée'),
('En préparation'),
('Prête'),
('En livraison'),
('Livrée'),
('Annulée');

INSERT INTO core_statutlivraison (appellation) VALUES
('Assignée'),
('En route vers restaurant'),
('Récupérée'),
('En route vers client'),
('Livrée'),
('Échec livraison');

INSERT INTO core_statutlivreur (appellation) VALUES
('Disponible'),
('Occupé'),
('En pause'),
('Hors service');

INSERT INTO core_statutrestaurant (appellation) VALUES
('Ouvert'),
('Fermé'),
('Fermé temporairement'),
('En maintenance');

INSERT INTO core_statutzone (appellation) VALUES
('Active'),
('Inactive'),
('En maintenance');

-- 2. Modes de paiement
INSERT INTO core_modepaiement (nom) VALUES
('Espèces'),
('Mobile Money'),
('Carte bancaire'),
('Virement');

-- 3. Zones d'Antananarivo
INSERT INTO core_zone (nom, description, zone) VALUES
('Analakely', 'Centre ville commercial', 'POLYGON((-18.9140 47.5205, -18.9150 47.5225, -18.9160 47.5215, -18.9150 47.5195, -18.9140 47.5205))'),
('Antsahamanitra', 'Quartier résidentiel', 'POLYGON((-18.9050 47.5180, -18.9070 47.5200, -18.9080 47.5190, -18.9060 47.5170, -18.9050 47.5180))'),
('Andravoahangy', 'Zone universitaire', 'POLYGON((-18.9200 47.5300, -18.9220 47.5320, -18.9230 47.5310, -18.9210 47.5290, -18.9200 47.5300))'),
('Tsaralalana', 'Quartier administratif', 'POLYGON((-18.9120 47.5240, -18.9140 47.5260, -18.9150 47.5250, -18.9130 47.5230, -18.9120 47.5240))'),
('Antaninarenina', 'Zone commerciale', 'POLYGON((-18.9180 47.5280, -18.9200 47.5300, -18.9210 47.5290, -18.9190 47.5270, -18.9180 47.5280))'),
('Isotry', 'Marché populaire', 'POLYGON((-18.9250 47.5150, -18.9270 47.5170, -18.9280 47.5160, -18.9260 47.5140, -18.9250 47.5150))'),
('Behoririka', 'Centre commercial', 'POLYGON((-18.9160 47.5220, -18.9180 47.5240, -18.9190 47.5230, -18.9170 47.5210, -18.9160 47.5220))'),
('Ambatonakanga', 'Quartier résidentiel', 'POLYGON((-18.9100 47.5320, -18.9120 47.5340, -18.9130 47.5330, -18.9110 47.5310, -18.9100 47.5320))');

-- 4. Points de récupération
INSERT INTO core_pointrecup (nom, geo_position) VALUES
('Analakely Market', '-18.9145,47.5210'),
('Université d''Antananarivo', '-18.9210,47.5305'),
('Gare Soarano', '-18.9135,47.5245'),
('Centre Commercial Tana Water Front', '-18.9175,47.5285'),
('Marché Isotry', '-18.9260,47.5155'),
('Behoririka Shopping', '-18.9170,47.5225'),
('Place de l''Indépendance', '-18.9125,47.5235'),
('Antsahamanitra Centre', '-18.9060,47.5185');

-- 5. Types de repas
INSERT INTO core_typerepas (nom) VALUES
('Plat principal'),
('Entrée'),
('Dessert'),
('Boisson'),
('Snack'),
('Menu complet');

-- 6. Restaurants d'Antananarivo
INSERT INTO core_restaurant (nom, adresse, description, image, geo_position) VALUES
('Chez Mariette', 'Analakely, près du marché', 'Restaurant traditionnel malgache, spécialités locales', 'mariette.jpg', '-18.9142,47.5212'),
('Le Sakamanga', 'Rue Rainitovo, Antaninarenina', 'Cuisine fusion malgache-française', 'sakamanga.jpg', '-18.9185,47.5285'),
('Restaurant Grillades', 'Andravoahangy', 'Spécialités grillades et zebu', 'grillades.jpg', '-18.9205,47.5295'),
('Café de la Gare', 'Soarano', 'Café et petite restauration', 'cafe_gare.jpg', '-18.9138,47.5248'),
('Tana Plaza Food Court', 'Behoririka', 'Court alimentaire moderne', 'tana_plaza.jpg', '-18.9172,47.5228'),
('Chez Lolo', 'Isotry', 'Cuisine populaire malgache', 'chez_lolo.jpg', '-18.9265,47.5158'),
('Villa Vanille', 'Tsaralalana', 'Restaurant gastronomique', 'villa_vanille.jpg', '-18.9125,47.5245'),
('Mama Afrika', 'Antsahamanitra', 'Spécialités africaines', 'mama_afrika.jpg', '-18.9065,47.5188');

-- 7. Repas malgaches typiques
INSERT INTO core_repas (nom, description, image, type_id, prix) VALUES
-- Plats principaux
('Romazava', 'Plat traditionnel malgache aux brèdes et viande de zébu', 'romazava.jpg', 1, 8000),
('Ravitoto sy henakisoa', 'Feuilles de manioc pilées avec porc', 'ravitoto.jpg', 1, 9000),
('Akoho sy voanio', 'Poulet au coco', 'akoho_voanio.jpg', 1, 12000),
('Hen''omby ritra', 'Viande de zébu grillée', 'henomby_ritra.jpg', 1, 15000),
('Lasary voatabia sy hen''akanga', 'Salade de haricots verts et pintade', 'lasary_voatabia.jpg', 1, 13000),
('Vary amin''anana', 'Riz aux légumes verts', 'vary_anana.jpg', 1, 6000),
('Poisson à la vanille', 'Poisson sauce vanille de Madagascar', 'poisson_vanille.jpg', 1, 18000),
('Koba', 'Gâteau traditionnel à base de riz et arachides', 'koba.jpg', 1, 5000),

-- Entrées
('Mofo gasy', 'Pain malgache traditionnel', 'mofo_gasy.jpg', 2, 2000),
('Sambos', 'Beignets farcis à la viande ou légumes', 'sambos.jpg', 2, 3000),
('Salade de palmiste', 'Salade de cœur de palmier', 'salade_palmiste.jpg', 2, 4000),
('Kitoza', 'Viande séchée malgache', 'kitoza.jpg', 2, 6000),

-- Desserts
('Koba akondro', 'Gâteau de banane et riz', 'koba_akondro.jpg', 3, 3000),
('Bonbon coco', 'Confiserie à la noix de coco', 'bonbon_coco.jpg', 3, 2500),
('Ramanonaka', 'Gâteau de riz gluant', 'ramanonaka.jpg', 3, 2000),

-- Boissons
('Ranonapango', 'Eau de riz grillé traditionnel', 'ranonapango.jpg', 4, 1500),
('Ranon''ampango', 'Thé de riz brûlé', 'ranon_ampango.jpg', 4, 1000),
('Litchi juice', 'Jus de litchi frais', 'litchi_juice.jpg', 4, 2500),
('Tamarind juice', 'Jus de tamarin', 'tamarind_juice.jpg', 4, 2000),
('Three Horses Beer', 'Bière locale malgache', 'thb.jpg', 4, 4000),

-- Snacks
('Mofo baolina', 'Beignets sucrés', 'mofo_baolina.jpg', 5, 1500),
('Arachides grillées', 'Cacahuètes grillées locales', 'arachides.jpg', 5, 1000),
('Bananes grillées', 'Bananes plantain grillées', 'bananes_grillees.jpg', 5, 2000),

-- Menus complets
('Menu Traditionnel', 'Romazava + vary + ranonapango', 'menu_trad.jpg', 6, 12000),
('Menu Découverte', 'Ravitoto + koba + litchi juice', 'menu_decouverte.jpg', 6, 15000),
('Menu Grillades', 'Hen''omby ritra + salade + THB', 'menu_grillade.jpg', 6, 22000);

-- 8. Clients
INSERT INTO core_client (email, mot_de_passe, contact, prenom, nom, date_inscri) VALUES
('rakoto.jean@gmail.com', 'hashed_password_1', '+261 34 12 345 67', 'Jean', 'Rakoto', '2024-01-15 10:30:00'),
('razafy.marie@yahoo.fr', 'hashed_password_2', '+261 33 98 765 43', 'Marie', 'Razafy', '2024-02-20 14:15:00'),
('andry.paul@outlook.com', 'hashed_password_3', '+261 32 55 123 88', 'Paul', 'Andry', '2024-03-10 09:45:00'),
('ratsimba.sarah@gmail.com', 'hashed_password_4', '+261 34 77 432 11', 'Sarah', 'Ratsimba', '2024-03-25 16:20:00'),
('rasolofo.michel@gmail.com', 'hashed_password_5', '+261 33 44 567 89', 'Michel', 'Rasolofo', '2024-04-05 11:30:00'),
('hery.nina@yahoo.fr', 'hashed_password_6', '+261 32 89 123 45', 'Nina', 'Hery', '2024-04-15 13:45:00'),
('rajao.david@gmail.com', 'hashed_password_7', '+261 34 22 678 90', 'David', 'Rajao', '2024-05-01 08:15:00'),
('raveloson.lucia@outlook.com', 'hashed_password_8', '+261 33 66 789 01', 'Lucia', 'Raveloson', '2024-05-20 15:30:00');

-- 9. Livreurs
INSERT INTO core_livreur (nom, contact, position, date_inscri) VALUES
('Randria Thierry', '+261 34 11 222 33', 'Analakely', '2024-01-10 08:00:00'),
('Razaka Joseph', '+261 33 44 555 66', 'Behoririka', '2024-01-15 09:30:00'),
('Ramanantsoa Eric', '+261 32 77 888 99', 'Andravoahangy', '2024-02-01 10:15:00'),
('Raharison Claude', '+261 34 55 111 22', 'Isotry', '2024-02-15 11:45:00'),
('Rakotozafy Bruno', '+261 33 88 333 44', 'Antsahamanitra', '2024-03-01 07:30:00'),
('Randriamampionona Solo', '+261 32 99 666 77', 'Tsaralalana', '2024-03-15 12:00:00');

-- 10. Horaires des restaurants (lundi=1, dimanche=7)
INSERT INTO core_horaire (restaurant_id, le_jour, horaire_debut, horaire_fin, mis_a_jour_le) VALUES
-- Chez Mariette (du lundi au samedi)
(1, 1, '07:00', '20:00', NOW()),
(1, 2, '07:00', '20:00', NOW()),
(1, 3, '07:00', '20:00', NOW()),
(1, 4, '07:00', '20:00', NOW()),
(1, 5, '07:00', '20:00', NOW()),
(1, 6, '07:00', '15:00', NOW()),
-- Le Sakamanga (tous les jours)
(2, 1, '11:00', '22:00', NOW()),
(2, 2, '11:00', '22:00', NOW()),
(2, 3, '11:00', '22:00', NOW()),
(2, 4, '11:00', '22:00', NOW()),
(2, 5, '11:00', '23:00', NOW()),
(2, 6, '11:00', '23:00', NOW()),
(2, 7, '11:00', '21:00', NOW()),
-- Restaurant Grillades (du mardi au dimanche)
(3, 2, '17:00', '23:00', NOW()),
(3, 3, '17:00', '23:00', NOW()),
(3, 4, '17:00', '23:00', NOW()),
(3, 5, '17:00', '23:00', NOW()),
(3, 6, '12:00', '23:00', NOW()),
(3, 7, '12:00', '22:00', NOW());

-- 11. Commissions des restaurants
INSERT INTO core_commission (restaurant_id, valeur, mis_a_jour_le) VALUES
(1, 15, NOW()),
(2, 20, NOW()),
(3, 18, NOW()),
(4, 12, NOW()),
(5, 25, NOW()),
(6, 10, NOW()),
(7, 30, NOW()),
(8, 22, NOW());

-- 12. Association restaurants-repas
INSERT INTO core_restaurantrepas (restaurant_id, repas_id) VALUES
-- Chez Mariette (cuisine traditionnelle)
(1, 1), (1, 2), (1, 6), (1, 8), (1, 9), (1, 12), (1, 16), (1, 17), (1, 23),
-- Le Sakamanga (fusion)
(2, 1), (2, 3), (2, 7), (2, 11), (2, 13), (2, 14), (2, 18), (2, 19), (2, 24),
-- Restaurant Grillades
(3, 4), (3, 5), (3, 12), (3, 19), (3, 25),
-- Café de la Gare
(4, 9), (4, 10), (4, 16), (4, 17), (4, 21), (4, 22),
-- Tana Plaza Food Court
(5, 3), (5, 7), (5, 10), (5, 11), (5, 18), (5, 20), (5, 21), (5, 22),
-- Chez Lolo
(6, 1), (6, 2), (6, 6), (6, 8), (6, 9), (6, 23),
-- Villa Vanille
(7, 3), (7, 4), (7, 7), (7, 13), (7, 14), (7, 15), (7, 25),
-- Mama Afrika
(8, 2), (8, 4), (8, 5), (8, 11), (8, 19), (8, 24);

-- 13. Association zones-restaurants
INSERT INTO core_zonerestaurant (restaurant_id, zone_id) VALUES
(1, 1), -- Chez Mariette à Analakely
(2, 5), -- Le Sakamanga à Antaninarenina
(3, 3), -- Restaurant Grillades à Andravoahangy
(4, 4), -- Café de la Gare à Tsaralalana
(5, 7), -- Tana Plaza à Behoririka
(6, 6), -- Chez Lolo à Isotry
(7, 4), -- Villa Vanille à Tsaralalana
(8, 2); -- Mama Afrika à Antsahamanitra

-- 14. Association zones-clients
INSERT INTO core_zoneclient (client_id, zone_id) VALUES
(1, 1), (1, 2), -- Jean Rakoto
(2, 3), (2, 4), -- Marie Razafy
(3, 1), (3, 7), -- Paul Andry
(4, 5), (4, 6), -- Sarah Ratsimba
(5, 2), (5, 8), -- Michel Rasolofo
(6, 3), (6, 4), -- Nina Hery
(7, 6), (7, 7), -- David Rajao
(8, 1), (8, 5); -- Lucia Raveloson

-- 15. Association zones-livreurs
INSERT INTO core_zonelivreur (zone_id, livreur_id) VALUES
(1, 1), (2, 1), -- Randria Thierry
(7, 2), (1, 2), -- Razaka Joseph
(3, 3), (4, 3), -- Ramanantsoa Eric
(6, 4), (5, 4), -- Raharison Claude
(2, 5), (8, 5), -- Rakotozafy Bruno
(4, 6), (5, 6); -- Randriamampionona Solo

-- 16. Historiques des statuts
INSERT INTO core_historiquestatutzone (zone_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-01-01 00:00:00'),
(2, 1, '2024-01-01 00:00:00'),
(3, 1, '2024-01-01 00:00:00'),
(4, 1, '2024-01-01 00:00:00'),
(5, 1, '2024-01-01 00:00:00'),
(6, 1, '2024-01-01 00:00:00'),
(7, 1, '2024-01-01 00:00:00'),
(8, 1, '2024-01-01 00:00:00');

INSERT INTO core_historiquestatutrestaurant (restaurant_id, statut_id, mis_a_jour_le) VALUES
(1, 1, NOW()),
(2, 1, NOW()),
(3, 1, NOW()),
(4, 1, NOW()),
(5, 1, NOW()),
(6, 1, NOW()),
(7, 1, NOW()),
(8, 1, NOW());

INSERT INTO core_historiquestatutlivreur (livreur_id, statut_id, mis_a_jour_le) VALUES
(1, 1, NOW()),
(2, 1, NOW()),
(3, 2, NOW()),
(4, 1, NOW()),
(5, 3, NOW()),
(6, 1, NOW());

-- 17. Commandes d'exemple
INSERT INTO core_commande (client_id, point_recup_id, cree_le, mode_paiement_id) VALUES
(1, 1, '2024-07-04 12:30:00', 2), -- Jean Rakoto, Mobile Money
(2, 2, '2024-07-04 13:15:00', 1), -- Marie Razafy, Espèces
(3, 3, '2024-07-04 18:45:00', 3), -- Paul Andry, Carte bancaire
(4, 4, '2024-07-04 19:20:00', 2), -- Sarah Ratsimba, Mobile Money
(5, 5, '2024-07-03 12:00:00', 1); -- Michel Rasolofo, Espèces

-- 18. Détails des commandes (repas commandés)
INSERT INTO core_commanderepas (commande_id, repas_id, quantite, ajoute_le) VALUES
-- Commande 1 (Jean Rakoto)
(1, 1, 1, '2024-07-04 12:30:00'), -- Romazava
(1, 16, 1, '2024-07-04 12:30:00'), -- Ranonapango
-- Commande 2 (Marie Razafy)
(2, 23, 1, '2024-07-04 13:15:00'), -- Menu Traditionnel
-- Commande 3 (Paul Andry)
(3, 4, 2, '2024-07-04 18:45:00'), -- Hen'omby ritra x2
(3, 19, 2, '2024-07-04 18:45:00'), -- Three Horses Beer x2
-- Commande 4 (Sarah Ratsimba)
(4, 7, 1, '2024-07-04 19:20:00'), -- Poisson à la vanille
(4, 18, 1, '2024-07-04 19:20:00'), -- Litchi juice
-- Commande 5 (Michel Rasolofo)
(5, 2, 1, '2024-07-03 12:00:00'), -- Ravitoto sy henakisoa
(5, 17, 1, '2024-07-03 12:00:00'); -- Ranon'ampango

-- 19. Historiques des statuts de commandes
INSERT INTO core_historiquestatutcommande (commande_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-07-04 12:30:00'), -- En attente
(1, 2, '2024-07-04 12:35:00'), -- Confirmée
(1, 3, '2024-07-04 12:45:00'), -- En préparation
(1, 4, '2024-07-04 13:15:00'), -- Prête
(2, 1, '2024-07-04 13:15:00'), -- En attente
(2, 2, '2024-07-04 13:20:00'), -- Confirmée
(3, 1, '2024-07-04 18:45:00'), -- En attente
(4, 1, '2024-07-04 19:20:00'), -- En attente
(5, 1, '2024-07-03 12:00:00'), -- En attente
(5, 2, '2024-07-03 12:05:00'), -- Confirmée
(5, 3, '2024-07-03 12:20:00'), -- En préparation
(5, 4, '2024-07-03 12:50:00'), -- Prête
(5, 5, '2024-07-03 13:10:00'), -- En livraison
(5, 6, '2024-07-03 13:40:00'); -- Livrée

-- 20. Livraisons
INSERT INTO core_livraison (livreur_id, commande_id, attribue_le) VALUES
(1, 1, '2024-07-04 13:15:00'), -- Randria Thierry pour commande 1
(5, 5, '2024-07-03 13:10:00'); -- Rakotozafy Bruno pour commande 5

-- 21. Historiques des statuts de livraisons
INSERT INTO core_historiquestatutlivraison (livraison_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-07-04 13:15:00'), -- Assignée
(2, 1, '2024-07-03 13:10:00'), -- Assignée
(2, 2, '2024-07-03 13:15:00'), -- En route vers restaurant
(2, 3, '2024-07-03 13:25:00'), -- Récupérée
(2, 4, '2024-07-03 13:30:00'), -- En route vers client
(2, 5, '2024-07-03 13:40:00'); -- Livrée

-- 22. Promotions
INSERT INTO core_promotion (repas_id, pourcentage_reduction, date_concerne) VALUES
(1, 20, '2024-07-05'), -- 20% sur Romazava
(23, 15, '2024-07-05'), -- 15% sur Menu Traditionnel
(7, 25, '2024-07-06'), -- 25% sur Poisson à la vanille
(19, 10, '2024-07-04'); -- 10% sur Three Horses Beer

-- 23. Limites de commandes journalières
INSERT INTO core_limitecommandesjournalieres (nombre_commandes, date) VALUES
(50, '2024-07-04'),
(60, '2024-07-05'),
(45, '2024-07-06'),
(55, '2024-07-07');

-- 24. Horaires spéciaux (jours fériés malgaches)
INSERT INTO core_horairespecial (restaurant_id, date_concerne, horaire_debut, horaire_fin, mis_a_jour_le) VALUES
(1, '2024-06-26', '08:00', '15:00', NOW()), -- Fête de l'Indépendance
(2, '2024-06-26', '12:00', '18:00', NOW()),
(3, '2024-06-26', '00:00', '00:00', NOW()), -- Fermé
(7, '2024-03-29', '10:00', '16:00', NOW()); -- Vendredi Saint

COMMIT;

-- Vérification des données insérées
SELECT 'Zones' as table_name, COUNT(*) as count FROM core_zone
UNION ALL
SELECT 'Restaurants', COUNT(*) FROM core_restaurant
UNION ALL
SELECT 'Repas', COUNT(*) FROM core_repas
UNION ALL
SELECT 'Clients', COUNT(*) FROM core_client
UNION ALL
SELECT 'Livreurs', COUNT(*) FROM core_livreur
UNION ALL
SELECT 'Commandes', COUNT(*) FROM core_commande
UNION ALL
SELECT 'Points de récupération', COUNT(*) FROM core_pointrecup;
