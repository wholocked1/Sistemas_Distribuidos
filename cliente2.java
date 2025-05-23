import org.msgpack.core.MessageBufferPacker;
import org.msgpack.core.MessagePack;
import org.msgpack.core.MessageUnpacker;

import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.util.Scanner;

public class Cliente2 {

    private static final String HOST = "127.0.0.1";
    private static final int PORT = 5560;
    private static final String NOME_CLIENTE = "cliente2";

    public static void main(String[] args) {
        try (Socket socket = new Socket(HOST, PORT)) {
            System.out.println("[INFO] Conectado ao servidor " + HOST + ":" + PORT);
            OutputStream out = socket.getOutputStream();
            InputStream in = socket.getInputStream();
            Scanner sc = new Scanner(System.in);

            while (true) {
                System.out.println("\nMenu:");
                System.out.println("1 - Visualizar mensagens privadas");
                System.out.println("2 - Enviar mensagem privada");
                System.out.println("3 - Publicar postagem");
                System.out.println("4 - Visualizar postagens públicas");
                System.out.println("0 - Sair");
                System.out.print("Escolha uma opção: ");
                String opcao = sc.nextLine().trim();

                switch (opcao) {
                    case "1":
                        receberMensagens(out, in);
                        break;
                    case "2":
                        enviarMensagem(sc, out, in);
                        break;
                    case "3":
                        publicarPostagem(sc, out, in);
                        break;
                    case "4":
                        visualizarPostagens(out, in);
                        break;
                    case "0":
                        System.out.println("[INFO] Encerrando cliente.");
                        return;
                    default:
                        System.out.println("[ERRO] Opção inválida.");
                }
            }
        } catch (Exception e) {
            System.err.println("[ERRO] " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void receberMensagens(OutputStream out, InputStream in) throws Exception {
        MessageBufferPacker packer = MessagePack.newDefaultBufferPacker();
        packer.packMapHeader(2);
        packer.packString("tipo");
        packer.packString("receber");
        packer.packString("destino");
        packer.packString(NOME_CLIENTE);
        packer.close();

        out.write(packer.toByteArray());

        byte[] buffer = new byte[2048];
        int read = in.read(buffer);
        if (read > 0) {
            processarMensagens(buffer, read);
        }
    }

    private static void enviarMensagem(Scanner sc, OutputStream out, InputStream in) throws Exception {
        System.out.print("Destino: ");
        String destino = sc.nextLine();
        System.out.print("Mensagem: ");
        String mensagem = sc.nextLine();

        MessageBufferPacker packer = MessagePack.newDefaultBufferPacker();
        packer.packMapHeader(4);
        packer.packString("tipo");
        packer.packString("enviar");
        packer.packString("origem");
        packer.packString(NOME_CLIENTE);
        packer.packString("destino");
        packer.packString(destino);
        packer.packString("mensagem");
        packer.packString(mensagem);
        packer.close();

        out.write(packer.toByteArray());

        byte[] buffer = new byte[1024];
        int read = in.read(buffer);
        if (read > 0) {
            exibirRespostaSimples(buffer, read);
        }
    }

    private static void publicarPostagem(Scanner sc, OutputStream out, InputStream in) throws Exception {
        System.out.print("Digite o conteúdo da postagem: ");
        String conteudo = sc.nextLine();

        MessageBufferPacker packer = MessagePack.newDefaultBufferPacker();
        packer.packMapHeader(3);
        packer.packString("tipo");
        packer.packString("postar");
        packer.packString("origem");
        packer.packString(NOME_CLIENTE);
        packer.packString("mensagem");
        packer.packString(conteudo);
        packer.close();

        out.write(packer.toByteArray());

        byte[] buffer = new byte[1024];
        int read = in.read(buffer);
        if (read > 0) {
            exibirRespostaSimples(buffer, read);
        }
    }

    private static void visualizarPostagens(OutputStream out, InputStream in) throws Exception {
        MessageBufferPacker packer = MessagePack.newDefaultBufferPacker();
        packer.packMapHeader(2);
        packer.packString("tipo");
        packer.packString("vizualizar");
        packer.packString("origem");
        packer.packString(NOME_CLIENTE);
        packer.close();

        out.write(packer.toByteArray());

        byte[] buffer = new byte[2048];
        int read = in.read(buffer);
        if (read > 0) {
            processarMensagens(buffer, read);
        }
    }

    private static void processarMensagens(byte[] buffer, int read) throws Exception {
        MessageUnpacker unpacker = MessagePack.newDefaultUnpacker(buffer, 0, read);
        int mapSize = unpacker.unpackMapHeader();

        for (int i = 0; i < mapSize; i++) {
            String key = unpacker.unpackString();
            if (key.equals("mensagens")) {
                int arraySize = unpacker.unpackArrayHeader();
                if (arraySize == 0) {
                    System.out.println("[INFO] Nenhuma mensagem recebida.");
                } else {
                    System.out.println("\nMensagens:");
                    for (int j = 0; j < arraySize; j++) {
                        int msgMap = unpacker.unpackMapHeader();
                        String origem = "", texto = "";
                        for (int k = 0; k < msgMap; k++) {
                            String field = unpacker.unpackString();
                            if (field.equals("origem")) {
                                origem = unpacker.unpackString();
                            } else if (field.equals("mensagem")) {
                                texto = unpacker.unpackString();
                            } else {
                                unpacker.skipValue();
                            }
                        }
                        System.out.println((j + 1) + ". " + origem + " → " + texto);
                    }
                }
            } else {
                unpacker.skipValue();
            }
        }
    }

    private static void exibirRespostaSimples(byte[] buffer, int read) throws Exception {
        MessageUnpacker unpacker = MessagePack.newDefaultUnpacker(buffer, 0, read);
        int mapSize = unpacker.unpackMapHeader();
        for (int i = 0; i < mapSize; i++) {
            String chave = unpacker.unpackString();
            String valor = unpacker.unpackString();
            System.out.println("[RESPOSTA] " + chave + ": " + valor);
        }
    }
}
