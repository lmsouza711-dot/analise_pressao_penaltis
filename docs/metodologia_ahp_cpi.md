# 📖 Documentação Metodológica: Índice de Pressão sob Pênalti & Clutch Penalty Index (CPI)

Esta documentação estabelece a fundamentação teórica, a engenharia de recursos (*feature engineering*), a auditoria de integridade de dados e a modelagem matemática por trás do cálculo de estresse cognitivo em cobranças de pênalti da Seleção Brasileira.

---

## 1. Fundamentos Científicos da Pressão no Futebol

O desenvolvimento deste índice é sustentado por estudos científicos empíricos sobre a performance humana sob estresse no esporte:

1. **Predição por Aprendizado de Máquina (Akıncıoğlu, Aydemir & Çil, 2024):** No artigo *"Machine learning-based identification of the strongest predictive features of scoring penalty kick in football"*, os autores demonstraram que variáveis como a semana da liga (representando a fase do campeonato), o placar antes do chute (diferença de gols) e o histórico de aproveitamento do cobrador são os preditores mais fortes para o sucesso ou falha da cobrança. O modelo classificatório alcançou **79,80% de precisão** ao considerar esses fatores contextuais.
2. **Carga e Distração Psicológica (Ellis & Ward, 2022):** Pesquisas com sensores de frequência cardíaca e respiratória confirmaram que o ambiente social e a relevância imediata do gol causam ansiedade cognitiva e alteram a coordenação motora fina do atleta.
3. **Estresse e Ansiedade Situacional (Jordet, 2024):** Geir Jordet identificou que o estresse do cobrador aumenta à medida que o tempo restante diminui, e que o impacto psicológico é significativamente maior quando a cobrança dita se o time vence ou evita uma derrota iminente (*avoid-loss scenarios*).

---

## 2. Engenharia de Variáveis (Feature Engineering)

A variável abstrata "Pressão Psicológica" é mensurada de forma aditiva por meio de 8 variáveis de dados divididas em 4 dimensões analíticas:

| Dimensão | Variável | Critério Contextual | Pontuação (Heurística) |
| :--- | :--- | :--- | :---: |
| **Nível Competitivo** | Competição | Liga Nacional | `+1` |
| | | Competição Continental (ex: Champions, Libertadores) | `+2` |
| | | Copa do Mundo (FIFA World Cup) | `+2.5` |
| | | Seleção Nacional (Amistosos / Qualificatórias) | `+3` |
| | Clássico | Sim | `+1` |
| **Importância do Jogo** | Etapa | Fase de Grupos / Rodada da Liga / Amistoso | `+0` |
| | | Oitavas de Final | `+1` |
| | | Quartas de Final | `+2` |
| | | Semifinal | `+3` |
| | | Final | `+4` |
| | Mata-mata | Sim (Cenário Eliminatório/Taça) | `+2` |
| **Situação do Placar** | Empate | Jogo empatado no momento | `+2` |
| | Time Perdendo | Time do cobrador está atrás no placar | `+3` |
| | Importância do Gol | Amplia vantagem | `+0` |
| | | Diminui desvantagem (mas continua atrás) | `+1` |
| | | Empata o jogo | `+2` |
| | | Coloca o time em vantagem | `+3` |
| **Pressão Temporal** | Minuto | 0' a 30' | `+0` |
| | | 31' a 60' | `+1` |
| | | 61' a 75' | `+2` |
| | | 76' a 90'+ | `+3` |

---

## 3. Determinação de Pesos via AHP (Analytic Hierarchy Process)

Para afastar a subjetividade da atribuição de notas, empregamos o método **AHP (Processo de Hierarquia Analítica)**, uma técnica matemática de decisão multicritério desenvolvida por Thomas Saaty. O AHP pondera as 4 dimensões principais por meio de matrizes de comparação pareada:

