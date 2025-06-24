CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    contact TEXT,
    prenom VARCHAR(100),
    nom VARCHAR(100)
);

-- Livreurs
CREATE TABLE livreurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    contact TEXT,
    position GEOGRAPHY(POINT, 4326)
);