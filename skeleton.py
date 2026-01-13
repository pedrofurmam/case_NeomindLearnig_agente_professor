import json
import csv
import random
import os
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, END
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")


# Aqui definimos o que o sistema "sabe" enquanto roda.
class LessonState(TypedDict):
    student_id: str                 # ID do aluno (Entrada)
    student_scores: dict            # Notas carregadas do CSV
    
    # Decisões (O que você vai preencher nas funções)
    focus_skill: str                # Qual matéria focar?
    difficulty: int                 # Qual dificuldade (1-5)?
    num_exercises: int              # Quantos exercícios?
    
    # Conteúdo Final
    selected_exercises: List[str]   # IDs dos exercícios escolhidos
    explanation: str                # Texto gerado pela IA
    
    # Validação
    is_valid: bool                  # O plano obedece as regras?


def load_data_node(state: LessonState) -> LessonState:
    print(f"--> [1] Carregando dados do aluno: {state['student_id']}")
    # DICA: Abra o arquivo diagnostic_results.csv e filtre pelo student_id
    # state['student_scores'] = ...

    aluno_id = state['student_id']
    
    caminho_arquivo = 'data/diagnostic_results.csv'

    # cria um dicionário para guardar as notas 
    notas_encontradas = {}

    # usa biblioteca CSV para ler o arquivo
    with open(caminho_arquivo, mode='r', encoding='utf-8') as f:

        # DictReader transforma cada linha em um dicionário usando o cabeçalho do CSV
        leitor = csv.DictReader(f)
        
        # for para percorrer cada linha do CSV
        for linha in leitor:
            
            if linha['student_id'] == aluno_id:
                
                habilidade = linha['skill']
                nota = float(linha['score'])
                notas_encontradas[habilidade] = nota

    # salva o resultado 
    state['student_scores'] = notas_encontradas
    
    
    print(f"Sucesso! Foram encontradas {len(state['student_scores'])} notas para este aluno.")

    return state

def diagnose_node(state: LessonState) -> LessonState:
    print("--> [2] Diagnosticando dificuldade...")
    # TAREFA: Ache a menor nota em state['student_scores']
    # state['focus_skill'] = "sinais_negativos" (exemplo)

    notas = state['student_scores']
    
    # verifica se há notas
    if not notas:
        print("Aviso: Nenhuma nota encontrada para este aluno.")
        state['focus_skill'] = "Geral"
        state['focus_score'] = 0.0
        return state

    menor_valor = min(notas.values())
    
    # é criado uma lista com as matérias que possuem a menor nota (empate)
    materias_empatadas = [skill for skill, score in notas.items() if score == menor_valor]
    
    # é ordenado alfabeticamente e é escolhida a primeira
    
    materias_empatadas.sort()
    pior_materia = materias_empatadas[0]
    
    # salva as informações no estado
    state['focus_skill'] = pior_materia
    state['focus_score'] = menor_valor
    
    print(f"Diagnóstico concluído: Focar em '{state['focus_skill']}' (Nota: {state['focus_score']})")
    
    return state

def plan_node(state: LessonState) -> LessonState:
    print("--> [3] Planejando a aula...")
    # TAREFA: Se nota baixa -> Dificuldade 1. Se nota alta -> Dificuldade 3.
    # state['difficulty'] = ...
    # state['num_exercises'] = ...

    # carrega as regras do policy
    with open('data/policy.json', 'r', encoding='utf-8') as f:
        policy = json.load(f)
    
    limite_max = policy.get('max_exercises', 5)
    limite_min = policy.get('min_exercises', 2)

    # seleciona a pior matéria
    materia_foco = state['focus_skill']
    # busca a nota daquela matéria. Se não achar  usa 0.0
    nota = state['student_scores'].get(materia_foco, 0.0)

    # seleciona a dificuldade de acordo com os 5 níveis

    if nota < 0.2:
        nivel = 1  # muito básico
    elif nota < 0.4:
        nivel = 2  # básico
    elif nota < 0.6:
        nivel = 3  # intermediário
    elif nota < 0.8:
        nivel = 4  # avançado
    else:
        nivel = 5  # muito avançado


    # lógica para a quantidade 
    if nota < 0.35:
        # aluno com muita dificuldade: máximo permitido para praticar muito
        quantidade_sugerida = limite_max
    elif nota < 0.75:
        # aluno mediano: um volume equilibrado
        quantidade_sugerida = 3
    else:
        # aluno avançado: não apenas 1, mas o mínimo necessário para manter o nível
        quantidade_sugerida = limite_min

    # consulta o catalogo de exercícios
    with open('data/content_catalog.json', 'r', encoding='utf-8') as f:
        catalogo = json.load(f)
    
    # verifica quantos exercícios existem exatamente para este tema e nível
    disponiveis = [e for e in catalogo if e['skill'] == materia_foco and e['difficulty'] == nivel]
    total_no_catalogo = len(disponiveis)

    # a quantidade final é o menor valor entre o que queremos e o que temos
    quantidade_final = min(quantidade_sugerida, total_no_catalogo)

    # salvando 
    state['difficulty'] = nivel
    state['num_exercises'] = quantidade_final

    print(f"Decisão: Para nota {nota:.2f}, selecionamos Nível {state['difficulty']}.")
    print(f"Plano: Recomendar {state['num_exercises']} exercícios.")

    return state

