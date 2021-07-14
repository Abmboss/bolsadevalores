import socket
import threading
from yahooquery import Ticker

class Servidor():
    """
    Classe Servidor - Calculadora remota - API Socket
    """
    def __init__(self, host, port):
        """
        Construtor da classe servidor
        """
        self._host = host
        self._port = port
        self._tcp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def start(self):
        """
        Inicia a execução do serviço
        """
        endpoint = (self._host,self._port)  
        try:
            self._tcp.bind(endpoint) 
            self._tcp.listen(1)  
            print("Servidor foi iniciado em ", self._host,":", self._port)
            while True:   
                con, client = self._tcp.accept()  
                self._service(con, client)
        except Exception as e:
            print("Erro ao inicializar o servidor ",e.args)
    
    def _service(self, con, client):
        """
        Método que implementa o serviço de calculadora
        :param con: Objeto socket utilizado para enviar e receber os dados
        :param client: Endereço e porta do cliente
        """
        print("Atendendo cliente ",client)
        while True: 
            try:
                msg = con.recv(2048)  
                msg_s = str(msg.decode('ascii'))
                petr = Ticker("ABEV3.SA")
                
                if msg_s == '1':
                    asset_profile = petr.asset_profile
                    resp = asset_profile['ABEV3.SA']['longBusinessSummary']
                    resp = resp.encode("ascii", "replace")
                elif msg_s == '2':
                    resp = petr.quotes['ABEV3.SA']['ask']
                elif msg_s == '3':
                    resp = petr.history(period="7d")
                elif msg_s == '4':
                    resp = petr.valuation_measures
                else:
                    resp = "Operacao invalida"
                
                con.send(bytes(str(resp),'ascii'))  
                print(client, "-> requisição atendida")
            except OSError as e:
                print("Erro na conexão ", client,": ",e.args)
                return
            except Exception as e:
                print("Erros nos dados recebidos do cliente ", client, ": ",e.args)
                con.send(bytes("Erro",'ascii'))

class ServidorMT(Servidor):
    """
    Classe ServidorMT - Calculadora remota - Multithreading
    """
    def __init__(self, host, port):
        """
        Construtor da classe ServidorMT
        """
        super().__init__(host,port)
        self.__threadPool = {} 
    
    def start(self):
        """
        Inicia a execução do serviço
        """
        
        endpoint = (self._host,self._port)  
        try:
            self._tcp.bind(endpoint) 
            self._tcp.listen(1)  
            print("Servidor foi iniciado em ", self._host,":", self._port)
            while True:   
                con, client = self._tcp.accept()  
                self.__threadPool[client] = threading.Thread(target=self._service, args=(con, client))
                self.__threadPool[client].start() 

        except Exception as e:
            print("Erro ao inicializar o servidor ",e.args)
    