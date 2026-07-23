import re
import os
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ============================================================
# 1. CONFIGURAÇÃO DO BANCO DE DADOS
# ============================================================
DB_USER = 'root'
DB_PASS_RAW = '192837465aA!'  # Sua senha
DB_HOST = 'localhost'
DB_NAME = 'database_relatorios_anafas'

encoded_pass = urllib.parse.quote_plus(DB_PASS_RAW)
db_connection_str = f'mysql+mysqlconnector://{DB_USER}:{encoded_pass}@{DB_HOST}/{DB_NAME}'
db_engine = create_engine(db_connection_str)

UPLOAD_FOLDER = 'uploads_historico'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================
# 2. LÓGICA DE PARSING (ENGINE ANAFAS)
# ============================================================
PHASES = ["A", "B", "C", "P", "N", "Z"]
IMP_COMBS = ["AB", "AN", "BC", "BN", "CA", "CN"]

def to_num_or_none(s):
    if s is None: return None
    s = str(s).strip().replace(",", ".")
    try: return float(s)
    except: return None

def split_minus_fix(line):
    return re.sub(r'(?<=\d)-(?=\d)', ' -', line)

def create_id_code(circuito, barra_origem, barra_destino):
    c = str(circuito or "").strip()
    bo = str(barra_origem or "").strip()
    bd = str(barra_destino or "").strip()
    return f"{c[-4:] if c else 'NA'}-{bo[:4] if bo else 'NA'}-{bd[:4] if bd else 'NA'}-{c[:2] if c else 'NA'}"

