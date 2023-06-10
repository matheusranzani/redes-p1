import socket
import asyncio

class Servidor:
    def __init__(self, porta):
        s = self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', porta))
        s.listen(5)
        self.apelido_lc_map_conexao = {}
        self.conexao_map_apelido = {}
        self.canais = {}
        self.canais_nome_real = {}

    def liberar_apelido(self, apelido):
        if apelido != b'*':
            del self.apelido_lc_map_conexao[apelido.lower()]

    def apelidar_conexao(self, conexao, apelido):
        if self.conexao_apelidada(conexao):
            apelido_atual = self.get_apelido(conexao)
            self.liberar_apelido(apelido_atual)
        self.apelido_lc_map_conexao[apelido.lower()] = conexao
        self.conexao_map_apelido[conexao] = apelido


    def ligar_conexao_a_canal(self, canal, conexao):
        canal_lc = canal.lower()
        conexoes = self.get_conexoes_do_canal(canal)
        if not conexoes: # se conjunto vazio (se nao ha conexoes: estamos abrindo um novo canal)
            self.canais_nome_real[canal_lc] = canal
        conexoes.add(conexao)
        self.canais[canal_lc] = conexoes

    def desligar_conexao_de_canal(self, canal, conexao):
        self.canais[canal.lower()].remove(conexao)

    def transmitir_exceto(self, canal, mensagem, exceto_conexao = None):
        conexoes = self.get_conexoes_do_canal(canal)
        for conexao in conexoes:
            if conexao != exceto_conexao:
                conexao.enviar(mensagem)


    def apelido_em_uso(self, apelido):
        return apelido.lower() in self.apelido_lc_map_conexao

    def conexao_apelidada(self, conexao):
        return conexao in self.conexao_map_apelido

    def get_apelido(self, conexao):
        return self.conexao_map_apelido.get(conexao, b'*')
    
    def get_conexao(self, apelido):
        return self.apelido_lc_map_conexao.get(apelido.lower())

    def get_conexoes_do_canal(self, canal): # Note que todos os canais existem para efeitos do usuario ded get_conexoes_do_canal!
        return self.canais.get(canal.lower(), set())
    
    def get_nome_real_do_canal(self, canal):
        return self.canais_nome_real.get(canal.lower())

    def get_apelidos_das_conexoes_do_canal(self, canal):
        apelidos = set()
        conexoes = self.get_conexoes_do_canal(canal)
        for con in conexoes:
            apelidos.add(self.get_apelido(con))
        return apelidos

    def get_canais(self):
        return self.canais


    def registrar_monitor_de_conexoes_aceitas(self, callback):
        asyncio.get_event_loop().add_reader(self.s, lambda: callback(Conexao(self.s.accept())))


class Conexao:
    def __init__(self, accept_tuple):
        self.s, _ = accept_tuple
        self.residuo = b''

    def registrar_recebedor(self, callback):
        asyncio.get_event_loop().add_reader(self.s, lambda: callback(self, self.s.recv(8192)))

    def enviar(self, dados):
        self.s.sendall(dados + b'\r\n')

    def fechar(self):
        asyncio.get_event_loop().remove_reader(self.s)
        self.s.close()



