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
        'numberItems': 50,
        'symbol': ticker
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()

def obter_valor_3_dias_atras(dados):
    hoje = datetime.datetime.now()
    tres_dias_atras = hoje - datetime.timedelta(days=3)
    tres_dias_atras_str = tres_dias_atras.strftime('%d/%m/%Y')

    for item in dados:
        if item[0]['display'] == tres_dias_atras_str:
            valor_acao = item[2]
            return valor_acao, tres_dias_atras_str

    return None, tres_dias_atras_str

async def carregar_dados_historicos(tickers, arquivo_json='dados_historicos.json'):
    dados_historicos = carregar_arquivo_json(arquivo_json)
    resultados_finais = {}

    for ticker in tickers:
        try:
            # Verificar se os dados já estão no arquivo e são de 3 dias atrás
            hoje = datetime.datetime.now()
            tres_dias_atras = hoje - datetime.timedelta(days=3)
            tres_dias_atras_str = tres_dias_atras.strftime('%d/%m/%Y')

            if ticker in dados_historicos and dados_historicos[ticker]['data'] == tres_dias_atras_str:
                preco_historico = dados_historicos[ticker]['preco_historico']
            else:
                # Buscar dados da API
                dados = await obter_preco_historico(ticker)
                preco_historico, data = obter_valor_3_dias_atras(dados)
                if preco_historico is not None:
                    dados_historicos[ticker] = {
                        'preco_historico': preco_historico,
                        'data': data
                    }
                    salvar_arquivo_json(dados_historicos, arquivo_json)
            resultados_finais[ticker] = {"preco_historico": preco_historico}
        except Exception as e:
            print(f"Erro ao obter dados para {ticker}: {e}")
            resultados_finais[ticker] = {"preco_historico": None}

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
