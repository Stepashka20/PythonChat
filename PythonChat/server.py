from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

chat_history = []


class Client(Protocol):
    ip: str
    login: str
    factory: 'Chat'

    def __init__(self, factory):
        """
        Инициализация фабрики клиента
        :param factory:
        """
        self.factory = factory

    def connectionMade(self):
        """
        Обработчик подключения нового клиента
        """
        self.ip = self.transport.getHost().host
        self.factory.clients.append(self)

        print(f"Client connected: {self.ip}")
        send_text = '\n'.join(chat_history) + "\n"
        self.transport.write(send_text.encode())

    def dataReceived(self, data: bytes):
        """
        Обработчик нового сообщения от клиента
        :param data:
        """
        message = data.decode().replace('\n', '')
        if self.login is not None:
            server_message = f"{self.login}: {message}"
            self.factory.notify_all_users(server_message)
            chat_history.append(f"{self.login}: {message}")
            print(server_message)
        else:
            if message.startswith("login:"):
                self.login = message.replace("login:", "")

                user_exists = 0
                for client in self.factory.clients:
                    if self.login == client.login:
                        user_exists += 1  # так как пользователь уже внесён в список,то одинаковых будет 2 пользователя

                if user_exists > 1:
                    self.transport.write("Login exists\n".encode())
                    # self.factory.clients.remove(self)

                else:

                    notification = f"New user connected: {self.login}"
                    chat_history.append(f"New user connected: {self.login}")
                    self.factory.notify_all_users(notification)
                    print(notification)
            else:
                print("Error: Invalid client login")

    def connectionLost(self, reason=None):
        """
        Обработчик отключения клиента
        :param reason:
        """
        self.factory.notify_all_users(f"{self.login} disconnected.Goodbye...")
        self.factory.clients.remove(self)
        print(f"Client disconnected: {self.ip}")


class Chat(Factory):
    clients: list

    def __init__(self):
        """
        Инициализация сервера
        """
        self.clients = []
        print("*" * 25, "\nStart server \nCompleted [OK]")

    def startFactory(self):
        """
        Запуск процесса ожидания новых клиентов
        :return:
        """
        print("\n\nStart listening for the clients...")

    def buildProtocol(self, addr):
        """
        Инициализация нового клиента
        :param addr:
        :return:
        """
        return Client(self)

    def notify_all_users(self, data: str):
        """
        Отправка сообщений всем текущим пользователям
        :param data:
        :return:
        """
        for user in self.clients:
            user.transport.write(f"{data}\n".encode())


if __name__ == '__main__':
    reactor.listenTCP(7540, Chat())
    reactor.run()
