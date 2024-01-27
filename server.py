import socket
import threading
import hashlib
import os
import time
import random

HEADER = 1024
FORMAT = 'utf-8'
remaining_time = 30  #Initialize remaining time to 30 seconds
privateString = "QyVylmPZGtacMvURbdjRRbyrSxtkkxDm" #Initialize unique private string
points = 0
isStarted = False

def generate_random_string():
    return os.urandom(32).hex()

#Authentication
def authenticate_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    #Receive "Start_Connection" from the client
    start_command = conn.recv(HEADER).decode(FORMAT)
    print(f"[{addr}] Received start command: {start_command}")

    if start_command == "Start_Connection":
        #Send a random string to the client
        random_string = generate_random_string()
        conn.send(random_string.encode())

        #Receive the hashed string from the client
        client_hash = conn.recv(HEADER).decode(FORMAT)

        #Verify the hash on the server side
        server_hash = hashlib.sha1((privateString + random_string).encode()).hexdigest()

        if server_hash == client_hash:
            print(f"[{addr}] Authentication successful.")
            conn.send("Authentication successful. Do you wish to proceed?(Y/N)".encode())
            return True
        else:
            print(f"[{addr}] Authentication failed.")
            conn.send("Authentication failed. Connection closed.".encode())
            return False
    else:
        print(f"[{addr}] Invalid start command. Connection closed.")
        conn.send("Invalid start command. Connection closed.".encode())
        return False
    
def handle_client(conn, addr):
    global points
    print(f"[NEW CONNECTION] {addr} connected.")
    picked_number = random.randint(0, 36)
    print("Picked number", picked_number)
    while remaining_time > 0:
        try:
            start_packet = conn.recv(HEADER)
            instruction = start_packet[0]
            if instruction == 0:
                #Start Game
                global isStarted
                isStarted = True
                send_question_packet(conn, "What is your guess? Number, even, odd?")

            elif instruction == 1:
                #Get remaining time
                send_remaining_time(conn)
                
            elif instruction == 2:
                #Terminate the game
                send_end_of_game(conn)
                break

            elif instruction == 3:
                #Guess instruction
                guessed = (start_packet[1:]).decode(FORMAT)
                #Calculate points
                if(guessed.isdigit()):
                    if int(guessed) == picked_number:
                        #If the number is guessed correctly, 35 points are earned and the game is over
                        send_packet(conn, 0, "Correct! You earned 35 points.")
                        points += calculate_points(guessed, picked_number)
                        send_end_of_game(conn)
                        break
                    else:
                        #If the number is guessed wrong, 1 points are lost and the game is over
                        send_packet(conn, 0, "Incorrect! You lost 1 point.")
                        points += calculate_points(guessed, picked_number)
                        send_end_of_game(conn)
                        break
                else:
                    #If it is known to be an even number, 1 point is earned.
                    if(picked_number % 2 == 0 and guessed.lower() == "even"):
                        send_packet(conn, 0, "Correct! You earned 1 point.")
                        points += calculate_points(guessed, picked_number)
                    #If it is known to be an odd number, 1 point is earned.
                    elif(picked_number % 2 == 1 and guessed.lower() == "odd"):
                        send_packet(conn, 0, "Correct! You earned 1 point.")
                        points += calculate_points(guessed, picked_number)
                    #If it is not known whether it is an odd or even number, 1 point is lost.
                    else:
                        send_packet(conn, 0,  "Incorrect! You lost 1 point.")
                        points += calculate_points(guessed, picked_number)

        except Exception as e:
            print(f"[CONNECTION ERROR] {addr} {e}")
            break

    send_end_of_game(conn)
    os._exit(0)

#Send packet to client
def send_packet(conn, packet_type, payload):
    try:
        packet = bytes([packet_type]) + payload.encode(FORMAT)
        conn.send(packet)
    except Exception as e:
        print(f"[SEND ERROR] {e}")

#When it is wanted to see the remaining time, send the remaining time
def send_remaining_time(conn):
    global remaining_time
    try:
        send_packet(conn, 1, str(remaining_time))
    except Exception as e:
        print(f"[SEND ERROR] {e}")

#Reduce time if multiple of 3 send remaining time
def server_time(conn):
    global remaining_time
    while remaining_time > 0:
        if isStarted:
            try:
                time.sleep(1)
                remaining_time -= 1  #Decrease remaining time
                if remaining_time % 3 == 0:
                    send_packet(conn, 1, str(remaining_time))
            except Exception as e:
                print(f"[SEND ERROR] {e}")
    send_end_of_game(conn)
    os._exit(0)

#Finish the game and submit the earned points
def send_end_of_game(conn):
    try:
        print("Finishing game")
        send_packet(conn, 2, str(points))
    except Exception as e:
        print(f"[SEND ERROR] {e}")

#Send the question
def send_question_packet(conn, question):
    try:
        send_packet(conn, 0, question)
    except Exception as e:
        print(f"[SEND ERROR] {e}")

#Calculate points based on user's guesses
def calculate_points(guess, correct_number):
    if guess.isdigit() and int(guess) == correct_number:
        return 35 #Correct number guess
    elif guess.lower() in ['even', 'odd'] and (correct_number % 2 == 0 and guess.lower() == 'even' or correct_number % 2 != 0 and guess.lower() == 'odd'):
        return 1 #Correct even or odd guess
    else:
        return -1 #Incorrect guess

#Start game
def start():
    PORT = 5050
    SERVER = '127.0.0.1'
    ADDR = (SERVER, PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        #If authentication is successful, start the game
        if authenticate_client(conn, addr):
            threading.Thread(target=handle_client, args=(conn, addr,)).start()
            threading.Thread(target=server_time, args=(conn,)).start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")
        #If authentication is failed, exit.
        else:
            conn.close()
            break
    
if __name__ == "__main__":
    print("[STARTING] server is starting...")
    start()