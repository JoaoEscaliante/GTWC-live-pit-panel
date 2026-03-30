# GTWC-live-pit-panel
Automated race weekend schedule and alert system for motorsport pit walls


# 🏁 GTWC Live Pit Wall Panel (Painel Ao Vivo de Box)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)

## 📌 Visão Geral do Projeto
Em categorias de automobilismo como o GT World Challenge (SRO), os cronogramas dos finais de semana de corrida são altamente dinâmicos. As operações no *pit wall* e os chefes de equipe geralmente dependem de cronogramas em PDF estáticos e impressos, colados nas paredes da garagem, o que leva a falhas de comunicação, perda de horários e falta de consciência situacional durante momentos de alta pressão.

O **GTWC Live Pit Wall Panel** é um painel digital automatizado e em tempo real, projetado para substituir os cronogramas de papel. Ele faz a ingestão dos cronogramas brutos em PDF da organização, processa os dados não estruturados e renderiza uma tela tática ao vivo e autoatualizável para as TVs dos boxes da equipe.

## 🚀 Principais Funcionalidades
* **Extração Automatizada de Dados:** Usa `pdfplumber` e `pandas` para analisar e transformar cronogramas oficiais em PDF, que são desorganizados e não estruturados, em DataFrames estruturados.
* **Rastreamento de Sessões ao Vivo:** Calcula automaticamente o tempo decorrido e exibe barras de progresso dinâmicas para a sessão que está acontecendo no momento.
* **Modo Corrida (Sequestro de Tela):** 15 minutos antes de uma sessão crítica (Treino Livre, Classificação, Corrida), o painel dispara um alerta visual. Assim que a sessão começa, ele oculta o cronograma padrão e entra em "Modo Corrida", focando a TV inteira da garagem apenas na sessão ativa da pista.
* **Filtro de Tarefas em Segundo Plano:** Diferencia de forma inteligente as ações urgentes de pista (ex: Classificação) das janelas de longa duração (ex: Horário de funcionamento do escritório) para evitar poluição visual.
* **Atualização Automática (Zero-Touch):** Sistema de loop integrado para atualizar a interface silenciosamente a cada 60 segundos, garantindo que o relógio e as barras andem sem necessidade de atualizar o navegador manualmente.

## 📺 Prévias do Painel
*(Adicione seus prints de tela aqui! Apague este texto e use o formato abaixo, colocando o link das suas imagens)*
## 🛠️ Arquitetura e Tecnologias
* **Linguagem:** Python
* **Processamento de Dados:** Pandas, Expressões Regulares (Regex)
* **Ingestão de PDF:** pdfplumber
* **Interface Frontend:** Streamlit (com HTML/CSS customizados injetados para animações e design responsivo)

## ⚙️ Como Executar Localmente

1. Clone este repositório:
```bash
git clone [https://github.com/seu-usuario/gtwc-live-pit-panel.git](https://github.com/seu-usuario/gtwc-live-pit-panel.git)
