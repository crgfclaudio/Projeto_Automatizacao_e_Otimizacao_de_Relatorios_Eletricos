# ⚡ Automação e Otimização de Relatórios Elétricos

Este projeto tem como objetivo **automatizar o processamento e a estruturação de relatórios técnicos da área elétrica**, convertendo arquivos de texto brutos (.txt) gerados por sistemas de análise elétrica em **planilhas organizadas (Excel e CSV)** com dados prontos para consulta, filtragem e análise.

---

## 🚀 Funcionalidades

- 🧩 **Leitura e parsing automatizado** de relatórios técnicos em formato texto.
- 📊 **Conversão estruturada** dos dados em planilhas Excel e CSV.
- ⚙️ **Filtragem e limpeza inteligente** das informações, incluindo:
  - Separação de blocos de curto-circuito e contribuição.
  - Identificação de barras, circuitos e fases.
  - Cálculo e extração de impedâncias, tensões e correntes.
- 🔍 **Geração automática de análises** em uma segunda aba (“Análise_Evento”), com indicadores elétricos como:
  - Correntes e ângulos para faltas trifásicas, bifásicas e monofásicas.
  - Cálculo de 3I₀, impedância Zan, entre outros parâmetros.
- 💾 **Exportação automática** em múltiplos formatos:
  - `relatorio_anafas_processado.xlsx` (planilha principal)
  - `relatorio_anafas_processado_dados_brutos.csv`
  - `relatorio_anafas_processado_analise_evento.csv`

  - relatorio.txt-> arquivo base utilizado
  - conversão_de_relatorio_e_CSV_organizado.py -> Codigo final que gerar e otimiza os dados do relatorio
---

## 🧠 Motivação

Os relatórios técnicos gerados pelos ANAFAS  são extensos, em formatos TXT e difíceis de manipular manualmente.  
Este projeto surgiu para **eliminar o retrabalho** na extração de dados, **reduzir erros manuais** e **agilizar a análise técnica**, permitindo que engenheiros foquem na interpretação dos resultados, e não na formatação.

---
# Para Maiores Informações técnicas e sobre o ANAFAS E seus relatorios leia Abaixo:
### Arquivo Txt utilizado como teste: relatorio.txt



## 1.Contexto 
O ANAFAS (Análise de Faltas Simultâneas) é um software desenvolvido pelo CEPEL 
(Centro de Pesquisas de Energia Elétrica), voltado para a simulação de 
curtos-circuitos em sistemas elétricos de potência. Seu principal diferencial é a 
capacidade de simular faltas simultâneas, permitindo que engenheiros, pesquisadores 
e estudantes avaliem como diferentes tipos de falhas afetam a rede elétrica de forma 
integrada. 
O programa utiliza modelos derivados do Sistema Interligado Nacional (SIN), que 
representa a rede elétrica brasileira. Dessa forma, os circuitos e barras analisados pelo 
ANAFAS têm correspondência direta com a realidade do país, tornando os estudos mais 
representativos e próximos das condições operacionais reais. 
No âmbito técnico, o ANAFAS possibilita a simulação de diversos tipos de falhas: faltas 
monofásicas (fase-terra), bifásicas, bifásicas-terra e trifásicas. Essas situações são de 
grande relevância para a engenharia elétrica, pois curtos-circuitos representam os 
principais distúrbios enfrentados pela rede de transmissão. O software calcula os valores 
de tensão e corrente em cada fase (A, B e C), bem como impedâncias equivalentes 
durante o evento de falha, fornecendo uma visão detalhada do comportamento do 
sistema. 
Atualmente os resultados são apresentados em forma de relatórios de texto (.txt). 
Esses relatórios incluem o índice de casos simulados, a descrição das contingências 
(como Caso-Base e Close-in), e os valores de tensão e corrente por barra e circuito. 
Apesar de completos, esses relatórios apresentam um problema de usabilidade: o 
formato textual é pouco estruturado e de difícil interpretação, especialmente para 
análises posteriores ou integração com ferramentas modernas de tratamento de dados. 



## 2. Visão

