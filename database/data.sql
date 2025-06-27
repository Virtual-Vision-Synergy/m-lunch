

--////////////////////////////////////DONNEE DE TEST NATAOKO Ewan--//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

-- Statuts donnee
-- Statuts Restaurant
INSERT INTO statut_restaurant (appellation) VALUES ('Ouvert'), ('Ferme');

-- Statuts Commande
INSERT INTO statut_commande (appellation) VALUES ('En attente'), ('En cours'), ('Livre');

-- Statuts Livreur
INSERT INTO statut_livreur (appellation) VALUES ('Disponible'), ('En livraison'), ('Inactif');

-- Statuts Livraison
INSERT INTO statut_livraison (appellation) VALUES ('En attente'), ('En livraison'), ('Livree'), ('Annulee');

--Zones donnee
-- Zones (secteurs)
INSERT INTO zones (nom, description, zone) VALUES
('Analakely', 'Centre-ville', NULL),
('Isoraka', 'Quartier animé', NULL),
('Ivandry', 'Zone résidentielle', NULL),
('Ankorondrano', 'Quartier d affaires', NULL);

--Restaurants et associations donnnee
-- Restaurants
INSERT INTO restaurants (nom, horaire_debut, horaire_fin, adresse, image, geo_position) VALUES
('Le Gourmet', '08:00', '22:00', '12 rue de la Paix', 'gourmet.png', NULL),
('Pizza Express', '10:00', '23:00', '45 avenue des Fleurs', 'pizza.png', NULL),
('Sakafo Malagasy', '07:30', '21:00', 'Marché Analakely', 'sakafo.png', NULL),
('Burger House', '09:00', '22:00', 'Boulevard Joffre', 'burger.png', NULL);

-- Lier restaurants à zones
INSERT INTO zones_restaurant (restaurant_id, zone_id) VALUES
(1, 1),
(2, 2),
(3, 1),
(3, 3),
(4, 4);

-- Commissions
INSERT INTO commissions (restaurant_id, valeur) VALUES
(1, 10),
(2, 15),
(3, 12),
(4, 8);

-- Historique des statuts restaurants
INSERT INTO historique_statut_restaurant (restaurant_id, statut_id, mis_a_jour_le) VALUES
(1, 1, NOW() - INTERVAL '10 days'),
(2, 1, NOW() - INTERVAL '9 days'),
(3, 1, NOW() - INTERVAL '8 days'),
(4, 1, NOW() - INTERVAL '7 days');

--Types de repas et repas donnee
-- Types de repas
INSERT INTO types_repas (nom) VALUES 
('Pizza'), ('Malagasy'), ('Sandwich'), ('Burger'), ('Salade');

-- Repas
INSERT INTO repas (nom, description, image, type_id, prix) VALUES
('Pizza Margherita', 'Pizza classique', 'pizza_margherita.png', 1, 12000),
('Pizza Reine', 'Pizza garnie', 'pizza_reine.png', 1, 15000),
('Romazava', 'Plat traditionnel malgache', 'romazava.png', 2, 9000),
('Ravitoto', 'Ravitoto sy henakisoa', 'ravitoto.png', 2, 9500),
('Sandwich Poulet', 'Sandwich au poulet', 'sandwich_poulet.png', 3, 7000),
('Burger Boeuf', 'Burger au boeuf', 'burger_boeuf.png', 4, 10000),
('Burger Poulet', 'Burger au poulet', 'burger_poulet.png', 4, 9500),
('Salade César', 'Salade fraîche', 'salade_cesar.png', 5, 8000);

-- Repas proposés par les restaurants
INSERT INTO repas_restaurant (restaurant_id, repas_id) VALUES
(1, 3), (1, 4), -- Le Gourmet : Romazava, Ravitoto
(2, 1), (2, 2), -- Pizza Express : Margherita, Reine
(3, 3), (3, 5), -- Sakafo Malagasy : Romazava, Sandwich Poulet
(4, 6), (4, 7), (4, 8); -- Burger House : Burger Boeuf, Burger Poulet, Salade César

--Clients donnee
-- Clients
INSERT INTO clients (email, mot_de_passe, contact, prenom, nom) VALUES
('alice@example.com', 'pass123', '0321234567', 'Alice', 'Randria'),
('bob@example.com', 'pass456', '0349876543', 'Bob', 'Rakoto'),
('carole@example.com', 'pass789', '0331122334', 'Carole', 'Rasoanaivo');