### Matriz de Comparação Pareada ($M$)
Comparamos a importância relativa de cada dimensão na geração de pressão psicológica:
1. **Situação de Placar** é considerada moderadamente mais importante que o **Nível Competitivo** (peso 3) e ligeiramente mais importante que **Importância do Jogo** (peso 2) e **Tempo Restante** (peso 2).
2. **Tempo Restante** (bater um pênalti aos 90 minutos) é considerado muito mais importante que o **Nível Competitivo** (peso 3) e comparável à **Importância do Jogo** (peso 1).
3. **Importância do Jogo** é considerada duas vezes mais importante que o **Nível Competitivo** (peso 2).

A ordem das linhas e colunas na matriz é: `[Nível Competitivo, Importância do Jogo, Situação de Placar, Pressão Temporal]`.

$$M = \begin{pmatrix} 
1 & 1/2 & 1/3 & 1/3 \\ 
2 & 1 & 1/2 & 1 \\ 
3 & 2 & 1 & 2 \\ 
3 & 1 & 1/2 & 1 
\end{pmatrix}$$

### Resolução Matemática (Autovetor e Pesos Finais)
Calculando a média geométrica das linhas e normalizando-as, obtemos os pesos de importância das dimensões:
*   **$W_1$ (Nível Competitivo):** `10.9%`
*   **$W_2$ (Importância do Jogo):** `22.5%`
*   **$W_3$ (Situação de Placar):** `41.8%` (Maior causador de pressão)
*   **$W_4$ (Pressão Temporal):** `24.8%`

### Fórmula do Pressure Score Normalizado (AHP 0-100)
Cada dimensão é calculada somando os pontos heurísticos e dividindo pelo seu valor máximo possível (gerando uma nota de 0 a 10). Em seguida, aplica-se os pesos do AHP:

$$\text{Score AHP} = \left( 0.109 \times S_{\text{comp}} + 0.225 \times S_{\text{jogo}} + 0.418 \times S_{\text{placar}} + 0.248 \times S_{\text{tempo}} \right) \times 10$$

---

## 4. O Clutch Penalty Index (CPI)

Para medir a eficácia real do batedor sob o efeito da pressão, criamos o **CPI (Clutch Penalty Index)**:

$$CPI = \frac{\sum \text{Pressure Score de todas as cobranças convertidas}}{\sum \text{Pressure Score de todas as cobranças realizadas}}$$

---

## 5. Auditoria e Integridade dos Dados (Data Quality Auditing)

Um dos pilares do rigor metodológico deste estudo foi a **auditoria de rotulagem de dados**:
*   **A Inconsistência:** O dataset original continha três registros atribuídos a Gabriel Martinelli. Contudo, ao verificar as súmulas e dados do *Transfermarkt*, constatou-se que esses pênaltis correspondiam a partidas disputadas pelo Lyon (2021) e Newcastle (2026) contra Lorient, Leeds e Brentford, respectivamente.
*   **A Correção:** Os registros foram reatribuídos a **Bruno Guimarães**, jogador do Newcastle e ex-Lyon.
*   **O Impacto no Modelo:** Gabriel Martinelli possui 0 cobranças sênior em tempo normal, enquanto Bruno Guimarães contava com 3 cobranças na carreira antes da partida contra a Noruega.

---

## 6. Mapeamento de Cobradores de Pênalti da Seleção (Starting XI - Pré-Jogo)

Ao expandir o escopo para o time titular sênior (dados históricos acumulados antes da partida do dia 05/07/2026), os dados revelam três categorias de cobradores:

1. **Batedores Ativos (com dados históricos):**
   *   **Vini Jr:** 13 cobranças (Aproveitamento: 11 acertos, 2 erros | CPI: 0.766).
   *   **Bruno Guimarães:** 3 cobranças (Aproveitamento: 3 acertos, 0 erros | CPI: 1.000).
   *   **Matheus Cunha:** 4 cobranças sênior (Aproveitamento: 4 acertos, 0 erros | CPI: 1.000).
   *   **Rayan Vitor:** 1 cobrança sênior (Aproveitamento: 1 acerto, 0 erros | CPI: 1.000).
2. **Sem Histórico de Cobranças em Tempo Normal (CPI = N/A):**
   *   Gabriel Martinelli, Casemiro, Danilo, Marquinhos, Gabriel Magalhães, Douglas Santos.
3. **Goleiro (CPI = N/A):**
   *   Alisson Becker.
