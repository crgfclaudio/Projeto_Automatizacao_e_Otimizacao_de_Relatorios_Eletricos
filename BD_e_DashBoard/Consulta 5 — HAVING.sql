-- Listar apenas os tipos de caso que possuem mais de 200 registros.

SELECT 
    Caso,
    COUNT(*) AS total_registros
FROM dados_brutos_anafas
GROUP BY Caso
HAVING COUNT(*) > 200;
