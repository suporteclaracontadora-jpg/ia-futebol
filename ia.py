import requests
import pandas as pd

def pegar_dados_laliga():

    url = "https://d.flashscore.com/x/feed/f_1_2024_2_es_es/result/?_="

    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-fsign": "SW9D1eZo"
    }

    response = requests.get(url, headers=headers)

    linhas = response.text.split("¬")

    jogos = []
    jogo = {}

    for linha in linhas:
        if linha.startswith("AA"):
            if jogo:
                jogos.append(jogo)
            jogo = {}

        if "AD" in linha:  # time casa
            jogo["time_casa"] = linha.split("=",1)[1]
        if "AE" in linha:  # time fora
            jogo["time_fora"] = linha.split("=",1)[1]
        if "AG" in linha:  # gols casa
            jogo["gols_casa"] = linha.split("=",1)[1]
        if "AH" in linha:  # gols fora
            jogo["gols_fora"] = linha.split("=",1)[1]

    if jogo:
        jogos.append(jogo)

    df = pd.DataFrame(jogos)
    df.to_csv("laliga_dados.csv", index=False, encoding="utf-8")

    print(f"{len(df)} jogos coletados com sucesso!")

pegar_dados_laliga()
