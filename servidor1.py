import zmq
import time
import msgpack

#servidor recebe o número de rank no terminal ao subir o arquivo
#servidor deve fazer requisição de hora para o servidor coordenador a hora certa
#servidor coordenador, se online, deve enviar o horário dele
#se o servidor coordenador ficar offline, o servidor que fez a requisição verificará os outros servidores para poder realizar a eleição
#se o servidor for o maior dentre eles, ele será eleito o novo coordenador
#fazer docker compose

# qnt = 3 #quantidade de servidores abertos
# coordenador = False #inicia o servidor como não coordenador
# rank = 0 #rank de cada servidor será dado pelo terminal ao iniciar
# rank = int(input("Qual o rank desse servidor:")) #recebe o rank dele
# nome = "servidor" + rank + ".txt" #gera o nome do arquivo de log
# arq = open(nome, "w") #abre o arquivo de log
# inicio = time.time #pega o time inical
# arq.write("Servidor aberto " + inicio + "\n") #coloca que o servidor foi aberto e o horário inicial

# while True:
#     if(coordenador == False):
#         #sub da hora e pedir por eleições
#         #eleição
#         for i in range(rank+1,qnt+1):
#             tempo = time.time
#             msg = {"mensagem": "eleicao", "timestamp": tempo, "servidor": i}
#             arq.write("Requisição de eleição feita em: " + tempo + "para o servidor: " + i + "\n")
#             #envia mensagem para broker
#         #ou
#         tempo = time.time
#         msg = {"mensagem": "eleicao", "timestamp": tempo, "servidor": rank}
#         arq.write("Requisição de eleição feita em: " + tempo)
#         #recebe a mensagem
#     else:
#         #pub da hora
print("ola")