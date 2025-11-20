import pandas as pd
import joblib
import os
from datetime import datetime

# === CONFIG (NOVOS MODELOS) ===
MODELO_GOLS = "modelo_multiliga_mais25.pkl"
MODELO_BTTS = "modelo_btts.pkl" # NOVO MODELO (Você precisará treinar e salvar)
DATASET_PREVISOES = "previsoes_do_dia.csv" # Arquivo gerado pelo ia.py (Passo 2)

# === Funções Auxiliares para Carregamento ===
def carregar_modelo(caminho_modelo):
    if os.path.exists(caminho_modelo):
        try:
            return joblib.load(caminho_modelo)
        except Exception as e:
            print(f"❌ Erro ao carregar modelo {caminho_modelo}: {e}")
            return None
    else:
        print(f"⚠ Modelo não encontrado: {caminho_modelo}. Previsões serão 0.")
        return None

# === Carregar Modelos ===
modelo_gols = carregar_modelo(MODELO_GOLS)
modelo_btts = carregar_modelo(MODELO_BTTS)

# === Carregar dataset de previsões ===
if not os.path.exists(DATASET_PREVISOES):
    print(f"⚠ Arquivo de previsões ({DATASET_PREVISOES}) não encontrado. Rode o ia.py primeiro.")
    exit()
    
df_previsoes = pd.read_csv(DATASET_PREVISOES)

if df_previsoes.empty:
    print("⚠ Nenhum jogo encontrado para prever no arquivo.")
    exit()

# === Funções de Previsão (Reutilizam a lógica do seu modelo) ===
# ATENÇÃO: Se o seu modelo for mais complexo, a lista 'features' precisa ser atualizada
FEATURES = ['gols_casa', 'gols_fora'] 

def prever_gols(row):
    if modelo_gols:
        try:
            X = row[FEATURES].values.reshape(1, -1)
            # Retorna a probabilidade da CLASSE POSITIVA (Mais de 2.5 Gols = 1)
            return modelo_gols.predict_proba(X)[0][1] 
        except Exception:
            return 0.0
    return 0.0

def prever_btts(row):
    """Calcula a probabilidade de Ambas Marcam (BTTS)."""
    if modelo_btts:
        try:
            X = row[FEATURES].values.reshape(1, -1)
            # Retorna a probabilidade da CLASSE POSITIVA (Ambas Marcam = 1)
            return modelo_btts.predict_proba(X)[0][1]
        except Exception:
            return 0.0
    return 0.0

# === Aplicar Previsões ao DataFrame ===
df_previsoes['prob_mais25'] = df_previsoes.apply(prever_gols, axis=1)
df_previsoes['prob_btts'] = df_previsoes.apply(prever_btts, axis=1)
df_previsoes['prob_menos35'] = 1 - df_previsoes['prob_mais25'] # Simples estimativa inversa

# Placeholder para o futuro modelo de escanteios
df_previsoes['escanteios_est'] = "A calcular"


# === Menu de Consultas com Base nas Previsões ===

print("\n=== IA LALIGA - CONSULTAS ===")
print("Opções disponíveis:")
print("1 - Jogos com +1.5 gols (prob_mais25 acima de 80%)") 
print("2 - Jogos com -3.5 gols (prob_menos35 acima de 80%)") 
print("3 - Quem tem chance de vencer (A ser implementado)") # Requer um modelo de 1X2
print("4 - Ambas Marcam (BTTS) acima de 70%") # NOVO FILTRO
print("5 - Previsão de Escanteios (A ser implementado)") # NOVO FILTRO
print("0 - Sair")

op = input("\nDigite a opção: ")

if op == "1":
    # Usando 0.8 como um filtro forte para Mais de 2.5 gols (proxy para +1.5)
    res = df_previsoes[df_previsoes['prob_mais25'] >= 0.80]
    print("\n=== +1.5 gols acima de 80% (Via +2.5) ===")
    print(res[['time_casa', 'time_fora', 'data', 'prob_mais25']])

elif op == "2":
    # Usando 0.8 como um filtro forte para Menos de 3.5 gols (estimativa)
    res = df_previsoes[df_previsoes['prob_menos35'] >= 0.80]
    print("\n=== -3.5 gols acima de 80% ===")
    print(res[['time_casa', 'time_fora', 'data', 'prob_menos35']])

elif op == "3":
    print("\n⚠ A previsão de 'Quem Vencer' requer um modelo 1X2 (Vitória Casa/Empate/Vitória Fora).")
    print("O modelo atual só prevê GOLS.")
    print("Por favor, treine e salve o 'modelo_1x2.pkl'.")

elif op == "4":
    res = df_previsoes[df_previsoes['prob_btts'] >= 0.70]
    print("\n=== Ambas Marcam (BTTS) acima de 70% ===")
    print(res[['time_casa', 'time_fora', 'data', 'prob_btts']])

elif op == "5":
    print("\n⚠ A previsão de Escanteios requer um modelo dedicado.")
    print(df_previsoes[['time_casa', 'time_fora', 'escanteios_est']])

elif op == "0":
    print("Saindo.")

else:
    print("Opção inválida.")