def processar_txt_anafas(filepath):
    print(">>> Iniciando processamento do TXT...")
    re_case = re.compile(r"^\s*(\d+)\s+(\w+)\s+(.+?)\s{2,}(.+)$")
    re_bar = re.compile(r"Bar\.?\s*(\d+)\s*\(([^)]+)\)", re.IGNORECASE)
    re_circuit = re.compile(r"Cir\.\s*([^\s]+)", re.IGNORECASE)
    re_triple = re.compile(r'([A-Za-z]{1,3})\s*([+-]?\d+(?:[.,]\d+)?)\s*([+-]?\d+(?:[.,]\d+)?)')

    try:
        with open(filepath, "r", encoding="latin-1") as f:
            lines = [ln.rstrip("\n") for ln in f]
    except Exception as e:
        print(f"Erro de leitura: {e}")
        return pd.DataFrame(), pd.DataFrame()

    rows = []
    i = 0
    current_case = None; secao = None
    curto_info = {"id": None, "nome": None, "tensao": {}, "corrente": {}}
    origem_contrib = {"id": None, "nome": None, "tensao": {}}

    while i < len(lines):
        raw = lines[i]; line = raw.strip()
        if "CEPEL" in raw or "ANAFAS" in raw or "DELETE" in raw or "-----" in raw: i += 1; continue

        mcase = re_case.match(line)
        if mcase:
            current_case = { "Caso": mcase.group(1), "Falta": mcase.group(2), "Localizacao": mcase.group(3).strip(), "Contingencia": mcase.group(4).strip() }
            curto_info = {"id": None, "nome": None, "tensao": {}, "corrente": {}}
            origem_contrib = {"id": None, "nome": None, "tensao": {}}
            secao = None; i += 1; continue

        tnorm = re.sub(r"\s+", "", line).upper()
        if "CURTO" in tnorm: secao = "CURTO"; i += 1; continue
        if "CONTRIB" in tnorm: secao = "CONTRIB"; i += 1; continue

        if secao == "CURTO":
            mbar = re_bar.search(raw)
            if mbar:
                curto_info["id"] = mbar.group(1); curto_info["nome"] = mbar.group(2).strip()
                curto_info["tensao"], curto_info["corrente"] = {}, {}; i += 1; continue
            if re.match(r'^[A-Za-z]', line):
                lproc = split_minus_fix(raw)
                triples = re_triple.findall(lproc)
                triples = [(l.upper(), to_num_or_none(v1), to_num_or_none(v2)) for (l,v1,v2) in triples if l.upper() != "G"]
                if triples:
                    half = len(triples)//2 if len(triples) >= 2 else len(triples)
                    for lab, m, a in triples[:half]:
                        if lab in PHASES: curto_info["tensao"][lab] = (m, a)
                    for lab, m, a in triples[half:]:
                        if lab in PHASES: curto_info["corrente"][lab] = (m, a)
            i += 1; continue

        if secao == "CONTRIB":
            mbar = re_bar.search(raw)
            if mbar:
                barra_id, barra_nome = mbar.group(1), mbar.group(2).strip()
                circ_m = re_circuit.search(raw)
                if not circ_m:
                    origem_contrib["id"], origem_contrib["nome"] = barra_id, barra_nome
                    origem_contrib["tensao"] = {}
                    j = i + 1
                    while j < len(lines) and not re_bar.search(lines[j]) and not re_case.match(lines[j]):
                        ln_proc = split_minus_fix(lines[j])
                        triples = re_triple.findall(ln_proc)
                        triples = [(l.upper(), to_num_or_none(mv), to_num_or_none(av)) for (l, mv, av) in triples]
                        for lab, m, a in triples:
                            if lab in PHASES: origem_contrib["tensao"][lab] = (m, a)
                        j += 1
                    i = j; continue
                
                circuito = circ_m.group(1).strip()
                dest_tens, dest_corr, imp_map = {}, {}, {}
                j = i + 1
                while j < len(lines):
                    ln_raw = lines[j]
                    if not ln_raw.strip(): j += 1; continue
                    if re_bar.search(ln_raw) or re_case.match(ln_raw) or "CEPEL" in ln_raw: break
                    lp = split_minus_fix(ln_raw)
                    triples = re_triple.findall(lp)
                    triples = [(l.upper(), to_num_or_none(mv), to_num_or_none(av)) for (l, mv, av) in triples if l.upper() != "G"]
                    if triples:
                        one_letter = [(l, m, a) for (l, m, a) in triples if len(l) == 1 and l in PHASES]
                        two_letter = [(l, m, a) for (l, m, a) in triples if len(l) > 1]
                        if one_letter:
                            for l, m, a in one_letter:
                                if l not in dest_tens: dest_tens[l] = (m, a)
                                else: dest_corr[l] = (m, a)
                        for l, m, a in two_letter: imp_map[l] = (m, a)
                    j += 1
                
                base_row = {"Caso": current_case.get("Caso"), "Falta": current_case.get("Falta"), "Localizacao": current_case.get("Localizacao"), "Contingencia": current_case.get("Contingencia"), "BarraOrigem": f"{origem_contrib.get('id','')} {origem_contrib.get('nome','')}".strip(), "BarraDestino": f"{barra_id} {barra_nome}", "Circuito": circuito, "Identificacao": create_id_code(circuito, origem_contrib.get('id',''), barra_id)}
                impedancias = [imp_map.get(comb, (None, None)) for comb in IMP_COMBS]
                has_imp = bool(imp_map)
                for k, ph in enumerate(PHASES):
                    row = base_row.copy()
                    if has_imp and k < len(IMP_COMBS):
                        row["Impedancia_Ponto"] = IMP_COMBS[k]; row["Impedancia_Mod"] = to_num_or_none(impedancias[k][0]); row["Impedancia_Ang"] = to_num_or_none(impedancias[k][1])
                    else:
                        row["Impedancia_Ponto"] = None; row["Impedancia_Mod"] = None; row["Impedancia_Ang"] = None
                    row.update({"Fase": ph, "TensaoModuloCurto": curto_info["tensao"].get(ph, (None,None))[0], "TensaoAnguloCurto": curto_info["tensao"].get(ph, (None,None))[1], "CorrenteModuloCurto": curto_info["corrente"].get(ph, (None,None))[0], "CorrenteAnguloCurto": curto_info["corrente"].get(ph, (None,None))[1], "TensaoModuloOrigem": origem_contrib["tensao"].get(ph, (None,None))[0], "TensaoAnguloOrigem": origem_contrib["tensao"].get(ph, (None,None))[1], "TensaoModuloDestino": dest_tens.get(ph, (None,None))[0], "TensaoAnguloDestino": dest_tens.get(ph, (None,None))[1], "CorrenteModuloCircuito": dest_corr.get(ph, (None,None))[0], "CorrenteAnguloCircuito": dest_corr.get(ph, (None,None))[1]})
                    rows.append(row)
                i = j; continue
        i += 1
    
    df_brutos = pd.DataFrame(rows)
    analise_rows = []
    if not df_brutos.empty:
        df_brutos["Identificacao"] = df_brutos["Identificacao"].astype(str).fillna("").str.strip()
        filtro_L = df_brutos[df_brutos["Identificacao"].str.contains(r"-\w*[LT]$", na=False)]
        for ident, sub in filtro_L.groupby("Identificacao"):
            def g(s, f, c):
                v = s[s["Fase"] == f][c].values
                return float(v[0]) if len(v)>0 and pd.notna(v[0]) else None
            base = sub[sub["Contingencia"].str.contains("CASO", case=False, na=False)]
            close = sub[sub["Contingencia"].str.contains("CLOSE", case=False, na=False)]
            analise_rows.append({
                "Identificacao": ident, "Localizacao": sub["Localizacao"].values[0],
                "IA_CC3F": g(base[base["Falta"].str.contains("FFF")], "A", "CorrenteModuloCircuito"),
                "ANG_IA_CC3F": g(base[base["Falta"].str.contains("FFF")], "A", "CorrenteAnguloCircuito"),
                "IB_CC2F": g(base[base["Falta"].str.contains("FF") & ~base["Falta"].str.contains("FFF")], "B", "CorrenteModuloCircuito"),
                "ANG_IB_CC2F": g(base[base["Falta"].str.contains("FF") & ~base["Falta"].str.contains("FFF")], "B", "CorrenteAnguloCircuito"),
                "IA_CCFT": g(base[base["Falta"].str.contains("FT")], "A", "CorrenteModuloCircuito"),
                "ANG_IA_CCFT": g(base[base["Falta"].str.contains("FT")], "A", "CorrenteAnguloCircuito"),
                "Zan_CCFT": g(sub[sub["Impedancia_Ponto"] == "AN"], "A", "Impedancia_Mod"),
                "ANG_Zan_CCFT": g(sub[sub["Impedancia_Ponto"] == "AN"], "A", "Impedancia_Ang"),
                "X3I0_CCFT": (g(base[base["Falta"].str.contains("FT")], "Z", "CorrenteModuloCircuito") or 0) * 3,
                "ANG_3I0_CCFT": g(base[base["Falta"].str.contains("FT")], "Z", "CorrenteAnguloCircuito"),
                "X3I0_FT_CloseIn": (g(close[close["Falta"].str.contains("FT")], "A", "CorrenteModuloCircuito") or 0) * 3,
                "ANG_3I0_FT_CloseIn": g(close[close["Falta"].str.contains("FT")], "A", "CorrenteAnguloCircuito"),
                "IA_FFF_CloseIn": g(close[close["Falta"].str.contains("FFF")], "A", "CorrenteModuloCircuito"),
                "ANG_IA_FFF_CloseIn": g(close[close["Falta"].str.contains("FFF")], "A", "CorrenteAnguloCircuito"),
            })
    return df_brutos, pd.DataFrame(analise_rows)

