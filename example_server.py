from Bottle import Bottle

bottle = Bottle("127.0.0.1", 8080)


@bottle.route("/")
def index(route, test):
    return test


if __name__ == '__main__':
    bottle.run()
