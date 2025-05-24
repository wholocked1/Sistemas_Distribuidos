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
Coloque em três terminais diferentes:

```
python server3.py
```
<br>

Depois insira a porta desejada, exemplo:
```
Porta do servidor (ex: 65432): 5555
```
<br>

## Clientes: <br>

### Python

```
python cliente.py
```
Depois insira o nome do cliente, exemplo:
```
nome do cliente: cliente1
```
### JavaScript
```
node cliente1.js
```
Não precisa incerir um nome!
### Java
```
javac -cp ".;msgpack-core-0.9.0.jar" cliente2.java
java -cp ".;msgpack-core-0.9.0.jar" Cliente2
```
Não precisa incerir um nome!


Git do Leo: https://gitlab.com/laferreira/fei/cc7261/-/blob/main/aulas/projeto.md
