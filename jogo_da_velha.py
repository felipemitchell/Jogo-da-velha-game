import tkinter as tk
from tkinter import messagebox
import sqlite3
from sqlite3 import Error

class JogoDaVelha:
    def __init__(self):
        # Inicializar banco de dados
        self.criar_banco_dados()
        
        # Configuração da janela principal
        self.janela = tk.Tk()
        self.janela.title("Jogo da Velha - Bot Imbatível")
        self.janela.geometry("400x500")
        
        # Variáveis do jogo
        self.tabuleiro = [""] * 9
        self.jogador_atual = "X"
        self.jogo_ativo = True
        
        # Interface do usuário
        self.criar_interface()
        
    def criar_banco_dados(self):
        """Cria o banco de dados e tabela para estatísticas"""
        try:
            self.conn = sqlite3.connect('jogo_velha.db')
            self.cursor = self.conn.cursor()
            
            # CREATE - Criar tabela se não existir
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS estatisticas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jogador TEXT NOT NULL,
                    vitorias INTEGER DEFAULT 0,
                    derrotas INTEGER DEFAULT 0,
                    empates INTEGER DEFAULT 0
                )
            ''')
            self.conn.commit()
            
        except Error as e:
            print(f"Erro ao criar banco de dados: {e}")
    
    def criar_interface(self):
        """Cria a interface gráfica do jogo"""
        # Frame para estatísticas
        frame_stats = tk.Frame(self.janela)
        frame_stats.pack(pady=10)
        
        tk.Button(frame_stats, text="Ver Estatísticas", 
                 command=self.mostrar_estatisticas).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_stats, text="Resetar Estatísticas", 
                 command=self.resetar_estatisticas).pack(side=tk.LEFT, padx=5)
        
        # Frame do tabuleiro
        frame_tabuleiro = tk.Frame(self.janela)
        frame_tabuleiro.pack(pady=20)
        
        self.botoes = []
        for i in range(9):
            linha = i // 3
            coluna = i % 3
            
            botao = tk.Button(frame_tabuleiro, text="", font=('Arial', 20), width=5, height=2,
                             command=lambda idx=i: self.fazer_jogada(idx))
            botao.grid(row=linha, column=coluna, padx=2, pady=2)
            self.botoes.append(botao)
        
        # Frame de controle
        frame_controle = tk.Frame(self.janela)
        frame_controle.pack(pady=10)
        
        tk.Button(frame_controle, text="Novo Jogo", 
                 command=self.novo_jogo).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_controle, text="Sair", 
                 command=self.janela.quit).pack(side=tk.LEFT, padx=5)
        
        # Label de status
        self.label_status = tk.Label(self.janela, text="Sua vez! Você é X", font=('Arial', 12))
        self.label_status.pack(pady=10)
    
    def fazer_jogada(self, posicao):
        """Processa a jogada do jogador humano"""
        if not self.jogo_ativo or self.tabuleiro[posicao] != "":
            return
        
        # Jogada do humano
        self.tabuleiro[posicao] = "X"
        self.botoes[posicao].config(text="X", state="disabled", bg="lightblue")
        
        if self.verificar_vitoria("X"):
            self.finalizar_jogo("Você venceu!")
            self.atualizar_estatisticas("Humano", vitoria=True)
            return
        elif self.verificar_empate():
            self.finalizar_jogo("Empate!")
            self.atualizar_estatisticas("Humano", empate=True)
            return
        
        # Jogada do bot
        self.jogada_bot()
    
    def jogada_bot(self):
        """Lógica do bot que nunca perde"""
        # Estratégia: usar minimax para jogada perfeita
        melhor_jogada = self.encontrar_melhor_jogada()
        
        if melhor_jogada is not None:
            self.tabuleiro[melhor_jogada] = "O"
            self.botoes[melhor_jogada].config(text="O", state="disabled", bg="lightcoral")
            
            if self.verificar_vitoria("O"):
                self.finalizar_jogo("O bot venceu!")
                self.atualizar_estatisticas("Humano", derrota=True)
            elif self.verificar_empate():
                self.finalizar_jogo("Empate!")
                self.atualizar_estatisticas("Humano", empate=True)
    
    def encontrar_melhor_jogada(self):
        """Encontra a melhor jogada usando algoritmo minimax"""
        # Verificar se pode vencer
        for i in range(9):
            if self.tabuleiro[i] == "":
                self.tabuleiro[i] = "O"
                if self.verificar_vitoria("O"):
                    self.tabuleiro[i] = ""
                    return i
                self.tabuleiro[i] = ""
        
        # Bloquear jogador se ele estiver prestes a vencer
        for i in range(9):
            if self.tabuleiro[i] == "":
                self.tabuleiro[i] = "X"
                if self.verificar_vitoria("X"):
                    self.tabuleiro[i] = ""
                    return i
                self.tabuleiro[i] = ""
        
        # Jogar no centro se disponível
        if self.tabuleiro[4] == "":
            return 4
        
        # Jogar nos cantos
        cantos = [0, 2, 6, 8]
        for canto in cantos:
            if self.tabuleiro[canto] == "":
                return canto
        
        # Jogar nas bordas
        bordas = [1, 3, 5, 7]
        for borda in bordas:
            if self.tabuleiro[borda] == "":
                return borda
        
        return None
    
    def verificar_vitoria(self, jogador):
        """Verifica se o jogador venceu"""
        combinacoes_vitoria = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Linhas
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Colunas
            [0, 4, 8], [2, 4, 6]              # Diagonais
        ]
        
        for combinacao in combinacoes_vitoria:
            if all(self.tabuleiro[pos] == jogador for pos in combinacao):
                return True
        return False
    
    def verificar_empate(self):
        """Verifica se o jogo empatou"""
        return all(celula != "" for celula in self.tabuleiro) and not self.verificar_vitoria("X") and not self.verificar_vitoria("O")
    
    def finalizar_jogo(self, mensagem):
        """Finaliza o jogo e mostra mensagem"""
        self.jogo_ativo = False
        self.label_status.config(text=mensagem)
        
        for botao in self.botoes:
            botao.config(state="disabled")
    
    def novo_jogo(self):
        """Inicia um novo jogo"""
        self.tabuleiro = [""] * 9
        self.jogo_ativo = True
        self.jogador_atual = "X"
        
        for botao in self.botoes:
            botao.config(text="", state="normal", bg="SystemButtonFace")
        
        self.label_status.config(text="Sua vez! Você é X")
    
    # OPERAÇÕES CRUD
    
    def atualizar_estatisticas(self, jogador, vitoria=False, derrota=False, empate=False):
        """UPDATE - Atualiza estatísticas do jogador"""
        try:
            # READ - Verificar se jogador existe
            self.cursor.execute("SELECT * FROM estatisticas WHERE jogador = ?", (jogador,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                # UPDATE - Atualizar estatísticas existentes
                if vitoria:
                    self.cursor.execute(
                        "UPDATE estatisticas SET vitorias = vitorias + 1 WHERE jogador = ?",
                        (jogador,)
                    )
                elif derrota:
                    self.cursor.execute(
                        "UPDATE estatisticas SET derrotas = derrotas + 1 WHERE jogador = ?",
                        (jogador,)
                    )
                elif empate:
                    self.cursor.execute(
                        "UPDATE estatisticas SET empates = empates + 1 WHERE jogador = ?",
                        (jogador,)
                    )
            else:
                # CREATE - Criar novo registro
                vitorias = 1 if vitoria else 0
                derrotas = 1 if derrota else 0
                empates = 1 if empate else 0
                
                self.cursor.execute(
                    "INSERT INTO estatisticas (jogador, vitorias, derrotas, empates) VALUES (?, ?, ?, ?)",
                    (jogador, vitorias, derrotas, empates)
                )
            
            self.conn.commit()
            
        except Error as e:
            print(f"Erro ao atualizar estatísticas: {e}")
    
    def mostrar_estatisticas(self):
        """READ - Mostra estatísticas dos jogadores"""
        try:
            self.cursor.execute("SELECT * FROM estatisticas")
            resultados = self.cursor.fetchall()
            
            if not resultados:
                messagebox.showinfo("Estatísticas", "Nenhuma estatística registrada ainda.")
                return
            
            mensagem = "=== ESTATÍSTICAS ===\n\n"
            for linha in resultados:
                id_jogador, jogador, vitorias, derrotas, empates = linha
                total_jogos = vitorias + derrotas + empates
                mensagem += f"Jogador: {jogador}\n"
                mensagem += f"Vitórias: {vitorias}\n"
                mensagem += f"Derrotas: {derrotas}\n"
                mensagem += f"Empates: {empates}\n"
                mensagem += f"Total de jogos: {total_jogos}\n"
                if total_jogos > 0:
                    porcentagem_vitoria = (vitorias / total_jogos) * 100
                    mensagem += f"Taxa de vitória: {porcentagem_vitoria:.1f}%\n"
                mensagem += "─" * 30 + "\n"
            
            messagebox.showinfo("Estatísticas", mensagem)
            
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar estatísticas: {e}")
    
    def resetar_estatisticas(self):
        """DELETE - Reseta todas as estatísticas"""
        try:
            if messagebox.askyesno("Confirmar", "Tem certeza que deseja resetar todas as estatísticas?"):
                self.cursor.execute("DELETE FROM estatisticas")
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Estatísticas resetadas com sucesso!")
                
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao resetar estatísticas: {e}")
    
    def executar(self):
        """Inicia o jogo"""
        self.janela.mainloop()
    
    def __del__(self):
        """Fecha conexão com banco de dados"""
        if hasattr(self, 'conn'):
            self.conn.close()

# Executar o jogo
if __name__ == "__main__":
    jogo = JogoDaVelha()
    jogo.executar()