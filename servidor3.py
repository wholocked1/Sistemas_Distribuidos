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
    global log_filename
    timestamp = time.asctime()
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# Load messages from log
def carregar_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    print("⚠️ Arquivo de log estava corrompido. Iniciando com lista vazia.")
                    return []
    return []

# Save message to log
def salvar_em_log(mensagem):
    todas_mensagens = carregar_log()
    todas_mensagens.append(mensagem)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(todas_mensagens, f, ensure_ascii=False, indent=2)

# Handle client connections
def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] {addr} conectado.")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            msg = msgpack.unpackb(data, raw=False)

            if msg["tipo"] == "enviar" or msg["tipo"] == "postar":
                with coord_lock:
                    mensagens.append(msg)
                    salvar_em_log(msg)
                resposta = {"status": "mensagem enviada!"}
                print(f"[DEBUG Python] Enviando: {resposta}")
                print(f"[DEBUG Python] Bytes: {list(msgpack.packb(resposta, use_bin_type=True))}")
                conn.sendall(msgpack.packb(resposta, use_bin_type=True))

            elif msg["tipo"] == "receber":
                with coord_lock:
                    recebidas = [m for m in mensagens if m["destino"] == msg["destino"] and m["origem"] == msg["origem"]]
                resposta = {"mensagens": recebidas}
                conn.sendall(msgpack.packb(resposta, use_bin_type=True))

            elif msg["tipo"] == "vizualizar":
                with coord_lock:
                    postagens = [m for m in mensagens if m["tipo"] == "postar" and m["origem"] == msg["origem"]]
                resposta = {"mensagens": postagens}
                conn.sendall(msgpack.packb(resposta, use_bin_type=True))

        except Exception as e:
            print(f"[ERRO] {e}")
            break
    conn.close()

# TCP socket message server starter in a thread
def start_message_server():
    global mensagens
    mensagens = carregar_log()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT + 1000))  # Porta para clientes
    server.listen()
    print("[SERVIDOR] Iniciado em", (HOST, PORT + 1000))

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

# Dummy implementation to avoid NameError during testing
def mandaHora():
    while True:
        time.sleep(10)

def verificaCoordenador():
    while True:
        time.sleep(10)

def sincCoordenador():
    while True:
        time.sleep(10)

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
