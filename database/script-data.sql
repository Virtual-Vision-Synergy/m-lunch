INSERT INTO core_statutcommande (appellation) VALUES
('En attente'),
('En cours'),
('En preparation'),
('Prete'),
('En livraison'),
('Livrée'),
('Annulée');

INSERT INTO core_statutlivraison (appellation) VALUES
('Assignee'),
('Effectuee');

INSERT INTO core_statutlivreur (appellation) VALUES
('Disponible'),
('En livraison'),
('Inactif');

INSERT INTO core_statutrestaurant (appellation) VALUES
('Actif'),
('Inactif');

INSERT INTO core_statutzone (appellation) VALUES
('Active'),
('Inactive');

INSERT INTO core_statutentite (appellation) VALUES
('Active'),
('Inactive');

INSERT INTO core_modepaiement (nom) VALUES
('Especes'),
('Mobile Money'),
('Carte bancaire');

INSERT INTO core_entite (nom) VALUES
('Zone Commerciale'),
('Zone Résidentielle'),
('Zone Universitaire'),
('Zone Administrative'),
('Zone Industrielle'),
('Zone Touristique');

INSERT INTO core_zone (nom, description, zone) VALUES
(
    'Antanimena',
    'Centre ville commercial',
    'POLYGON((47.5200 -18.8970, 47.5220 -18.8970, 47.5220 -18.8990, 47.5200 -18.8990, 47.5200 -18.8970))'
),
(
    'Andohalo',
    'Quartier historique résidentiel',
    'POLYGON((47.5300 -18.9165, 47.5320 -18.9165, 47.5320 -18.9185, 47.5300 -18.9185, 47.5300 -18.9165))'
);

INSERT INTO core_pointrecup (nom, geo_position) VALUES
-- Antanimena
('Antanimena - Victoria Plaza', 'POINT(47.5220 -18.9000)'),
('Antanimena - Gare Soarano',      'POINT(47.5195 -18.9050)'),
('Antanimena - Analakely Market', 'POINT(47.5210 -18.8985)'),
-- Andohalo
('Andohalo - Cathédrale',         'POINT(47.530654 -18.917852)'),
('Andohalo - Palais de justice',  'POINT(47.5329118 -18.9209601)'),
('Andohalo - Lycée Andohalo',     'POINT(47.5311 -18.9184)');

INSERT INTO core_typerepas (nom) VALUES
('Plat principal'),
('Entree'),
('Dessert'),
('Boisson');

INSERT INTO core_restaurant (nom, adresse, description, image, geo_position, mot_de_passe) VALUES
-- Antanimena
('La Varangue', 'Rue Andrianary Ratianarivo, Antanimena', 'Cuisine raffinee franco malgache dans un cadre elegant', 'lavarangue.png', 'POINT(47.5234 -18.9078)', 'mdp'),
('Le Rossini', 'Rue de Russie, Antanimena', 'Restaurant italien chic, pates maison et grillades', 'lerossini.png', 'POINT(47.5210 -18.9065)', 'mdp'),
('No Comment Bar', 'Rue Ravelojaona, Antanimena', 'Bar restaurant branche, musique live et tapas', 'nocomment.png', 'POINT(47.5198 -18.9042)', 'mdp'),
('Le Buffet du Jardin', 'Jardin Antaninarenina', 'Buffet a volonte en plein air, specialites locales', 'buffetjardin.png', 'POINT(47.5241 -18.9085)', 'mdp'),

-- Andohalo
('La Table d Andohalo', 'Place Andohalo', 'Cuisine traditionnelle avec vue sur la ville', 'tabledandohalo.png', 'POINT(47.5309 -18.9172)', 'pbkdf2_sha256$600000$default$password5'),
('Andohalo Cafe', 'Rue du Lycee Andohalo', 'Cafe convivial avec patisseries artisanales', 'andohalocafe.png', 'POINT(47.5321 -18.9184)', 'pbkdf2_sha256$600000$default$password6'),
('Rova Grill', 'Pres du Palais de la Reine, Andohalo', 'Viandes grillees et plats malgaches traditionnels', 'rovagrill.png', 'POINT(47.5317 -18.9168)', 'pbkdf2_sha256$600000$default$password7'),
('Maison des Saveurs', 'Rue de la Cathedrale, Andohalo', 'Fusion de saveurs europeennes et malgaches', 'maisonsaveurs.png', 'POINT(47.5303 -18.9175)', 'pbkdf2_sha256$600000$default$password8');