--Commandes et détails des commandes donnee
-- Commandes (différentes dates pour test graphique)
INSERT INTO commandes (client_id, cree_le) VALUES
(1, NOW() - INTERVAL '6 days'),
(2, NOW() - INTERVAL '5 days'),
(3, NOW() - INTERVAL '4 days'),
(1, NOW() - INTERVAL '3 days'),
(2, NOW() - INTERVAL '2 days'),
(3, NOW() - INTERVAL '1 days'),
(1, NOW());

-- Commande repas (quantités variées)
INSERT INTO commande_repas (commande_id, repas_id, quantite, ajoute_le) VALUES
(1, 3, 2, NOW() - INTERVAL '6 days'), -- Le Gourmet, Romazava
(1, 4, 1, NOW() - INTERVAL '6 days'), -- Le Gourmet, Ravitoto
(2, 1, 1, NOW() - INTERVAL '5 days'), -- Pizza Express, Margherita
(2, 2, 2, NOW() - INTERVAL '5 days'), -- Pizza Express, Reine
(3, 5, 3, NOW() - INTERVAL '4 days'), -- Sakafo Malagasy, Sandwich Poulet
(4, 6, 2, NOW() - INTERVAL '3 days'), -- Burger House, Burger Boeuf
(4, 8, 1, NOW() - INTERVAL '3 days'), -- Burger House, Salade César
(5, 7, 2, NOW() - INTERVAL '2 days'), -- Burger House, Burger Poulet
(6, 3, 1, NOW() - INTERVAL '1 days'), -- Sakafo Malagasy, Romazava
(7, 2, 1, NOW()); -- Pizza Express, Reine

-- Historique statut commande
INSERT INTO historique_statut_commande (commande_id, statut_id, mis_a_jour_le) VALUES
(1, 3, NOW() - INTERVAL '5 days'),
(2, 3, NOW() - INTERVAL '4 days'),
(3, 3, NOW() - INTERVAL '3 days'),
(4, 3, NOW() - INTERVAL '2 days'),
(5, 3, NOW() - INTERVAL '1 days'),
(6, 3, NOW()),
(7, 3, NOW());

-- Commandes additionnelles pour tests de livraison
INSERT INTO commandes (client_id, cree_le) VALUES
(1, NOW() - INTERVAL '2 days'),
(2, NOW() - INTERVAL '1 day'),
(1, NOW() - INTERVAL '12 hours'),
(2, NOW() - INTERVAL '8 hours'),
(1, NOW() - INTERVAL '4 hours');

-- Détails des commandes additionnelles
INSERT INTO commande_repas (commande_id, repas_id, quantite) VALUES
(8, 1, 2), -- Commande 8
(8, 2, 1),
(9, 3, 1), -- Commande 9
(9, 4, 2),
(10, 5, 2), -- Commande 10
(11, 6, 1), -- Commande 11
(12, 1, 3); -- Commande 12

--Livreurs et affectations donnee
-- Livreurs
INSERT INTO livreurs (nom, contact) VALUES
('Jean Rakoto', '0321234567'),
('Miora Randria', '0349876543'),
('Hery Rasoa', '0331122334'),
('Lala Rabe', '0329988776');

-- Affectation secteur (zones_livreurs)
INSERT INTO zones_livreurs (livreur_id, zone_id) VALUES
(1, 1), -- Jean à Analakely
(2, 2), -- Miora à Isoraka
(3, 3), -- Hery à Ivandry
(4, 1); -- Lala à Analakely

-- Historique statut livreur
INSERT INTO historique_statut_livreur (livreur_id, statut_id, mis_a_jour_le) VALUES
(1, 1, NOW() - INTERVAL '2 days'),
(2, 2, NOW() - INTERVAL '1 days'),
(3, 3, NOW() - INTERVAL '3 days'),
(4, 1, NOW());

--Livraisons donnee
-- Livraisons pour commandes initiales
INSERT INTO livraisons (livreur_id, commande_id) VALUES
(1, 1),
(2, 2),
(4, 3);

