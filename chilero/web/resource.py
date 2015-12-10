from .response import JSONResponse
from .view import View


class Resource(View):
    """
    Base class for HTTP Resources (RESTful?)
    """

    # TODO: Optimize for alphanumeric as base pattern
    id_pattern = '{id}'

    # Allow nested resources
    nested_collection_resources = None
    nested_entity_resources = None

    def response(self, *args, **kwargs):
        if self.is_entity():
            return EntityResponse(self, *args, **kwargs)
        else:
            return CollectionResponse(self, *args, **kwargs)

    def get_resource_name(self):
        return self.resource_name \
            if hasattr(self, 'resource_name') \
            else self.__class__.__name__.lower()

    def get_index_url(self, resource=None, **kwargs):
        return self.get_full_url(
            self.app.reverse(
                '{}_index'.format(resource or self.get_resource_name()),
                **kwargs
            )
        )

    def get_object_url(self, id, resource=None):
        return self.get_full_url(
            self.app.reverse(
                '{}_item'.format(resource or self.get_resource_name()), id=id
            )
        )

    def get_self_url(self):
        resource = self.get_resource_name()
        return self.get_index_url(resource) if self.is_collection() \
            else self.get_object_url(
                self.request.match_info.get('id', None), resource
            )

    def is_entity(self):
        """
        Hacky solution to detect if current instance of the class is an entity
        or collection endpoint.
        """
        return 'id' in self.request.match_info

    def is_collection(self):
        return not self.is_entity()

    def has_nested_resources(self):
        if self.is_collection():
            return True if self.nested_collection_resources else False
        else:
            return True if self.nested_entity_resources else False

    def get_nested_resources(self):
        if self.is_collection():
            return self.nested_collection_resources
        else:
            return self.nested_entity_resources

    def get_nested_urls(self):

        current_args = self.request.match_info.copy()
        if 'id' in current_args:
            id = current_args.pop('id')
            current_args['{}_id'.format(self.get_resource_name())] = id

        return {
            k: self.get_index_url(c.__name__.lower(), **current_args)
            for k, c in self.get_nested_resources().items()
        }


class ResourceResponse(JSONResponse):

    def __init__(self, resource, kind=None, extra_content=None, **kwargs):
        data = dict(
            element='resource:{}'.format(kind),
            self=resource.get_self_url()
        )

        if resource.has_nested_resources():
            data['resources'] = resource.get_nested_urls()

        if extra_content is not None:
            data.update(extra_content)

        super(ResourceResponse, self).__init__(data, **kwargs)


class CollectionResponse(ResourceResponse):

    def __init__(self, resource, extra_content=None, **kwargs):

        super(CollectionResponse, self).__init__(
            resource, 'collection', extra_content=extra_content, **kwargs)


class EntityResponse(ResourceResponse):

    def __init__(self, resource, body=None, extra_content=None, **kwargs):

        if extra_content is None:
            extra_content = {}

        extra_content['body'] = body

        super(EntityResponse, self).__init__(
            resource, 'entity', extra_content=extra_content, **kwargs)