# ============================================================
# 3. ROTAS DA API
# ============================================================

@app.route('/api/upload-txt', methods=['POST'])
def upload_e_processar():
    if 'file' not in request.files: return jsonify({'error': 'Arquivo vazio'}), 400
    file = request.files['file']
    filename = file.filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_name = f"{timestamp}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, saved_name)
    file.save(filepath)

    try:
        df_brutos, df_analise = processar_txt_anafas(filepath)
        
        with db_engine.connect() as conn:
            # 1. Controle Importacao
            conn.execute(text("INSERT INTO controle_importacao (nome_arquivo, observacao) VALUES (:nome, :obs)"), 
                         {"nome": saved_name, "obs": "Via Web"})
            conn.commit()
            
            # Pega ID
            id_imp = conn.execute(text("SELECT MAX(id_importacao) FROM controle_importacao")).fetchone()[0]

            # 2. Historico Operacoes (CORRIGIDO: usa data_hora ou DEFAULT)
            # Vamos omitir a coluna de data para usar o DEFAULT CURRENT_TIMESTAMP do banco
            conn.execute(text("INSERT INTO historico_operacoes (id_importacao, tipo_operacao, descricao) VALUES (:id, 'IMPORTACAO', :desc)"),
                         {"id": id_imp, "desc": f"Processamento de {filename}"})
            
            # 3. Arquivos Gerados (Requer que ENUM aceite 'TXT')
            conn.execute(text("INSERT INTO arquivos_gerados (id_importacao, nome_arquivo, tipo_arquivo, caminho_arquivo) VALUES (:id, :nome, 'TXT', :path)"),
                         {"id": id_imp, "nome": saved_name, "path": filepath})
            conn.commit()

        # Inserção de Dados
        if not df_brutos.empty:
            df_brutos['id_importacao'] = id_imp
            cols = ['id_importacao', 'Caso', 'Falta', 'Localizacao', 'Contingencia', 'Fase', 'TensaoModuloCurto', 'TensaoAnguloCurto', 'CorrenteModuloCurto', 'CorrenteAnguloCurto', 'BarraOrigem', 'TensaoModuloOrigem', 'TensaoAnguloOrigem', 'BarraDestino', 'TensaoModuloDestino', 'TensaoAnguloDestino', 'Circuito', 'CorrenteModuloCircuito', 'CorrenteAnguloCircuito', 'Identificacao', 'Impedancia_Ponto', 'Impedancia_Mod', 'Impedancia_Ang']
            df_brutos[df_brutos.columns.intersection(cols)].to_sql('dados_brutos_anafas', con=db_engine, if_exists='append', index=False, chunksize=1000)

        if not df_analise.empty:
            df_analise['id_importacao'] = id_imp
            df_analise.to_sql('analise_evento', con=db_engine, if_exists='append', index=False)

        return jsonify({'message': 'Sucesso', 'id': id_imp, 'rows': len(df_brutos)})
    except Exception as e:
        print(f"ERRO: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    with db_engine.connect() as conn:
        try:
            # CORRIGIDO: usa h.data_hora em vez de h.data_operacao
            sql = text("""
                SELECT 
                    h.tipo_operacao, 
                    h.descricao, 
                    c.nome_arquivo, 
                    DATE_FORMAT(h.data_hora, '%d/%m/%Y %H:%i') as data_formatada
                FROM historico_operacoes h
                LEFT JOIN controle_importacao c ON h.id_importacao = c.id_importacao
                ORDER BY h.id_historico DESC 
                LIMIT 50
            """)
            res = conn.execute(sql)
            return jsonify([dict(r._mapping) for r in res])
        except Exception as e:
            print(f"Erro logs: {e}")
            return jsonify({'erro_banco': str(e)}), 500

# Demais rotas (Dashboard, Brutos, Analise)
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    with db_engine.connect() as conn:
        imp = conn.execute(text("SELECT COUNT(*) FROM controle_importacao")).fetchone()[0]
        evs = conn.execute(text("SELECT COUNT(*) FROM dados_brutos_anafas")).fetchone()[0]
        chart = conn.execute(text("SELECT Localizacao, COUNT(*) as qtd FROM dados_brutos_anafas GROUP BY Localizacao ORDER BY qtd DESC LIMIT 5"))
        return jsonify({'imports': imp, 'events': evs, 'chart': [dict(r._mapping) for r in chart]})

@app.route('/api/dados/brutos', methods=['GET'])
def get_brutos():
    page = int(request.args.get('page', 1))
    limit = 50
    offset = (page-1)*limit
    with db_engine.connect() as conn:
        res = conn.execute(text(f"SELECT * FROM dados_brutos_anafas ORDER BY id DESC LIMIT {limit} OFFSET {offset}"))
        return jsonify([dict(r._mapping) for r in res])

@app.route('/api/dados/analise', methods=['GET'])
def get_analise():
    with db_engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM analise_evento ORDER BY idAnalise DESC LIMIT 100"))
        return jsonify([dict(r._mapping) for r in res])

if __name__ == '__main__':
    app.run(port=5000, debug=True)