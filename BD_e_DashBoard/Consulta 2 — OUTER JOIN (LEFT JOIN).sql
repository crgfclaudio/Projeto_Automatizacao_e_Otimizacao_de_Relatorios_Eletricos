-- 1. define qual schema esta sendo utilizando
USE database_relatorios_anafas;

-- Listar todas as importações, mesmo aquelas que não possuem análise de evento.

SELECT
    c.id_importacao,
    c.nome_arquivo,
    a.idAnalise
FROM controle_importacao c
LEFT JOIN analise_evento a
    ON c.id_importacao = a.id_importacao;
