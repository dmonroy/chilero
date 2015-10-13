from chilero import web


class HelloView(web.View):

    def get(self):
        return web.Response('Hello world!')


def main():
    routes = [
        ['/', HelloView]
    ]

    web.run(web.Application, routes)

if __name__ == '__main__':
    main()
