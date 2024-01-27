# Socket-Programming
This project was done using the Python programming language. I created a client-server program and established successful communication. Client program should authenticate itself to the server and then server will start the “Guess the Word” game. Server authenticates client by using unique private string. The sha1 hashing mechanism is used to encrypt the unique key to avoid sending unique private string plainly over the network. For this reason, I used hashlib library.
In the game part, the communication between peers (client and server) is asynchronous. Client may send 4 different types of instructions such as start the game, terminate the game, get the remaining time and guess the number. The server application has 3 types of messages related with the game such as question, remaining time and end of the game. Client must react to user inputs immediately and, send corresponding packets to the server. This means that, client application should not be unresponsive when waiting the server packets. Therefore, I used threading python library as the client application needs to use multithreading.

# Running The Application
* Run the following command to start the server: python server.py
* Run the following command to start the client: python client.py
* Start guessing the number directly or whether the number is even or odd.