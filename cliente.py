import socket
import threading
import tkinter as tk
from tkinter import messagebox, PhotoImage
import time


class DialogBase(tk.Toplevel):
    """Classe base para todos os diálogos da aplicação, implementando funcionalidades comuns
    como configuração de janela, ícone e posicionamento
    """

    def __init__(self, parent, titulo, tamanho='300x150'):
        """Inicializa um novo diálogo

        Args:
            parent: Janela pai do diálogo
            titulo: Título da janela
            tamanho: Dimensões da janela no formato "LARGURAxALTURA"
        """
        super().__init__(parent)
        self.configurar_janela(titulo, tamanho)
        self.result = None

    def configurar_janela(self, titulo, tamanho):
        """Configura as propriedades básicas da janela

        Args:
            titulo: Título da janela
            tamanho: Dimensões da janela
        """
        self.title(titulo)
        self.geometry(tamanho)
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.on_cancel)
        self.definir_icone()
        self.configurar_modal()
        self.centralizar()

    def definir_icone(self):
        """Define o ícone da janela"""
        try:
            self.icon = PhotoImage(file='./images/Mark_RGB_Blue.png')
            self.iconphoto(False, self.icon)
        except:
            pass

    def configurar_modal(self):
        """Configura a janela como modal, bloqueando interação com outras janelas"""
        self.attributes('-topmost', True)
        self.grab_set()

    def centralizar(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def on_cancel(self):
        """Manipula o evento de cancelamento/fechamento da janela"""
        self.result = None
        self.destroy()


class ConfigDialog(DialogBase):
    """Diálogo para configuração da conexão com o servidor"""

    def __init__(self, parent):
        """Inicializa o diálogo de configuração

        Args:
            parent: Janela pai do diálogo
        """
        super().__init__(parent, 'Conectar-se', '250x150')
        self.host = tk.StringVar()
        self.port = tk.StringVar()
        self.criar_widgets()

    def criar_widgets(self):
        """Cria e organiza todos os widgets do diálogo de configuração"""
        frame = tk.Frame(self, padx=20, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.criar_campos_entrada(frame)
        self.criar_botoes(frame)
        self.configurar_atalhos()

    def criar_campos_entrada(self, frame):
        """Cria os campos de entrada para host e porta

        Args:
            frame: Frame onde os campos serão adicionados
        """
        tk.Label(frame, text='Host:').grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        host_entry = tk.Entry(frame, textvariable=self.host, width=20)
        host_entry.grid(row=0, column=1, pady=5, padx=5)
        host_entry.focus()

        tk.Label(frame, text='Porta:').grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        tk.Entry(frame, textvariable=self.port, width=20).grid(
            row=1, column=1, pady=5, padx=5
        )

    def criar_botoes(self, frame):
        """Cria os botões de ação do diálogo

        Args:
            frame: Frame onde os botões serão adicionados
        """
        button_frame = tk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(
            button_frame,
            text='Conectar',
            command=self.on_ok,
            bg='#4CAF50',
            fg='white',
            width=10,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame,
            text='Cancelar',
            command=self.on_cancel,
            bg='#F44336',
            fg='white',
            width=10,
        ).pack(side=tk.LEFT, padx=5)

    def configurar_atalhos(self):
        """Configura atalhos de teclado para o diálogo"""
        self.bind('<Return>', lambda e: self.on_ok())
        self.bind('<Escape>', lambda e: self.on_cancel())

    def on_ok(self):
        """Valida os campos e testa a conexão antes de fechar o diálogo"""
        if not self.validar_campos():
            return

        host = self.host.get().strip()
        port = int(self.port.get().strip())

        if self.testar_conexao(host, port):
            self.result = (host, port)
            self.destroy()

    def validar_campos(self):
        """Valida os campos de host e porta

        Returns:
            bool: True se os campos são válidos, False caso contrário
        """
        if not self.host.get().strip():
            messagebox.showerror('Erro', 'O campo Host não pode estar vazio')
            return False

        try:
            int(self.port.get().strip())
            return True
        except ValueError:
            messagebox.showerror('Erro', 'A porta deve ser um número válido')
            return False

    def testar_conexao(self, host, port):
        """Testa a conexão com o servidor

        Args:
            host: Endereço do servidor
            port: Porta do servidor

        Returns:
            bool: True se a conexão foi bem sucedida, False caso contrário
        """
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(3)
            test_socket.connect((host, port))
            test_socket.close()
            return True
        except Exception as e:
            messagebox.showerror(
                'Erro de Conexão',
                f'Não foi possível conectar ao servidor {host}:{port}\n\nErro: {str(e)}',
            )
            return False


class NomeDialog(DialogBase):
    def __init__(self, parent):
        super().__init__(parent, 'Nome')
        self.criar_widgets()

    def criar_widgets(self):
        """Cria e organiza todos os widgets do diálogo de nome"""
        frame = tk.Frame(self, padx=20, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='Digite seu nome', font=('Arial', 12)).pack(
            pady=(5, 10)
        )

        self.nome_entry = tk.Entry(frame, width=30)
        self.nome_entry.pack(pady=5)
        self.nome_entry.focus_set()

        self.criar_botoes(frame)
        self.configurar_atalhos()

    def criar_botoes(self, frame):
        """Cria os botões de ação do diálogo

        Args:
            frame: Frame onde os botões serão adicionados
        """
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text='OK',
            command=self.on_ok,
            bg='#4CAF50',
            fg='white',
            width=10,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame,
            text='Cancelar',
            command=self.on_cancel,
            bg='#F44336',
            fg='white',
            width=10,
        ).pack(side=tk.LEFT, padx=5)

    def configurar_atalhos(self):
        """Configura atalhos de teclado para o diálogo"""
        self.bind('<Return>', lambda e: self.on_ok())
        self.bind('<Escape>', lambda e: self.on_cancel())

    def on_ok(self):
        """Valida o nome inserido antes de fechar o diálogo"""
        nome = self.nome_entry.get().strip()
        if nome:
            self.result = nome
            self.destroy()
        else:
            messagebox.showwarning('Aviso', 'Nome é obrigatório', parent=self)


class SalaDialog(DialogBase):
    def __init__(self, parent, host, port):
        super().__init__(parent, 'Selecionar Sala', '400x300')
        self.host = host
        self.port = port
        self.salas_disponiveis = []
        self.criar_widgets()
        self.after(100, self.obter_salas)

    def criar_widgets(self):
        """Cria e organiza todos os widgets do diálogo de seleção de sala"""
        frame = tk.Frame(self, padx=20, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame, text='Salas Disponíveis:', font=('Arial', 12, 'bold')
        ).pack(anchor=tk.W, pady=(0, 10))

        self.criar_lista_salas(frame)
        self.criar_botoes(frame)

    def criar_lista_salas(self, frame):
        """Cria a lista de salas disponíveis com barra de rolagem

        Args:
            frame: Frame onde a lista será adicionada
        """
        list_frame = tk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.sala_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('Arial', 10),
            height=10,
        )
        self.sala_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.sala_listbox.yview)

        self.sala_listbox.bind('<Double-1>', lambda e: self.selecionar_sala())

        self.status_label = tk.Label(
            frame, text='Carregando salas...', fg='blue'
        )
        self.status_label.pack(pady=5)

    def criar_botoes(self, frame):
        """Cria os botões de ação do diálogo de sala

        Args:
            frame: Frame onde os botões serão adicionados
        """
        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.btn_nova_sala = tk.Button(
            button_frame,
            text='Nova Sala',
            command=self.criar_nova_sala,
            bg='#4CAF50',
            fg='white',
            width=15,
        )
        self.btn_nova_sala.pack(side=tk.LEFT, padx=5)

        self.btn_entrar = tk.Button(
            button_frame,
            text='Entrar',
            command=self.selecionar_sala,
            bg='#2196F3',
            fg='white',
            width=15,
            state=tk.DISABLED,
        )
        self.btn_entrar.pack(side=tk.RIGHT, padx=5)

        self.btn_atualizar = tk.Button(
            button_frame,
            text='Atualizar',
            command=self.obter_salas,
            bg='#FF9800',
            fg='white',
            width=15,
        )
        self.btn_atualizar.pack(side=tk.RIGHT, padx=5)

    def obter_salas(self):
        """Obtém a lista de salas disponíveis do servidor"""
        self.status_label.config(text='Carregando salas...', fg='blue')
        self.sala_listbox.delete(0, tk.END)
        self.btn_entrar.config(state=tk.DISABLED)

        try:
            with socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            ) as temp_socket:
                temp_socket.settimeout(5)
                temp_socket.connect((self.host, self.port))

                if temp_socket.recv(1024).decode() == 'SALA':
                    temp_socket.send(b'#LISTAR_SALAS#')
                    temp_socket.send(b'#LISTAR_SALAS#')

                    salas_data = temp_socket.recv(1024).decode()
                    self.atualizar_lista_salas(salas_data)
                else:
                    self.status_label.config(
                        text='Erro ao comunicar com o servidor', fg='red'
                    )

        except Exception as e:
            self.status_label.config(text=f'Erro: {str(e)}', fg='red')

    def atualizar_lista_salas(self, salas_data):
        """Atualiza a interface com a lista de salas recebida

        Args:
            salas_data: String com as salas disponíveis separadas por |
        """
        self.salas_disponiveis = [
            sala for sala in salas_data.split('|') if sala
        ]

        if self.salas_disponiveis:
            for sala in self.salas_disponiveis:
                self.sala_listbox.insert(tk.END, sala)
            self.status_label.config(
                text=f'{len(self.salas_disponiveis)} sala(s) disponível(is)',
                fg='green',
            )
            self.sala_listbox.selection_set(0)
            self.btn_entrar.config(state=tk.NORMAL)
        else:
            self.status_label.config(
                text='Nenhuma sala disponível. Crie uma nova!', fg='orange'
            )

    def selecionar_sala(self):
        """Confirma a seleção da sala e fecha o diálogo"""
        selection = self.sala_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                'Aviso', 'Selecione uma sala ou crie uma nova', parent=self
            )
            return

        self.result = self.sala_listbox.get(selection[0])
        self.destroy()

    def criar_nova_sala(self):
        """Abre o diálogo para criar uma nova sala"""
        nova_sala_dialog = NovaSalaDialog(self)
        self.wait_window(nova_sala_dialog)

        if nova_sala_dialog.result:
            self.result = nova_sala_dialog.result
            self.destroy()


