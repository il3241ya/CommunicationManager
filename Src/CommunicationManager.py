import zmq

# Строитель для CommunicationManager
class CommunicationManagerBuilder:
    def __init__(self, address):
        self.communication_manager = CommunicationManager(address)

    def with_error_handler(self):
        # Настраиваем обработчик ошибок в CommunicationManager
        self.communication_manager.error_handler = None
        return self

    def with_pre_processor(self, pre_processor):
        # Настраиваем предварительный обработчик в CommunicationManager
        self.communication_manager.pre_processor = None
        return self

    def build(self):
        # Возвращаем готовый CommunicationManager
        return self.communication_manager

# Основной класс CommunicationManager
class CommunicationManager:
    def __init__(self, address):
        self.address = address
        self.context = zmq.Context()
        self.error_handler = None
        self.pre_processor = None
        self.socket = None

    def create_socket(self, socket_type):
        try:
            # Создаем сокет и применяем предварительный обработчик
            self.socket = self.context.socket(socket_type)
            self.socket.bind(self.address)
        except zmq.ZMQError as e:
            # Обрабатываем ошибку при создании сокета
            if self.error_handler:
                self.error_handler(e)

    def send_message(self, message):
        try:
            # Отправляем сообщение
            self.socket.send_string(message)
        except zmq.ZMQError as e:
            # Обрабатываем ошибку при отправке сообщения
            if self.error_handler:
                self.error_handler(e)

    def receive_message(self):
        try:
            # Принимаем сообщение
            return self.socket.recv_string()
        except zmq.ZMQError as e:
            # Обрабатываем ошибку при приеме сообщения
            if self.error_handler:
                self.error_handler(e)

if __name__ == "__main__":
    address_cm1 = "tcp://localhost:5556"
    address_cm2 = "tcp://localhost:5555"

    cm1 = CommunicationManager(address_cm1)
    cm2 = CommunicationManager(address_cm2)

    # Создание сокетов
    cm1.create_socket(zmq.PAIR)
    cm2.create_socket(zmq.PAIR)

    # Пример обмена сообщениями
    while True:
        # Отправка сообщения от cm1
        message_cm1 = f"Сообщение от CM1: Hi"
        cm1.send_message(message_cm1)
        print(f"Отправлено CM1: {message_cm1}")
        time.sleep(1)
        # Прием сообщения в cm2
        received_message_cm2 = cm2.receive_message()
        print(f"Получено CM2: {received_message_cm2}")

        time.sleep(1)