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
nome = "broker.txt"
arq = open(nome, "w")
arq.write("Broker ativado com sucesso (" + time.asctime() + ")\n")
#leitura do arquivo de IP dos servidores
ip = open("ip", "r")
ips = ip.readline()
print(ips)
ip.close()
#conexão com o servidor por msgpack usando REP
ctx = zmq.Context() 
client = ctx.socket(zmq.REP)
porta = "tcp://*:" + ips
client.bind(porta)
arq.write("Conexão com server 1 realizada por msgpack (" + time.asctime()+")\n") #escreve no log que a conexão ocorreu
#recebe uma mensagem de pedido de hora do servidor
msg_p = client.recv()
msg = msgpack.unpackb(msg_p)
print(f'Mensagem recebida: {msg}')
#manda a mensagem para o servidor para colocar a hora certa
ans = {"hora_atual": time.asctime(), "mensagem":"hora certa"}
ans_p = msgpack.packb(ans)
client.send(ans_p)
print('mensagem enviada')