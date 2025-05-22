
-- Création des tables principales pour Cinéphoria

CREATE TABLE genre (
    id SERIAL PRIMARY KEY,
    genre VARCHAR(50) NOT NULL
);

CREATE TABLE qualite (
    id SERIAL PRIMARY KEY,
    type_qualite VARCHAR(50),
    prix_seance FLOAT
);

CREATE TABLE utilisateur (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    identifiant VARCHAR(20) UNIQUE,
    nom VARCHAR(50),
    prenom VARCHAR(50),
    ville VARCHAR(50),
    pays VARCHAR(50),
    is_active BOOLEAN,
    is_staff BOOLEAN
);

CREATE TABLE cinema (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    adresse TEXT,
    cp VARCHAR(10),
    ville VARCHAR(50),
    pays VARCHAR(50),
    telephone VARCHAR(20),
    horaire_ouverture TIME,
    horaire_fermeture TIME
);

CREATE TABLE film (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(100),
    duree INTEGER,
    synopsis TEXT,
    affiche_url VARCHAR(300),
    date_ajout DATE,
    age_minimum INTEGER,
    label_coup_de_coeur BOOLEAN,
    note FLOAT,
    genre_id INTEGER REFERENCES genre(id),
    modificateur_id INTEGER REFERENCES utilisateur(id)
);

CREATE TABLE salle (
    id SERIAL PRIMARY KEY,
    numero_salle VARCHAR(2),
    total_places INTEGER,
    places_pmr INTEGER,
    qualite_id INTEGER REFERENCES qualite(id),
    cinema_id INTEGER REFERENCES cinema(id)
);

CREATE TABLE siege (
    id SERIAL PRIMARY KEY,
    salle_id INTEGER REFERENCES salle(id),
    numero_siege INTEGER,
    rangee VARCHAR(10),
    occupe BOOLEAN,
    place_pmr BOOLEAN
);

CREATE TABLE seance (
    id SERIAL PRIMARY KEY,
    film_id INTEGER REFERENCES film(id),
    salle_id INTEGER REFERENCES salle(id),
    heure_debut TIME,
    heure_fin TIME,
    jours_diffusion JSON
);

CREATE TABLE reservation (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateur(id),
    seance_id INTEGER REFERENCES seance(id),
    date_reservation DATE,
    nombre_places INTEGER,
    prix_total FLOAT,
    statut VARCHAR(50)
);

CREATE TABLE reservation_siege (
    id SERIAL PRIMARY KEY,
    reservation_id INTEGER REFERENCES reservation(id),
    siege_id INTEGER REFERENCES siege(id)
);

CREATE TABLE billet (
    id SERIAL PRIMARY KEY,
    reservation_id INTEGER UNIQUE REFERENCES reservation(id),
    numero_billet VARCHAR(20),
    qr_code VARCHAR(255)
);

CREATE TABLE avis (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateur(id),
    film_id INTEGER REFERENCES film(id),
    note FLOAT,
    commentaire TEXT,
    date DATE,
    valide BOOLEAN
);

CREATE TABLE contact (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateur(id),
    cinema_id INTEGER REFERENCES cinema(id),
    nom VARCHAR(100),
    objet_demande VARCHAR(100),
    description TEXT,
    date DATE,
    statut VARCHAR(50)
);

CREATE TABLE incident (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateur(id),
    salle_id INTEGER REFERENCES salle(id),
    siege_id INTEGER REFERENCES siege(id),
    type_incident VARCHAR(100),
    type_materiel VARCHAR(100),
    description TEXT,
    date DATE,
    statut VARCHAR(50)
);

CREATE TABLE log_activite (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateur(id),
    action VARCHAR(255),
    date TIMESTAMP,
    details TEXT
);

CREATE TABLE notification (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateur(id),
    message VARCHAR(255),
    date TIMESTAMP,
    lue BOOLEAN
);

CREATE TABLE cinema_film (
    id SERIAL PRIMARY KEY,
    cinema_id INTEGER REFERENCES cinema(id),
    film_id INTEGER REFERENCES film(id)
);
