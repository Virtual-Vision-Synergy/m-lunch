INSERT INTO clients (email, mot_de_passe, contact, prenom, nom)
VALUES ('test@example.com','pbkdf2_sha256$1000000$kwNeF2rJE7CFT2D36oBcjN$vSQgEvCUyu9OXzXvT7PPqlzhapv6/mLwqOOFsxxM+CA=','0341234567','Jean','Rakoto'),
       ('bob@example.com', 'pbkdf2_sha256$1000000$Sa2WOaNUsu0BgwVlByLweo$4tq/VO3lZLONVfETT9RBYOCfy8O22DuytPY+HMLVu4I=', '0347654321', 'Bob', 'Rakoto');

INSERT INTO zones (nom, description, zone)
VALUES
('Analakely', 'Centre ville', ST_GeogFromText('POLYGON((47.516 -18.911, 47.521 -18.911, 47.521 -18.906, 47.516 -18.906, 47.516 -18.911))')),
('Ankatso', 'Quartier universitaire', ST_GeogFromText('POLYGON((47.510 -18.900, 47.515 -18.900, 47.515 -18.895, 47.510 -18.895, 47.510 -18.900))'));

INSERT INTO restaurants (nom, horaire_debut, horaire_fin, adresse, image, geo_position)
VALUES
('Pizza Tana', '10:00', '22:00', 'Rue de lUniversité, Ankatso', 'https://via.placeholder.com/100x75?text=PizzaTana', ST_GeogFromText('POINT(47.512 -18.897)')),
('Snack City', '08:00', '20:00', 'Place de lIndépendance, Analakely', 'https://via.placeholder.com/100x75?text=SnackCity', ST_GeogFromText('POINT(47.519 -18.908)'));

-- Pizza Tana in Ankatso
INSERT INTO zones_restaurant (restaurant_id, zone_id)
VALUES (1, 2);

-- Snack City in Analakely
INSERT INTO zones_restaurant (restaurant_id, zone_id)
VALUES (2, 1);

-- jean prefers Analakely (zone_id = 1)
INSERT INTO zones_clients (client_id, zone_id)
VALUES (1, 1);

-- Bob prefers Ankatso (zone_id = 2)
INSERT INTO zones_clients (client_id, zone_id)
VALUES (2, 2);

INSERT INTO types_repas (nom) VALUES
('Entrée'), ('Plat principal'), ('Dessert'), ('Boisson');

INSERT INTO repas (nom, description, image, type_id, prix)
VALUES
('Salade verte', 'Légumes frais et vinaigrette', 'https://via.placeholder.com/100x75?text=Salade', 1, 2500),
('Steak frites', 'Steak grillé avec pommes frites', 'https://via.placeholder.com/100x75?text=Steak', 2, 9500),
('Tarte au citron', 'Tarte maison citronnée', 'https://via.placeholder.com/100x75?text=Tarte', 3, 3500),
('Coca-Cola', 'Bouteille 50cl', 'https://via.placeholder.com/100x75?text=Coca', 4, 2000);

-- Entrée
INSERT INTO repas (nom, description, image, type_id, prix) VALUES
('Nems au poulet', 'Nems croustillants au poulet et légumes', 'https://via.placeholder.com/100x75?text=Nems', 1, 3000);

-- Plat principal
INSERT INTO repas (nom, description, image, type_id, prix) VALUES
('Burger classique', 'Burger au steak haché, fromage, salade', 'https://via.placeholder.com/100x75?text=Burger', 2, 8500);

-- Dessert
INSERT INTO repas (nom, description, image, type_id, prix) VALUES
('Brownie', 'Brownie chocolat fondant', 'https://via.placeholder.com/100x75?text=Brownie', 3, 4000);

-- Boisson
INSERT INTO repas (nom, description, image, type_id, prix) VALUES
('Jus de mangue', 'Jus de mangue naturel 33cl', 'https://via.placeholder.com/100x75?text=Mangue', 4, 2500);

INSERT INTO repas_restaurant (restaurant_id, repas_id)
VALUES (1, 1), (1, 2), (1, 3), (1, 4);

INSERT INTO repas_restaurant (restaurant_id, repas_id) VALUES
(2, 5), (2, 6), (2, 7), (2, 8);

-- This meal is available now
INSERT INTO disponibilite_repas (repas_id, debut, fin)
VALUES (5, NOW() - INTERVAL '1 hour', NOW() + INTERVAL '2 hours');

-- This meal is NOT available
INSERT INTO disponibilite_repas (repas_id, debut, fin)
VALUES (6, NOW() - INTERVAL '5 hours', NOW() - INTERVAL '1 hour');

INSERT INTO statut_commande (id, appellation) VALUES
(1, 'En attente'),
(2, 'En préparation'),
(3, 'En livraison'),
(4, 'Livrée'),
(5, 'Annulée');

-- Alice placed 2 orders
INSERT INTO commandes (id, client_id, cree_le) VALUES
(1, 1, NOW() - INTERVAL '5 days'),
(2, 1, NOW() - INTERVAL '1 day');

-- Bob placed 1 order
INSERT INTO commandes (id, client_id, cree_le) VALUES
(3, 2, NOW() - INTERVAL '2 days');

-- Commande 1 (Alice)
INSERT INTO commande_repas (commande_id, repas_id, quantite) VALUES
(1, 5, 2),
(1, 6, 1);

-- Commande 2 (Alice)
INSERT INTO commande_repas (commande_id, repas_id, quantite) VALUES
(2, 7, 1);

-- Commande 3 (Bob)
INSERT INTO commande_repas (commande_id, repas_id, quantite) VALUES
(3, 8, 3);

-- Commande 1 (Alice): Livrée
INSERT INTO historique_statut_commande (commande_id, statut_id, mis_a_jour_le) VALUES
(1, 1, NOW() - INTERVAL '5 days'),
(1, 2, NOW() - INTERVAL '4 days'),
(1, 3, NOW() - INTERVAL '3 days'),
(1, 4, NOW() - INTERVAL '2 days');

-- Commande 2 (Alice): Annulée
INSERT INTO historique_statut_commande (commande_id, statut_id, mis_a_jour_le) VALUES
(2, 1, NOW() - INTERVAL '1 day'),
(2, 5, NOW() - INTERVAL '12 hours');

-- Commande 3 (Bob): En livraison
INSERT INTO historique_statut_commande (commande_id, statut_id, mis_a_jour_le) VALUES
(3, 1, NOW() - INTERVAL '2 days'),
(3, 2, NOW() - INTERVAL '36 hours'),
(3, 3, NOW() - INTERVAL '18 hours');
INSERT INTO point_de_recuperation (nom, geo_position)
VALUES
  ('Point A', ST_SetSRID(ST_MakePoint(47.5162, -18.8792), 4326)),  -- Antananarivo approx
  ('Point B', ST_SetSRID(ST_MakePoint(47.5321, -18.9137), 4326)),
  ('Point C', ST_SetSRID(ST_MakePoint(47.5450, -18.8900), 4326)),
  ('Point D', ST_SetSRID(ST_MakePoint(47.5650, -18.8950), 4326));