INSERT INTO core_repas (nom, description, image, type_id, prix) VALUES
-- Plats principaux (16)
('Romazava', 'Plat traditionnel malgache aux bredes et viande de zebu', 'romazava.png', 1, 8000),
('Ravitoto sy henakisoa', 'Feuilles de manioc pilees avec porc', 'ravitoto.png', 1, 9000),
('Akoho sy voanio', 'Poulet au lait de coco et epices', 'akoho_voanio.png', 1, 9500),
('Hen omby ritra', 'Zebu braise aux aromates locaux', 'henomby_ritra.png', 1, 10000),
('Tilapia grille', 'Poisson tilapia grille accompagne de riz', 'tilapia.png', 1, 8500),
('Kitoza', 'Viande de zebu sechee grillee au feu de bois', 'kitoza.png', 1, 9500),
('Poulet grille', 'Poulet marine grille accompagne de legumes', 'poulet_grille.png', 1, 8000),
('Henakisoa sy tsaramaso', 'Porc mijote aux haricots rouges', 'henakisoa_tsaramaso.png', 1, 9500),
('Foza sy legioma', 'Crabe malgache mijote avec legumes', 'foza.png', 1, 9800),
('Sakay sy henakisoa', 'Porc epice malgache', 'masikita.png', 1, 9000),
('Koba akondro', 'Plat regional a base de banane et riz', 'koba_akondro.png', 1, 8500),
('Lasary voatabia', 'Salade tomate malgache', 'lasary_voatabia.png', 1, 3000),
('Vary amin anana', 'Riz accompagne de brèdes', 'vary_anana.png', 1, 7500),
('Akoho gasy', 'Poulet malgache traditionnel', 'akoho_gasy.png', 1, 9500),
('Masikita', 'Brochette de viande grillee', 'masikita.png', 1, 7000),
('Hen omby amin ala', 'Zebu sauvage mijote', 'henomby_ala.png', 1, 10500),

-- Entrees (16)
('Sambos', 'Petits chaussons frits farcis a la viande ou legumes', 'sambos.png', 2, 3500),
('Achards', 'Legumes marines et epices', 'achards.png', 2, 3000),
('Soupe chinoise', 'Bouillon aux vermicelles et legumes', 'soupe_chinoise.png', 2, 4000),
('Salade composee', 'Legumes frais et vinaigrette', 'salade.png', 2, 4500),
('Beignets legumes', 'Petits beignets croustillants de legumes', 'beignet_legumes.png', 2, 3500),
('Crevettes panees', 'Crevettes croustillantes avec sauce', 'crevettes_panees.png', 2, 5000),
('Bruschetta', 'Pain grille avec tomates et basilic', 'bruschetta.png', 2, 4000),
('Salade exotique', 'Fruits et legumes frais avec vinaigrette', 'salade_exotique.png', 2, 4500),
('Veloute de giraumon', 'Soupe onctueuse de giraumon', 'veloute_giraumon.png', 2, 4200),
('Croustillant au fromage', 'Feuilleté croustillant au fromage', 'croustillant_fromage.png', 2, 4700),
('Omelette malgache', 'Omelette aux epices locales', 'omelette.png', 2, 3500),
('Tartare de poisson', 'Poisson cru mariné aux epices', 'tartare_poisson.png', 2, 5500),
('Soupe de legume', 'Soupe legere aux legumes frais', 'soupe_legume.png', 2, 3500),
('Salade de papaye', 'Salade de papaye verte', 'salade_papaye.png', 2, 4000),
('Ceviche malgache', 'Poisson mariné au citron vert', 'ceviche.png', 2, 4800),
('Terrine de legumes', 'Terrine froide aux legumes', 'terrine_legumes.png', 2, 4300),

-- Desserts (16)
('Koba', 'Gateau malgache aux cacahuetes et riz', 'koba_akondro.png', 3, 3000),
('Mofo gasy', 'Beignets malgaches au riz', 'vary_anana.png', 3, 2000),
('Bonbons coco', 'Confiseries a la noix de coco', 'smoothie.png', 3, 2500),
('Flan maison', 'Flan traditionnel au caramel', 'cafe_glace.png', 3, 3500),
('Banane flambe', 'Banane cuite au sucre et flambe au rhum', 'jus_mangue.png', 3, 4000),
('Tarte aux fruits', 'Tarte croustillante aux fruits frais', 'jus_litchi.png', 3, 4500),
('Salade de fruits', 'Melange de fruits tropicaux', 'jus_goyave.png', 3, 3000),
('Riz au lait', 'Dessert onctueux au lait et riz', 'ranovola.png', 3, 2500),
('Glace maison', 'Glace artisanale', 'cafe_glace.png', 3, 4000),
('Beignet sucre', 'Beignet sucre croustillant', 'beignet_legumes.png', 3, 2200),
('Mousse au chocolat', 'Mousse legere au chocolat', 'smoothie.png', 3, 4800),
('Pudding au riz', 'Pudding traditionnel au riz', 'vary_anana.png', 3, 3200),
('Sorbet tropical', 'Sorbet aux fruits exotiques', 'jus_litchi.png', 3, 3500),
('Gateau au miel', 'Gateau moelleux au miel', 'koba_akondro.png', 3, 3700),
('Crepe sucree', 'Crepe fine sucree', 'sambos.png', 3, 2900),
('Tarte au citron', 'Tarte acidulee au citron', 'jus_citron.png', 3, 4200),

