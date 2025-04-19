import socket
import threading
import msgpack



print("1 - Publicar mensagem (visível para todos)")
print("2 - Enviar mensagem privada")
print("Exit - Sair\n")
username = "Pedro"

while True:
    op = input("O que deseja fazer (1/2/exit)? ").strip()
    
    if op == "exit":
       print("Cliente Desligado.")
       break
    elif op == "1":
        msg = input("Digite a mensagem pública: ")
        # Cada publicação deve ser associada ao usuário que a postou e registrada com um timestamp
        pacote = {
            "from": username,
            "to": "ALL",
            "message": msg
        }

    elif op == "2":
        destino = input("Para quem deseja enviar? ")
        msg = input("Digite a mensagem: ")
        pacote = {
            "from": username,
            "to": destino,
            "message": msg
            }
        
        host = 'localhost'
        port = 5555 # troca de mensagens será feita na porta 5555
        #As mensagens devem ser entregues de forma confiável e ordenada

        #usaremos o servidor2 para trocar mensagem entre as pessoas por TCP/IP
        try:
            # Cria socket TCP/IP
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock2.connect((host, port))  # Tenta conexão com o servidor de mensagens

            # Envia nome do usuário (opcional, se o servidor espera)
            sock2.send(msgpack.packb(username, use_bin_type=True))

            # Envia a mensagem empacotada
            sock2.send(msgpack.packb(pacote, use_bin_type=True))

            print("Mensagem enviada com sucesso!")

            sock2.close()

        except ConnectionRefusedError:
            print("Não foi possível conectar ao servidor de mensagens (porta 5555).")
        except Exception as e:
            print(f"Erro inesperado: {e}")






    elif op == "Sair": #fazer tratamento de string para aceitação de lowercase, fiquei com preguiça
        print("Cliente Desligado.")
        break
    else:
        print("Opção inválida. Use 1, 2 ou exit.")
