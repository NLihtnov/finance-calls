import datetime
import asyncio
import aiohttp
import json

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

def obter_valor_3_dias_atras(dados, ticker):
    hoje = datetime.datetime.now()
    tres_dias_atras = hoje - datetime.timedelta(days=3)
    tres_dias_atras_str = tres_dias_atras.strftime('%d/%m/%Y')

    for item in dados:
        if item[0]['display'] == tres_dias_atras_str:
            valor_acao = item[2]
            return valor_acao

    return None

async def carregar_dados_historicos(tickers):
    dados_historicos = {}

    async def fetch_historico(ticker):
        try:
            dados = await obter_preco_historico(ticker)
            preco_historico = obter_valor_3_dias_atras(dados, ticker)
            return ticker, preco_historico
        except Exception as e:
            print(f"Erro ao obter dados para {ticker}: {e}")
            return ticker, None

    tasks = [fetch_historico(ticker) for ticker in tickers]
    results = await asyncio.gather(*tasks)

    for ticker, preco_historico in results:
        if preco_historico is not None:
            dados_historicos[ticker] = {"preco_historico": preco_historico}

    return dados_historicos
