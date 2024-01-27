import socket
import hashlib
import threading
import os

HEADER = 1024
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
privateString = "" #Initialize unique private string

#Authentication
def authenticate_server(client): 
    #Send "Start_Connection" to the server
    client.send("Start_Connection".encode())

    #Receive a random string from the server
    randomString = client.recv(HEADER).decode(FORMAT)

    #Concatenate private_string and random_string and hash the result
    hashedString = hashlib.sha1((privateString + randomString).encode()).hexdigest()

    #Send the hashed string to the server
    client.send(hashedString.encode())

    #Receive the authentication result from the server
    auth_result = client.recv(HEADER).decode(FORMAT)
    if auth_result.startswith("Authentication successful"):
        #If it is wanted to proceed, then return True
        answer = input(auth_result)
        send_packet(client, 0, answer)
        if answer == 'Y':
            return True
        else: 
            return False
    else:
        print("Authentication failed. Connection closed.")
        return False

#Receive packet from server 
def receive(conn):
    while True:
        try:
            packet = conn.recv(HEADER)
            if packet:
                packet_type = packet[0]
                payload = packet[1:].decode(FORMAT)
                #If packet type is 0, print the message
                if packet_type == 0:
                    print(f"{payload}")
                #If packet type is 1, print the remaining time
                elif packet_type == 1:
                    print(f"Remaining Time: {payload} seconds")
                #If packet type is 2, print points that are earned and terminate the game
                elif(packet_type == 2):
                    print("End of Game. Points:", str(payload))
                    send_packet(conn, 0, DISCONNECT_MESSAGE)
                    os._exit(0)
                    break
        except Exception as e:
            print(f"[RECEIVE ERROR] {e}")
            break

#Send packet to server
def send_packet(conn, packet_type, payload):
    try:
        packet = bytes([packet_type]) + payload.encode(FORMAT)
        conn.send(packet)
    except Exception as e:
        print(f"[SEND PACKET ERROR] {e}")

#Send instructions
def send_instruction(conn, instruction, data=""):
    try:
        send_packet(conn, instruction, data)
    except Exception as e:
        print(f"[SEND INSTRUCTION ERROR] {e}")

#Send guesses
def send_guess(conn, guess_type,):
    try:
        if guess_type.lower() == "number":
            guess = input("Enter your guess: ")
            #Send the guessed number
            send_instruction(conn, 3, f"{guess}")
        else:
            #Send guess type whether it is even or odd
            send_instruction(conn, 3, guess_type)

    except Exception as e:
        print(f"[SEND GUESS ERROR] {e}")
    
#Send what the player wants to do
def send_input(client_socket):
    while True:
        #Get input from the player on what they want to do
        choice = input("0 for question,1 for remaining time, 2 for exitting, 3 for guessing\n")
        #If the coice is 0, send the question it is wanted to see
        if(choice == "0"):
            send_instruction(client_socket, 0)
        #If the coice is 1, send the remaining time it is wanted to see
        elif(choice == "1"):
            send_instruction(client_socket, 1)
        #If the coice is 2, send packet to exit the game
        elif(choice == "2"):
            send_instruction(client_socket, 2)
        #If the choice is 3, depending on the input, either send the predicted number or send whether it is even or odd.
        elif(choice == "3"):
            guess = input("Guess the word for typing number first then provide number, or even or odd\n")
            send_guess(client_socket,guess)

#Start game
def start():
        PORT = 5050
        SERVER = '127.0.0.1'
        ADDR = (SERVER, PORT)    
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        #If authentication is failed, exit.
        if not authenticate_server(client):
            print("Exiting.")
            client.close()
            return
        else:
            #If authentication is successful, start the game
            print("Starting the 'Number Guessing Game' Find the number between 0-36")
            threading.Thread(target=receive, args=(client,)).start()
            threading.Thread(target=send_input, args=(client,)).start()

if __name__ == "__main__":
    start()