import zmq
import time

# Initialize the Log
log_filename = "broker_log.txt"

def log(msg):
    timestamp = time.asctime()
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(log_filename, "a") as f:
        f.write(line + "\n")

log("Broker iniciado")

ctx = zmq.Context()

# PUB para enviar as informações de IP
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5558")
log("PUB socket em tcp://*:5558")

# REP para mandar o rank
rep = ctx.socket(zmq.REP)
rep.bind("tcp://*:5559")
log("REP socket em tcp://*:5559")

connected_servers = []  # Lista de portas dos servidores
rank_map = {}  # Rank dos servidores

current_rank = 1

poller = zmq.Poller()
poller.register(rep, zmq.POLLIN)

while True:
    socks = dict(poller.poll(timeout=1000))
    if rep in socks and socks[rep] == zmq.POLLIN:
        message = rep.recv_string()
        log(f"Pedido de conexão: {message}")

        # Novo rank para o coordenador
        if message not in rank_map:
            rank_map[message] = current_rank
            connected_servers.append(message)
            log(f"Rank {current_rank} para o Server {message}")
            current_rank += 1
        else:
            log(f"Server {message} reconectado com o rank {rank_map[message]}")

        # Envia o rank para o servidor
        rep.send_string(str(rank_map[message]))

        # Publica a lista de servidor
        server_list_str = str(connected_servers)
        pub.send_string(server_list_str)
        log(f"Server list publicado: {server_list_str}")
