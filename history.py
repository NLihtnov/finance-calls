# history.py

import datetime
import asyncio
import aiohttp
import json
import os
from threading import Thread
import time

async def obter_preco_historico(ticker):
    url = 'https://www.infomoney.com.br/wp-json/infomoney/v1/quotes/history'
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.infomoney.com.br',
        'pragma': 'no-cache',
        'referer': f'https://www.infomoney.com.br/cotacoes/b3/acao/{ticker.lower()}/historico/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'x-requested-with': 'XMLHttpRequest'
    }
    data = {
        'page': 0,
        'numberItems': 5000,
        'symbol': ticker
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()

def obter_valor_n_dias_atras(dados, dias):
    hoje = datetime.datetime.now()
    data_alvo = hoje - datetime.timedelta(days=dias)
    data_alvo_str = data_alvo.strftime('%d/%m/%Y')

    for item in dados:
        if item[0]['display'] == data_alvo_str:
            valor_acao = item[2]
            return valor_acao, data_alvo_str

    return None, data_alvo_str

async def carregar_dados_historicos(tickers, arquivo_json='dados_historicos.json'):
    dados_historicos = carregar_arquivo_json(arquivo_json)
    resultados_finais = {}

    intervalos = {
        "3_dias": 3,
        "5_dias": 5,
        "10_dias": 10,
        "30_dias": 30,
        "60_dias": 60,
        "90_dias": 90,
        "1_ano": 365,
        "2_anos": 365*2,
        "3_anos": 365*3,
        "5_anos": 365*5
    }

    for ticker in tickers:
        try:
            # Buscar dados da API
            dados = await obter_preco_historico(ticker)
            historico_ticker = {}
            for nome_intervalo, dias in intervalos.items():
                preco_historico, data = obter_valor_n_dias_atras(dados, dias)
                if preco_historico is not None:
                    historico_ticker[nome_intervalo] = {
                        'preco_historico': preco_historico,
                        'data': data
                    }
                else:
                    historico_ticker[nome_intervalo] = {
                        'preco_historico': None,
                        'data': data
                    }
            dados_historicos[ticker] = historico_ticker
            salvar_arquivo_json(dados_historicos, arquivo_json)
            resultados_finais[ticker] = historico_ticker
        except Exception as e:
            print(f"Erro ao obter dados para {ticker}: {e}")
            resultados_finais[ticker] = {nome_intervalo: {"preco_historico": None, "data": None} for nome_intervalo in intervalos}

    return resultados_finais

def carregar_arquivo_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            return json.load(f)
    return {}

def salvar_arquivo_json(dados, arquivo):
    with open(arquivo, 'w') as f:
        json.dump(dados, f, indent=4)

def atualizar_dados_periodicamente(intervalo, tickers, arquivo_json):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        loop.run_until_complete(carregar_dados_historicos(tickers, arquivo_json))
        time.sleep(intervalo)

# Exemplo de uso
if __name__ == "__main__":
    tickers = ['PETR4', 'VALE3', 'ITUB4']
    dados = asyncio.run(carregar_dados_historicos(tickers))
    print(dados)
