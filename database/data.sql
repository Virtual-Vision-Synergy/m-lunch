INSERT INTO zones (nom, description, zone)
VALUES 
-- Zone 1 : Ambohijatovo
('Ambohijatovo', 'Zone autour Ambohijatovo', 
 ST_GeogFromText('POLYGON((47.515 -18.907, 47.518 -18.907, 47.518 -18.904, 47.515 -18.904, 47.515 -18.907))')
),

-- Zone 2 : Analakely
('Analakely', 'Zone commerciale du centre ville', 
 ST_GeogFromText('POLYGON((47.5155 -18.913, 47.519 -18.913, 47.519 -18.909, 47.5155 -18.909, 47.5155 -18.913))')
),

-- Zone 3 : Ankatso (Université)
('Ankatso', 'Zone universitaire autour de Université Antananarivo', 
 ST_GeogFromText('POLYGON((47.524 -18.899, 47.528 -18.899, 47.528 -18.895, 47.524 -18.895, 47.524 -18.899))')
),

-- Zone 4 : Isoraka
('Isoraka', 'Quartier résidentiel et diplomatique', 
 ST_GeogFromText('POLYGON((47.512 -18.911, 47.516 -18.911, 47.516 -18.907, 47.512 -18.907, 47.512 -18.911))')
);


INSERT INTO restaurants (nom, adresse, image, geo_position) VALUES
('Le Carré', 'Ambatonakanga, Antananarivo', 'lecarre.jpg',
 ST_SetSRID(ST_MakePoint(47.5162, -18.9086), 4326)),

('KUDéTA Urban Club', 'Antsahavola, Antananarivo', 'kudeta.jpg',
 ST_SetSRID(ST_MakePoint(47.5180, -18.9103), 4326)),

('La Varangue', 'Antaninarenina, Antananarivo', 'lavarangue.jpg',
 ST_SetSRID(ST_MakePoint(47.5192, -18.9105), 4326)),

('Villa Vanille', 'Isoraka, Antananarivo', 'villavanille.jpg',
 ST_SetSRID(ST_MakePoint(47.5169, -18.9118), 4326)),

('Les 3 Metis', 'Antsakaviro, Antananarivo', '3metis.jpg',
 ST_SetSRID(ST_MakePoint(47.5156, -18.9125), 4326)),

('Nerone Ristorante Italiano', 'Ambatonakanga, Antananarivo', 'nerone.jpg',
 ST_SetSRID(ST_MakePoint(47.5178, -18.9081), 4326)),

('La Table d’Eugène', 'Ankorondrano, Antananarivo', 'eugene.jpg',
 ST_SetSRID(ST_MakePoint(47.5270, -18.8715), 4326)),

('Café de la Gare', 'Soarano, Antananarivo', 'gare.jpg',
 ST_SetSRID(ST_MakePoint(47.5153, -18.9044), 4326));



INSERT INTO point_de_recuperation (nom, geo_position) VALUES
('Soarano', ST_SetSRID(ST_MakePoint(47.5162, -18.9050), 4326)),
('Ankorondrano', ST_SetSRID(ST_MakePoint(47.5289, -18.8792), 4326)),
('Analakely', ST_SetSRID(ST_MakePoint(47.5165, -18.9130), 4326)),
('Isoraka', ST_SetSRID(ST_MakePoint(47.5148, -18.9105), 4326)),
('Ambanidia', ST_SetSRID(ST_MakePoint(47.5295, -18.9032), 4326));


INSERT INTO commandes (client_id, point_recup_id) VALUES
(16, 3),
(16, 2),
(16, 1);

INSERT INTO commande_repas (commande_id, repas_id, quantite) VALUES
(4, 1, 2),  -- commande 1 → 2x ravitoto
(5, 2, 1),  -- commande 1 → 1x poulet
(6, 3, 3);  -- commande 2 → 3x mofo gasy


INSERT INTO types_repas (nom) VALUES
('Plat principal'),
('Entrée'),
('Dessert'),
('Boisson');


