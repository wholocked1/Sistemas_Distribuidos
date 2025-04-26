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

nome = "broker.txt"
arq = open(nome, "w")
arq.write("Broker ativado com sucesso (" + time.asctime() + ")\n")