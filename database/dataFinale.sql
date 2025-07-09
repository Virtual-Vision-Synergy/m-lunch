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
('La Varangue', 'Rue Andrianary Ratianarivo, Antanimena', 'Cuisine raffinee franco malgache dans un cadre elegant', 'lavarangue.jpg', '-18.9078,47.5234', 'pbkdf2_sha256$600000$default$password1'),
('Le Rossini', 'Rue de Russie, Antanimena', 'Restaurant italien chic, pates maison et grillades', 'lerossini.jpg', '-18.9065,47.5210', 'pbkdf2_sha256$600000$default$password2'),
('No Comment Bar', 'Rue Ravelojaona, Antanimena', 'Bar restaurant branche, musique live et tapas', 'nocomment.jpg', '-18.9042,47.5198', 'pbkdf2_sha256$600000$default$password3'),
('Le Buffet du Jardin', 'Jardin Antaninarenina', 'Buffet a volonte en plein air, specialites locales', 'buffetjardin.jpg', '-18.9085,47.5241', 'pbkdf2_sha256$600000$default$password4'),

-- Andohalo
('La Table d Andohalo', 'Place Andohalo', 'Cuisine traditionnelle avec vue sur la ville', 'tabledandohalo.jpg', '-18.9172,47.5309', 'pbkdf2_sha256$600000$default$password5'),
('Andohalo Cafe', 'Rue du Lycee Andohalo', 'Cafe convivial avec patisseries artisanales', 'andohalocafe.jpg', '-18.9184,47.5321', 'pbkdf2_sha256$600000$default$password6'),
('Rova Grill', 'Pres du Palais de la Reine, Andohalo', 'Viandes grillees et plats malgaches traditionnels', 'rovagrill.jpg', '-18.9168,47.5317', 'pbkdf2_sha256$600000$default$password7'),
('Maison des Saveurs', 'Rue de la Cathedrale, Andohalo', 'Fusion de saveurs europeennes et malgaches', 'maisonsaveurs.jpg', '-18.9175,47.5303', 'pbkdf2_sha256$600000$default$password8');

INSERT INTO core_repas (nom, description, image, type_id, prix) VALUES
-- Plats principaux (16)
('Romazava', 'Plat traditionnel malgache aux bredes et viande de zebu', 'romazava.jpg', 1, 8000),
('Ravitoto sy henakisoa', 'Feuilles de manioc pilees avec porc', 'ravitoto.jpg', 1, 9000),
('Akoho sy voanio', 'Poulet au lait de coco et epices', 'akoho_voanio.jpg', 1, 9500),
('Hen omby ritra', 'Zebu braise aux aromates locaux', 'henomby.jpg', 1, 10000),
('Tilapia grille', 'Poisson tilapia grille accompagne de riz', 'tilapia.jpg', 1, 8500),
('Kitoza', 'Viande de zebu sechee grillee au feu de bois', 'kitoza.jpg', 1, 9500),
('Poulet grille', 'Poulet marine grille accompagne de legumes', 'poulet_grille.jpg', 1, 8000),
('Henakisoa sy tsaramaso', 'Porc mijote aux haricots rouges', 'henakisoa_tsaramaso.jpg', 1, 9500),
('Foza sy legioma', 'Crabe malgache mijote avec legumes', 'foza.jpg', 1, 9800),
('Sakay sy henakisoa', 'Porc epice malgache', 'sakay_henakisoa.jpg', 1, 9000),
('Koba akondro', 'Plat regional a base de banane et riz', 'koba_akondro.jpg', 1, 8500),
('Lasary voatabia', 'Salade tomate malgache', 'lasary_voatabia.jpg', 1, 3000),
('Vary amin anana', 'Riz accompagne de brèdes', 'vary_anana.jpg', 1, 7500),
('Akoho gasy', 'Poulet malgache traditionnel', 'akoho_gasy.jpg', 1, 9500),
('Masikita', 'Brochette de viande grillee', 'masikita.jpg', 1, 7000),
('Hen omby amin ala', 'Zebu sauvage mijote', 'henomby_ala.jpg', 1, 10500),

-- Entrees (16)
('Sambos', 'Petits chaussons frits farcis a la viande ou legumes', 'sambos.jpg', 2, 3500),
('Achards', 'Legumes marines et epices', 'achards.jpg', 2, 3000),
('Soupe chinoise', 'Bouillon aux vermicelles et legumes', 'soupe_chinoise.jpg', 2, 4000),
('Salade composee', 'Legumes frais et vinaigrette', 'salade.jpg', 2, 4500),
('Beignets legumes', 'Petits beignets croustillants de legumes', 'beignet_legumes.jpg', 2, 3500),
('Crevettes panees', 'Crevettes croustillantes avec sauce', 'crevettes_panees.jpg', 2, 5000),
('Bruschetta', 'Pain grille avec tomates et basilic', 'bruschetta.jpg', 2, 4000),
('Salade exotique', 'Fruits et legumes frais avec vinaigrette', 'salade_exotique.jpg', 2, 4500),
('Veloute de giraumon', 'Soupe onctueuse de giraumon', 'veloute_giraumon.jpg', 2, 4200),
('Croustillant au fromage', 'Feuilleté croustillant au fromage', 'croustillant_fromage.jpg', 2, 4700),
('Omelette malgache', 'Omelette aux epices locales', 'omelette.jpg', 2, 3500),
('Tartare de poisson', 'Poisson cru mariné aux epices', 'tartare_poisson.jpg', 2, 5500),
('Soupe de legume', 'Soupe legere aux legumes frais', 'soupe_legume.jpg', 2, 3500),
('Salade de papaye', 'Salade de papaye verte', 'salade_papaye.jpg', 2, 4000),
('Ceviche malgache', 'Poisson mariné au citron vert', 'ceviche.jpg', 2, 4800),
('Terrine de legumes', 'Terrine froide aux legumes', 'terrine_legumes.jpg', 2, 4300),

