const net = require('net');
const msgpack = require('@msgpack/msgpack');
const readline = require('readline');

const HOST = '127.0.0.1';
const PORT = 65432;
const NOME_CLIENTE = "cliente1"; // Altere se for cliente2

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const client = new net.Socket();

// Log utilitário
function logInfo(msg) {
    console.log(`[INFO] ${msg}`);
}
function logErro(msg) {
    console.error(`[ERRO] ${msg}`);
}

function prompt(texto) {
    return new Promise(resolve => rl.question(texto, resolve));
}

async function publicar_postagem() {
    const conteudo = await prompt("Digite o conteúdo da postagem: ");

    const payload = {
        tipo: "postar",
        origem: NOME_CLIENTE,
        mensagem: conteudo
    };

    const data = msgpack.encode(payload);
    logInfo(`Publicando postagem: "${conteudo}"`);
    client.write(data);

    client.once('data', data => {
        try {
            const resposta = msgpack.decode(data);
            logInfo(`Resposta do servidor: ${JSON.stringify(resposta)}`);
        } catch (e) {
            logErro(`Erro ao decodificar resposta: ${e.message}`);
        }
        menu();
    });
}

function visualizar_postagens() {
    const payload = {
        tipo: "vizualizar",
        origem: NOME_CLIENTE
    };

    logInfo(`Solicitando postagens de: ${NOME_CLIENTE}`);
    client.write(msgpack.encode(payload));

    client.once('data', data => {
        try {
            const resposta = msgpack.decode(data);
            const postagens = resposta.mensagens || [];

            if (postagens.length === 0) {
                logInfo("Nenhuma postagem encontrada.");
            } else {
                console.log("\nPostagens encontradas:\n");
                postagens.forEach((post, i) => {
                    const texto = post.mensagem || "";
                    console.log(` ${i + 1}. ${texto}`);
                });
            }
        } catch (e) {
            logErro(`Erro ao processar postagens: ${e.message}`);
        }
        menu();
    });
}

// Enviar mensagem privada
async function enviar_mensagem_privada() {
    const destino = await prompt("Digite o destinatário (ex: cliente2): ");
    const mensagem = await prompt("Digite sua mensagem: ");

    const payload = {
        tipo: "enviar",
        origem: NOME_CLIENTE,
        destino,
        mensagem
    };

    const data = msgpack.encode(payload);
    logInfo(`Enviando mensagem para ${destino}: "${mensagem}"`);
    client.write(data);

    client.once('data', data => {
        try {
            const resposta = msgpack.decode(data);
            logInfo(`Resposta do servidor: ${JSON.stringify(resposta)}`);
        } catch (e) {
            logErro(`Erro ao decodificar resposta: ${e.message}`);
        }
        menu();
    });
}

// Visualizar mensagens recebidas
function visualizar_mensagens() {
    const payload = {
        tipo: "receber",
        destino: NOME_CLIENTE
    };

    logInfo(`Solicitando mensagens para: ${NOME_CLIENTE}`);
    client.write(msgpack.encode(payload));

    client.once('data', data => {
        try {
            const resposta = msgpack.decode(data);
            const mensagens = resposta.mensagens || [];

            if (mensagens.length === 0) {
                logInfo("Nenhuma mensagem recebida.");
            } else {
                console.log("\nMensagens recebidas:");
                mensagens.forEach((msg, i) => {
                    const origem = msg.origem || "desconhecido";
                    const texto = msg.mensagem || "";
                    console.log(` ${i + 1}. ${origem} → ${texto}`);
                });
            }
        } catch (e) {
            logErro(`Erro ao processar mensagens: ${e.message}`);
        }
        menu();
    });
}

// Menu interativo
async function menu() {
    console.log("\nMenu:");
    console.log("1 - Publicar mensagem");
    console.log("2 - Enviar mensagem privada");
    console.log("3 - Visualizar mensagens privadas");
    console.log("4 - Visualizar postagens públicas");
    console.log("0 - Sair");

    const escolha = await prompt("Escolha uma opção: ");

    switch (escolha.trim()) {
        case "1":
            publicar_postagem();
            break;
        case "2":
            enviar_mensagem_privada();
            break;
        case "3":
            visualizar_mensagens();
            break;

        case "4":
            visualizar_postagens();
            break;
        case "0":
            logInfo("Encerrando cliente.");
            client.end();
            rl.close();
            break;
        default:
            console.log("Opção inválida.");
            menu();
    }
}

// Conectar ao servidor
client.connect(PORT, HOST, () => {
    logInfo(`Conectado ao servidor em ${HOST}:${PORT}`);
    menu();
});

client.on('error', (err) => {
    logErro(`Erro na conexão: ${err.message}`);
    rl.close();
});