INSERT INTO repas (nom, description, image, type_id, prix) VALUES
('Ravitoto sy Henakisoa', 'Feuilles de manioc pilées avec porc', NULL, 1, 6000),
('Romazava', 'Bouillon de viande aux brèdes', NULL, 1, 6500),
('Akoho sy Voanio', 'Poulet au coco à la malgache', NULL, 1, 7000),
('Sambos', 'Sambos à la viande ou légumes', NULL, 2, 2000),
('Mofo Gasy', 'Galette de riz sucrée', NULL, 3, 1500),
('Bonbon Coco', 'Friandise au coco râpé', NULL, 3, 1000),
('Ranovola', 'Eau de riz grillé', NULL, 4, 500),
('Jus naturel', 'Jus de fruits frais locaux', NULL, 4, 2000);



INSERT INTO repas_restaurant (restaurant_id,repas_id) VALUES
(1,1),
(1,2),
(8,3),
(8,4);


-- Données de test pour le système de panier
-- À exécuter après la création des tables

-- 1. STATUTS (nécessaires pour les références)
INSERT INTO statut_commande (appellation) VALUES 
('en cours'),
('validée'),
('payée'),
('en préparation'),
('prête'),
('en livraison'),
('livrée'),
('annulée');

INSERT INTO statut_restaurant (appellation) VALUES 
('ouvert'),
('fermé'),
('temporairement fermé');

INSERT INTO statut_livreur (appellation) VALUES 
('disponible'),
('occupé'),
('hors service');

INSERT INTO statut_livraison (appellation) VALUES 
('en attente'),
('en cours'),
('livrée'),
('échouée');

INSERT INTO statut_zone (appellation) VALUES 
('active'),
('inactive');

INSERT INTO statut_entite (appellation) VALUES 
('active'),
('inactive');

-- 2. TYPES DE REPAS
INSERT INTO types_repas (nom) VALUES 
('Plat principal'),
('Entrée'),
('Dessert'),
('Boisson'),
('Menu complet'),
('Salade'),
('Sandwich'),
('Pizza'),
('Burger'),
('Plat africain');

-- 3. CLIENTS DE TEST
INSERT INTO clients (email, mot_de_passe, contact, prenom, nom) VALUES 
('scurry.com', 'pbkdf2_sha256$600000$test$hashedpassword', '+261 34 12 345 67', 'Steph', 'Curry'),
('marie.martin@email.com', 'pbkdf2_sha256$600000$test$hashedpassword', '+261 32 98 765 43', 'Marie', 'Martin'),
('client.test@email.com', 'pbkdf2_sha256$600000$test$hashedpassword', '+261 33 11 22 33', 'Client', 'Test');

-- 4. RESTAURANTS
INSERT INTO restaurants (nom, adresse, image, geo_position) VALUES 
('Chez Mama', 'Analakely, Antananarivo', '/media/restaurants/chez_mama.jpg', ST_SetSRID(ST_MakePoint(47.5208, -18.8792), 4326)),
('Le Gourmet', 'Isoraka, Antananarivo', '/media/restaurants/le_gourmet.jpg', ST_SetSRID(ST_MakePoint(47.5300, -18.8700), 4326)),
('Pizza Corner', 'Tsaralalana, Antananarivo', '/media/restaurants/pizza_corner.jpg', ST_SetSRID(ST_MakePoint(47.5150, -18.8850), 4326)),
('Saveurs Malgaches', 'Ankadifotsy, Antananarivo', '/media/restaurants/saveurs.jpg', ST_SetSRID(ST_MakePoint(47.5400, -18.8600), 4326));

-- 5. STATUTS DES RESTAURANTS (ouverts)
INSERT INTO historique_statut_restaurant (restaurant_id, statut_id) VALUES 
(1, 1), -- Chez Mama ouvert
(2, 1), -- Le Gourmet ouvert
(3, 1), -- Pizza Corner ouvert
(4, 1); -- Saveurs Malgaches ouvert

-- 6. REPAS VARIÉS
INSERT INTO repas (nom, description, image, type_id, prix) VALUES 
-- Chez Mama (plats malgaches)
('Romazava', 'Plat traditionnel malgache aux brèdes et viande de zébu', '/media/repas/romazava.jpg', 1, 12000),
('Ravitoto', 'Feuilles de manioc pilées avec viande de porc', '/media/repas/ravitoto.jpg', 1, 10000),
('Vary amin''anana', 'Riz aux brèdes avec viande', '/media/repas/vary_anana.jpg', 1, 8000),
('Henakisoa sy tsaramaso', 'Porc aux haricots rouges', '/media/repas/henakisoa.jpg', 1, 11000),

