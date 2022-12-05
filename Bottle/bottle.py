from functools import wraps
from socket import create_server
from select import select
from re import compile

from Bottle import Protocol, RequestError


class Bottle:
    def __init__(self, host: str, port: int):
        self.running = True

        self.socket = create_server((host, port))
        self.socket.settimeout(Protocol.TIMEOUT)
        self.socket.listen()

        self.clients = {}
        self.routes = {}

    def route(self, route: str):
        def decorator(func):
            @wraps(func)
            def wrap(*args, **kwargs):
                header = "HTTP/1.1 {code} {status}\r\n" \
                         "Connection: keep-alive\r\n" \
                         "Content-Type: {type}\r\n" \
                         "Content-Length: {length}\r\n\r\n"

                code = 200
                status = 'OK'

                try:
                    response = func(*args, **kwargs)

                except RequestError:
                    response = 'placeholder'  # TODO: handle RequestError

                return (
                    header.format(
                        code=code,
                        status=status,
                        type='',
                        length=len(response)
                    ) +
                    response
                ).encode()

            self.routes.update({compile(route): wrap})
            return wrap

        return decorator

    def handle_request(self, request):
        request = Protocol.process_request(request)
        match request:
            case {'Method': 'GET', 'Route': requested_route, 'Variables': kwargs}:
                for route, func in self.routes.items():
                    if route.fullmatch(requested_route):
                        return func(requested_route, **kwargs)

        return b''

    def accept(self):
        connection, address = self.socket.accept()

        self.clients.update({
            connection: address
        })

    def respond(self):
        ins, outs, errs = select(
            self.clients.keys(),
            (),
            (),
            0.1
        )

        for client in ins:
            data, received = Protocol.receive(client)

            if received:
                if data:
                    client.send(self.handle_request(data))

                else:
                    self.clients.pop(client)

    def run(self):
        while self.running:
            try:
                self.accept()

            except TimeoutError:
                pass

            self.respond()
