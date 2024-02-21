from abc import ABC, abstractmethod

import time
import zmq


class CommunicationManagerBuilder:
    def __init__(self, address):
        self.communication_manager = CommunicationManager(address)

    def build(self):
        return self.communication_manager


class CommunicationManager:
    def __init__(self, address):
        self.address = address
        self.context = zmq.Context()
        self.socket = None

    def create_socket(self, socket_type):
        try:
            self.socket = self.context.socket(socket_type)
            self.socket.bind(self.address) if socket_type == zmq.PUSH else self.socket.connect(self.address)
        except zmq.error.ZMQError as e:
            print(f"Ошибка при создании сокета: {e}")

    def receive_message(self):
        try:
            return self.socket.recv_string()
        except zmq.error.ZMQError as e:
            print(f"Ошибка при приеме сообщения: {e}")

    def send_message(self, message):
        try:
            self.socket.send_string(message)
        except zmq.error.ZMQError as e:
            print(f"Ошибка при отправке сообщения: {e}")


if __name__ == "__main__":
    send_address = "tcp://localhost:5555"
    receive_address = "tcp://localhost:5556"

    # Использование строителя для отправителя
    sender_manager = (
        CommunicationManagerBuilder(send_address)
        .build()
    )
    receiver_manager = (
        CommunicationManagerBuilder(receive_address)
        .build()
    )

    # Создание сокетов
    sender_manager.create_socket(zmq.PUSH)
    receiver_manager.create_socket(zmq.PULL)
    while True:
        # Отправка сообщения
        sender_manager.send_message("Сообщение от отправителя CM1")

        # Прием сообщения
        received_message = receiver_manager.receive_message()
        print(f"Получено сообщение: {received_message}")
