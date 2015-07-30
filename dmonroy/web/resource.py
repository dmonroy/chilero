from .view import View


class Resource(View):
    """
    Base class for HTTP Resources (RESTful?)
    """

    # TODO: Optimize for alphanumeric as base pattern
    id_pattern = '{id}'
