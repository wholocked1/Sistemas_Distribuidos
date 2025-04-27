import zmq
import msgpack
import time

# precisa verificar a mensagem:
# pegar todas os pedidos de tempo e passar para o servidor Coordenador
# pegar a hora do Coordenador e passar para os outros servidores
# pegar todos os pedidos de eleição e passar para os ranks acima dele
# pegar as respostas dos outros ranks para que seja enviada a resposta
# salvar:
# dicionário com rank (chave) e IP
# rank do Coordenador
# tamanho de servidores

#arquivo de log do broker
lista_ip = {}
qtde = 3
nome = "broker.txt"
arq = open(nome, "w")
arq.write("Broker ativado com sucesso (" + time.asctime() + ")\n")
#leitura do arquivo de IP dos servidores
ip = open("ip", "r")
ips = ip.readline()
print(ips)
ip.close()
separado = ips.split(" ")
#conexão com o servidor por msgpack usando REP
ctx = zmq.Context() 
client = ctx.socket(zmq.REP)
porta = "tcp://*:" + separado[0]
client.bind(porta)
lista_ip["1"] = separado[0]
arq.write(f"Conexão com server 1 na porta {separado[0]} realizada por msgpack (" + time.asctime()+")\n") #escreve no log que a conexão ocorreu
ctx1 = zmq.Context() 
client1 = ctx1.socket(zmq.REP)
porta1 = "tcp://*:" + separado[1]
client.bind(porta1)
lista_ip["2"] = separado[1]
arq.write(f"Conexão com server 2 na porta {separado[1]} realizada por msgpack (" + time.asctime()+")\n") #escreve no log que a conexão ocorreu
ctx2 = zmq.Context() 
client2 = ctx2.socket(zmq.REP)
porta2 = "tcp://*:" + separado[2]
client.bind(porta2)
lista_ip["3"] = separado[2]
arq.write(f"Conexão com server 3 na porta {separado[2]} realizada por msgpack (" + time.asctime()+")\n") #escreve no log que a conexão ocorreu
#recebe uma mensagem de pedido de hora do servidor
print(lista_ip)
msg_p = client.recv()
msg = msgpack.unpackb(msg_p)
print(f'Mensagem recebida: {msg}')
#manda a mensagem para o servidor para colocar a hora certa
ans = {"hora_atual": time.asctime(), "mensagem":"hora certa"}
ans_p = msgpack.packb(ans)
client.send(ans_p)
print('mensagem enviada')