-- Historique statut livraison initial
INSERT INTO historique_statut_livraison (livraison_id, statut_id, mis_a_jour_le) VALUES
(1, 3, NOW() - INTERVAL '1 days'),
(2, 2, NOW()),
(3, 1, NOW());

-- Livraisons pour commandes additionnelles
INSERT INTO livraisons (livreur_id, commande_id, attribue_le) VALUES
(1, 8, NOW() - INTERVAL '2 days'),
(2, 9, NOW() - INTERVAL '1 day'),
(3, 10, NOW() - INTERVAL '12 hours'),
(1, 11, NOW() - INTERVAL '8 hours'),
(2, 12, NOW() - INTERVAL '4 hours');

-- Historique statut livraison additionnel
INSERT INTO historique_statut_livraison (livraison_id, statut_id, mis_a_jour_le) VALUES
-- Livraison 4: Livree
(4, 1, NOW() - INTERVAL '2 days'),
(4, 2, NOW() - INTERVAL '1 day 23 hours'),
(4, 3, NOW() - INTERVAL '1 day 22 hours'),

-- Livraison 5: En livraison
(5, 1, NOW() - INTERVAL '1 day'),
(5, 2, NOW() - INTERVAL '23 hours'),

-- Livraison 6: En attente
(6, 1, NOW() - INTERVAL '12 hours'),

-- Livraison 7: Annulee
(7, 1, NOW() - INTERVAL '8 hours'),
(7, 4, NOW() - INTERVAL '7 hours'),

-- Livraison 8: En attente
(8, 1, NOW() - INTERVAL '4 hours');

--/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



-- View: v_restaurants_list
CREATE OR REPLACE VIEW v_restaurants_list AS
SELECT
    r.id,
    r.nom,
    r.horaire_debut,
    r.horaire_fin,
    r.adresse,
    r.image,
    c.valeur AS commission,
    z.nom AS secteur,
    s.statut AS statut
FROM restaurants r
LEFT JOIN commissions c ON c.restaurant_id = r.id
LEFT JOIN zones_restaurant zr ON zr.restaurant_id = r.id
LEFT JOIN zones z ON z.id = zr.zone_id
LEFT JOIN (
    SELECT hsr.restaurant_id, sr.appellation AS statut
    FROM (
        SELECT DISTINCT ON (restaurant_id) *
        FROM historique_statut_restaurant
        ORDER BY restaurant_id, mis_a_jour_le DESC, id DESC
    ) hsr
    JOIN statut_restaurant sr ON hsr.statut_id = sr.id
) s ON s.restaurant_id = r.id;

-- View: v_livreurs_list
CREATE OR REPLACE VIEW v_livreurs_list AS
SELECT
    l.id,
    l.nom,
    l.contact,
    l.photo,
    z.nom AS secteur,
    s.appellation AS statut
FROM livreurs l
LEFT JOIN zones_livreurs zl ON zl.livreur_id = l.id
LEFT JOIN zones z ON z.id = zl.zone_id
LEFT JOIN (
    SELECT hsl.livreur_id, sl.appellation
    FROM (
        SELECT DISTINCT ON (livreur_id) *
        FROM historique_statut_livreur
        ORDER BY livreur_id, mis_a_jour_le DESC, id DESC
    ) hsl
    JOIN statut_livreur sl ON hsl.statut_id = sl.id
) s ON s.livreur_id = l.id;

-- View: v_livraisons_list
CREATE OR REPLACE VIEW v_livraisons_list AS
SELECT
    l.id,
    l.livreur_id,
    l.commande_id,
    l.attribue_le,
    lr.nom AS livreur_nom,
    r.nom AS restaurant_nom,
    z.nom AS secteur,
    sl.appellation AS statut,
    SUM(cr.quantite * rp.prix) AS total_commande
FROM livraisons l
JOIN livreurs lr ON l.livreur_id = lr.id
JOIN commandes c ON l.commande_id = c.id
JOIN commande_repas cr ON c.id = cr.commande_id
JOIN repas rp ON cr.repas_id = rp.id
JOIN repas_restaurant rr ON rp.id = rr.repas_id
JOIN restaurants r ON rr.restaurant_id = r.id
JOIN zones_restaurant zr ON r.id = zr.restaurant_id
JOIN zones z ON z.id = zr.zone_id
LEFT JOIN (
    SELECT hsl.livraison_id, sl.appellation
    FROM (
        SELECT DISTINCT ON (livraison_id) *
        FROM historique_statut_livraison
        ORDER BY livraison_id, mis_a_jour_le DESC, id DESC
    ) hsl
    JOIN statut_livraison sl ON hsl.statut_id = sl.id
) sl ON sl.livraison_id = l.id
GROUP BY l.id, lr.nom, r.nom, z.nom, sl.appellation;

