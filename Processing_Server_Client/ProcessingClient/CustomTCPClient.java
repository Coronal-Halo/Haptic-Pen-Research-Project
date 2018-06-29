import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.net.InetSocketAddress;

/**
 * A simple Swing-based client for the capitalization server.
 * It has a main frame window with a text field for entering
 * strings and a textarea to see the results of capitalizing
 * them.
 */
public class CustomTCPClient {
    Socket socket = null;
    ObjectOutputStream oos = null;
    ObjectInputStream ois = null;
    
    public void InitSocket(String serverAddr, int port) throws UnknownHostException, IOException, ClassNotFoundException, InterruptedException {
    	//establish socket connection to server; creating the socket with a timeout.
		System.out.println("Initializing socket connection to server...");
		socket = new Socket();
		socket.connect(new InetSocketAddress(serverAddr, port), 5000);
    }
    
    public void sendData(String data) throws IOException {
		System.out.println("Sending data to the server...");
    	oos = new ObjectOutputStream(socket.getOutputStream());
    	oos.writeObject(data);
    	System.out.println("Data sent");
    }
    
    public String readResponse() throws IOException, ClassNotFoundException {
    	ois = new ObjectInputStream(socket.getInputStream());
    	//while(ois.available() == 0); // This does not work well
    	String response = (String) ois.readObject();
    	return response;
    }
    
    public void closeIOStream() throws IOException {
    	ois.close();
		oos.close();
    }

    public void closeSocket() throws IOException {
    	socket.close();
    }
    
  // Example code
	public static void main(String[] args) throws Exception {
		// get the localhost IP address, if server is running on some other IP, you need to use that
		String host = "192.168.43.195";
	    int port = 8080;
	    
		CustomTCPClient client = new CustomTCPClient();
		client.InitSocket(host, port);
		client.sendData("hello");
		
		// read resposne from server. I am not sure if there needs to be some delay but this works fine for me
		String resp = client.readResponse();
		System.out.println(resp);
		
		// Close IOstreams and socket after done using them
		client.closeIOStream();
		client.closeSocket();
	}
}
	
