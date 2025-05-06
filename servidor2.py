import socket
import threading
import msgpack
import json
import os

mensagens = []  # Lista em memória


#para fins de depuração iremos asalvar um registro de auditoria com todos as mensagens
LOG_PATH = "log_mensagens.json"

def carregar_log():
    if os.path.exists(LOG_PATH): # biblioteca os serve para verificar se o arquivo existe naquele diretorio
        with open(LOG_PATH, "r", encoding="utf-8") as f: #abrir arquivo para apenas leitura (é necessario que ele exista por isso a condição)
            return json.load(f) #retorna o conteúdo do arquivo
    return [] #retorna a lista vazia se não existir

def salvar_em_log(mensagem):
    todas_mensagens = carregar_log() #declarar uma variavel para armazenar todo o conteudo anterior
    todas_mensagens.append(mensagem) # adiciona na ponta a ultima mensagem, como é json nao da problema
    with open(LOG_PATH, "w", encoding="utf-8") as f: # abre o arquivo em write (apaga tudo) dava pra ter usado o wa+ fiquei com preguiça
        json.dump(todas_mensagens, f, ensure_ascii=False, indent=2) # serializa a string para um formato determinado , consultar docs.python.org 
 
def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] {addr} conectado.")

    while True:

        # deve ser colocado em um try catch em um while pois o dado vem fragmentado, ele depende do tamanho do buffer para receber e o quanto um dado consegue ser serializado por um determinado computador,
        # vimos esse conceito em redes de computadores
        try:
            data = conn.recv(1024)# o tamanho do buffer deev ter a base 2 para evitar qualquer tipo de problema, ta na documentação
            if not data:
                break
            #realiza o unpack da mensagem enquanto está recebendo
            msg = msgpack.unpackb(data, raw=False)
            # foi criado dois tipos de mensagens, envio e recebimento, quando o pacote é de envio salvara no json, quando de recebimento le o json e retorna para o cliente
            if msg["tipo"] == "enviar":
                mensagens.append(msg)
                salvar_em_log(msg)
                conn.send(msgpack.packb({"status": "mensagem enviada!"}, use_bin_type=True))

            elif msg["tipo"] == "receber":
                destino = msg["destino"]
                recebidas = [m for m in mensagens if m["destino"] == destino]
                conn.send(msgpack.packb({"mensagens": recebidas}, use_bin_type=True))
        # caso ocorra algum erro inesperado tem o catch (fins de depuração), não remover
        except Exception as e:
            print(f"[ERRO] {e}")
            break

    conn.close() # fecha a conexão, não é necessario manter ela ativa 24/7 gasta recurso, se precisar chamer de novo o servidor se vira

def start_server(): # fluxo principal
    global mensagens # como mensagens é uma variavel global ultilizada fora dessa função deve ser declarada como global
    mensagens = carregar_log()  # Recarrega mensagens do arquivo no início

    HOST = '127.0.0.1' # escolhi um host aleatorio para o servidor, caso for subir algo no docker só precisa alterar aqui e nada quebra
    PORT = 65432 # porta de escolha aleatoria para nao conflitar com os outros servidores 

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #iniciando o socket em TCP/IP
    server.bind((HOST, PORT)) #bind no host e porta
    server.listen() # comecar a escuta do servidor

    print("[SERVIDOR] Iniciado em", (HOST, PORT))# log para mostrar que o servidor foi iniciado

    while True:
        conn, addr = server.accept() #aceitar outra conexao qualquer, sem filtro
        thread = threading.Thread(target=handle_client, args=(conn, addr)) # iniciar as tratativas do cliente em uma thread paralela, mais de um cliente pode acessar o servidor por vez
        thread.start()



#dizer para o python para chamar essa função assim que esse código foi inicializado
if __name__ == "__main__":
    start_server()