Para estudantes, professores, engenheiros e equipes técnicas que precisam analisar 
relatórios de curto-circuito emitidos pelo simulador de falhas Anafas. 
Que enfrentam dificuldades porque os relatórios gerados pelo Anafas são atualmente 
exportados apenas em .txt, sem estrutura clara, o que gera desperdício de tempo, 
dificuldade de rastreamento de informações específicas e maior complexidade na 
análise. 
O sistema que auxilie na estruturação e análise dos relatórios do ANAFAS. 
É  uma ferramenta de apoio à análise de estudos elétricos. 
Que  simplifica o acesso, otimiza a análise, garante rastreabilidade e facilita a geração 
de relatórios personalizados. 
Ao contrário de processos manuais de interpretação e armazenamento de relatórios 
em texto puro. 
Nosso produto oferece eficiência e facilidade de uso, permitindo que usuários foquem 
na análise técnica em vez de lidar com a desorganização dos dados.



## 🧠 Glossário Técnico
### Buscando auxiliar no entendimento dos dados gerados do relatorio 

| **Termo** | **Descrição** |
|------------|---------------|
| **ANAFAS (Análise de Faltas Simultâneas)** | Software desenvolvido pelo **ELETROBRAS CEPEL** destinado à simulação de curtos-circuitos simultâneos em sistemas elétricos de potência. |
| **CEPEL (Centro de Pesquisas de Energia Elétrica)** | Instituição de pesquisa vinculada à ELETROBRAS responsável pelo desenvolvimento do ANAFAS e outras ferramentas de análise elétrica. |
| **Barra** | Elemento do sistema elétrico que representa um ponto de conexão, onde linhas de transmissão, transformadores, cargas ou geradores se encontram. Em termos simples, é o “nó” da rede elétrica. |
| **Circuito** | Trecho do sistema que conecta duas barras, representando linhas de transmissão ou transformadores. É através dele que a energia elétrica flui de um ponto a outro. |
| **Caso** | Cenário específico de simulação executado no ANAFAS. Cada caso recebe um número de identificação e uma descrição associada. |
| **Caso-Base** | Simulação de referência, utilizada como comparativo para outros cenários. |
| **Caso-Close-in** | Variações do caso-base que representam faltas próximas ou alterações pontuais na rede. |
| **Contingência** | Situação de falha ou indisponibilidade em um componente da rede elétrica (barra, circuito ou transformador). |
| **Falta** | Termo técnico para um curto-circuito. Indica uma conexão indesejada entre fases ou entre uma fase e a terra. |
| **Fase** | Condutor que transporta a corrente elétrica ativa da fonte de energia para os pontos de consumo, possuindo uma diferença de potencial (tensão) em relação ao neutro e à terra, necessários para que o circuito funcione. |
| **FT** | Falta monofásica à terra — curto entre uma fase e o solo. |
| **FF** | Falta bifásica — curto entre duas fases. |
| **FFT** | Falta bifásica-terra — duas fases em curto com o solo. |
| **FFF** | Falta trifásica — curto entre as três fases simultaneamente. |
| **Tensão (TEN.)** | Diferença de potencial elétrico entre dois pontos da rede. |
| **Corrente (CORR.)** | Fluxo de carga elétrica em um circuito. |
| **Impedância** | Grandeza elétrica que expressa a oposição ao fluxo de corrente alternada, combinando resistência e reatância. |
| **Módulo (mod.)** | Valor numérico absoluto de uma grandeza elétrica (tensão ou corrente). |
| **Ângulo (ang.)** | Defasagem temporal de uma onda elétrica em graus. Indica o deslocamento de fase entre diferentes grandezas elétricas. |
| **Fases (A, B, C)** | Referem-se às três fases do sistema trifásico. Esse tipo de sistema é padrão em redes de transmissão de energia elétrica. |
| **Sistema Interligado Nacional (SIN)** | Conjunto que integra a maioria da rede elétrica brasileira, conectando geradores e consumidores em todo o território nacional. |
| **Relatório de Casos** | Arquivo de saída gerado pelo ANAFAS contendo os resultados de cada simulação executada. |
| **Contribuição** | Representa a relação entre a barra de origem e a barra de destino, gerando corrente e/ou impedância conforme o caso analisado. |


