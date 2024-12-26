.echo on
ATTACH DATABASE 'db_email_analysis.db' AS analysis;

SELECT COUNT(*) as unanalyzed_count 
FROM emails e 
WHERE NOT EXISTS (
    SELECT 1 
    FROM analysis.email_analysis a 
    WHERE a.email_id = e.id
);
