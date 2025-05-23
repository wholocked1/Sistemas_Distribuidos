import java.io.*;
import java.net.*;
import java.util.*;
import org.msgpack.core.MessagePack;
import org.msgpack.core.MessagePacker;
import org.msgpack.core.MessageUnpacker;

public class cliente2 {
    private static final String NOME_CLIENTE = "clienteJava"; 
    private static Socket socket;

    public static void main(String[] args) {
        String HOST = "127.0.0.1";
        int PORT = 5560;

        try {
            socket = new Socket(HOST, PORT);
            menu();
        } catch (IOException e) {
            System.err.println("Error connecting to server: " + e.getMessage());
        } finally {
            try {
                if (socket != null && !socket.isClosed()) {
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
                    visualizarPostagens(scanner);
                    break;
                case "3":
                    enviarMensagemPrivada(scanner);
                    break;
                case "4":
                    visualizarMensagens(scanner);
                    break;
                case "0":
                    System.out.println("Encerrando... Adeus!");
                    return;
                default:
                    System.out.println("Opção inválida.");
                    break;
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

    private static void visualizarPostagens(Scanner scanner) {
        System.out.print("Digite com quem deseja visualizar as postagens (ex: cliente1): ");
        String origem = scanner.nextLine();

        Map<String, Object> payload = new HashMap<>();
        payload.put("tipo", "vizualizar");
        payload.put("origem", origem);

        try {
            sendMessage(payload);
            Map<String, Object> dados = receiveMessage();
            List<Map<String, Object>> mensagens = castToListOfMap(dados.get("mensagens"));

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
        System.out.print("Digite com quem deseja visualizar a conversa (ex: cliente2): ");
        String origem = scanner.nextLine();

        Map<String, Object> payload = new HashMap<>();
        payload.put("tipo", "receber");
        payload.put("origem", origem);
        payload.put("destino", NOME_CLIENTE);

        try {
            sendMessage(payload);
            Map<String, Object> dados = receiveMessage();
            List<Map<String, Object>> mensagens = castToListOfMap(dados.get("mensagens"));

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
        OutputStream outputStream = socket.getOutputStream();
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();

        MessagePacker packer = MessagePack.newDefaultPacker(byteArrayOutputStream);
        packer.packMapHeader(payload.size());

        for (Map.Entry<String, Object> entry : payload.entrySet()) {
            packer.packString(entry.getKey());
            Object value = entry.getValue();
            if (value == null) {
                packer.packNil();
            } else if (value instanceof String) {
                packer.packString((String) value);
            } else if (value instanceof Integer) {
                packer.packInt((Integer) value);
            } else if (value instanceof Boolean) {
                packer.packBoolean((Boolean) value);
            } else {
                packer.packString(value.toString());
            }
        }

        packer.close();

        byte[] data = byteArrayOutputStream.toByteArray();

        // Send length prefix for framing
        DataOutputStream dos = new DataOutputStream(outputStream);
        dos.writeInt(data.length);
        dos.write(data);
        dos.flush();
    }

    private static Map<String, Object> receiveMessage() throws IOException {
        InputStream inputStream = socket.getInputStream();
        DataInputStream dis = new DataInputStream(inputStream);

        // Read length prefix
        int length = dis.readInt();
        byte[] buffer = new byte[length];

        int read = 0;
        while (read < length) {
            int r = dis.read(buffer, read, length - read);
            if (r == -1) {
                throw new IOException("Stream closed prematurely");
            }
            read += r;
        }

        MessageUnpacker unpacker = MessagePack.newDefaultUnpacker(buffer);

        Map<String, Object> response = new HashMap<>();
        int mapSize = unpacker.unpackMapHeader();

        for (int i = 0; i < mapSize; i++) {
            String key = unpacker.unpackString();
            // Try to unpack value dynamically by type
            Object value = unpackDynamic(unpacker);
            response.put(key, value);
        }

        unpacker.close();

        return response;
    }

    private static Object unpackDynamic(MessageUnpacker unpacker) throws IOException {
        switch (unpacker.getNextFormat().getValueType()) {
            case NIL:
                unpacker.unpackNil();
                return null;
            case BOOLEAN:
                return unpacker.unpackBoolean();
            case INTEGER:
                return unpacker.unpackInt();
            case FLOAT:
                return unpacker.unpackDouble();
            case STRING:
                return unpacker.unpackString();
            case ARRAY:
                int arraySize = unpacker.unpackArrayHeader();
                List<Object> list = new ArrayList<>(arraySize);
                for (int i = 0; i < arraySize; i++) {
                    list.add(unpackDynamic(unpacker));
                }
                return list;
            case MAP:
                int mapSize = unpacker.unpackMapHeader();
                Map<String, Object> map = new HashMap<>();
                for (int i = 0; i < mapSize; i++) {
                    String key = unpacker.unpackString();
                    Object value = unpackDynamic(unpacker);
                    map.put(key, value);
                }
                return map;
            case BINARY:
                int len = unpacker.unpackBinaryHeader();
                byte[] bytes = new byte[len];
                unpacker.readPayload(bytes);
                return bytes;
            case EXTENSION:
                // ignore extension types for now
                unpacker.skipValue();
                return null;
            default:
                unpacker.skipValue();
                return null;
        }
    }

    @SuppressWarnings("unchecked")
    private static List<Map<String, Object>> castToListOfMap(Object obj) {
        if (obj instanceof List<?>) {
            List<?> rawList = (List<?>) obj;
            if (!rawList.isEmpty() && rawList.get(0) instanceof Map<?, ?>) {
                List<Map<String, Object>> listOfMap = new ArrayList<>();
                for (Object item : rawList) {
                    listOfMap.add((Map<String, Object>) item);
                }
                return listOfMap;
            }
        }
        return null;
    }
}