class NovaSalaDialog(DialogBase):
    def __init__(self, parent):
        super().__init__(parent, 'Nova Sala')
        self.criar_widgets()

    def criar_widgets(self):
        """Cria os principais elementos da tela, como o frame dos campos e botões"""
        frame = tk.Frame(self, padx=20, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='Digite o nome da sala', font=('Arial', 12)).pack(
            pady=(5, 10)
        )

        self.sala_entry = tk.Entry(frame, width=30)
        self.sala_entry.pack(pady=5)
        self.sala_entry.focus_set()

        self.criar_botoes(frame)
        self.configurar_atalhos()

    def criar_botoes(self, frame):
        """Cria os botões de ação do diálogo

        Args:
            frame: Frame onde os botões serão adicionados
        """
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text='Criar',
            command=self.on_ok,
            bg='#4CAF50',
            fg='white',
            width=10,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame,
            text='Cancelar',
            command=self.on_cancel,
            bg='#F44336',
            fg='white',
            width=10,
        ).pack(side=tk.LEFT, padx=5)

    def configurar_atalhos(self):
        """Configura atalhos de teclado para o diálogo"""
        self.bind('<Return>', lambda e: self.on_ok())
        self.bind('<Escape>', lambda e: self.on_cancel())

    def on_ok(self):
        """Valida os campos e testa a conexão antes de fechar o diálogo"""
        sala = self.sala_entry.get().strip()
        if sala:
            self.result = sala
            self.destroy()
        else:
            messagebox.showwarning(
                'Aviso', 'Nome da sala é obrigatório', parent=self
            )


