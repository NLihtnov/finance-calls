# interface.py

import time
import logging
import tkinter as tk
from tkinter import ttk
import asyncio
from threading import Thread
from getPrice import carregar_dados_acoes
from history import carregar_dados_historicos, atualizar_dados_periodicamente

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def exibir_dados_acoes():
    start_time = time.time()
    logging.info("Iniciando a carga dos dados das ações...")

    dados_acoes = await carregar_dados_acoes()

    # Carregar dados históricos
    tickers = list(dados_acoes.keys())
    dados_historicos = await carregar_dados_historicos(tickers)

    end_time = time.time()
    logging.info(f"Dados carregados em {end_time - start_time:.2f} segundos")

    root = tk.Tk()
    root.title("Preços das Ações")
    root.state('zoomed')  # Abre a janela maximizada

    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame)
    tree["columns"] = ("ticker", "preco", "preco_historico")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("ticker", anchor=tk.W, width=80)
    tree.column("preco", anchor=tk.W, width=100)
    tree.column("preco_historico", anchor=tk.W, width=150)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("ticker", text="Ticker", anchor=tk.W)
    tree.heading("preco", text="Preço (BRL)", anchor=tk.W)
    tree.heading("preco_historico", text="Preço 3 dias atrás (BRL)", anchor=tk.W)

    for ticker, dados in dados_acoes.items():
        preco_historico = dados_historicos.get(ticker, {}).get("preco_historico", "N/A")
        preco_historico_str = f"{preco_historico:.2f}" if isinstance(preco_historico, (int, float)) else preco_historico
        tree.insert("", "end", values=(ticker, f"{dados['preco']:.2f}", preco_historico_str))

    tree.pack(fill=tk.BOTH, expand=True)

    logging.info("Janela exibida")
    root.mainloop()

if __name__ == "__main__":
    # Iniciar atualização periódica em segundo plano
    tickers = ['PETR4', 'VALE3', 'ITUB4']
    thread = Thread(target=atualizar_dados_periodicamente, args=(60, tickers, 'dados_historicos.json'))
    thread.daemon = True
    thread.start()

    # Executar a interface
    asyncio.run(exibir_dados_acoes())
