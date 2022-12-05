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
                header = "HTTP/1.1 {status}\r\n" \
                         "Connection: keep-alive\r\n" \
                         "Content-Type: {type}\r\n" \
                         "Content-Length: {length}\r\n\r\n"

                status = '200 OK'
                t = 'text/html; charset=utf-8'

                try:
                    result = func(
                        *args,
                        **{key: value for key, value in kwargs.items() if key in func.__code__.co_varnames}
                    )
                    
                    try:
                        response, t = result
                    
                    except (TypeError, ValueError):
                        response = result
                    
                    response = Protocol.pack(response)

                except RequestError as e:
                    response = e.response.encode()
                    status = e.status_code

                except TypeError:
                    response = b'illegal parameter'
                    status = '403 Forbidden'

                return (
                    header.format(
                        status=status,
                        type=t,
                        length=len(response)
                    ).encode() +
                    response
                )

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
