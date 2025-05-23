import java.io.*;
import java.net.*;
import java.util.*;
import org.msgpack.core.MessagePack;
import org.msgpack.core.MessageUnpacker;

public class Client {
    private static final String NOME_CLIENTE = "cliente2"; 
    private static Socket socket;

    public static void main(String[] args) {
        String HOST = "127.0.0.1";
        int PORT = 65432;

        try {
            socket = new Socket(HOST, PORT);
            menu();
        } catch (IOException e) {
            System.err.println("Error connecting to server: " + e.getMessage());
        } finally {
            try {
                if (socket != null) {
                    socket.close();
                }
            } catch (IOException e) {
                System.err.println("Error closing socket: " + e.getMessage());
            }
        }
    }

    private static void menu() {
        Scanner scanner = new Scanner(System.in);
        while (true) {
            System.out.println("\nMenu:");
            System.out.println("1 - Publicar mensagem");
            System.out.println("2 - Ver mensagens publicadas");
            System.out.println("3 - Enviar mensagem privada");
            System.out.println("4 - Visualizar mensagens privadas");
            System.out.println("0 - Sair");

            System.out.print("Escolha uma opção: ");
            String escolha = scanner.nextLine();

            switch (escolha) {
                case "1":
                    publicarMensagem(scanner);
                    break;
                case "2":
                    vizualizarPostagens(scanner);
                    break;
                case "3":
                    enviarMensagemPrivada(scanner);
                    break;
                case "4":
                    visualizarMensagens(scanner);
                    break;
                case "0":
                    return;
                default:
                    System.out.println("Opção inválida.");
            }
        }
    }

    private static void publicarMensagem(Scanner scanner) {
        System.out.print("Digite sua postagem: ");
        String postagem = scanner.nextLine();

        Map<String, Object> payload = new HashMap<>();
        payload.put("tipo", "postar");
        payload.put("origem", NOME_CLIENTE);
        payload.put("destino", "");
        payload.put("mensagem", postagem);

        try {
            sendMessage(payload);
            Map<String, Object> resposta = receiveMessage();
            System.out.println("Status: " + resposta.get("status"));
        } catch (IOException e) {
            System.err.println("Erro ao publicar mensagem: " + e.getMessage());
        }
    }

    private static void vizualizarPostagens(Scanner scanner) {
        System.out.print("Digite com quem deseja vizualizar as postagens (ex: cliente1): ");
        String origem = scanner.nextLine();

        Map<String, Object> payload = new HashMap<>();
        payload.put("tipo", "vizualizar");
        payload.put("origem", origem);

        try {
            sendMessage(payload);
            Map<String, Object> dados = receiveMessage();
            List<Map<String, Object>> mensagens = (List<Map<String, Object>>) dados.get("mensagens");

            if (mensagens == null || mensagens.isEmpty()) {
                System.out.println("Nenhuma mensagem recebida.");
                return;
            }

            System.out.println("\nMensagens recebidas:\n");
            for (int i = 0; i < mensagens.size(); i++) {
                Map<String, Object> msg = mensagens.get(i);
                String msgOrigem = (String) msg.getOrDefault("origem", "desconhecido");
                String texto = (String) msg.getOrDefault("mensagem", "");
                System.out.printf("%d. %s → %s%n", i + 1, msgOrigem, texto);
            }
        } catch (IOException e) {
            System.err.println("Erro ao visualizar mensagens: " + e.getMessage());
        }
    }

    private static void enviarMensagemPrivada(Scanner scanner) {
        System.out.print("Digite o destinatário (ex: cliente2): ");
        String destino = scanner.nextLine();
        System.out.print("Digite sua mensagem: ");
        String mensagem = scanner.nextLine();

        Map<String, Object> payload = new HashMap<>();
        payload.put("tipo", "enviar");
        payload.put("origem", NOME_CLIENTE);
        payload.put("destino", destino);
        payload.put("mensagem", mensagem);

        try {
            sendMessage(payload);
            Map<String, Object> resposta = receiveMessage();
            System.out.println("Status: " + resposta.get("status"));
        } catch (IOException e) {
            System.err.println("Erro ao enviar mensagem privada: " + e.getMessage());
        }
    }

    private static void visualizarMensagens(Scanner scanner) {
        System.out.print("Digite com quem deseja vizualizar a conversa (ex: cliente2): ");
        String origem = scanner.nextLine();

        Map<String, Object> payload = new HashMap<>();
        payload.put("tipo", "receber");
        payload.put("origem", origem);
        payload.put("destino", NOME_CLIENTE);

        try {
            sendMessage(payload);
            Map<String, Object> dados = receiveMessage();
            List<Map<String, Object>> mensagens = (List<Map<String, Object>>) dados.get("mensagens");

            if (mensagens == null || mensagens.isEmpty()) {
                System.out.println("Nenhuma mensagem recebida.");
                return;
            }

            System.out.println("\nMensagens recebidas:\n");
            for (int i = 0; i < mensagens.size(); i++) {
                Map<String, Object> msg = mensagens.get(i);
                String msgOrigem = (String) msg.getOrDefault("origem", "desconhecido");
                String texto = (String) msg.getOrDefault("mensagem", "");
                System.out.printf("%d. %s → %s%n", i + 1, msgOrigem, texto);
            }
        } catch (IOException e) {
            System.err.println("Erro ao visualizar mensagens: " + e.getMessage());
        }
    }

    private static void sendMessage(Map<String, Object> payload) throws IOException {
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        MessagePack.newDefaultPacker(byteArrayOutputStream).packMapHeader(payload.size());
        for (Map.Entry<String, Object> entry : payload.entrySet()) {
            MessagePack.newDefaultPacker(byteArrayOutputStream).packString(entry.getKey());
            MessagePack.newDefaultPacker(byteArrayOutputStream).packString(entry.getValue().toString());
        }
        socket.getOutputStream().write(byteArrayOutputStream.toByteArray());
        socket.getOutputStream().flush();
    }

    private static Map<String, Object> receiveMessage() throws IOException {
        InputStream inputStream = socket.getInputStream();
        byte[] buffer = new byte[4096];
        int bytesRead = inputStream.read(buffer);
        if (bytesRead == -1) {
            throw new IOException("Nenhuma resposta do servidor.");
        }

        MessageUnpacker unpacker = MessagePack.newDefaultUnpacker(buffer, 0, bytesRead);
        Map<String, Object> response = new HashMap<>();
        int mapSize = unpacker.unpackMapHeader();
        for (int i = 0; i < mapSize; i++) {
            String key = unpacker.unpackString();
            String value = unpacker.unpackString();
            response.put(key, value);
        }
        return response;
    }
}
