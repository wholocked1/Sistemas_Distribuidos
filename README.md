# Sistemas Distribuidos
Antes de executar qualquer um dos códigos, é importante que, no prompt de comando, realize o download das dependências que são usadas por esse projeto:<br>
```
pip install msgpack
pip install zmq
```
## Linguagem: Python, JavaScript e Java<br>
<br>
Ordem para execução do projeto:<br>

IMPORTANTE: Cada parte deste código deve ser realizada em um terminal diferente!

## Broker:
Execulte antes de todos os outros:

```
python broker.py
```
<br>

## Servers:
Suba um servidor (o servidor 3 contempla já todas as integrações com postagens e troca de mensagens):

```
python server3.py
```
<br>

Depois insira a porta desejada (sugerimos fortemente abrir na porta 5555), exemplo:
```
Porta do servidor (ex: 65432): 5555
```
<br>

## Clientes: <br>

### JavaScript
```
node cliente1.js
```
Inserir o nome do cliente
### Java

#### Windows
```
javac -cp ".;msgpack-core-0.9.0.jar" cliente2.java
java -cp ".;msgpack-core-0.9.0.jar" cliente2
```

#### Linux

```
javac -cp ".:msgpack-core-0.9.0.jar" Cliente2.java
java -cp ".:msgpack-core-0.9.0.jar" Cliente2
```
Inserir o nome do cliente <br>
Inserir a porta 6555 para comunicação


Git do Leo: https://gitlab.com/laferreira/fei/cc7261/-/blob/main/aulas/projeto.md
