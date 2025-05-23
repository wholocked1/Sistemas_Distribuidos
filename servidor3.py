import socket
import threading
import msgpack
import json
import os
import zmq
import time

# Global variables
mensagens = []  # List to store messages
LOG_PATH = "log_mensagens.json"  # Path for logging messages

# Get the port number from user input
port_input = input('Porta do servidor (ex: 65432): ').strip()
try:
    PORT = int(port_input)
except ValueError:
    print("Porta inválida. Favor informar um número válido.")
    exit(1)

HOST = '127.0.0.1'  # Fixed host for socket server
log_filename = f"servidor_{PORT}_log.txt"  # Log file for the server

# Time synchronization variables
coordenador = False
rankCoordenador = 1
rank = 0
logical_clock = 0
local_clock = time.time()
coord_thread = None
coord_lock = threading.Lock()
serversConhecidos = set()

# Function to log messages
def log(msg):
    timestamp = time.asctime()
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# Load messages from log
def carregar_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save message to log
def salvar_em_log(mensagem):
    todas_mensagens = carregar_log()
    todas_mensagens.append(mensagem)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(todas_mensagens, f, ensure_ascii=False, indent=2)

# Handle client connections (normal socket TCP server part)
def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] {addr} conectado.")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            msg = msgpack.unpackb(data, raw=False)
            # Message processing
            if msg["tipo"] == "enviar" or msg["tipo"] == "postar":
                mensagens.append(msg)
                salvar_em_log(msg)
                conn.send(msgpack.packb({"status": "mensagem enviada!"}, use_bin_type=True))
            elif msg["tipo"] == "receber":
                recebidas = [m for m in mensagens if m["destino"] == msg["destino"] and m["origem"] == msg["origem"]]
                conn.send(msgpack.packb({"mensagens": recebidas}, use_bin_type=True))
            elif msg["tipo"] == "vizualizar":
                postagens = [m for m in mensagens if m["tipo"] == "postar" and m["origem"] == msg["origem"]]
                conn.send(msgpack.packb({"mensagens": postagens}, use_bin_type=True))
        except Exception as e:
            print(f"[ERRO] {e}")
            break
    conn.close()

# TCP socket message server starter in a thread
def start_message_server():
    global mensagens
    mensagens = carregar_log()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, 5560))
    server.listen()
    print("[SERVIDOR] Iniciado em", (HOST, 5560))

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

# Time synchronization functions
def sincCoordenador():
    global local_clock, logical_clock, coordenador, coord_thread
    log("Iniciando sincronização do coordenador")
    while True:
        time.sleep(10)
        with coord_lock:
            if not coordenador:
                log("Saindo da sincronização porque servidor não é mais coordenador")
                break
        if not serversConhecidos:
            log("Nenhum servidor conhecido para sincronizar")
            continue
        log(f"Coordenador sincronizando com servers: {serversConhecidos}")
        times = []
        for server_port in serversConhecidos:
            try:
                if int(server_port) == PORT:
                    times.append(local_clock)
                    continue
                req_socket = context.socket(zmq.REQ)
                req_socket.setsockopt(zmq.LINGER, 0)
                req_socket.connect(f"tcp://localhost:{server_port}")
                req_socket.send_string("TIME_REQUEST")
                if req_socket.poll(2000) & zmq.POLLIN:
                    reply = req_socket.recv_string()
                    server_time = float(reply)
                    log(f"Horário recebido {server_time} do servidor {server_port}")
                    times.append(server_time)
                else:
                    log(f"Sem resposta do server {server_port} por time out")
                req_socket.close()
            except Exception as e:
                log(f"Erro no request {server_port}: {e}")

        average_time = sum(times) / len(times) if times else local_clock
        log(f"Tempo estimado calculado: {average_time}")

        for server_port in serversConhecidos:
            try:
                if int(server_port) == PORT:
                    diff = average_time - local_clock
                    local_clock += diff
                    log(f"Tempo interno ajustado {diff}, agora {local_clock}")
                    continue
                req_socket = context.socket(zmq.REQ)
                req_socket.setsockopt(zmq.LINGER, 0)
                req_socket.connect(f"tcp://localhost:{server_port}")
                req_socket.send_string(f"ADJUST_TIME {average_time}")
                if req_socket.poll(2000) & zmq.POLLIN:
                    ack = req_socket.recv_string()
                    log(f"Ajustando {server_port}: {ack}")
                else:
                    log(f"Sem ACK em {server_port} após ADJUST_TIME")
                req_socket.close()
            except Exception as e:
                log(f"Erro ao ajustar {server_port}: {e}")

        logical_clock += 1
        log(f"Incremento do relógio lógico {logical_clock}")

