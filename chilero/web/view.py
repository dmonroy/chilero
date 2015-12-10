class View(object):
    def __init__(self, request, app, *args, **kwargs):
        self.request = request
        self.app = app
        self.args = args
        self.kwargs = kwargs

    def get_full_url(self, path):
        return '{}://{}{}'.format(
            self.request.scheme, self.request.host, path
        )
