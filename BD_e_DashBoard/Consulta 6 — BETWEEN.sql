-- Buscar análises de evento com corrente trifásica entre dois valores.

SELECT *
FROM analise_evento
WHERE IA_CC3F BETWEEN 100 AND 500;