def generate_node(state: LessonState) -> LessonState:
    print("--> [4] Gerando conteúdo...")
    # TAREFA A: Selecione exercícios do content_catalog.json compatíveis
    # TAREFA B: Use IA para gerar o texto explicativo
    # state['explanation'] = "Olá! Vamos treinar..."

    # seleciona do catalogo
    with open('data/content_catalog.json', 'r', encoding='utf-8') as f:
        catalogo = json.load(f)
    
    # filtra conforme o tema e dificuldade, salva o id na classe state
    exercicios_filtrados = [
        item['id'] for item in catalogo 
        if item['skill'] == state['focus_skill'] and item['difficulty'] == state['difficulty']
    ]

    # garante que pegamos apenas a quantidade exata planejada
    state['selected_exercises'] = exercicios_filtrados[:state['num_exercises']]

    # geração da explicação com IA 
    client = OpenAI(api_key=API_KEY)

    # passa no prompt a materia, dificuldade e numero de exercicos
    prompt_usuario = (
        f"Você é um professor e vai se comunicar com um aluno que está estudando {state['focus_skill']}, então explique essa matéria de forma clara e objetiva para o aluno."
        f"ele está no nível {state['difficulty']}/5 de dificuldade dessa matéria. "
        f"No seu texto, você DEVE citar explicitamente que ele deve realizar os seguintes exercícios: {state['selected_exercises']} para praticar e consolidar o aprendizado. "
        f"Seja motivador, direto e breve."
    )
    

    try:
        resposta = client.responses.create(
            model="gpt-4o-mini", 
            input=prompt_usuario,
            max_output_tokens=300, # limitar o tamanho da resposta ajuda na velocidade
            temperature=0.5
        )

        # salva o texto gerado 
        state['explanation'] = resposta.output_text
    except Exception as e:
        print(f"Erro ao chamar a IA: {e}")
        state['explanation'] = (
        f"Vamos praticar {state['focus_skill']}! "
        f"Resolva os exercícios {state['selected_exercises']}."
    )

    print(f"Sucesso: {len(state['selected_exercises'])} exercícios selecionados e texto gerado.")


    return state

def validate_node(state: LessonState) -> LessonState:
    print("--> [5] Validando regras...")
    # TAREFA: Verifique se num_exercises <= max_exercises (do policy.json)
    # state['is_valid'] = True
    
    # carrega as regras do policy
    with open('data/policy.json', 'r', encoding='utf-8') as f:
        policy = json.load(f)
    
    max_permitido = policy.get('max_exercises', 5)

    # coleta dados gerados nas etapas anteriores
    exercicios_gerados = state.get('selected_exercises', [])
    qtd_gerada = len(exercicios_gerados)
    texto_ia = state.get('explanation', "")

    # lógica de validação quantidade não pode ser zero e nem maior que o máximo da política
    valida_qtd = 2 <= qtd_gerada <= max_permitido
    
    # verifica se otexto da IA não é  uma string vazia)
    valida_texto = len(texto_ia.strip()) > 0

    #validação final
    if valida_qtd and valida_texto:
        state['is_valid'] = True
        print(f"   Sucesso: Plano validado! ({qtd_gerada} exercícios)")
    else:
        state['is_valid'] = False
        print(f"   Falha: Plano inválido (Qtd: {qtd_gerada}, Texto: {len(texto_ia)} carac.)")
    
    return state

    return state


def router(state: LessonState) -> Literal["end", "plan"]:
    if state.get("is_valid"):
        print(">>> Sucesso: Aula pronta! <<<")
        return "end"
    else:
        print(">>> Erro: Aula inválida. <<<")
        return "end" # Simplificação para o teste

def build_graph():
    workflow = StateGraph(LessonState)

    # Adiciona as casas (Nós)
    workflow.add_node("load", load_data_node)
    workflow.add_node("diagnose", diagnose_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("validate", validate_node)

    # Adiciona as setas (Arestas)
    workflow.set_entry_point("load")
    workflow.add_edge("load", "diagnose")
    workflow.add_edge("diagnose", "plan")
    workflow.add_edge("plan", "generate")
    workflow.add_edge("generate", "validate")
    
    # Decisão final
    workflow.add_conditional_edges(
        "validate",
        router,
        {"end": END, "plan": "plan"}
    )

    return workflow.compile()

# --- 4. EXECUTAR ---
if __name__ == "__main__":
    app = build_graph()
    
    # Simula a entrada de um aluno
    input_data = {"student_id": "ALUNO-001"}
    
    print("=== Iniciando Robô Professor ===")
    try:
        final_state = app.invoke(input_data)
        print("\n=== RESULTADO FINAL ===")
        print(f"Foco: {final_state.get('focus_skill')}")
        print(f"Texto: {final_state.get('explanation')}")
        print(f"Exercícios: {final_state.get('selected_exercises')}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