-- Le Gourmet (cuisine française)
('Steak grillé', 'Steak de zébu grillé avec frites maison', '/media/repas/steak.jpg', 1, 18000),
('Poisson grillé', 'Poisson frais grillé avec légumes', '/media/repas/poisson.jpg', 1, 15000),
('Salade César', 'Salade fraîche avec croûtons et parmesan', '/media/repas/cesar.jpg', 6, 7500),
('Crème brûlée', 'Dessert français traditionnel', '/media/repas/creme_brulee.jpg', 3, 4000),

-- Pizza Corner
('Pizza Margherita', 'Pizza classique tomate, mozzarella, basilic', '/media/repas/margherita.jpg', 8, 14000),
('Pizza 4 Fromages', 'Pizza aux quatre fromages', '/media/repas/4fromages.jpg', 8, 16000),
('Pizza Pepperoni', 'Pizza au pepperoni épicé', '/media/repas/pepperoni.jpg', 8, 15000),
('Calzone', 'Pizza fermée farcie à la ricotta', '/media/repas/calzone.jpg', 8, 13000),

-- Saveurs Malgaches
('Akoho sy voanio', 'Poulet au coco traditionnel', '/media/repas/akoho.jpg', 1, 9500),
('Kitoza', 'Viande séchée traditionnelle', '/media/repas/kitoza.jpg', 2, 6000),
('Mofo gasy', 'Pain malgache traditionnel', '/media/repas/mofo.jpg', 2, 2000),
('Ranonapango', 'Eau de riz grillé traditionnel', '/media/repas/ranonapango.jpg', 4, 1500),

-- Boissons communes
('Coca-Cola', 'Boisson gazeuse 33cl', '/media/repas/coca.jpg', 4, 2500),
('Eau minérale', 'Bouteille d''eau 50cl', '/media/repas/eau.jpg', 4, 1500),
('Jus de fruits', 'Jus de fruits frais local', '/media/repas/jus.jpg', 4, 3000),
('THB', 'Bière locale 65cl', '/media/repas/thb.jpg', 4, 4000);

-- 7. ASSOCIATION REPAS-RESTAURANTS
INSERT INTO repas_restaurant (restaurant_id, repas_id) VALUES 
-- Chez Mama (repas 1-4)
(1, 1), (1, 2), (1, 3), (1, 4),
(1, 17), (1, 18), (1, 19), (1, 20), -- boissons

-- Le Gourmet (repas 5-8)
(2, 5), (2, 6), (2, 7), (2, 8),
(2, 17), (2, 18), (2, 19), (2, 20), -- boissons

-- Pizza Corner (repas 9-12)
(3, 9), (3, 10), (3, 11), (3, 12),
(3, 17), (3, 18), (3, 19), (3, 20), -- boissons

-- Saveurs Malgaches (repas 13-16)
(4, 13), (4, 14), (4, 15), (4, 16),
(4, 17), (4, 18), (4, 19), (4, 20); -- boissons

-- 8. DISPONIBILITÉ DES REPAS (tous disponibles)
INSERT INTO disponibilite_repas (repas_id, est_dispo) 
SELECT id, true FROM repas;

-- 9. PROMOTIONS DE TEST
INSERT INTO promotions (repas_id, pourcentage_reduction, date_concerne) VALUES 
(1, 10, CURRENT_DATE), -- Romazava -10%
(9, 15, CURRENT_DATE), -- Pizza Margherita -15%
(5, 20, CURRENT_DATE), -- Steak grillé -20%
(13, 25, CURRENT_DATE); -- Akoho sy voanio -25%

-- 10. ZONES DE LIVRAISON
INSERT INTO zones (nom, description, zone) VALUES 
('Centre-ville', 'Zone du centre-ville d''Antananarivo', 
 ST_SetSRID(ST_MakePolygon(ST_MakeLine(ARRAY[
   ST_MakePoint(47.5100, -18.8700),
   ST_MakePoint(47.5400, -18.8700),
   ST_MakePoint(47.5400, -18.8900),
   ST_MakePoint(47.5100, -18.8900),
   ST_MakePoint(47.5100, -18.8700)
 ])), 4326)),
