import socket
import threading
import msgpack


# O SERVIDOR DOIS VAI SER ULTILIZADO PARA TROCAS DE MENSAGENS ENTRE CLIENTES VIA MSGPACK


#1 inicializar o servidor de troca de mensagens

#dicionário para mapear cliente e socket para futuras comunicacoes
clientes = {}

def handle_client(conn, addr):
    try:
        # Recebe o nome do usuário
        nome_raw = conn.recv(4096)
        nome = msgpack.unpackb(nome_raw, raw=False)
        print(f"[+] Conectado: {nome} ({addr})")

        # Adiciona o cliente à lista
        clientes[nome] = conn

        # Espera a mensagem empacotada (from, to e message)
        data = conn.recv(4096)
        if not data:
            return

        pacote = msgpack.unpackb(data, raw=False)
        destino = pacote["to"]

        if destino in clientes:
            try:
                clientes[destino].send(msgpack.packb(pacote, use_bin_type=True))
                print(f" {nome} -> {destino}: {pacote['message']}")
            except Exception as e:
                print(f" Erro ao enviar mensagem para {destino}: {e}")
        else:
            print(f" Destinatário '{destino}' não está conectado.")

    except Exception as e:
        print(f" Erro com cliente {addr}: {e}")
    finally:
        conn.close()





def main():
    host = 'localhost'
    port = 5555

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    print(f" Servidor de mensagens ligado em {host}:{port}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()