-- Boissons (16)
('Ranovola', 'Eau de riz grillee traditionnelle', 'ranovola.png', 4, 1500),
('THB', 'Biere locale emblématique', 'thb.png', 4, 4000),
('Jus de litchi', 'Jus naturel de litchi', 'jus_litchi.png', 4, 2500),
('Soda', 'Boisson gazeuse classique', 'soda.png', 4, 2000),
('Jus de mangue', 'Jus frais de mangue', 'jus_mangue.png', 4, 2500),
('Biere locale blonde', 'Biere artisanale legere', 'thb.png', 4, 4000),
('The chaud', 'The noir traditionnel', 'the.png', 4, 1500),
('Cafe malagasy', 'Cafe local prepare traditionnellement', 'cafe_glace.png', 4, 2000),
('Jus de citron', 'Jus de citron frais', 'jus_citron.png', 4, 2200),
('Limonade', 'Boisson rafraichissante sucree', 'limonade.png', 4, 2100),
('Smoothie exotique', 'Smoothie aux fruits tropicaux', 'smoothie.png', 4, 3000),
('Eau minerale', 'Eau minerale naturelle', 'eau.png', 4, 1200),
('Cafe glacé', 'Cafe servi avec glace', 'cafe_glace.png', 4, 2500),
('The glacé', 'The servi froid', 'the_glace.png', 4, 2500),
('Cocktail sans alcool', 'Boisson festive sans alcool', 'cocktail.png', 4, 3500),
('Jus de goyave', 'Jus naturel de goyave', 'jus_goyave.png', 4, 2600);

INSERT INTO core_livreur (nom, contact, position, geo_position, date_inscri) VALUES
-- Antanimena
('Randria Thierry', '+261 34 11 222 33', 'Antanimena - Centre', '-18.8985,47.5210', NOW()),
('Rakoto Hery', '+261 33 22 333 44', 'Antanimena - Marché', '-18.8980,47.5205', NOW()),
('Rajaonarison Lala', '+261 32 55 666 77', 'Antanimena - Gare', '-18.8975,47.5215', NOW()),

-- Andohalo
('Razaka Joseph', '+261 33 44 555 66', 'Andohalo - Cathédrale', '-18.9170,47.5310', NOW()),
('Ramanantsoa Eric', '+261 32 77 888 99', 'Andohalo - Palais', '-18.9175,47.5318', NOW()),
('Rakotovao Mamy', '+261 34 88 999 00', 'Andohalo - Lycée', '-18.9168,47.5305', NOW());

INSERT INTO core_horaire (restaurant_id, le_jour, horaire_debut, horaire_fin, mis_a_jour_le) VALUES
-- Antanimena restaurants (id 1 à 4 supposés)
-- La Varangue
(1, 0, '08:00', '21:00', NOW()),
(1, 1, '08:00', '21:00', NOW()),
(1, 2, '08:00', '21:00', NOW()),
(1, 3, '08:00', '21:00', NOW()),
(1, 4, '08:00', '22:00', NOW()),
(1, 5, '09:00', '18:00', NOW()),
(1, 6, '09:00', '16:00', NOW()),

-- Le Rossini
(2, 0, '11:00', '22:00', NOW()),
(2, 1, '11:00', '22:00', NOW()),
(2, 2, '11:00', '22:00', NOW()),
(2, 3, '11:00', '22:00', NOW()),
(2, 4, '11:00', '23:00', NOW()),
(2, 5, '12:00', '23:00', NOW()),
(2, 6, '12:00', '20:00', NOW()),

-- No Comment Bar
(3, 0, '16:00', '02:00', NOW()),
(3, 1, '16:00', '02:00', NOW()),
(3, 2, '16:00', '02:00', NOW()),
(3, 3, '16:00', '02:00', NOW()),
(3, 4, '16:00', '03:00', NOW()),
(3, 5, '16:00', '03:00', NOW()),
(3, 6, '16:00', '01:00', NOW()),

