-- Listar arquivos gerados apenas para importações que possuem mais de 1 operação registrada.

SELECT *
FROM arquivos_gerados
WHERE id_importacao IN (
    SELECT id_importacao
    FROM historico_operacoes
    GROUP BY id_importacao
    HAVING COUNT(*) > 1
);
