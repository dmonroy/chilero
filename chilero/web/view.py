import os


class View(object):
    def __init__(self, request, app, *args, **kwargs):
        self.request = request
        self.app = app
        self.args = args
        self.kwargs = kwargs

    def get_full_url(self, path):
        if 'BASE_URL' in os.environ:  # pragma: no cover
            base = os.getenv('BASE_URL')
        else:
            base = '{}://{}'.format(
                self.request.scheme, self.request.host, path
            )

        path = path[1:] if path.startswith('/') else path

        return os.path.join(base, path)
