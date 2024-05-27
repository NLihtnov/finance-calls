import time
import logging
import tkinter as tk
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor, as_completed
from getPrice import obter_preco_google
import json

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def carregar_dados_acoes_paralelo(filename='tickers.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        tickers_data = json.load(file)
        tickers = tickers_data['tickers']

    dados_acoes = {}

    def fetch_preco(ticker):
        try:
            preco = obter_preco_google(ticker)
            return ticker, preco
        except Exception as e:
            logging.error(f"Erro ao obter dados para {ticker}: {e}")
            return ticker, None

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(fetch_preco, ticker): ticker for ticker in tickers}
        for future in as_completed(future_to_ticker):
            ticker, preco = future.result()
            if preco is not None:
                dados_acoes[ticker] = {"preco": preco}

    return dados_acoes

def exibir_dados_acoes():
    start_time = time.time()
    logging.info("Iniciando a carga dos dados das ações...")

    dados_acoes = carregar_dados_acoes_paralelo()

    end_time = time.time()
    logging.info(f"Dados carregados em {end_time - start_time:.2f} segundos")

    root = tk.Tk()
    root.title("Preços das Ações")
    root.state('zoomed')  # Abre a janela maximizada

    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame)
    tree["columns"] = ("ticker", "preco")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("ticker", anchor=tk.W, width=80)
    tree.column("preco", anchor=tk.W, width=100)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("ticker", text="Ticker", anchor=tk.W)
    tree.heading("preco", text="Preço (BRL)", anchor=tk.W)

    for ticker, dados in dados_acoes.items():
        tree.insert("", "end", values=(ticker, f"{dados['preco']:.2f}"))

    tree.pack(fill=tk.BOTH, expand=True)

    logging.info("Janela exibida")
    root.mainloop()

if __name__ == "__main__":
    exibir_dados_acoes()
