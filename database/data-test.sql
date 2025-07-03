INSERT INTO core_client (email, mot_de_passe, contact, prenom, nom, date_inscri)
VALUES (
    'jean.dupont@example.com',
    'pbkdf2_sha256$1000000$u4yE7LSeHt9Uj0rpGgYMri$1m8Ot1gjRDSfm7q1xMMQQonwpWYSKVkULFkmncO9g4A=',
    '0341234567',
    'Jean',
    'Dupont',
    NOW()
);

INSERT INTO core_restaurant (nom, adresse, image, geo_position) VALUES
('La Varangue', '17 Rue Printsy Ratsimamanga, Antananarivo', 'varangue.jpg', '-18.8792, 47.5079'),
('Kudéta', 'Lot II M 85 Ambohijatovo, Antananarivo', 'kudeta.jpg', '-18.9103, 47.5255'),
('Le Carré', 'Rue Ravelojaona, Antananarivo', 'carre.jpg', '-18.9150, 47.5310'),
('Sakamanga', 'Ambohidahy, Antananarivo', 'sakamanga.jpg', '-18.9050, 47.5265'),
('La Table dEugène', 'Ivandry, Antananarivo', 'eugene.jpg', '-18.8700, 47.5320'),
('Café de la Gare', 'Soarano, Antananarivo', 'cafegare.jpg', '-18.9110, 47.5180');

INSERT INTO core_zone (nom, description, zone) VALUES
('Antananarivo Centre', 'Centre-ville de Tana', 'Antananarivo, Centre'),
('Antananarivo Nord', 'Quartiers nord de Tana', 'Antananarivo, Nord');

INSERT INTO core_zonerestaurant (zone_id, restaurant_id) VALUES
(1, 1),  -- Centre - La Varangue
(1, 2),  -- Centre - Kudéta
(2, 3),  -- Nord   - Le Carré
(2, 4),  -- Nord   - Sakamanga
(2, 5),  -- Nord   - La Table d’Eugène
(1, 6);  -- Centre - Café de la Gare
