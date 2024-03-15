import socket
import threading
import time
import random

class VectorClock:
    def __init__(self, num_processes):
        self.num_processes = num_processes
        self.clock = [0] * num_processes

    def increment(self, process_id):
        if process_id < self.num_processes:
            self.clock[process_id] += 1
        else:
            print(f"Erro: Processo {process_id} não existe.")

    def update(self, other_clock):
        if len(other_clock) == self.num_processes:
            for i in range(self.num_processes):
                self.clock[i] = max(self.clock[i], other_clock[i])
            print("Vetor de atualizado:", self.clock)
        else:
            print("Erro: Tamanho do relógio vetorial incompatível.")

    def __str__(self):
        return str(self.clock)

class Process:
    def __init__(self, process_id, port, num_processes):
        self.process_id = process_id
        self.port = port
        self.num_processes = num_processes
        self.vector_clock = VectorClock(num_processes)

    def send_message(self):
        receiver_port = random.randint(5001, 5000 + self.num_processes)
        message = "Oi, processo!"
        sender_vector = str(self.vector_clock)
        print(f"P{self.process_id + 1} enviando mensagem com vetor: {sender_vector}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', receiver_port))
            s.sendall(f"{message};{sender_vector}".encode())

    def receive_message(self, message, sender_vector):
        sender_vector = eval(sender_vector)
        self.vector_clock.update(sender_vector)
        self.vector_clock.increment(self.process_id)
        print(f"P{self.process_id + 1} recebeu a mensagem '{message}' com vetor {sender_vector}, seu vetor é: {self.vector_clock}")

    def start(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024).decode()
                    message, sender_vector = data.split(";")
                    self.receive_message(message, sender_vector)

def simulate(num_processes):
    processes = []
    for i in range(num_processes):
        port = 5001 + i
        process = Process(i, port, num_processes)
        processes.append(process)
        process.start()

    while True:
        time.sleep(random.uniform(1, 4))
        sender = random.choice(processes)
        sender.send_message()

if __name__ == "__main__":
    num_processes = 4
    simulate(num_processes)