-- Desserts (16)
('Koba', 'Gateau malgache aux cacahuetes et riz', 'koba.jpg', 3, 3000),
('Mofo gasy', 'Beignets malgaches au riz', 'mofo_gasy.jpg', 3, 2000),
('Bonbons coco', 'Confiseries a la noix de coco', 'bonbon_coco.jpg', 3, 2500),
('Flan maison', 'Flan traditionnel au caramel', 'flan.jpg', 3, 3500),
('Banane flambe', 'Banane cuite au sucre et flambe au rhum', 'banane_flambe.jpg', 3, 4000),
('Tarte aux fruits', 'Tarte croustillante aux fruits frais', 'tarte_fruits.jpg', 3, 4500),
('Salade de fruits', 'Melange de fruits tropicaux', 'salade_fruits.jpg', 3, 3000),
('Riz au lait', 'Dessert onctueux au lait et riz', 'riz_lait.jpg', 3, 2500),
('Glace maison', 'Glace artisanale', 'glace.jpg', 3, 4000),
('Beignet sucre', 'Beignet sucre croustillant', 'beignet_sucre.jpg', 3, 2200),
('Mousse au chocolat', 'Mousse legere au chocolat', 'mousse_chocolat.jpg', 3, 4800),
('Pudding au riz', 'Pudding traditionnel au riz', 'pudding_riz.jpg', 3, 3200),
('Sorbet tropical', 'Sorbet aux fruits exotiques', 'sorbet.jpg', 3, 3500),
('Gateau au miel', 'Gateau moelleux au miel', 'gateau_miel.jpg', 3, 3700),
('Crepe sucree', 'Crepe fine sucree', 'crepe.jpg', 3, 2900),
('Tarte au citron', 'Tarte acidulee au citron', 'tarte_citron.jpg', 3, 4200),

-- Boissons (16)
('Ranovola', 'Eau de riz grillee traditionnelle', 'ranovola.jpg', 4, 1500),
('THB', 'Biere locale emblématique', 'thb.jpg', 4, 4000),
('Jus de litchi', 'Jus naturel de litchi', 'jus_litchi.jpg', 4, 2500),
('Soda', 'Boisson gazeuse classique', 'soda.jpg', 4, 2000),
('Jus de mangue', 'Jus frais de mangue', 'jus_mangue.jpg', 4, 2500),
('Biere locale blonde', 'Biere artisanale legere', 'biere_b.jpg', 4, 4000),
('The chaud', 'The noir traditionnel', 'the.jpg', 4, 1500),
('Cafe malagasy', 'Cafe local prepare traditionnellement', 'cafe.jpg', 4, 2000),
('Jus de citron', 'Jus de citron frais', 'jus_citron.jpg', 4, 2200),
('Limonade', 'Boisson rafraichissante sucree', 'limonade.jpg', 4, 2100),
('Smoothie exotique', 'Smoothie aux fruits tropicaux', 'smoothie.jpg', 4, 3000),
('Eau minerale', 'Eau minerale naturelle', 'eau.jpg', 4, 1200),
('Cafe glacé', 'Cafe servi avec glace', 'cafe_glace.jpg', 4, 2500),
('The glacé', 'The servi froid', 'the_glace.jpg', 4, 2500),
('Cocktail sans alcool', 'Boisson festive sans alcool', 'cocktail.jpg', 4, 3500),
('Jus de goyave', 'Jus naturel de goyave', 'jus_goyave.jpg', 4, 2600);

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
-- Restaurant 1
(1, 1), (1, 2), (1, 3), (1, 4),    
(1, 17), (1, 18), (1, 19),         
(1, 33), (1, 34), (1, 35),         
(1, 49), (1, 50), (1, 51),        

-- Restaurant 2
(2, 5), (2, 6), (2, 7), (2, 8),
(2, 20), (2, 21), (2, 22),
(2, 36), (2, 37), (2, 38),
(2, 52), (2, 53), (2, 54),

-- Restaurant 3
(3, 9), (3, 10), (3, 11), (3, 12),
(3, 23), (3, 24), (3, 25),
(3, 39), (3, 40), (3, 41),
(3, 55), (3, 56), (3, 57),

-- Restaurant 4
(4, 13), (4, 14), (4, 15), (4, 16),
(4, 26), (4, 27), (4, 28),
(4, 42), (4, 43), (4, 44),
(4, 58), (4, 59), (4, 60),

-- Restaurant 5
(5, 1), (5, 5), (5, 9), (5, 13),
(5, 17), (5, 21), (5, 25),
(5, 33), (5, 37), (5, 41),
(5, 49), (5, 53), (5, 57),

-- Restaurant 6
(6, 2), (6, 6), (6, 10), (6, 14),
(6, 18), (6, 22), (6, 26),
(6, 34), (6, 38), (6, 42),
(6, 50), (6, 54), (6, 58),

-- Restaurant 7
(7, 3), (7, 7), (7, 11), (7, 15),
(7, 19), (7, 23), (7, 27),
(7, 35), (7, 39), (7, 43),
(7, 51), (7, 55), (7, 59),

-- Restaurant 8
(8, 4), (8, 8), (8, 12), (8, 16),
(8, 20), (8, 24), (8, 28),
(8, 36), (8, 40), (8, 44),
(8, 52), (8, 56), (8, 60);


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

