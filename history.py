import datetime
import asyncio
import aiohttp

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
    # Data atual
    hoje = datetime.datetime.now()
    # Data de 3 dias atrás
    tres_dias_atras = hoje - datetime.timedelta(days=3)
    tres_dias_atras_str = tres_dias_atras.strftime('%d/%m/%Y')

    for item in dados:
        if item[0]['display'] == tres_dias_atras_str:
            valor_acao = item[2]
            print(f"Valor da ação em {tres_dias_atras_str}: {valor_acao}")
            return

    print(f"Dados para a data {tres_dias_atras_str} não encontrados.")

async def main():
    ticker = 'VALE3'
    dados = await obter_preco_historico(ticker)
    obter_valor_3_dias_atras(dados)

if __name__ == "__main__":
    asyncio.run(main())
