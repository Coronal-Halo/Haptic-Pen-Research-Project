/** 
 * Author: Yuxiang Huang
 * Date: June 28th, 2018
 * This is a multi-threaded GUI and server program
 * Note: server code imported from the CustomTCPServerThread class,
 * which is inside the file "CustomTCPServerThread.java" under the 
 * same folder as this file
 */
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.PrintWriter;
import java.lang.ClassNotFoundException;
import java.net.ServerSocket;
import java.net.Socket;

// GUI related variables
int startServerRectX, startServerRectY;    // Position of "Start Servers" square button
int stopServerRectX, stopServerRectY;      // Position of "Start Servers" square button
int textRespX, textRespY;                  // Position for the response textbox
int textMsgToSendX, textMsgToSendY;        // Position for the msgToSend textbox
int rectWidth = 40;                        // Width of the "send msg" button
int rectLength = 120;                      // Length of the "send msg" button
color rectColor, baseColor;
color rectHighlight, circleHighlight;
color currentColor;
boolean startServerRectOver = false;
boolean stopServerRectOver = false;
boolean serverStart = false;               // flag indicating the user pressed "Start Server" button
boolean serverRunning = false;             // flag indicating if the server is currently running
String input = null;                       // input from client
String response = null;                    // response sent from the server

// Network, server and thread related variables
Socket socket = null;
ObjectOutputStream oos = null;
ObjectInputStream ois = null;
int port_server = 80;                      // Port listened by the server

Thread serverThread = null;                // Server thread

//static ServerSocket variable
CustomTCPServer TCPServer = null;

void setup() {
  // Set up buttons, positions and colors
  size(640, 360);
  rectColor = color(0);
  rectHighlight = color(51);
  baseColor = color(102);
  
  startServerRectX = width/2-rectLength/2;
  startServerRectY = 3*height/5-rectWidth/2;
  stopServerRectX = width/2-rectLength/2;
  stopServerRectY = 3*height/4-rectWidth/2;
  ellipseMode(CENTER);
  
  textRespX = width/2-rectLength;
  textRespY = height/2-rectWidth;
  textMsgToSendX = width/2-rectLength;
  textMsgToSendY = height/3-rectWidth;
}

void draw() {
  update(mouseX, mouseY);
  
  if (startServerRectOver) {
    fill(rectHighlight);
  } else {
    fill(rectColor);
  }
  stroke(255);
  rect(startServerRectX, startServerRectY, rectLength, rectWidth);
  
  if (stopServerRectOver) {
    fill(rectHighlight);
  } else {
    fill(rectColor);
  }
  stroke(255);
  rect(stopServerRectX, stopServerRectY, rectLength, rectWidth);
  
  textSize(14); 
  fill(color(255));
  text("Start Server", startServerRectX + rectLength/5, startServerRectY + rectWidth/3, width, 100);
  text("Stop Server", stopServerRectX + rectLength/5, stopServerRectY + rectWidth/3, width, 100);
  text("Message from Client "+input, textRespX, textRespY, width, 100); 
  text("Response Sent: "+response, textMsgToSendX, textMsgToSendY, width, 100);
  
  // serverStart turns to TRUE after user clicks "Start Server" button
  if(serverStart) {
    // Start the server thread if the server is not already running
    if(!serverRunning) {
      TCPServer = new CustomTCPServer();
      TCPServer.shutdown(false);
      serverThread = new Thread(TCPServer); 
      serverThread.start();
      serverRunning = true;
    }
  }
  
  /*if(TCPServer == null){
    System.out.print("TCPServer is null!"); 
  }*/
  
  // serverStart turns to FALSE after user clicks "Stop Server" button
  if(!serverStart){
    // Terminate the server thead
    if(TCPServer != null){
      TCPServer.shutdown(true);
      try {
        TCPServer.server.close();
        System.out.println("Server shut down"); 
      } catch (IOException e) {
        System.out.println("Error closing server socket"); 
      }
      // Free the memory after terminating thread
      TCPServer = null;
      serverThread = null;
    }
    serverRunning = false;
  }
}

void mousePressed() {
  // If clicks the circle, enter server mode
  if (startServerRectOver) {
    currentColor = rectColor;
    serverStart = true;
  } else if(stopServerRectOver) {
    currentColor = rectColor;
    serverStart = false;
  }
}

// Check if the mouse is over one of the buttons
boolean overRect(int x, int y, int width, int height)  {
  if (mouseX >= x && mouseX <= x+width && 
      mouseY >= y && mouseY <= y+height) {
    return true;
  } else {
    return false;
  }
}

// Update mouse position
void update(int x, int y) {
  if ( overRect(startServerRectX, startServerRectY, rectLength, rectWidth) ) {
    startServerRectOver = true;
    stopServerRectOver = false;
  } else if ( overRect(stopServerRectX, stopServerRectY, rectLength, rectWidth) ) {
    startServerRectOver = false;
    stopServerRectOver = true;
  } else {
    startServerRectOver = stopServerRectOver = false;
  }
}