-- Le Buffet du Jardin
(4, 0, '07:00', '15:00', NOW()),
(4, 1, '07:00', '15:00', NOW()),
(4, 2, '07:00', '15:00', NOW()),
(4, 3, '07:00', '15:00', NOW()),
(4, 4, '07:00', '15:00', NOW()),
(4, 5, '08:00', '14:00', NOW()),
(4, 6, '08:00', '13:00', NOW()),

-- Andohalo restaurants (id 5 à 8 supposés)
-- La Table d Andohalo
(5, 0, '09:00', '20:00', NOW()),
(5, 1, '09:00', '20:00', NOW()),
(5, 2, '09:00', '20:00', NOW()),
(5, 3, '09:00', '20:00', NOW()),
(5, 4, '09:00', '22:00', NOW()),
(5, 5, '10:00', '18:00', NOW()),
(5, 6, '10:00', '16:00', NOW()),

-- Andohalo Cafe
(6, 0, '07:00', '19:00', NOW()),
(6, 1, '07:00', '19:00', NOW()),
(6, 2, '07:00', '19:00', NOW()),
(6, 3, '07:00', '19:00', NOW()),
(6, 4, '07:00', '21:00', NOW()),
(6, 5, '08:00', '14:00', NOW()),
(6, 6, '08:00', '12:00', NOW()),

-- Rova Grill
(7, 0, '12:00', '23:00', NOW()),
(7, 1, '12:00', '23:00', NOW()),
(7, 2, '12:00', '23:00', NOW()),
(7, 3, '12:00', '23:00', NOW()),
(7, 4, '12:00', '00:00', NOW()),
(7, 5, '12:00', '00:00', NOW()),
(7, 6, '12:00', '22:00', NOW()),

-- Maison des Saveurs
(8, 0, '11:00', '22:00', NOW()),
(8, 1, '11:00', '22:00', NOW()),
(8, 2, '11:00', '22:00', NOW()),
(8, 3, '11:00', '22:00', NOW()),
(8, 4, '11:00', '23:00', NOW()),
(8, 5, '11:00', '22:00', NOW()),
(8, 6, '11:00', '20:00', NOW());

INSERT INTO core_commission (restaurant_id, valeur, mis_a_jour_le) VALUES
(1, 10, NOW()),
(2, 12, NOW()),
(3, 8, NOW()),
(4, 7, NOW()),
(5, 11, NOW()),
(6, 9, NOW()),
(7, 12, NOW()),
(8, 7, NOW());

INSERT INTO core_restaurantrepas (restaurant_id, repas_id) VALUES
-- Restaurant 1 - La Varangue (8 repas : ID 1-8)
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),

-- Restaurant 2 - Le Rossini (8 repas : ID 9-16) 
(2, 9), (2, 10), (2, 11), (2, 12), (2, 13), (2, 14), (2, 15), (2, 16),

-- Restaurant 3 - No Comment Bar (8 repas : ID 17-24)
(3, 17), (3, 18), (3, 19), (3, 20), (3, 21), (3, 22), (3, 23), (3, 24),

-- Restaurant 4 - Le Buffet du Jardin (8 repas : ID 25-32)
(4, 25), (4, 26), (4, 27), (4, 28), (4, 29), (4, 30), (4, 31), (4, 32),

-- Restaurant 5 - La Table d Andohalo (8 repas : ID 33-40)
(5, 33), (5, 34), (5, 35), (5, 36), (5, 37), (5, 38), (5, 39), (5, 40),

-- Restaurant 6 - Andohalo Cafe (8 repas : ID 41-48)
(6, 41), (6, 42), (6, 43), (6, 44), (6, 45), (6, 46), (6, 47), (6, 48),

-- Restaurant 7 - Rova Grill (8 repas : ID 49-56)
(7, 49), (7, 50), (7, 51), (7, 52), (7, 53), (7, 54), (7, 55), (7, 56),

-- Restaurant 8 - Maison des Saveurs (8 repas : ID 57-64)
(8, 57), (8, 58), (8, 59), (8, 60), (8, 61), (8, 62), (8, 63), (8, 64);


-- Association zones-restaurants
INSERT INTO core_zonerestaurant (restaurant_id, zone_id) VALUES
(1, 1), -- Chez Mariette - Antanimena
(2, 1), -- La Varangue - Antanimena
(3, 1), -- Le Rossini - Antanimena
(4, 1), -- No Comment Bar - Antanimena

(5, 2), -- Le Buffet du Jardin - Andohalo
(6, 2), -- La Table d Andohalo - Andohalo
(7, 2), -- Andohalo Cafe - Andohalo
(8, 2); -- Rova Grill - Andohalo

