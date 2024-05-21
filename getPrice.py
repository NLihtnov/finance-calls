import yfinance as yf

def obter_precos_e_pl_acoes(tickers):
    dados_acoes = {}
    
    for ticker in tickers:
        acao = yf.Ticker(ticker)
        info = acao.info
        historico = acao.history(period="1d")
        preco_atual = historico["Close"].iloc[-1]
        pl = info.get("trailingPE", "N/A")
        if pl != "N/A":
            pl = round(pl, 2)
        dados_acoes[ticker] = {"preco": round(preco_atual, 2), "P/L": pl}
        
    return dados_acoes

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
dados_acoes = obter_precos_e_pl_acoes(tickers)

print("Preços e P/L das Ações:")
for ticker, dados in dados_acoes.items():
    preco = f"{dados['preco']:.2f}"
    pl = f"{dados['P/L']:.2f}" if dados['P/L'] != "N/A" else "N/A"
    print(f"{ticker}: Preço: {preco}, P/L: {pl}")
