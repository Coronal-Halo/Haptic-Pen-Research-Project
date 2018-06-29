/** 
 * Author: Yuxiang Huang
 * Date: June 25th, 2018
 * Note: java network related code is imported from the CustomTCPClient class,
 * which is inside the file "CustomTCPClient.java", under the same folder as 
 * this file
 */
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.net.InetSocketAddress;

// GUI related variables
int clientRectX, clientRectY;        // Position of "send msg" square button
int textRespX, textRespY;            // Position for the response textbox
int textMsgToSendX, textMsgToSendY;  // Position for the msgToSend textbox
int rectWidth = 40;                  // Width of the "send msg" button
int rectLength = 100;                // Length of the "send msg" button
color rectColor, baseColor;
color rectHighlight, circleHighlight;
color currentColor;
boolean clientRectOver = false;

// Network related variables
Socket socket = null;
ObjectOutputStream oos = null;
ObjectInputStream ois = null;
String host = "192.168.43.195";
int port_client = 8080;

// socket server port on which it will listen
int port_server = 80;
// Client dec
CustomTCPClient client;

String msgToSend = "";

void setup() {
  // Set up buttons, positions and colors
  size(640, 360);
  rectColor = color(0);
  rectHighlight = color(51);
  baseColor = color(102);
  
  clientRectX = width/2-rectLength/2;
  clientRectY = 3*height/4-rectWidth/2;
  ellipseMode(CENTER);
  
  textRespX = width/2-rectLength;
  textRespY = height/2-rectWidth;
  textMsgToSendX = width/2-rectLength;
  textMsgToSendY = height/3-rectWidth;
}

void draw() {
  update(mouseX, mouseY);
  
  if (clientRectOver) {
    fill(rectHighlight);
  } else {
    fill(rectColor);
  }
  stroke(255);
  rect(clientRectX, clientRectY, rectLength, rectWidth);
  
  textSize(14); 
  fill(color(255));
  text("Send Msg", clientRectX + rectLength/5, clientRectY + rectWidth/3, width, 100);
  text("Response from Server: ", textRespX, textRespY, width, 100); 
  text("Message to Send: " + msgToSend, textMsgToSendX, textMsgToSendY, width, 100);
}

void mousePressed() {
  // If clicks the circle, enter client mode
  if (clientRectOver) { //<>//
    currentColor = rectColor;
    client = new CustomTCPClient();
    
    try{
      client.InitSocket(host, port_client);
      client.sendData(msgToSend);
      // read resposne from server. I am not sure if there needs to be some delay but this works fine for me
      String resp = client.readResponse();
      if(resp != null){
        System.out.println(resp);
        fill(color(20));
        text("Response from Server:" + resp, 100, 50, width, 100); 
      }
      // Close IOstreams and socket after done using them
      client.closeIOStream();
      client.closeSocket();
    } catch(UnknownHostException e){
      System.out.print("UnKnownHostException on client mode"); 
    } catch(IOException e) {
      System.out.print("IOException on client mode"); 
    } catch (ClassNotFoundException e) {
      System.out.print("ClassNotFoundException on client mode"); 
    } catch (InterruptedException e) {
      System.out.print("InterruptException on client mode"); 
    }
  }
}

void keyPressed() {
  // Check if the pressed key is a special key
  if (key==CODED) {
      println ("unknown special key");
  } else {
    if (key==BACKSPACE) {
      if (msgToSend.length()>0)
        msgToSend = msgToSend.substring(0, msgToSend.length()-1);
    } else if (key==RETURN || key==ENTER) {
      println ("ENTER pressed");
    } else {
      msgToSend += key;
    } 
    //println (msgToSend);
  } 
}

// Check if the mouse is over the "send msg" button
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
  if ( overRect(clientRectX, clientRectY, rectLength, rectWidth) ) {
    clientRectOver = true;
  } else {
    clientRectOver = false;
  }
}
