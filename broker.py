import zmq
import time

#arquivo de log do broker
lista_ip = []
qtde = 3
rank = 0
nome = "broker.txt"
arq = open(nome, "w")
arq.write("Broker ativado com sucesso (" + time.asctime() + ")\n")

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5559")

ctx = zmq.Context()
rep = ctx.socket(zmq.REP)
rep.bind("tcp://*:5558")

while True:
    messege = rep.recv()
    arq.write(f"Mensagem recebido do servidor de porta: {messege}, rank enviado: {rank}, horário: {time.asctime()}")
    lista_ip.append(messege)
    rep.send(rank)
    pub.send_string(lista_ip)
    rank += 1

