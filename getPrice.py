import requests
from bs4 import BeautifulSoup
import json

def obter_preco_google(ticker):
    url = f"https://www.google.com/search?q={ticker}+ação"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar a página: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        # Localiza o preço do ticker na página
        price_span = soup.find("span", {"jsname": "vWLAgc"})
        if price_span:
            price = price_span.text.replace(",", ".")
            return float(price)
        else:
            raise Exception(f"Não foi possível encontrar o preço para o ticker {ticker}")
    except Exception as e:
        raise Exception(f"Erro ao processar os dados para {ticker}: {e}")

# Carrega tickers do arquivo JSON
with open('tickers.json', 'r', encoding='utf-8') as file:
    tickers_data = json.load(file)
    tickers = tickers_data['tickers']

dados_acoes = {}

for ticker in tickers:
    try:
        preco = obter_preco_google(ticker)
        dados_acoes[ticker] = {"preco": preco}
    except Exception as e:
        print(f"Erro ao obter dados para {ticker}: {e}")

print("Preços das Ações:")
for ticker, dados in dados_acoes.items():
    print(f"{ticker}: Preço: {dados['preco']:.2f} BRL")