def eleicao():
    global coordenador, rankCoordenador, rank, coord_thread
    log("Eleição iniciada. Encontrando novo coordenador")
    antigoCoordenadorRank = rankCoordenador
    candidates = [int(s) for s in serversConhecidos if s.isdigit() and int(s) != antigoCoordenadorRank]
    log(f"Candidatos a eleição: {candidates}")
    if not candidates:
        log("Sem candidatos para eleição")
        return
    novoCoordenadorRank = min(candidates)
    log(f"Resultado da eleição: Menor Rank = {novoCoordenadorRank}")

    with coord_lock:
        eraCoordenador = coordenador
        rankCoordenador = novoCoordenadorRank
        coordenador = (rank == rankCoordenador)

        if coordenador and not eraCoordenador:
            log("Sou o novo coordenador! Iniciando funções de coordenador...")
            if coord_thread is None or not coord_thread.is_alive():
                coord_thread = threading.Thread(target=sincCoordenador, daemon=True)
                coord_thread.start()
        elif not coordenador and eraCoordenador:
            log("Não sou mais coordenador, parando funções de coordenador.")
        else:
            log(f"Coordenador atual é rank {rankCoordenador}")

def verificaCoordenador():
    global coordenador, rankCoordenador, rank
    while True:
        time.sleep(5)
        with coord_lock:
            coordenadorAtual = rankCoordenador
        if coordenadorAtual == rank:
            continue
        if coordenadorAtual not in (int(s) for s in serversConhecidos if s.isdigit()):
            log(f"Coordenador rank {coordenadorAtual} fora da lista. Iniciando eleição.")
            eleicao()
            continue

        coord_str = str(coordenadorAtual)
        try:
            ping_socket = context.socket(zmq.REQ)
            ping_socket.setsockopt(zmq.LINGER, 0)
            ping_socket.connect(f"tcp://localhost:{coord_str}")
            ping_socket.send_string("TIME_REQUEST")
            if ping_socket.poll(2000) & zmq.POLLIN:
                _ = ping_socket.recv_string()
                log(f"Coordenador (rank {coordenadorAtual}) está vivo.")
            else:
                log(f"Coordenador (rank {coordenadorAtual}) não responde. Iniciando eleição.")
                eleicao()
            ping_socket.close()
        except Exception as e:
            log(f"Erro ao dar ping no coordenador (rank {coordenadorAtual}): {e}")
            eleicao()

def mandaHora():
    global local_clock
    while True:
        try:
            message = rep.recv_string()
            log(f"Mensagem recebida: {message}")
            if message == "TIME_REQUEST":
                rep.send_string(str(local_clock))
                log(f"Enviando tempo local {local_clock}")
            elif message.startswith("ADJUST_TIME"):
                parts = message.split()
                if len(parts) == 2:
                    try:
                        avg_time = float(parts[1])
                        diff = avg_time - local_clock
                        local_clock += diff
                        rep.send_string("ACK")
                        log(f"Relógio ajustado em {diff}, novo valor: {local_clock}")
                    except ValueError:
                        rep.send_string("ERR_INVALID_TIME")
                        log("Erro no valor para ajuste de tempo")
                else:
                    rep.send_string("ERR_INVALID_COMMAND")
                    log("Comando ADJUST_TIME inválido")
            else:
                rep.send_string("ERR_UNKNOWN_COMMAND")
                log(f"Comando desconhecido: {message}")
        except zmq.ZMQError:
            break

# Initialize ZeroMQ context and sockets
context = zmq.Context()
rep = context.socket(zmq.REP)
rep.bind(f"tcp://*:{PORT}")
log(f"REP socket em tcp://*:{PORT}")

# Request to get rank
broker_req = context.socket(zmq.REQ)
broker_req.connect("tcp://localhost:5559")
log("Conectado no broker REQ em tcp://localhost:5559")
broker_req.send_string(str(PORT))
rank_str = broker_req.recv_string()
try:
    rank = int(rank_str)
except ValueError:
    log(f"Rank inválido recebido do broker: {rank_str}")
    rank = 0

coordenador = (rank == rankCoordenador)
log(f"Rank recebido: {rank}, Coordenador: {coordenador}")

# Subscribe to receive known servers
sub = context.socket(zmq.SUB)
sub.setsockopt_string(zmq.SUBSCRIBE, "")
sub.connect("tcp://localhost:5558")
log("Conectando no PUB do Broker em tcp://localhost:5558")

poller = zmq.Poller()
poller.register(rep, zmq.POLLIN)
poller.register(sub, zmq.POLLIN)

# Start threads for time synchronization and election
threading.Thread(target=mandaHora, daemon=True).start()
threading.Thread(target=verificaCoordenador, daemon=True).start()

if coordenador:
    coord_thread = threading.Thread(target=sincCoordenador, daemon=True)
    coord_thread.start()
else:
    coord_thread = None

# Start the TCP socket message server in a separate thread to avoid blocking
message_server_thread = threading.Thread(target=start_message_server, daemon=True)
message_server_thread.start()

# Main loop for handling subscriptions and logging status
try:
    while True:
        socks = dict(poller.poll(timeout=1000))
        if sub in socks and socks[sub] == zmq.POLLIN:
            try:
                msg = sub.recv_string()
                known_list = eval(msg)
                serversConhecidos.clear()
                serversConhecidos.update(str(s) for s in known_list)
                log(f"Lista recebida: {serversConhecidos}")
            except Exception as e:
                log(f"Erro ao ler lista: {e}")

        logical_clock += 1
        log(f"Status - Local: {local_clock:.3f}, Lógico: {logical_clock}, Coordenador rank: {rankCoordenador}, É coordenador: {coordenador}, Servers conhecidos: {serversConhecidos}")

except KeyboardInterrupt:
    print("Servidor finalizado manualmente.")


