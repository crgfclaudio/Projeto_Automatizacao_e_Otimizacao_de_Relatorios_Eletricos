-- Listar importações que possuem pelo menos um registro no histórico de operações.

SELECT *
FROM controle_importacao c
WHERE EXISTS (
    SELECT 1
    FROM historico_operacoes h
    WHERE h.id_importacao = c.id_importacao
);
