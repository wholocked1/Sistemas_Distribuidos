import socket
import msgpack

#Explicação do que cada coisa faz ta no cliente 1

NOME_CLIENTE = "cliente2"

def publicar_mensagem():
    postagem = input("Digite sua postagem: ")

    payload = {
        "tipo": "postar",
        "origem": NOME_CLIENTE,
        "destino": "",
        "mensagem": postagem
    }

    soc.send(msgpack.packb(payload, use_bin_type=True))# comprimir o pacote de dado para ser enviada pela camada de rede
    resposta = msgpack.unpackb(soc.recv(1024), raw=False)   # o servidor nos retornara um resposta se ele receber algo, fiz essa interação para ficar algo legal e resposivo tipo o simbolo da nike quando a mensagem  no zap é enviada
    print("Status:", resposta.get("status")) # retornar o status

def vizualizar_postagens():
    origem = input("Digite com quem deseja vizualizar as postagens (ex: cliente1): ")
    payload = {
        "tipo": "vizualizar",
        "origem": origem
    }

    try:
        soc.send(msgpack.packb(payload, use_bin_type=True))
        resposta = soc.recv(4096)

        if not resposta:
            print("Nenhuma resposta do servidor.")
            return

        dados = msgpack.unpackb(resposta, raw=False)
        mensagens = dados.get("mensagens", [])

        if not mensagens:
            print("Nenhuma mensagem recebida.")
            return

        print("\nMensagens recebidas:\n")
        for i, msg in enumerate(mensagens, 1):
            origem = msg.get("origem", "desconhecido")
            texto = msg.get("mensagem", "")
            print(f"{i}. {origem} → {texto}")

    except Exception as e:
        print(f"Erro ao visualizar mensagens: {e}")

def enviar_mensagem_privada():
    destino = input("Digite o destinatário (ex: cliente1): ") 
    mensagem = input("Digite sua mensagem: ")

    payload = {
        "tipo": "enviar",
        "origem": NOME_CLIENTE,
        "destino": destino,
        "mensagem": mensagem
    }

    soc.send(msgpack.packb(payload, use_bin_type=True))
    resposta = msgpack.unpackb(soc.recv(1024), raw=False)
    print("Status:", resposta.get("status"))

def visualizar_mensagens():
    origem = input("Digite com quem deseja vizualizar a conversa (ex: cliente1): ")
    payload = {
        "tipo": "receber",
        "origem": origem,
        "destino": NOME_CLIENTE
    }

    try:
        soc.send(msgpack.packb(payload, use_bin_type=True))
        resposta = soc.recv(4096)

        if not resposta:
            print("Nenhuma resposta do servidor.")
            return

        dados = msgpack.unpackb(resposta, raw=False)
        mensagens = dados.get("mensagens", [])

        if not mensagens:
            print("Nenhuma mensagem recebida.")
            return

        print("\nMensagens recebidas:\n")
        for i, msg in enumerate(mensagens, 1):
            origem = msg.get("origem", "desconhecido")
            texto = msg.get("mensagem", "")
            print(f"{i}. {origem} → {texto}")

    except Exception as e:
        print(f"Erro ao visualizar mensagens: {e}")

def menu():
    #fiz um menu interativo (ou quase isso) para usarmos em nosso projeto
    while True:
        print("\nMenu:")
        print("1 - Publicar mensagem")
        print("2 - Ver mensagens publicadas")
        print("3 - Enviar mensagem privada")
        print("4 - Visualizar mensagens privadas")
        print("0 - Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            publicar_mensagem()
        elif escolha == "2":
            vizualizar_postagens()
        elif escolha == "3":
            enviar_mensagem_privada()
        elif escolha == "4":
            visualizar_mensagens()
        elif escolha == "0":
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 65432

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((HOST, PORT))

    try:
        menu()
    finally:
        soc.close()