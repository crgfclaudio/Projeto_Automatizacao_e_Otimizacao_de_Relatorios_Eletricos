-- 1. define qual schema esta sendo utilizando
USE database_relatorios_anafas;

-- 2. cria as tables utilizadas 
CREATE TABLE controle_importacao (
    id_importacao BIGINT AUTO_INCREMENT PRIMARY KEY,

    nome_arquivo VARCHAR(255) NOT NULL,

    data_importacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    observacao VARCHAR(255),

    UNIQUE (nome_arquivo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE dados_brutos_anafas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    id_importacao BIGINT NULL,

    Caso INT NOT NULL,
    Falta VARCHAR(10) NOT NULL,
    Localizacao VARCHAR(255),
    Contingencia VARCHAR(255),

    Fase ENUM('A','B','C','P','N','Z') NOT NULL,

    TensaoModuloCurto DOUBLE,
    TensaoAnguloCurto DOUBLE,

    CorrenteModuloCurto DOUBLE,
    CorrenteAnguloCurto DOUBLE,

    BarraOrigem VARCHAR(255),
    TensaoModuloOrigem DOUBLE,
    TensaoAnguloOrigem DOUBLE,

    BarraDestino VARCHAR(255),
    TensaoModuloDestino DOUBLE,
    TensaoAnguloDestino DOUBLE,

    Circuito VARCHAR(100),
    CorrenteModuloCircuito DOUBLE,
    CorrenteAnguloCircuito DOUBLE,

    Identificacao VARCHAR(255),

    Impedancia_Ponto VARCHAR(5),
    Impedancia_Mod DOUBLE,
    Impedancia_Ang DOUBLE,

    INDEX idx_identificacao (Identificacao),
    INDEX idx_falta (Falta),
    INDEX idx_caso (Caso),
    INDEX idx_contingencia (Contingencia),
    INDEX idx_fase (Fase),

    CONSTRAINT fk_dados_importacao
        FOREIGN KEY (id_importacao)
        REFERENCES controle_importacao(id_importacao)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE analise_evento (
    idAnalise INT AUTO_INCREMENT PRIMARY KEY,

    id_importacao BIGINT NULL,

    Identificacao VARCHAR(100),
    Localizacao VARCHAR(255),

    IA_CC3F DOUBLE,
    ANG_IA_CC3F DOUBLE,

    IB_CC2F DOUBLE,
    ANG_IB_CC2F DOUBLE,

    IA_CCFT DOUBLE,
    ANG_IA_CCFT DOUBLE,

    X3I0_CCFT DOUBLE,
    ANG_3I0_CCFT DOUBLE,

    Zan_CCFT DOUBLE,
    ANG_Zan_CCFT DOUBLE,

    X3I0_FT_CloseIn DOUBLE,
    ANG_3I0_FT_CloseIn DOUBLE,

    IA_FFF_CloseIn DOUBLE,
    ANG_IA_FFF_CloseIn DOUBLE,

    CONSTRAINT fk_analise_importacao
        FOREIGN KEY (id_importacao)
        REFERENCES controle_importacao(id_importacao)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE historico_operacoes (
    id_historico BIGINT AUTO_INCREMENT PRIMARY KEY,

    id_importacao BIGINT NOT NULL,

    tipo_operacao VARCHAR(50) NOT NULL,
    descricao TEXT,

    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_hist_importacao
        FOREIGN KEY (id_importacao)
        REFERENCES controle_importacao(id_importacao)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE arquivos_gerados (
    id_arquivo BIGINT AUTO_INCREMENT PRIMARY KEY,

    id_importacao BIGINT NOT NULL,

    nome_arquivo VARCHAR(255) NOT NULL,
    tipo_arquivo ENUM('CSV','XLSX','PDF') NOT NULL,
    caminho_arquivo VARCHAR(500),

    data_geracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_arq_importacao
        FOREIGN KEY (id_importacao)
        REFERENCES controle_importacao(id_importacao)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- 3. Utiliza Table Data Import Wizard para as table analise_evento e dados_brutos_anafas

-- 4. Registra ou reaproveita a importação garantindo que cada importacao é unica
INSERT INTO controle_importacao (nome_arquivo, observacao)
VALUES ('relatorio_anafas_processado.csv', 'Primeira carga ANAFAS')
ON DUPLICATE KEY UPDATE
    id_importacao = LAST_INSERT_ID(id_importacao);

-- 5. Guarda o ID da importação
SET @id_importacao := LAST_INSERT_ID();

-- 6. Associa aos dados brutos
UPDATE dados_brutos_anafas
SET id_importacao = @id_importacao
WHERE id_importacao IS NULL;

-- 7. Associa à análise de evento
UPDATE analise_evento
SET id_importacao = @id_importacao
WHERE id_importacao IS NULL;

-- 8. Registra ações importantes no sistema  
INSERT INTO historico_operacoes (id_importacao, tipo_operacao, descricao)
VALUES (@id_importacao, 'IMPORT_CSV', 'Importação dos dados brutos ANAFAS');

INSERT INTO historico_operacoes (id_importacao, tipo_operacao, descricao)
VALUES (@id_importacao, 'GERACAO_ANALISE', 'Tabela analise_evento gerada com sucesso');

-- 9. Guardar informações sobre arquivos produzidos pelo sistema
INSERT INTO arquivos_gerados
(id_importacao, nome_arquivo, tipo_arquivo, caminho_arquivo)
VALUES
(@id_importacao, 'relatorio_anafas_processado.csv', 'CSV', '/dados/anafas/');
 
 INSERT INTO arquivos_gerados
(id_importacao, nome_arquivo, tipo_arquivo, caminho_arquivo)
VALUES
(@id_importacao, 'relatorio_anafas_processado.xlsx', 'XLSX', '/dados/anafas/');

-- 10. Mostrando as Tabelas Criadas e todas as colunas

SELECT * FROM dados_brutos_anafas;
SELECT * FROM analise_evento;
SELECT * FROM controle_importacao;
SELECT * FROM historico_operacoes;
SELECT * FROM arquivos_gerados;










