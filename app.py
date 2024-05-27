import time
import logging
import tkinter as tk
from tkinter import ttk
from getPrice import carregar_dados_acoes

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def exibir_dados_acoes():
    start_time = time.time()
    logging.info("Iniciando a carga dos dados das ações...")

    dados_acoes = carregar_dados_acoes()

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
