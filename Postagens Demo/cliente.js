const net = require('net');
const msgpack = require('@msgpack/msgpack');
const readline = require('readline');

const HOST = '127.0.0.1';
const PORT = 65432;
const NOME_CLIENTE = "cliente1"; // Altere para "cliente2" em outro script

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const client = new net.Socket();

// Função auxiliar para ler entrada do usuário como Promise
function prompt(texto) {
    return new Promise(resolve => rl.question(texto, resolve));
}

async function publicarMensagem() {
    const postagem = await prompt("Digite sua mensagem: ");
        const payload = {
            tipo: "postar",
            origem: NOME_CLIENTE,
            destino: "",
            mensagem: postagem
        };

        client.write(msgpack.encode(payload), (err) => {
            if (err) {
                console.error("Erro ao enviar mensagem:", err);
                return;
            }

            client.once('data', (data) => {
                const resposta = msgpack.decode(data);
                console.log("Status:", resposta.status);
                menu();
            });
        });
    }


async function vizualizarPostagens() {
    const origem = await prompt("Digite o destinatário (ex: cliente2): ");

        const payload = {
            tipo: "vizualizar",
            origem: origem
        };

        client.write(msgpack.encode(payload), (err) => {
            if (err) {
                console.error("Erro ao enviar mensagem:", err);
                return;
            }

            client.once('data', (data) => {
                const resposta = msgpack.decode(data);
                const mensagens = resposta.mensagens || [];

            if (mensagens.length === 0) {
                console.log("Nenhuma mensagem recebida.");
                menu();
                return;
            }
            console.log("\nMensagens recebidas:\n");
            mensagens.forEach((msg, index) => {
                const msgOrigem = msg.origem || "desconhecido";
                const texto = msg.mensagem || "";
                console.log(`${index + 1}. ${msgOrigem} → ${texto}`);
            });

            menu();
        });
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

    client.write(msgpack.encode(payload));

    client.once('data', data => {
        const resposta = msgpack.decode(data);
        console.log("Status:", resposta.status);
        menu(); // volta pro menu
    });
}

// Visualizar mensagens recebidas
function visualizar_mensagens() {
    const payload = {
        tipo: "receber",
        destino: NOME_CLIENTE
    };

    client.write(msgpack.encode(payload));

    client.once('data', data => {
        try {
            const resposta = msgpack.decode(data);
            const mensagens = resposta.mensagens || [];

            if (mensagens.length === 0) {
                console.log("Nenhuma mensagem recebida.");
            } else {
                console.log("\nMensagens recebidas:\n");
                mensagens.forEach((msg, i) => {
                    const origem = msg.origem || "desconhecido";
                    const texto = msg.mensagem || "";
                    console.log(`${i + 1}. ${origem} → ${texto}`);
                });
            }
        } catch (err) {
            console.log("Erro ao visualizar mensagens:", err.message);
        }
        menu(); // volta pro menu
    });
}

// Menu interativo
async function menu() {
    console.log("\nMenu:");
    console.log("1 - Publicar mensagem (em construção)");
    console.log("2 - Enviar mensagem privada");
    console.log("3 - Visualizar mensagens privadas cliente 2");
    console.log("0 - Sair");

    const escolha = await prompt("Escolha uma opção: ");

    switch (escolha.trim()) {
        case '1':
            publicarMensagem();
            break;
        case '2':
            vizualizarPostagens();
            break;
        case "3":
            enviar_mensagem_privada();
            break;
        case "4":
            visualizar_mensagens();
            break;
        case "0":
            console.log("Encerrando...");
            client.end();
            rl.close();
            break;
        default:
            console.log("Opção inválida.");
            menu();
    }
}

// Conectar ao servidor e iniciar menu
client.connect(PORT, HOST, () => {
    console.log("Conectado ao servidor.");
    menu();
});
