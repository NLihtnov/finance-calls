# interface.py
import json
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
    columns = ["ticker", "preco", "3_dias", "5_dias", "10_dias", "30_dias", "60_dias", "90_dias", "1_ano", "2_anos", "3_anos", "5_anos"]
    tree["columns"] = columns

    tree.column("#0", width=0, stretch=tk.NO)
    for col in columns:
        tree.column(col, anchor=tk.W, width=100)
        tree.heading(col, text=col.replace("_", " ").title(), anchor=tk.W)

    for ticker, dados in dados_acoes.items():
        valores = [ticker]
        preco_atual = dados['preco']
        preco_atual_str = f"{preco_atual:.2f}"
        valores.append(preco_atual_str)

        for intervalo in columns[2:]:
            preco_historico = dados_historicos.get(ticker, {}).get(intervalo, {}).get("preco_historico", "N/A")
            if isinstance(preco_historico, (int, float)):
                preco_historico_str = f"{preco_historico:.2f}"
                if preco_atual > preco_historico:
                    preco_atual_str = f"{preco_atual:.2f} ↑"
                    valores.append((preco_historico_str, 'green'))
                elif preco_atual < preco_historico:
                    preco_atual_str = f"{preco_atual:.2f} ↓"
                    valores.append((preco_historico_str, 'red'))
                else:
                    valores.append(preco_historico_str)
            else:
                valores.append(preco_historico)

        tree.insert("", "end", values=valores)

    tree.pack(fill=tk.BOTH, expand=True)

    def set_cell_style(tree, col, val, tag, row):
        if isinstance(val, tuple):
            val, color = val
            tree.set(row, col, val)
            tree.tag_configure(tag, foreground=color)

    for row in tree.get_children():
        for col in columns[1:]:
            set_cell_style(tree, col, tree.set(row, col), f"{col}_style", row)

    logging.info("Janela exibida")
    root.mainloop()

if __name__ == "__main__":
    # Ler o array de tickers do arquivo JSON
    with open('tickers.json', 'r') as file:
        tickers_data = json.load(file)
        tickers = tickers_data['tickers']  # Supondo que o arquivo JSON tenha um formato {"tickers": ["PETR4", "VALE3", "ITUB4"]}

    # Iniciar atualização periódica em segundo plano
    thread = Thread(target=atualizar_dados_periodicamente, args=(60, tickers, 'dados_historicos.json'))
    thread.daemon = True
    logging.info("Atualização de dados iniciada")
    thread.start()

    # Executar a interface
    asyncio.run(exibir_dados_acoes())
