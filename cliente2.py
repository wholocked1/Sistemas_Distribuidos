import socket
import msgpack

#Explicação do que cada coisa faz ta no cliente 1

NOME_CLIENTE = "cliente2"  

def enviar_mensagem_privada():
    destino = input("Digite o destinatário (ex: cliente2): ") 
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

def visualizar_mensagens(soc, NOME_CLIENTE):
    payload = {
        "tipo": "receber",
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
    while True:
        print("\nMenu:")
        print("1 - Publicar mensagem (not done)") 
        print("2 - Enviar mensagem privada")
        print("3 - Visualizar mensagens privadas com o cliente 1")
        print("0 - Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == "2":
            enviar_mensagem_privada()
        elif escolha == "3":
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