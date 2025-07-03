-- Script de réinitialisation complète de la base de données

-- 1. Désactiver temporairement les contraintes de clé étrangère
SET session_replication_role = 'replica';

-- 2. Vider toutes les tables en commençant par les tables enfants
-- Ordre de suppression soigneusement organisé pour respecter les dépendances
TRUNCATE TABLE
    core_historiquestatutzone,
    core_historiquestatutrestaurant,
    core_historiquestatutlivreur,
    core_historiquestatutlivraison,
    core_historiquestatutcommande,
    core_promotion,
    core_commanderepas,
    core_livraison,
    core_commande,
    core_zoneclient,
    core_zonelivreur,
    core_zonerestaurant,
    core_restaurantrepas,
    core_repas,
    core_typerepas,
    core_livreur,
    core_pointrecup,
    core_client,
    core_restaurant,
    core_zone,
    core_statutcommande,
    core_statutlivraison,
    core_statutlivreur,
    core_statutrestaurant,
    core_statutzone,
    core_modepaiement,
    core_horaire,
    core_horairespecial,
    core_commission
RESTART IDENTITY CASCADE;

-- 3. Réinitialiser les séquences pour toutes les tables avec auto-incrément
-- Liste complète et organisée des séquences à réinitialiser
DO $$
DECLARE
    seq_record RECORD;
    seq_name TEXT;
    table_name TEXT;
    column_name TEXT;
BEGIN
    FOR seq_record IN 
        SELECT 
            n.nspname AS schema_name,
            c.relname AS table_name,
            a.attname AS column_name
        FROM pg_class c
        JOIN pg_attribute a ON a.attrelid = c.oid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'r'
        AND a.attnum > 0
        AND NOT a.attisdropped
        AND pg_get_serial_sequence(quote_ident(n.nspname) || '.' || quote_ident(c.relname), a.attname) IS NOT NULL
        AND n.nspname = 'public' -- ou votre schéma si différent
    LOOP
        seq_name := pg_get_serial_sequence(quote_ident(seq_record.schema_name) || '.' || quote_ident(seq_record.table_name), seq_record.column_name);
        EXECUTE format('SELECT setval(%L, COALESCE((SELECT MAX(%I) FROM %I.%I), 0) + 1, false)', 
                      seq_name, 
                      seq_record.column_name, 
                      seq_record.schema_name, 
                      seq_record.table_name);
    END LOOP;
END $$;

-- 4. Réactiver toutes les contraintes
SET session_replication_role = 'origin';

-- 5. Vérification (optionnelle)
-- Cette requête peut être utilisée pour vérifier que toutes les tables sont vides
SELECT n.nspname AS schema_name, c.relname AS table_name, c.reltuples AS rows
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' 
AND n.nspname NOT IN ('pg_catalog', 'information_schema')
AND n.nspname = 'public' -- ou votre schéma si différent
ORDER BY c.reltuples DESC;