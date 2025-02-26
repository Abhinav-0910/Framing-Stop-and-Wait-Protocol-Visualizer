import socket
import threading

PORT = 65432  # Port number to listen on
TIMEOUT_MS = 5000  # Timeout in milliseconds for retransmission
OUTPUT_FILENAME = "CN/received.txt"  # File to write received data
expected_seq_num = 0  # Expected sequence number for acknowledgment

def handle_client(client_socket, client_address):
    global expected_seq_num
    print(f"New client connected: {client_address[0]}")

    with open(OUTPUT_FILENAME, "a") as file_writer:
        while True:
            try:
                received_message = client_socket.recv(1024).decode().strip()
                if not received_message:
                    break

                if received_message.lower() == 'exit':
                    print(f"Client {client_address[0]} requested to close the connection.")
                    break

                # Parse the received message
                seq_num, data = received_message.split(":", 1)
                seq_num = int(seq_num)

                # Check if the sequence number matches the expected number
                if seq_num == expected_seq_num:
                    # Write the data to the file
                    file_writer.write(data + "\n")
                    file_writer.flush()
                    print(f"Received and wrote to file: {data}")

                    # Send acknowledgment with the expected sequence number
                    client_socket.sendall(f"ACK:{expected_seq_num}\n".encode())
                    print(f"Sent ACK for seq number: {expected_seq_num}")

                    # Increment the expected sequence number
                    expected_seq_num += 1
                else:
                    print(f"Received out-of-order frame, expected: {expected_seq_num} but got: {seq_num}")

            except Exception as e:
                print(f"Client handling exception: {str(e)}")
                break

    client_socket.close()
    print(f"Connection closed for client: {client_address[0]}")
    expected_seq_num=0

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen()

    print(f"Server is listening on port {PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    main()