class ClienteChat:
    """Classe principal do cliente de chat, responsável por gerenciar a interface e a comunicação com o servidor"""

    def __init__(self, root):
        """Inicializa o cliente de chat

        Args:
            root: Janela principal da aplicação
        """
        self.root = root
        self.configurar_janela()
        self.inicializar_variaveis()
        self.root.after(100, self.iniciar_configuracao)

    def configurar_janela(self):
        """Configura as propriedades da janela principal"""
        self.root.title('Chat')
        self.root.geometry('500x600')
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.definir_icone()
        self.root.withdraw()

    def definir_icone(self):
        """Define o ícone da janela principal"""
        try:
            self.icon = PhotoImage(file='./images/Mark_RGB_Blue.png')
            self.root.iconphoto(False, self.icon)
        except Exception as e:
            print(f'Erro ao carregar ícone: {e}')

    def inicializar_variaveis(self):
        """Inicializa as variáveis de controle do cliente"""
        self.host = None
        self.port = None
        self.client_socket = None
        self.connected = False
        self.sala = None
        self.nome = None
        self.thread_ativa = False
        self.receive_thread = None

    def iniciar_configuracao(self):
        """Inicia o processo de configuração do cliente, incluindo conexão, nome e sala"""
        if not self.configurar_conexao():
            return

        if not self.configurar_nome():
            return

        if not self.configurar_sala():
            return

        self.criar_interface()
        self.conectar_servidor()
        self.root.deiconify()

    def configurar_conexao(self):
        """Configura a conexão com o servidor através do diálogo de configuração

        Returns:
            bool: True se a configuração foi bem sucedida, False caso contrário
        """
        config_dialog = ConfigDialog(self.root)
        self.root.wait_window(config_dialog)

        if config_dialog.result is None:
            self.root.quit()
            return False

        self.host, self.port = config_dialog.result
        return True

    def configurar_nome(self):
        """Configura o nome do usuário através do diálogo de nome

        Returns:
            bool: True se o nome foi configurado, False caso contrário
        """
        nome_dialog = NomeDialog(self.root)
        self.root.wait_window(nome_dialog)

        if nome_dialog.result is None:
            self.root.quit()
            return False

        self.nome = nome_dialog.result
        return True

    def configurar_sala(self):
        """Configura a sala através do diálogo de seleção de sala

        Returns:
            bool: True se a sala foi selecionada, False caso contrário
        """
        temp_window = tk.Toplevel(self.root)
        temp_window.withdraw()

        sala_dialog = SalaDialog(temp_window, self.host, self.port)
        self.root.wait_window(sala_dialog)
        temp_window.destroy()

        if sala_dialog.result is None:
            self.root.quit()
            return False

        self.sala = sala_dialog.result
        return True

    def criar_interface(self):
        """Cria a interface principal do chat"""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.criar_barra_info(main_frame)
        self.criar_area_mensagens(main_frame)
        self.criar_area_entrada(main_frame)

    def criar_barra_info(self, frame):
        """Cria a barra de informações superior

        Args:
            frame: Frame onde a barra será adicionada
        """
        info_frame = tk.Frame(frame)
        info_frame.pack(fill=tk.X)

        tk.Label(
            info_frame, text=f'Conectado a: {self.host}:{self.port}'
        ).pack(side=tk.LEFT)
        tk.Label(info_frame, text=f'Sala: {self.sala}').pack(
            side=tk.LEFT, padx=10
        )

        self.btn_sair_sala = tk.Button(
            info_frame,
            text='Sair da Sala',
            command=self.sair_da_sala,
            bg='#FF5722',
            fg='white',
        )
        self.btn_sair_sala.pack(side=tk.RIGHT)

    def criar_area_mensagens(self, frame):
        """Cria a área de exibição de mensagens

        Args:
            frame: Frame onde a área será adicionada
        """
        self.mensagens_area = tk.Text(
            frame, state=tk.DISABLED, wrap=tk.WORD, height=20, bg='#f5f5f5'
        )
        self.mensagens_area.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = tk.Scrollbar(self.mensagens_area)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.mensagens_area.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.mensagens_area.yview)

    def criar_area_entrada(self, frame):
        """Cria a área de entrada de mensagens

        Args:
            frame: Frame onde a área será adicionada
        """
        entrada_frame = tk.Frame(frame)
        entrada_frame.pack(fill=tk.X, pady=5)

        self.entrada_mensagem = tk.Entry(entrada_frame)
        self.entrada_mensagem.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)
        )
        self.entrada_mensagem.bind('<Return>', self.enviar_mensagem)
        self.entrada_mensagem.focus()

        self.btn_enviar = tk.Button(
            entrada_frame,
            text='Enviar',
            command=self.enviar_mensagem,
            bg='#4CAF50',
            fg='white',
        )
        self.btn_enviar.pack(side=tk.RIGHT)

    def conectar_servidor(self):
        """Estabelece conexão com o servidor e inicia a thread de recebimento de mensagens"""
        try:
            self.client_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            self.client_socket.connect((self.host, self.port))

            if self.client_socket.recv(1024).decode() == 'SALA':
                self.client_socket.send(self.sala.encode())
                self.client_socket.send(self.nome.encode())

            self.connected = True
            self.thread_ativa = True

            self.receive_thread = threading.Thread(
                target=self.receber_mensagens
            )
            self.receive_thread.daemon = True
            self.receive_thread.start()

            self.adicionar_mensagem(
                f'Conectado ao servidor. Bem-vindo à sala {self.sala}!'
            )

        except Exception as e:
            messagebox.showerror(
                'Erro de Conexão',
                f'Erro ao estabelecer comunicação com o servidor: {str(e)}',
            )
            self.root.quit()

    def receber_mensagens(self):
        """Thread que recebe mensagens do servidor continuamente"""
        while self.thread_ativa and self.connected:
            try:
                mensagem = self.client_socket.recv(1024).decode()
                if mensagem:
                    self.adicionar_mensagem(mensagem)
            except:
                if self.thread_ativa:
                    self.adicionar_mensagem('Conexão com o servidor perdida!')
                self.connected = False
                break

    def enviar_mensagem(self, event=None):
        """Envia uma mensagem para o servidor

        Args:
            event: Evento que disparou a função (opcional)
        """
        mensagem = self.entrada_mensagem.get().strip()
        if mensagem and self.connected:
            try:
                self.client_socket.send(mensagem.encode())
                self.entrada_mensagem.delete(0, tk.END)
            except:
                self.adicionar_mensagem(
                    'Erro ao enviar mensagem. Verifique sua conexão.'
                )
                self.connected = False

    def adicionar_mensagem(self, mensagem):
        """Adiciona uma mensagem à área de chat

        Args:
            mensagem: Texto da mensagem a ser adicionada
        """
        try:
            if (
                hasattr(self, 'mensagens_area')
                and self.mensagens_area.winfo_exists()
            ):
                self.mensagens_area.config(state=tk.NORMAL)
                self.mensagens_area.insert(tk.END, mensagem + '\n')
                self.mensagens_area.see(tk.END)
                self.mensagens_area.config(state=tk.DISABLED)
        except tk.TclError:
            pass

    def sair_da_sala(self):
        """Gerencia o processo de sair da sala atual e entrar em uma nova"""
        if not messagebox.askyesno(
            'Sair da Sala', f"Deseja realmente sair da sala '{self.sala}'?"
        ):
            return

        self.desconectar()
        self.limpar_interface()
        self.root.withdraw()

        if not self.configurar_sala():
            return

        self.criar_interface()
        self.conectar_servidor()
        self.root.deiconify()

    def desconectar(self):
        """Desconecta do servidor e finaliza a thread de recebimento"""
        self.thread_ativa = False
        if self.connected and self.client_socket:
            try:
                self.client_socket.close()
                self.connected = False
            except:
                pass
        time.sleep(0.2)

    def limpar_interface(self):
        """Limpa a interface do cliente"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_closing(self):
        """Manipula o evento de fechamento da aplicação"""
        if messagebox.askokcancel('Sair', 'Deseja realmente sair do chat?'):
            self.desconectar()
            self.root.destroy()


try:
    root = tk.Tk()
    app = ClienteChat(root)
    root.mainloop()
except Exception as e:
    print(f'❌ {e}')
