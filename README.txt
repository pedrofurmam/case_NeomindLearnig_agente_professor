🎓 Robô Professor: Automação de Planos de Estudo com IA
Este projeto é uma Prova de Conceito (POC) de um agente pedagógico inteligente que automatiza o diagnóstico e a criação de roteiros de estudo personalizados. Utilizando o framework LangGraph para orquestração e a API da OpenAI para geração de conteúdo, o sistema transforma dados brutos de desempenho em uma experiência de aprendizagem direcionada.
+2

🎯 Objetivo
Reduzir o tempo operacional de professores no envio de planos de estudo detalhados para grandes volumes de alunos, garantindo que cada estudante receba o material adequado ao seu nível atual de forma automática.
+1

🛠️ Pré-requisitos e Instalação
Para rodar este projeto, você precisará do Python 3.10 ou superior. Instale as bibliotecas necessárias através do terminal:

Bash

pip install langgraph openai
🚀 Como Executar
Chave da API: Insira sua chave da OpenAI na variável API_KEY dentro do arquivo skeleton.py.

Arquivos de Dados: Certifique-se de que a pasta data/ contenha os seguintes arquivos:

diagnostic_results.csv

content_catalog.json

policy.json

Execução: Rode o comando abaixo no terminal:

Bash

python skeleton.py
🧠 Lógica de Desenvolvimento e Suposições
Durante a construção do pipeline, tomei decisões de engenharia para lidar com lacunas de informações e garantir a robustez do programa:


Engenharia de Prompt e Faixa Etária: Como a faixa etária dos alunos não foi definida, adotei uma linguagem didática e encorajadora padrão, embora o ideal fosse segmentar o prompt para diferentes idades.


Gestão de Tempo: O campo max_time_minutes da política foi considerado, mas como o catálogo não traz o tempo específico de cada exercício, o sistema prioriza a entrega da quantidade ideal de itens planejada.

Seleção Resiliente de Exercícios: Implementei uma lógica que verifica a disponibilidade real no catálogo antes de fechar o plano. Mesmo que a política permita até 5 exercícios, o código se adapta ao estoque atual (que possui 2 por categoria), garantindo que a regra de negócio seja respeitada sem causar erros de execução.
+1


Integridade de Dados: Presumi que o campo skill é padronizado entre todos os arquivos para garantir o cruzamento correto das informações. Além disso, foquei o diagnóstico na menor nota individual, ignorando o campo ability_score por falta de especificações sobre seu peso pedagógico.
+1

Validação de Regras: O nó final de validação assegura que o plano obedece ao mínimo de 2 e máximo de 5 exercícios; se os critérios da escola não forem atendidos, a aula não é validada para segurança do aluno.

🏗️ Pipeline da Solução
O fluxo de trabalho é dividido em 5 etapas principais:

Leitura: Coleta as notas do aluno.

Processamento (Diagnóstico): Identifica a maior lacuna de aprendizado com critérios claros de desempate.

Configuração do Treino (Planejamento): Define a dificuldade e a quantidade de exercícios com base no desempenho e no inventário.

Geração: Utiliza LLM para criar uma explicação clara, citando obrigatoriamente os IDs dos exercícios selecionados.

Validação: Checa se a aula gerada cumpre todos os requisitos de qualidade e política.