-- Association zones-livreurs
INSERT INTO core_zonelivreur (zone_id, livreur_id) VALUES
(1, 1), -- Randria Thierry - Antanimena
(1, 2), -- Rakoto Hery - Antanimena
(1, 3), -- Rajaonarison Lala - Antanimena

(2, 4), -- Razaka Joseph - Andohalo
(2, 5), -- Ramanantsoa Eric - Andohalo
(2, 6); -- Rakotovao Mamy - Andohalo

INSERT INTO core_referencezoneentite (zone_id, entite_id) VALUES
(1, 1), -- Antanimena -> Zone Commerciale
(2, 2); -- Andohalo -> Zone Residentielle

INSERT INTO core_historiquestatutzone (zone_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-01-01 00:00:00'),
(2, 1, '2024-01-01 00:00:00');

INSERT INTO core_historiquestatutentite (entite_id, statut_id, mis_a_jour_le) VALUES
(1, 1, '2024-01-01 00:00:00'), -- Zone Commerciale
(2, 1, '2024-01-01 00:00:00'), -- Zone Residentielle
(3, 1, '2024-01-01 00:00:00'), -- Zone Universitaire
(4, 1, '2024-01-01 00:00:00'), -- Zone Administrative
(5, 1, '2024-01-01 00:00:00'), -- Zone Industrielle
(6, 1, '2024-01-01 00:00:00'); -- Zone Touristique

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
(3, 1, NOW()),
(4, 1, NOW()),
(5, 1, NOW()),
(6, 1, NOW());

-- DONNÉES MANQUANTES CRITIQUES

-- 1. Disponibilité des repas (CRITIQUE pour les suivis)
INSERT INTO core_disponibiliterepas (repas_id, est_dispo, mis_a_jour_le) VALUES
-- Tous les repas sont disponibles par défaut
(1, TRUE, NOW()), (2, TRUE, NOW()), (3, TRUE, NOW()), (4, TRUE, NOW()),
(5, TRUE, NOW()), (6, TRUE, NOW()), (7, TRUE, NOW()), (8, TRUE, NOW()),
(9, TRUE, NOW()), (10, TRUE, NOW()), (11, TRUE, NOW()), (12, TRUE, NOW()),
(13, TRUE, NOW()), (14, TRUE, NOW()), (15, TRUE, NOW()), (16, TRUE, NOW()),
(17, TRUE, NOW()), (18, TRUE, NOW()), (19, TRUE, NOW()), (20, TRUE, NOW()),
(21, TRUE, NOW()), (22, TRUE, NOW()), (23, TRUE, NOW()), (24, TRUE, NOW()),
(25, TRUE, NOW()), (26, TRUE, NOW()), (27, TRUE, NOW()), (28, TRUE, NOW()),
(29, TRUE, NOW()), (30, TRUE, NOW()), (31, TRUE, NOW()), (32, TRUE, NOW()),
(33, TRUE, NOW()), (34, TRUE, NOW()), (35, TRUE, NOW()), (36, TRUE, NOW()),
(37, TRUE, NOW()), (38, TRUE, NOW()), (39, TRUE, NOW()), (40, TRUE, NOW()),
(41, TRUE, NOW()), (42, TRUE, NOW()), (43, TRUE, NOW()), (44, TRUE, NOW()),
(45, TRUE, NOW()), (46, TRUE, NOW()), (47, TRUE, NOW()), (48, TRUE, NOW()),
(49, TRUE, NOW()), (50, TRUE, NOW()), (51, TRUE, NOW()), (52, TRUE, NOW()),
(53, TRUE, NOW()), (54, TRUE, NOW()), (55, TRUE, NOW()), (56, TRUE, NOW()),
(57, TRUE, NOW()), (58, TRUE, NOW()), (59, TRUE, NOW()), (60, TRUE, NOW()),
(61, TRUE, NOW()), (62, TRUE, NOW()), (63, TRUE, NOW()), (64, TRUE, NOW());


-- 4. Historique des zones de récupération
INSERT INTO core_historiquezonesrecuperation (zone_id, point_recup_id, mis_a_jour_le) VALUES
(1, 1, NOW()), -- Antanimena -> Victoria Plaza
(1, 2, NOW()), -- Antanimena -> Gare Soarano  
(1, 3, NOW()), -- Antanimena -> Analakely Market
(2, 4, NOW()), -- Andohalo -> Cathédrale
(2, 5, NOW()), -- Andohalo -> Palais de justice
(2, 6, NOW()); -- Andohalo -> Lycée Andohalo

