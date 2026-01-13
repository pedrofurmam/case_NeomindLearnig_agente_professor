# 🎓 Robô Professor: Automação de Planos de Estudo com IA

[cite_start]Este projeto é uma **Prova de Conceito (POC)** de um agente pedagógico inteligente desenvolvido para automatizar o diagnóstico e a criação de roteiros de estudo personalizados[cite: 4]. Utilizando o framework **LangGraph** para orquestração de estados e a API da **OpenAI** para geração de conteúdo, o sistema transforma dados de desempenho em uma experiência de aprendizagem direcionada e eficiente.

## 🎯 Objetivo
[cite_start]O objetivo principal é mitigar o tempo gasto por professores no envio manual de planos de estudo detalhados, garantindo que cada aluno receba materiais e mensagens personalizadas de forma automática e em escala[cite: 3, 4, 14].

## 🛠️ Instalação e Requisitos

### Pré-requisitos
* **Python 3.10 ou superior**: Recomenda-se evitar versões experimentais (como a 3.14) para garantir a estabilidade das bibliotecas de IA.
* **OpenAI API Key**: Necessária para a geração das explicações pedagógicas.

### Bibliotecas Necessárias
Instale as dependências via terminal:

```bash
pip install langgraph openai
