from Bottle import Bottle, RequestError, File
from pathlib import Path

bottle = Bottle("127.0.0.1", 8080)
source_path = Path('./')


@bottle.route("/")
def index(route):
    return File('src/index.html')


@bottle.route("/error")
def error(route):
    raise RequestError("404 Not Found", "error page")


@bottle.route("/echo")
def echo(route, text=''):
    return text


@bottle.route("/*.*")
def get_file(route):
    file_path = source_path / Path(route[1:])

    if source_path in file_path.parents and file_path.is_file():
        return File(file_path)

    raise RequestError("403 Forbidden", "requested file is out of source path")


if __name__ == '__main__':
    bottle.run()
