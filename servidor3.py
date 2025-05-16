import zmq
import time
import msgpack
#servidor recebe o número de rank no terminal ao subir o arquivo
#servidor deve fazer requisição de hora para o servidor coordenador a hora certa
#servidor coordenador, se online, deve enviar o horário dele
#se o servidor coordenador ficar offline, o servidor que fez a requisição verificará os outros servidores para poder realizar a eleição
#se o servidor for o maior dentre eles, ele será eleito o novo coordenador
#fazer docker compose
coordenador = False
ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.setsockopt_string(zmq.SUBSCRIBE, "")
sub.connect("tcp://localhost:5558")
ip = input('IP desse servidor:') #pede o input do número do servidor de forma manual para teste
ctx = zmq.Context()
rep = ctx.socket(zmq.REP)
Ip_Server = "tcp://*:" + ip
rep.bind(Ip_Server)

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5559")

socket.send(ip)
mensagem = socket.recv()
rank = int(mensagem)

if(rank == 1):
    coordenador = True

nome = "servidor" + str(rank) + ".txt" #gera o nome do arquivo de log
arq = open(nome, "w") #abre o arquivo de log
inicio = time.time() #pega o time inical
arq.write(f"Servidor aberto ({time.ctime(inicio)})\n") #coloca que o servidor foi aberto e o horário inicial

while True:
    #tem que fazer o poller para dectar mensagens do PUB


# qnt = 3 #quantidade de servidores abertos
# coordenador = False #inicia o servidor como não coordenador
# rank = 0 #rank de cada servidor será dado pelo terminal ao iniciar
# rank = int(input("Qual o rank desse servidor:")) #recebe o rank dele
# nome = "servidor" + str(rank) + ".txt" #gera o nome do arquivo de log
# arq = open(nome, "w") #abre o arquivo de log
# inicio = time.time() #pega o time inical
# arq.write(f"Servidor aberto ({time.ctime(inicio)})\n") #coloca que o servidor foi aberto e o horário inicial
# if(rank == 1):
#     arq_ip = open("ip", "w") #abre um arquivo que coloca os endereços de IP dos servidores
#     ip = input('IP desse servidor:') #pede o input do número do servidor de forma manual para teste
#     arq_ip.write(ip + " ")#escreve no arquivo no número do IP do servidor
#     arq_ip.close()
# else:
#     arq_ip = open("ip", "a") #abre um arquivo que coloca os endereços de IP dos servidores
#     ip = input('IP desse servidor:') #pede o input do número do servidor de forma manual para teste
#     arq_ip.write(ip + " ")#escreve no arquivo no número do IP do servidor
#     arq_ip.close()
# arq.write(f"O IP desse servidor é: " + ip + f"({ time.ctime(inicio)})\n") #escreve no log qual o IP do servidor
# #abre a conexão do msgpack por Request
# ctx = zmq.Context() 
# client = ctx.socket(zmq.REQ)
# porta = "tcp://localhost:" + ip
# client.connect(porta)
# arq.write("Comunicação via Msgpack aberta (" + f"{time.ctime(inicio)}" + ")\n") #coloca no log que a comunicação foi aberta
# print("ok")
# #envia mensagem para o broker para pedir a hora certa
# # msg = {"mensagem": "quero hora", "timestamp": time.localtime(inicio)}
# # msg_p = msgpack.packb(msg)
# # client.send(msg_p)
# # print('mensagem enviada')
# # #recebe a mensagem de hora certa e mostra no console
# # msg_p = client.recv()
# # msg = msgpack.unpackb(msg_p)
# # print(f'Mensagem recebida: {msg}')
# if(rank == 1):
#     coordenador = True
#     time.sleep(15)
# while True:
#     if(coordenador == False):
#         #sub da hora e pedir por eleições
#         msg = {"mensagem": "quero hora", "timestamp": time.ctime(inicio)}
#         msg_p = msgpack.packb(msg)
#         client.send(msg_p)
#         print('mensagem enviada')
#         arq.write("Pedido de hora realizado (" + f"{time.ctime(inicio)}" + ")")
#         msg_p = client.recv()
#         msg = msgpack.unpackb(msg_p)
#         print(f'Mensagem recebida: {msg}')
        
#         if(msg["mensagem"] == 1):
#             msg = {"mensagem":"eleicao", "timestamp": time.ctime(inicio)}
#             msg_p = msgpack.packb(msg)
#             client.send(msg_p)
#         else:
#             inicio = inicio + msg_p["timestamp"]
#             arq.write(f"Hora atualizada com sucesso ({time.ctime(inicio)})")
#         #eleição
#         # for i in range(rank+1,qnt+1):
#         #     tempo = time.time
#         #     msg = {"mensagem": "eleicao", "timestamp": tempo, "servidor": i}
#         #     arq.write("Requisição de eleição feita em: " + tempo + "para o servidor: " + i + "\n")
#         #     #envia mensagem para broker
#         # #ou
#         # tempo = time.time
#         # msg = {"mensagem": "eleicao", "timestamp": tempo, "servidor": rank}
#         # arq.write("Requisição de eleição feita em: " + tempo)
#         #recebe a mensagem
        
#     else:
#         #pub da hora
#         msg_p = client.recv()
#         msg = msgpack.unpackb(msg_p)
#         print(f'Mensagem recebida: {msg}')
#         arq.write("Pedido de hora recebido (" + time.ctime() + ")")
#         msg = {"mensagem": "hora certa", "timestamp": time.time()}
#         msg_p = msgpack.packb(msg)
#         client.send(msg_p)
#         print('mensagem enviada')
#         arq.write(f"Hora enviada com sucesso ({time.ctime()})")
#     inicio = inicio + rank

