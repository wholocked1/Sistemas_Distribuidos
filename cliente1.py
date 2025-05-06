import socket
import msgpack

NOME_CLIENTE = "cliente1"  # Altere para "cliente2" no outro script



def enviar_mensagem_privada():
    destino = input("Digite o destinatário (ex: cliente2): ") # versatilidade para conseguir escolher o cliente a ser enviado por hora só foi feito entre o cliente 1 e 2
    mensagem = input("Digite sua mensagem: ")


    # chamei de payload por conta de um conceito de redes de computadores, não me aprofundarei no assunto
    payload = {
        "tipo": "enviar",
        "origem": NOME_CLIENTE,
        "destino": destino,
        "mensagem": mensagem
    }

    soc.send(msgpack.packb(payload, use_bin_type=True))# comprimir o pacote de dado para ser enviada pela camada de rede
    resposta = msgpack.unpackb(soc.recv(1024), raw=False)   # o servidor nos retornara um resposta se ele receber algo, fiz essa interação para ficar algo legal e resposivo tipo o simbolo da nike quando a mensagem  no zap é enviada
    print("Status:", resposta.get("status")) # retornar o status

def visualizar_mensagens(soc, NOME_CLIENTE):

    # o mesmo pacote pode enviar e receber a mensagem, a forma como será descompactao depende do campo do tipo
    payload = {
        "tipo": "receber",
        "destino": NOME_CLIENTE
    }

    try:
        soc.send(msgpack.packb(payload, use_bin_type=True))
        resposta = soc.recv(4096)
        # deve ser colocado em um try catch em um while pois o dado vem fragmentado, ele depende do tamanho do buffer para receber e o quanto um dado consegue ser serializado por um determinado computador,
        # vimos esse conceito em redes de computadores
        if not resposta:
            print("Nenhuma resposta do servidor.")
            return

        dados = msgpack.unpackb(resposta, raw=False) # desempacotar a mensagem
        mensagens = dados.get("mensagens", [])

        if not mensagens:
            print("Nenhuma mensagem recebida.")
            return

        print("\nMensagens recebidas:\n")
        #logica para verificar as mensagens recebidas de cada pessoa
        for i, msg in enumerate(mensagens, 1):
            origem = msg.get("origem", "desconhecido")
            texto = msg.get("mensagem", "")
            print(f"{i}. {origem} → {texto}")

    except Exception as e:
        
        # fins de depuração
        print(f"Erro ao visualizar mensagens: {e}")

def menu():
    #fiz um menu interativo (ou quase isso) para usarmos em nosso projeto
    while True:
        print("\nMenu:")
        print("1 - Publicar mensagem (em construção)") #alguem precisa implementar essa parte (não serei eu)
        print("2 - Enviar mensagem privada")
        print("3 - Visualizar mensagens privadas cliente 2")
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