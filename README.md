# 🚌 MUV Viseu - Consultor de Horários & Rotas (Linhas C1 e C2)

Uma aplicação web interativa desenvolvida em **Python** e **Streamlit** para consulta rápida, visualização gráfica e gestão dos horários e paragens dos autocarros das **Linhas C1 e C2** do MUV (**Mobilidade Urbana de Viseu**).

---

## 🌟 Principais Funcionalidades

### 1. 🔍 Consulta Inteligente de Viagens
- **Cálculo de Viagens Circulares:** Suporte completo ao circuito contínuo de Viseu. Se a paragem de destino for antecedente no percurso, a aplicação calcula automaticamente a viagem na volta seguinte com passagem pelo terminal.
- **Filtro Temporal Dinâmico:** Escolha de horário de referência com suporte a botão instantâneo **"⏱️ Usar Hora Atual"**.
- **Contagem Decrescente:** Exibição do tempo restante para a partida da paragem de origem (*ex.: "Faltam 8 min"* ou *"A sair agora"*).
- **Regime de Dias:** Seleção entre **Dias Úteis** e **Sábados, Domingos e Feriados**.

### 2. 🗺️ Mapa Interativo de Paragens e Percurso (`PyDeck`)
- Visualização geoespacial das paragens ao longo de toda a cidade de Viseu.
- **Marcadores Coloridos:**
  - 🟢 **Verde:** Paragem de Origem selecionada.
  - 🔴 **Vermelho:** Paragem de Destino selecionada.
  - 🔵 **Azul:** Paragens intermédias do circuito.
- **Linha de Rota:** Trajeto visual unindo ordenadamente todas as paragens da linha.

### 3. 📂 Upload Automático e Parsing de Ficheiros PDF
- Possibilidade de fazer upload de novos ficheiros PDF oficiais de horários da MUV.
- Extração automática de dados utilizando a biblioteca `pdfplumber` e Expressões Regulares (`re`).
- **Persistência Local (JSON Cache):** Os novos horários e paragens extraídos são guardados localmente em `custom_schedules.json`, mantendo as alterações salvas permanentemente entre sessões.
- **Painel de Pré-visualização:** Conferência dos dados extraídos do PDF antes da importação definitiva.
- **Botão de Restauro:** Opção de restaurar os dados originais oficiais de Setembro/2025 a qualquer momento.

### 4. 📥 Exportação Multi-Formato
- **Tabela CSV:** Descarregue a lista de resultados calculados para análise ou utilização externa.
- **Relatório PDF:** Geração instantânea de relatório oficial formatado (`fpdf2`).
- **Lembrete de Calendário (`.ics`):** Exportação direta de evento para adicionar o horário da viagem ao Google Calendar, Apple Calendar ou Microsoft Outlook.

### 5. 📱 Otimização Mobile
- Separador dedicado com **cartões expansíveis (Accordions)** e métricas simplificadas para consulta rápida em dispositivos móveis e smartphones.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Framework Web:** Streamlit
- **Processamento de Dados:** Pandas
- **Visualização Geoespacial:** PyDeck
- **Leitura de PDFs:** `pdfplumber`
- **Geração de PDF:** `fpdf2`

---

## 📁 Estrutura do Repositório

```text
muv-viseu-streamlit/
├── app.py                   # Código principal da aplicação Streamlit (versão v4)
├── custom_schedules.json    # Ficheiro de cache gerado automaticamente ao importar PDFs
├── requirements.txt         # Dependências do projeto Python
└── README.md                # Documentação oficial do repositório
```

---

## 🚀 Como Executar Localmente

### 1. Clonar o repositório
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd muv-viseu-streamlit
```

### 2. Criar e ativar um ambiente virtual (Opcional, mas recomendado)
```bash
python -m venv venv
# No Linux/macOS:
source venv/bin/activate
# No Windows:
venv\Scripts\activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Iniciar a aplicação Streamlit
```bash
streamlit run app.py
```

Aceda à aplicação no seu navegador no endereço local indicado pelo Streamlit.

---

## 📋 Ficheiro `requirements.txt`

Assegure-se de que o ficheiro `requirements.txt` contém os seguintes pacotes:

```text
streamlit>=1.28.0
pandas>=2.0.0
pydeck>=0.8.0
fpdf2>=2.7.0
pdfplumber>=0.10.0
```

---

## 📄 Fonte dos Dados & Isenção de Responsabilidade

Os dados base apresentados nesta aplicação foram compilados a partir dos horários oficiais públicos da **MUV - Mobilidade Urbana de Viseu** (Linhas C1 e C2, em vigor a partir de 1 de setembro de 2025). Esta é uma aplicação independente desenvolvida para facilitar a mobilidade dos cidadãos e passageiros de Viseu.

---
*Desenvolvido em Python & Streamlit.*