--view livreur-detail
CREATE OR REPLACE VIEW v_livreurs_detail AS
SELECT
    l.*,
    z.nom AS secteur,
    s.appellation AS statut
FROM livreurs l
LEFT JOIN zones_livreurs zl ON zl.livreur_id = l.id
LEFT JOIN zones z ON z.id = zl.zone_id
LEFT JOIN (
    SELECT hsl.livreur_id, sl.appellation
    FROM (
        SELECT DISTINCT ON (livreur_id) *
        FROM historique_statut_livreur
        ORDER BY livreur_id, mis_a_jour_le DESC, id DESC
    ) hsl
    JOIN statut_livreur sl ON hsl.statut_id = sl.id
) s ON s.livreur_id = l.id;

--view restaurant-detail
CREATE OR REPLACE VIEW v_restaurants_detail AS
SELECT
    r.*,
    c.valeur as commission,
    s.appellation as statut,
    z.nom as secteur
FROM restaurants r
LEFT JOIN commissions c ON c.restaurant_id = r.id
LEFT JOIN (
    SELECT DISTINCT ON (restaurant_id) restaurant_id, statut_id
    FROM historique_statut_restaurant
    ORDER BY restaurant_id, mis_a_jour_le DESC, id DESC
) hsr ON hsr.restaurant_id = r.id
LEFT JOIN statut_restaurant s ON s.id = hsr.statut_id
LEFT JOIN zones_restaurant zr ON zr.restaurant_id = r.id
LEFT JOIN zones z ON z.id = zr.zone_id;

--view livraisons-detail
CREATE OR REPLACE VIEW v_livraisons_detail AS
SELECT
    l.id,
    l.livreur_id,
    l.commande_id,
    l.attribue_le,
    lr.nom AS livreur_nom,
    r.nom AS restaurant_nom,
    z.nom AS secteur,
    sl.appellation AS statut,
    SUM(cr.quantite * rp.prix) AS total_commande
FROM livraisons l
JOIN livreurs lr ON l.livreur_id = lr.id
JOIN commandes c ON l.commande_id = c.id
JOIN commande_repas cr ON c.id = cr.commande_id
JOIN repas rp ON cr.repas_id = rp.id
JOIN repas_restaurant rr ON rp.id = rr.repas_id
JOIN restaurants r ON rr.restaurant_id = r.id
JOIN zones_restaurant zr ON r.id = zr.restaurant_id
JOIN zones z ON z.id = zr.zone_id
LEFT JOIN (
    SELECT hsl.livraison_id, sl.appellation
    FROM (
        SELECT DISTINCT ON (livraison_id) *
        FROM historique_statut_livraison
        ORDER BY livraison_id, mis_a_jour_le DESC, id DESC
    ) hsl
    JOIN statut_livraison sl ON hsl.statut_id = sl.id
) sl ON sl.livraison_id = l.id
WHERE l.id = %s
GROUP BY l.id, lr.nom, r.nom, z.nom, sl.appellation;

--restaurant-orders
CREATE OR REPLACE VIEW v_restaurant_orders AS
SELECT
    c.id,
    c.cree_le,
    cl.nom AS client_nom,
    r.id AS restaurant_id
FROM commandes c
JOIN clients cl ON cl.id = c.client_id
JOIN commande_repas cr ON cr.commande_id = c.id
JOIN repas_restaurant rr ON rr.repas_id = cr.repas_id
JOIN restaurants r ON r.id = rr.restaurant_id
GROUP BY c.id, c.cree_le, cl.nom, r.id;

--view restaurant-commandes-en-cours
CREATE OR REPLACE VIEW v_restaurant_commandes_en_cours AS
SELECT
    rr.restaurant_id,
    COUNT(DISTINCT c.id) AS nb
