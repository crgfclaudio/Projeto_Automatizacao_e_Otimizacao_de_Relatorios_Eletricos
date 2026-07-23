USE database_relatorios_anafas;

-- Identificar registros de dados brutos que são nulos ou não nulos


SELECT *
FROM dados_brutos_anafas
WHERE id_importacao IS NULL;

SELECT *
FROM dados_brutos_anafas
WHERE Impedancia_Ponto IS NULL;

SELECT *
FROM analise_evento
WHERE id_importacao IS not NULL;
