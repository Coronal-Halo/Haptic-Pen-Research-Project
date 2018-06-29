import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

class CustomTCPServer implements Runnable{
  Socket socket = null;
  ObjectOutputStream oos = null;
  ObjectInputStream ois = null;
  String host = "192.168.43.195";
  int port_server = 80;
  
  String input = null;			                          //Input message from client
  boolean shutdown = false;    	                      //Flag to indicate is the server should keep running
  public ServerSocket server;	                        //public ServerSocket object

  public void run() {
      try {
          //Create the socket server object
          server = new ServerSocket(port_server);		
          //server.setSoTimeout(6000);
          
          //keep listens for 6 secs or until receives 'exit' call from client or is manually shutdown
          while(!shutdown){
              System.out.println("Waiting for client..."); 
             
              // Creating socket and waiting for client connection
              Socket socket = server.accept();		
              
              // Creating input and output IOStreams to reveive request and send response
              BufferedReader in = new BufferedReader(
                      new InputStreamReader(socket.getInputStream()));
              PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
              //DataOutputStream dOut = new DataOutputStream(socket.getOutputStream());
              //ObjectOutputStream oos = new ObjectOutputStream(socket.getOutputStream());
              
              //Keep consuming the input buffer till finish reading the message from client
              while (true) {
                input = in.readLine();
                  if (input == null || input.equals(".")) {
                      break;
                  }
                  //Send input back to client as response
                  System.out.println(input);          
                  //dOut.writeByte(1);
                  //oos.writeByte(1);
              }
        
              //close resources
              in.close();
              out.close();
              socket.close();
        
              //terminate the server if server sends exit request
              if(input != null && input.equalsIgnoreCase("exit")) break;
          }
          
          server.close();
          System.out.println("Server shut down");
        } catch (IOException e1) {
			  //If ever occurs IOException, close the server
          System.out.println("IOException on server mode.");
          if (server != null && !server.isClosed()){
            try {
              server.close(); 
              System.out.println("Server shut down");
            } catch (IOException e2) {
              e2.printStackTrace(System.err); 
            }
          }
        }
  }
    
    public void shutdown(boolean status) {
      shutdown = status;
      if(shutdown == true) {
        System.out.println("Shutting down Socket server...");
      }
    }
}