('Isoraka', 'Quartier d''Isoraka', 
 ST_SetSRID(ST_MakePolygon(ST_MakeLine(ARRAY[
   ST_MakePoint(47.5250, -18.8650),
   ST_MakePoint(47.5450, -18.8650),
   ST_MakePoint(47.5450, -18.8750),
   ST_MakePoint(47.5250, -18.8750),
   ST_MakePoint(47.5250, -18.8650)
 ])), 4326));

-- 11. POINTS DE RÉCUPÉRATION
INSERT INTO point_de_recuperation (nom, geo_position) VALUES 
('Analakely Centre', ST_SetSRID(ST_MakePoint(47.5208, -18.8792), 4326)),
('Gare Soarano', ST_SetSRID(ST_MakePoint(47.5180, -18.8850), 4326)),
('Tsaralalana', ST_SetSRID(ST_MakePoint(47.5150, -18.8860), 4326)),
('Isoraka Bureau', ST_SetSRID(ST_MakePoint(47.5300, -18.8700), 4326)),
('Ankadifotsy Marché', ST_SetSRID(ST_MakePoint(47.5400, -18.8600), 4326)),
('67 Ha', ST_SetSRID(ST_MakePoint(47.5500, -18.8950), 4326)),
('Behoririka', ST_SetSRID(ST_MakePoint(47.5100, -18.8780), 4326)),
('Antaninarenina', ST_SetSRID(ST_MakePoint(47.5220, -18.8720), 4326));

-- 12. STATUTS DES ZONES (actives)
INSERT INTO historique_statut_zone (zone_id, statut_id) VALUES 
(1, 1), -- Centre-ville active
(2, 1); -- Isoraka active

-- 13. ZONES DESSERVIES PAR LES RESTAURANTS
INSERT INTO zones_restaurant (restaurant_id, zone_id) VALUES 
(1, 1), (1, 2), -- Chez Mama dessert les 2 zones
(2, 1), (2, 2), -- Le Gourmet dessert les 2 zones
(3, 1), (3, 2), -- Pizza Corner dessert les 2 zones
(4, 1), (4, 2); -- Saveurs Malgaches dessert les 2 zones

-- 14. HORAIRES DES RESTAURANTS (7 jours par semaine)
INSERT INTO horaire (restaurant_id, le_jour, horaire_debut, horaire_fin) VALUES 
-- Chez Mama (1-7 = lundi à dimanche)
(1, 1, '07:00', '21:00'), (1, 2, '07:00', '21:00'), (1, 3, '07:00', '21:00'),
(1, 4, '07:00', '21:00'), (1, 5, '07:00', '21:00'), (1, 6, '07:00', '22:00'), (1, 7, '08:00', '20:00'),

-- Le Gourmet
(2, 1, '11:00', '23:00'), (2, 2, '11:00', '23:00'), (2, 3, '11:00', '23:00'),
(2, 4, '11:00', '23:00'), (2, 5, '11:00', '23:00'), (2, 6, '11:00', '24:00'), (2, 7, '11:00', '22:00'),

-- Pizza Corner
(3, 1, '16:00', '23:00'), (3, 2, '16:00', '23:00'), (3, 3, '16:00', '23:00'),
(3, 4, '16:00', '23:00'), (3, 5, '16:00', '24:00'), (3, 6, '16:00', '24:00'), (3, 7, '16:00', '23:00'),

-- Saveurs Malgaches
(4, 1, '06:00', '20:00'), (4, 2, '06:00', '20:00'), (4, 3, '06:00', '20:00'),
(4, 4, '06:00', '20:00'), (4, 5, '06:00', '20:00'), (4, 6, '06:00', '21:00'), (4, 7, '07:00', '19:00');

-- 15. COMMISSIONS DES RESTAURANTS
INSERT INTO commissions (restaurant_id, valeur) VALUES 
(1, 15), -- Chez Mama 15%
(2, 12), -- Le Gourmet 12%
(3, 18), -- Pizza Corner 18%
(4, 10); -- Saveurs Malgaches 10%