FROM commandes c
JOIN commande_repas cr ON cr.commande_id = c.id
JOIN repas r ON r.id = cr.repas_id
JOIN repas_restaurant rr ON rr.repas_id = r.id
WHERE c.id IN (
    SELECT hsc.commande_id
    FROM historique_statut_commande hsc
    JOIN statut_commande sc ON sc.id = hsc.statut_id
    WHERE sc.appellation IN ('En attente', 'En cours')
)
GROUP BY rr.restaurant_id;

--view restaurant-status-history
CREATE OR REPLACE VIEW v_restaurant_status_history AS
SELECT 
    h.id, h.restaurant_id, h.statut_id, h.mis_a_jour_le,
    sr.appellation as statut_nom
FROM historique_statut_restaurant h
JOIN statut_restaurant sr ON h.statut_id = sr.id;


-- Vue pour le total brut et le nombre de commandes livrées par restaurant et par jour
CREATE OR REPLACE VIEW v_restaurant_financial_daily AS
SELECT
    rr.restaurant_id,
    DATE(c.cree_le) AS jour,
    COALESCE(SUM(cr.quantite * rp.prix), 0) AS total,
    COUNT(DISTINCT c.id) AS nb_commandes
FROM commandes c
JOIN commande_repas cr ON cr.commande_id = c.id
JOIN repas rp ON rp.id = cr.repas_id
JOIN repas_restaurant rr ON rr.repas_id = rp.id
JOIN livraisons l ON l.commande_id = c.id
JOIN (
    SELECT hsl.livraison_id, sl.appellation
    FROM (
        SELECT DISTINCT ON (livraison_id) *
        FROM historique_statut_livraison
        ORDER BY livraison_id, mis_a_jour_le DESC, id DESC
    ) hsl
    JOIN statut_livraison sl ON hsl.statut_id = sl.id
) latest_status ON latest_status.livraison_id = l.id
WHERE latest_status.appellation = 'Livree'
GROUP BY rr.restaurant_id, DATE(c.cree_le);

-- Vue pour le total brut et le nombre de commandes livrées par restaurant et par mois
CREATE OR REPLACE VIEW v_restaurant_financial_monthly AS
SELECT
    rr.restaurant_id,
    TO_CHAR(DATE_TRUNC('month', c.cree_le), 'MM/YYYY') AS mois,
    COALESCE(SUM(cr.quantite * rp.prix), 0) AS total,
    COUNT(DISTINCT c.id) AS nb_commandes
FROM commandes c
JOIN commande_repas cr ON cr.commande_id = c.id
JOIN repas rp ON rp.id = cr.repas_id
JOIN repas_restaurant rr ON rr.repas_id = rp.id
JOIN livraisons l ON l.commande_id = c.id
JOIN (
    SELECT hsl.livraison_id, sl.appellation
    FROM (
        SELECT DISTINCT ON (livraison_id) *
        FROM historique_statut_livraison
        ORDER BY livraison_id, mis_a_jour_le DESC, id DESC
    ) hsl
    JOIN statut_livraison sl ON hsl.statut_id = sl.id
) latest_status ON latest_status.livraison_id = l.id
WHERE latest_status.appellation = 'Livree'
GROUP BY rr.restaurant_id, DATE_TRUNC('month', c.cree_le);

-- Vue pour le total brut et le nombre de commandes livrées sur une période
CREATE OR REPLACE VIEW v_restaurant_financial_period AS
SELECT
    rr.restaurant_id,
    COALESCE(SUM(cr.quantite * rp.prix), 0) AS total_brut,
    COUNT(DISTINCT c.id) AS nb_commandes
FROM commandes c
JOIN commande_repas cr ON cr.commande_id = c.id
JOIN repas rp ON rp.id = cr.repas_id
JOIN repas_restaurant rr ON rr.repas_id = rp.id
JOIN livraisons l ON l.commande_id = c.id
JOIN (
    SELECT hsl.livraison_id, sl.appellation
    FROM (
        SELECT DISTINCT ON (livraison_id) *
        FROM historique_statut_livraison
        ORDER BY livraison_id, mis_a_jour_le DESC, id DESC
    ) hsl
    JOIN statut_livraison sl ON hsl.statut_id = sl.id
) latest_status ON latest_status.livraison_id = l.id
WHERE latest_status.appellation = 'Livree'
GROUP BY rr.restaurant_id;