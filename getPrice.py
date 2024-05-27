import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json

async def obter_preco_google(ticker):
    url = f"https://www.google.com/search?q={ticker}+ação"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"Erro ao acessar a página: {response.status}")
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            price_span = soup.find("span", {"jsname": "vWLAgc"})
            if price_span:
                price = price_span.text.replace(",", ".")
                return float(price)
            else:
                raise Exception(f"Não foi possível encontrar o preço para o ticker {ticker}")

async def carregar_dados_acoes(filename='tickers.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        tickers_data = json.load(file)
        tickers = tickers_data['tickers']

    dados_acoes = {}

    async def fetch_preco(ticker):
        try:
            preco = await obter_preco_google(ticker)
            return ticker, preco
        except Exception as e:
            print(f"Erro ao obter dados para {ticker}: {e}")
            return ticker, None

    tasks = [fetch_preco(ticker) for ticker in tickers]
    results = await asyncio.gather(*tasks)

    for ticker, preco in results:
        if preco is not None:
            dados_acoes[ticker] = {"preco": preco}

    return dados_acoes