-- 16. LIVREURS DE TEST
INSERT INTO livreurs (nom, contact, position) VALUES 
('Rakoto Jean', '+261 34 11 22 33', ST_SetSRID(ST_MakePoint(47.5200, -18.8800), 4326)),
('Rabe Paul', '+261 32 44 55 66', ST_SetSRID(ST_MakePoint(47.5350, -18.8750), 4326)),
('Randria Michel', '+261 33 77 88 99', ST_SetSRID(ST_MakePoint(47.5180, -18.8820), 4326));

-- 17. STATUTS DES LIVREURS (disponibles)
INSERT INTO historique_statut_livreur (livreur_id, statut_id) VALUES 
(1, 1), -- Rakoto disponible
(2, 1), -- Rabe disponible
(3, 1); -- Randria disponible

-- 18. ZONES COUVERTES PAR LES LIVREURS
INSERT INTO zones_livreurs (livreur_id, zone_id) VALUES 
(1, 1), (1, 2), -- Rakoto couvre les 2 zones
(2, 1), (2, 2), -- Rabe couvre les 2 zones
(3, 1), (3, 2); -- Randria couvre les 2 zones

-- 19. ZONES PRÉFÉRÉES DES CLIENTS
INSERT INTO zones_clients (client_id, zone_id) VALUES 
(1, 1), -- John préfère le centre-ville
(2, 2), -- Marie préfère Isoraka
(3, 1); -- Client test préfère le centre-ville

-- 20. COMMANDE DE TEST EN COURS POUR LE CLIENT 1 (John Doe)
INSERT INTO commandes (client_id, cree_le) VALUES 
(1, NOW() - INTERVAL '30 minutes');

-- 21. ARTICLES DANS LE PANIER DU CLIENT 1
INSERT INTO commande_repas (commande_id, repas_id, quantite) VALUES 
(1, 1, 2), -- 2 Romazava
(1, 9, 1), -- 1 Pizza Margherita
(1, 17, 3), -- 3 Coca-Cola
(1, 5, 1); -- 1 Steak grillé

-- 22. COMMANDE VIDE POUR LE CLIENT 2 (pour tester panier vide)
INSERT INTO commandes (client_id, cree_le) VALUES 
(2, NOW() - INTERVAL '10 minutes');

-- 23. LIMITE DE COMMANDES JOURNALIÈRES
INSERT INTO limite_commandes_journalieres (nombre_commandes, date) VALUES 
(100, CURRENT_DATE);

-- 24. ENTITÉS ET RÉFÉRENCES (optionnel pour les tests de base)
INSERT INTO entites (nom) VALUES 
('Livraison Express'),
('Service Client'),
('Gestion Restaurants');

INSERT INTO historique_statut_entite (entite_id, statut_id) VALUES 
(1, 1), (2, 1), (3, 1);

INSERT INTO reference_zone_entite (zone_id, entite_id) VALUES 
(1, 1), (1, 2), (1, 3),
(2, 1), (2, 2), (2, 3);

-- 25. RELATIONS ZONES-POINTS DE RÉCUPÉRATION
INSERT INTO historique_zones_recuperation (zone_id, point_recup_id) VALUES 
(1, 1), (1, 2), (1, 3), (1, 7), (1, 8), -- Centre-ville
(2, 4), (2, 5); -- Isoraka

-- INFORMATIONS POUR LES TESTS:
-- 
-- CLIENTS DE TEST:
-- - john.doe@email.com (ID: 1) - A un panier avec des articles
-- - marie.martin@email.com (ID: 2) - A un panier vide
-- - client.test@email.com (ID: 3) - Nouveau client sans commande
-- 
-- MOTS DE PASSE (à hasher avec Django): "password123"
-- 
-- REPAS AVEC PROMOTIONS:
-- - Romazava (ID: 1) - 10% de réduction
-- - Pizza Margherita (ID: 9) - 15% de réduction
-- - Steak grillé (ID: 5) - 20% de réduction
-- - Akoho sy voanio (ID: 13) - 25% de réduction
-- 
-- POINTS DE RÉCUPÉRATION DISPONIBLES:
-- - Analakely Centre, Gare Soarano, Tsaralalana, etc.
-- 
-- POUR TESTER:
-- 1. Connectez-vous avec john.doe@email.com pour voir un panier avec articles
-- 2. Connectez-vous avec marie.martin@email.com pour voir un panier vide
-- 3. Ajoutez/supprimez des articles
-- 4. Testez la validation de commande avec différents points de récupération

