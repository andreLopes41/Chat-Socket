import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, PhotoImage
import time


class Servidor:
    """Classe do Serviddor"""

    def __init__(self, root):
        """Inicializa o servidor

        Args:
            root: Janela pai do servidor
        """
        self.root = root
        self.configurar_janela()
        self.criar_widgets()
        self.inicializar_variaveis()

    def configurar_janela(self):
        """Define as propriedades da Janela do Servidor como título, tamanho, janela é redimesionável e seu ícone"""
        self.root.title('Gerenciar Servidor')
        self.root.geometry('600x400')
        self.root.resizable(True, True)
        try:
            self.root.iconphoto(
                False, PhotoImage(file='./images/Mark_RGB_Blue.png')
            )
        except:
            pass

    def criar_widgets(self):
        """Cria os principais elementos da tela, como o frame dos campos, botões e o frame de logs"""
        self.criar_frame_config()
        self.criar_area_logs()

    def criar_frame_config(self):
        """Cria o frame superior que contém os campos de entrada para host e porta, além dos botões de iniciar e pausar o servidor"""
        frame_config = tk.Frame(self.root)
        frame_config.pack(pady=10)

        tk.Label(frame_config, text='Host:').grid(
            row=0, column=0, padx=5, pady=5
        )
        self.host_entry = tk.Entry(frame_config, width=15)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_config, text='Porta:').grid(
            row=0, column=2, padx=5, pady=5
        )
        self.port_entry = tk.Entry(frame_config, width=6)
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)

        self.btn_iniciar = tk.Button(
            frame_config,
            text='Iniciar Servidor',
            command=self.iniciar_servidor,
            bg='#4CAF50',
            fg='white',
        )
        self.btn_iniciar.grid(row=0, column=4, padx=5, pady=5)

        self.btn_pausar = tk.Button(
            frame_config,
            text='Pausar Servidor',
            command=self.pausar_servidor,
            bg='#F44336',
            fg='white',
            state=tk.DISABLED,
        )
        self.btn_pausar.grid(row=0, column=5, padx=5, pady=5)

    def criar_area_logs(self):
        """Cria a área de logs do servidor, onde serão exibidas todas as mensagens de status e eventos"""
        tk.Label(self.root, text='Logs do Servidor:').pack(
            anchor=tk.W, padx=10
        )
        self.log_area = scrolledtext.ScrolledText(
            self.root, width=70, height=20
        )
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def inicializar_variaveis(self):
        """Inicializa as variáveis de controle do servidor, como status de execução, socket e dicionário de salas"""
        self.servidor_rodando = False
        self.server = None
        self.thread_servidor = None
        self.salas = {}

    def log(self, mensagem):
        """Adiciona uma mensagem ao log com timestamp atual

        Args:
            mensagem: Texto da mensagem a ser registrada no log
        """
        timestamp = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())
        log_msg = f'[{timestamp}] {mensagem}\n'
        self.log_area.insert(tk.END, log_msg)
        self.log_area.see(tk.END)
        print(log_msg, end='')

    def validar_campos(self):
        """Valida os campos de host e porta antes de iniciar o servidor

        Returns:
            tuple: (host, port) se os campos forem válidos, None caso contrário
        """
        host = self.host_entry.get().strip()
        if not host:
            self.log('Erro: Campo Host não preenchido')
            return None

        porta = self.port_entry.get().strip()
        if not porta:
            self.log('Erro: Campo Porta não preenchido')
            return None

        try:
            port = int(porta)
            return host, port
        except ValueError:
            self.log('Erro: Porta inválida, deve ser um número')
            return None

    def iniciar_servidor(self):
        """Inicia o servidor em uma thread separada após validar os campos de entrada"""
        if self.servidor_rodando:
            return

        dados = self.validar_campos()
        if not dados:
            return

        host, port = dados
        self.thread_servidor = threading.Thread(
            target=self.executar_servidor, args=(host, port)
        )
        self.thread_servidor.daemon = True
        self.thread_servidor.start()

        self.servidor_rodando = True
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_pausar.config(state=tk.NORMAL)
        self.log(f'Servidor iniciado em {host}:{port}')

    def pausar_servidor(self):
        """Pausa a execução do servidor e fecha todas as conexões ativas"""
        if not self.servidor_rodando:
            return

        self.servidor_rodando = False
        if self.server:
            try:
                self.server.close()
            except:
                pass

        self.log('Servidor pausado')
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_pausar.config(state=tk.DISABLED)

    def broadcast(self, sala, mensagem):
        """Envia uma mensagem para todos os clientes em uma sala específica

        Args:
            sala: Nome da sala
            mensagem: Mensagem a ser enviada
        """
        if sala not in self.salas:
            return

        clientes_para_remover = []
        for cliente in self.salas[sala]:
            try:
                if isinstance(mensagem, str):
                    mensagem = mensagem.encode()
                cliente.send(mensagem)
            except:
                clientes_para_remover.append(cliente)

        for cliente in clientes_para_remover:
            if cliente in self.salas[sala]:
                self.salas[sala].remove(cliente)

    def processar_cliente(self, client, addr):
        """Processa a conexão inicial de um cliente, determinando se é uma solicitação de lista de salas ou entrada em sala

        Args:
            client: Socket do cliente
            addr: Endereço do cliente
        """
        try:
            self.log(f'{addr} se conectou ao Servidor')
            client.send(b'SALA')
            sala = client.recv(1024).decode()

            if sala == '#LISTAR_SALAS#':
                self.enviar_lista_salas(client, addr)
                return

            nome = client.recv(1024).decode()
            self.adicionar_cliente_sala(client, nome, sala, addr)

        except Exception as e:
            self.fechar_conexao(client)

    def enviar_lista_salas(self, client, addr):
        """Envia a lista de salas disponíveis para um cliente

        Args:
            client: Socket do cliente
            addr: Endereço do cliente
        """
        client.recv(1024).decode()
        salas_disponiveis = '|'.join(self.salas.keys())
        client.send(salas_disponiveis.encode())
        self.log(f'Lista de salas enviada para {addr}')
        client.close()

    def adicionar_cliente_sala(self, client, nome, sala, addr):
        """Adiciona um cliente a uma sala e inicia uma thread para gerenciar suas mensagens

        Args:
            client: Socket do cliente
            nome: Nome do usuário
            sala: Nome da sala
            addr: Endereço do cliente
        """
        if sala not in self.salas:
            self.salas[sala] = []

        self.salas[sala].append(client)
        self.log(f'{nome} se conectou na sala {sala} INFO {addr}')
        self.broadcast(sala, f'{nome} Entrou na sala\n')

        thread_cliente = threading.Thread(
            target=self.gerenciar_mensagens, args=(nome, sala, client)
        )
        thread_cliente.daemon = True
        thread_cliente.start()

    def gerenciar_mensagens(self, nome, sala, client):
        """Gerencia o recebimento de mensagens de um cliente específico

        Args:
            nome: Nome do usuário
            sala: Nome da sala
            client: Socket do cliente
        """
        while self.servidor_rodando:
            try:
                mensagem = client.recv(1024)
                if not mensagem:
                    break

                mensagem_formatada = f'{nome}: {mensagem.decode()}\n'
                self.log(f'[Sala {sala}] {mensagem_formatada.strip()}')
                self.broadcast(sala, mensagem_formatada)
            except:
                break

        self.remover_cliente(nome, sala, client)

    def remover_cliente(self, nome, sala, client):
        """Remove um cliente de uma sala e notifica os demais usuários

        Args:
            nome: Nome do usuário
            sala: Nome da sala
            client: Socket do cliente
        """
        if sala in self.salas and client in self.salas[sala]:
            self.salas[sala].remove(client)
            self.log(f'{nome} saiu da sala {sala}')
            self.broadcast(sala, f'{nome}: Saiu da sala\n')
        self.fechar_conexao(client)

    def fechar_conexao(self, client):
        """Fecha a conexão com um cliente

        Args:
            client: Socket do cliente
        """
        try:
            client.close()
        except:
            pass

    def executar_servidor(self, host, port):
        """Executa o loop principal do servidor, aceitando novas conexões

        Args:
            host: Endereço IP do servidor
            port: Porta do servidor
        """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((host, port))
            self.server.listen()
            self.server.settimeout(1)

            while self.servidor_rodando:
                try:
                    client, addr = self.server.accept()
                    self.processar_cliente(client, addr)
                except socket.timeout:
                    continue
                except:
                    if self.servidor_rodando:
                        continue
        except Exception as e:
            if self.servidor_rodando:
                self.log(f'Erro ao iniciar servidor: {str(e)}')
        finally:
            if self.server:
                self.server.close()


try:
    root = tk.Tk()
    app = Servidor(root)
    root.mainloop()
except Exception as e:
    print(f'❌ {e}')
