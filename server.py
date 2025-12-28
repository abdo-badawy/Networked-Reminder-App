import socket
import threading

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode()
        if data:
            
            task, r_time = data.split("|")
            print(f" [RECEIVED] New Reminder: '{task}' at {r_time} from {addr}")
    except Exception as e:
        print(f" [ERROR] {e}")
    finally:
        conn.close()

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", port))
    server.listen(5)
    print(f"[SERVER STARTED] Listening on port: {port}...")
    
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":

    MY_PORT = 14253
    start_server(MY_PORT)