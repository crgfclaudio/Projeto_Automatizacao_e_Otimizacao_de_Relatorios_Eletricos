-- Obter o valor máximo e médio da corrente trifásica (IA_CC3F)

SELECT
    MAX(IA_CC3F) AS corrente_maxima,
    AVG(IA_CC3F) AS corrente_media
FROM analise_evento;
