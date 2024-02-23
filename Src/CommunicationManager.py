import zmq
import logging

import zmq
import logging

# Строитель для CommunicationManager
class CommunicationManagerBuilder:
    def __init__(self, address):
        self.communication_manager = CommunicationManager(address)

    def with_error_handler(self):
        # Настраиваем обработчик ошибок в CommunicationManager
        self.communication_manager.error_handler = self.communication_manager.default_error_handler
        return self

    def with_logger(self, logger_creator):
        # Настраиваем предварительный обработчик в CommunicationManager
        self.communication_manager.logger = CommunicationManager.default_logger()
        return self

    def build(self):
        # Возвращаем готовый CommunicationManager
        return self.communication_manager

# Основной класс CommunicationManager
class CommunicationManager:
    def __init__(self, address):
        self.address = address
        self.context = zmq.Context()
        self.error_handler = self.default_error_handler
        self.logger = None #self.default_logger('communication_logs.log')
        self.socket = None

    def create_socket(self, socket_type, start_func):
        try:
            # Создаем сокет и применяем предварительный обработчик
            self.socket = self.context.socket(socket_type)
            if start_func == 'bind':
                self.socket.bind(self.address)
                if self.logger: self.logger.info(f"OK: Socket is open in {start_func} mode at {self.address}")
            if start_func == 'connect':
                self.socket.connect(self.address)
                if self.logger: self.logger.info(f"OK: Socket is open in {start_func} mode at {self.address}")
        except zmq.ZMQError as e:
            # Обрабатываем ошибку при создании сокета
            if self.error_handler:
                self.error_handler(e)

    def send_message(self, message):
        try:
            # Отправляем сообщение
            self.socket.send_string(message)
            if self.logger: self.logger.info(f"OK: Message sent to {self.address}")
        except zmq.ZMQError as e:
            # Обрабатываем ошибку при отправке сообщения
            if self.error_handler:
                self.error_handler(e)

    def receive_message(self):
        try:
            # Принимаем сообщение
            if self.logger: self.logger.info(f"OK: Message received from {self.address}")
            return self.socket.recv_string()
        except zmq.ZMQError as e:
            # Обрабатываем ошибку при приеме сообщения
            if self.error_handler:
                self.error_handler(e)

    def close_socket(self):
        if self.socket:
            self.socket.close()

    def close_context(self):
        if self.context:
            self.context.term()

    def default_error_handler(self, error):
        self.close_socket()
        self.close_context()
        if self.logger: self.logger.error(f"ERROR: {error}")

    @classmethod
    def default_logger(cls, log_file_path='communication_logs.log'):
        # Настройка логгера
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        # Создаем и настраиваем логгер
        logger = logging.getLogger('communication_logger')
        logger.addHandler(file_handler)

        return logger


if __name__ == "__main__":
    address = "tcp://*:5555"
    cm1 = (
    CommunicationManagerBuilder(address)
    .with_error_handler()
    .with_logger(CommunicationManager.default_logger)
    .build()
    )
    # Создание сокетов
    cm1.create_socket(zmq.PAIR, 'bind')
    # Пример обмена сообщениями
    while True:
        mes_out = "CM1"
        cm1.send_message(mes_out)

        mes_in = cm1.receive_message()
        print(mes_in)