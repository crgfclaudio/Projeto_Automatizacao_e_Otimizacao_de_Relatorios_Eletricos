-- Contar quantos registros de dados brutos existem por tipo de falta.

SELECT 
    Falta,
    COUNT(*) AS total_registros
FROM dados_brutos_anafas
GROUP BY Falta;

