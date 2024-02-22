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
            if self.pre_processor:
                self.pre_processor(self.socket)
            # Привязываем или подключаем сокет в зависимости от типа
            self.socket.bind(self.address) if socket_type == zmq.PUSH else self.socket.connect(self.address)
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

# Пример использования
send_address = "tcp://*:5555"
receive_address = "tcp://localhost:5555"

# Использование строителя для отправителя
sender_manager = (
    CommunicationManagerBuilder(send_address)
    .with_error_handler()
    .with_pre_processor(lambda socket: print("Pre-processing for sender"))
    .build()
)

# Использование строителя для приемника
receiver_manager = (
    CommunicationManagerBuilder(receive_address)
    .with_error_handler()
    .with_pre_processor(lambda socket: print("Pre-processing for receiver"))
    .build()
)
while True:
    # Создание сокетов
    sender_manager.create_socket(zmq.PUSH)
    receiver_manager.create_socket(zmq.PULL)

    # Отправка сообщения
    sender_manager.send_message("Сообщение от отправителя")

    # Прием сообщения
    received_message = receiver_manager.receive_message()
    print(f"Получено сообщение: {received_message}")