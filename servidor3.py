import zmq
import time
import threading

def main():
    ip = input('Porta do servidor: ').strip()
    log_filename = f"servidor_{ip}_log.txt"

    def log(msg):
        timestamp = time.asctime()
        line = f"[{timestamp}] {msg}"
        print(line)
        with open(log_filename, "a") as f:
            f.write(line + "\n")

    log("Ativando o server ...")
    context = zmq.Context()

    # REP para pedir hora
    rep = context.socket(zmq.REP)
    rep.bind(f"tcp://*:{ip}")
    log(f"REP socket em tcp://*:{ip}")

    # Request para pedir o Rank
    broker_req = context.socket(zmq.REQ)
    broker_req.connect("tcp://localhost:5559")
    log("Conectado no broker REQ em tcp://localhost:5559")

    broker_req.send_string(ip)
    rank_str = broker_req.recv_string()
    rank = int(rank_str)

    coordinator_rank = 1

    coordenador = (rank == coordinator_rank)
    log(f"Rank recebido: {rank}, Coordenador: {coordenador}")

    # Sub para receber os servers abertos
    sub = context.socket(zmq.SUB)
    sub.setsockopt_string(zmq.SUBSCRIBE, "")
    sub.connect("tcp://localhost:5558")
    log("Conectando no PUB do Broker em tcp://localhost:5558")

    logical_clock = 0
    local_clock = time.time()

    known_servers = set()

    poller = zmq.Poller()
    poller.register(rep, zmq.POLLIN)
    poller.register(sub, zmq.POLLIN)

    # Thread para o coordenador
    coord_lock = threading.Lock()

    # Sincronização do coordenador
    def coordinator_sync():
        nonlocal local_clock, logical_clock, coordenador
        while True:
            time.sleep(10)
            with coord_lock:
                if not coordenador:
                    # Se o coordenador não existir mais
                    log("Não tem mais coordenador.")
                    break

            if not known_servers:
                log("Server desconhecido")
                continue

            log(f"Coordenador sincronizando com servers: {known_servers}")

            times = []
            for server_port in known_servers:
                try:
                    if server_port == ip:
                        times.append(local_clock)
                        continue
                    req_socket = context.socket(zmq.REQ)
                    req_socket.setsockopt(zmq.LINGER, 0)
                    req_socket.connect(f"tcp://localhost:{server_port}")
                    req_socket.send_string("TIME_REQUEST")
                    if req_socket.poll(2000) & zmq.POLLIN:  # tempo de timeout
                        reply = req_socket.recv_string()
                        server_time = float(reply)
                        log(f"Horário recebido {server_time} do servidor {server_port}")
                        times.append(server_time)
                    else:
                        log(f"Sem resposta do server {server_port} por causa de time out")
                    req_socket.close()
                except Exception as e:
                    log(f"Erro no request {server_port}: {e}")

            if times:
                average_time = sum(times) / len(times)
            else:
                average_time = local_clock

            log(f"Tempo estimado calculado: {average_time}")

            for server_port in known_servers:
                try:
                    if server_port == ip:
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
                        log(f"Sem ACK em {server_port} depois ADJUST_TIME")
                    req_socket.close()
                except Exception as e:
                    log(f"Erro na hora de realizar {server_port}: {e}")

            logical_clock += 1
            log(f"Incremento do relógio lógico {logical_clock}")

    # Eleição
    def election():
        nonlocal coordenador, coordinator_rank, rank
        log("Eleição iniciada. Encontrando novo coordenador")
        candidates = [int(s) for s in known_servers if s.isdigit()]
        print(candidates)
        if not candidates:
            log("Sem candidatos a eleição")
            return
        new_coord_rank = min(candidates)
        log(f"Resultado das eleições: Menor Rank = {new_coord_rank}")
        with coord_lock:
            old_coord = coordinator_rank
            coordinator_rank = new_coord_rank
            coordenador = (rank == coordinator_rank)
            if coordenador and (old_coord != coordinator_rank):
                log("Eu sou o novo servidor coordenador")
                # Start coordinator thread if not running
                threading.Thread(target=coordinator_sync, daemon=True).start()
            elif not coordenador and (old_coord == rank):
                log("Não é mais coordenador pelo rank mais baixo.")
            else:
                log(f"Coordenador agora é o rank =  {coordinator_rank}")

    # Verificação de vida do coordenador
    def coordinator_health_check():
        while True:
            time.sleep(5)  # checa acada 5 segundos
            with coord_lock:
                current_coord = coordinator_rank
            if current_coord == rank:
                # Se sou coordenador, não preciso verificar
                continue
            if current_coord not in (int(s) for s in known_servers if s.isdigit()):
                log(f"Coordenador de rank {current_coord} não está respondendo; iniciando eleições")
                election()
                continue

            # Ping para verificação de vida do coordenador
            coord_str = str(current_coord)
            try:
                ping_socket = context.socket(zmq.REQ)
                ping_socket.setsockopt(zmq.LINGER, 0)
                ping_socket.connect(f"tcp://localhost:{coord_str}")
                ping_socket.send_string("TIME_REQUEST")
                if ping_socket.poll(2000) & zmq.POLLIN:
                    _ = ping_socket.recv_string()
                    log(f"Coordenador (rank {current_coord}) está vivo.")
                else:
                    log(f"Coordenador (rank {current_coord}) não está respondendo; iniciando eleições.")
                    election()
                ping_socket.close()
            except Exception as e:
                log(f"Erro na hora de dar ping no coordenador (rank {current_coord}): {e}")
                election()

    # REP para realizar qualquer tipo de pedido
    def rep_listener():
        nonlocal local_clock
        while True:
            try:
                message = rep.recv_string()
                log(f"Mensagem recevida: {message}")
                if message == "TIME_REQUEST":
                    rep.send_string(str(local_clock))
                    log(f"Local time enviado {local_clock}")
                elif message.startswith("ADJUST_TIME"):
                    parts = message.split()
                    if len(parts) == 2:
                        try:
                            avg_time = float(parts[1])
                            diff = avg_time - local_clock
                            local_clock += diff
                            rep.send_string("ACK")
                            log(f"Relógio ajustado para {diff}, Novo relógio local: {local_clock}")
                        except ValueError:
                            rep.send_string("ERR_INVALID_TIME")
                            log("Erro na hora de ajustar a hora")
                    else:
                        rep.send_string("ERR_INVALID_COMMAND")
                        log("Erro")
                else:
                    rep.send_string("ERR_UNKNOWN_COMMAND")
                    log(f"Mensagem desconhecida: {message}")
            except zmq.ZMQError:
                break

    # Começa as threads
    threading.Thread(target=rep_listener, daemon=True).start()
    threading.Thread(target=coordinator_health_check, daemon=True).start()

    # Loop principal
    while True:
        poller = zmq.Poller()
        poller.register(sub, zmq.POLLIN)
        # Update do PUB
        socks = dict(poller.poll(timeout=1000))
        if sub in socks and socks[sub] == zmq.POLLIN:
            try:
                msg = sub.recv_string()
                known_list = eval(msg)
                known_servers.clear()
                known_servers.update(str(s) for s in known_list)
                log(f"Lista recebida: {known_servers}")
            except Exception as e:
                log(f"Erro na hora de ler a lista: {e}")

        logical_clock += 1
        log(f"Status - Local: {local_clock:.3f}, Logical: {logical_clock}, Rank Coordenador: {coordinator_rank}, É Coordenador: {coordenador}, Server conhecidos: {known_servers}")

if __name__ == "__main__":
    main()
