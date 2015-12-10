from .view import View


class Resource(View):
    """
    Base class for HTTP Resources (RESTful?)
    """

    # TODO: Optimize for alphanumeric as base pattern
    id_pattern = '{id}'

    def get_resource_name(self):
        return self.resource_name \
            if hasattr(self, 'resource_name') \
            else self.__name__.lower()

    def get_index_url(self, resource=None):
        return self.get_full_url(
            self.app.reverse(
                '{}_index'.format(resource or self.get_resource_name())
            )
        )

    def get_object_url(self, id, resource=None):
        return self.get_full_url(
            self.app.reverse(
                '{}_item'.format(resource or self.get_resource_name()), id=id
            )
        )
