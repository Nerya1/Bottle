from Bottle import File


class Protocol:
    TIMEOUT = 0.2

    @staticmethod
    def receive(socket):
        try:
            return socket.recv(1024), True

        except TimeoutError:
            return None, False

    @staticmethod
    def process_variables(request):
        request = request.split('&')

        dct = {}

        for arg in request:
            key, value = arg.split('=')
            dct.update({key: value.replace('+', ' ')})

        return dct

    @staticmethod
    def process_request(request):
        request = request.decode().strip('\r\n')

        head, *args = request.split('\r\n')
        method, route, version = head.split()
        variables = {}

        if '?' in route:
            route, variables = route.split('?')
            variables = Protocol.process_variables(variables)

        dct = {
            'Method': method,
            'Route': route,
            'Version': version,
            'Variables': variables
        }

        for arg in args:
            key, value = arg.split(': ')
            dct.update({key: value})

        return dct

    @staticmethod
    def pack(item):
        match item:
            case str():
                return item.encode()

            case File():
                with open(item.path, 'rb') as file:
                    return file.read()
