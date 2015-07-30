from .view import View


class Resource(View):
    """
    Base class for HTTP Resources (RESTful?)
    """
    id_pattern = r'{id:^\w+$}'
