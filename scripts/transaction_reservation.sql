
BEGIN;

-- Étape 1 : création de la réservation
INSERT INTO reservation (utilisateur_id, seance_id, date_reservation, nombre_places, prix_total, statut)
VALUES (3, 12, CURRENT_DATE, 2, 21.00, 'confirmée')
RETURNING id;

-- Supposons que l'ID retourné est 42
-- Étape 2 : assignation des sièges
INSERT INTO reservation_siege (reservation_id, siege_id)
VALUES 
  (42, 101),
  (42, 102);

-- Étape 3 : génération du billet
INSERT INTO billet (reservation_id, numero_billet, qr_code)
VALUES (
  42,
  'ABC123XYZ',
  'qrcodes/qr_code_billet_ABC123XYZ.png'
);

COMMIT;
