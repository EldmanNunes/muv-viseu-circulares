# 🚌 MUViseu Circulares - Consultor de Horários & Rotas (Linhas C1 e C2)

Uma aplicação web interativa desenvolvida em **Python** e **Streamlit** para consulta rápida, visualização gráfica e gestão dos horários e paragens dos autocarros das **Linhas C1 e C2** do MUV (**Mobilidade Urbana de Viseu**).

---

## 🌟 Principais Funcionalidades

### 1. 🔍 Consulta Inteligente & 3 Regimes de Horários
- **Suporte aos 3 Regimes MUV:** 
  - 💼 **Dias Úteis**: Frequências regulares (06:30 às 19:50).
  - 📅 **Sábados**: Horários das 07:00 às 18:00.
  - 🔴 **Domingos e Feriados (**):** Subconjunto dos horários de sábado assinalados com `**` nas tabelas oficiais MUV (07:00 às 12:00).
- **Cálculo de Viagens Circulares:** Suporte ao circuito contínuo de Viseu com passagem pelo terminal.
- **⚡ Comparador C1 vs C2:** Identifica a linha mais rápida para a sua viagem e indica quantos minutos poupa.
- **Contagem Decrescente:** Tempo restante em tempo real para a partida.

### 2. 📍 Navegação por Pontos de Referência
- Mapeamento de locais emblemáticos nos seletores de paragem:
  - 🚌 Central de Camionagem / Rodoviária (COMV)
  - 🛍️ Shopping Palácio do Gelo & Supermercado Continente
  - 🏥 Hospital de São Teotónio
  - 🎓 Instituto Politécnico de Viseu (IPV) & Residências
  - 🏛️ Loja do Cidadão & Biblioteca Municipal
  - 🌲 Parque do Fontelo & Estádio
  - 🏡 Minha Casa (Manuel Silva Almeida)

### 3. ⭐ Gestor de Percursos Favoritos
- Guarde as suas viagens diárias e aceda-lhes instantaneamente com 1-clique.

### 4. 📂 Upload Automático e Parsing de PDFs (com separação dos 3 Regimes)
- Upload de PDFs oficiais da MUV com extração automática por `pdfplumber` e RegEx.
- **Parsing por Regime:** Classificação automática das partidas em **Dias Úteis**, **Sábados** e **Domingos/Feriados (**)**.
- **Persistência Local (JSON Cache):** Gravação permanente em `custom_schedules.json`.

### 5. 📥 Exportação Multi-Formato
- Tabela **CSV**, Relatório **PDF** e Lembrete de Calendário **`.ics`** (Google/Apple/Outlook).

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Framework Web:** Streamlit
- **Processamento de Dados:** Pandas
- **Visualização Geoespacial:** PyDeck
- **Leitura de PDFs:** `pdfplumber`
- **Geração de PDF:** `fpdf2`

---

## 📋 Ficheiro `requirements.txt`

```text
streamlit>=1.28.0
pandas>=2.0.0
pydeck>=0.8.0
fpdf2>=2.7.0
pdfplumber>=0.10.0
```

---

## 📄 Isenção de Responsabilidade
Aplicação independente concebida para a mobilidade em Viseu com base nos horários oficiais do MUV.
