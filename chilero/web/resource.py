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

    def __init__(self, *args, **kwargs):
        self._parent = kwargs.pop('parent') if 'parent' in kwargs else None
        super(Resource, self).__init__(*args, **kwargs)

    def response(self, *args, **kwargs):
        if self.is_entity():
            return EntityResponse(self, *args, **kwargs)
        else:
            return CollectionResponse(self, *args, **kwargs)

    def get_resource_name(self):
        return self.resource_name \
            if hasattr(self, 'resource_name') \
            else self.__class__.__name__.lower()

    def default_kwargs_for_urls(self):
        """
        Default keyword arguments for building the resource's urls.

        :return: dict
        """
        return {}

    def get_index_url(self, resource=None, **kwargs):
        """
        Builds the url of the resource's index.

        :param resource: name of the resource or None
        :param kwargs: additional keyword arguments to build the url
        :return: url of the resource's index
        """
        default_kwargs = self.default_kwargs_for_urls() \
            if resource == self.get_resource_name() else {}

        default_kwargs.update(kwargs)

        return self.get_full_url(
            self.app.reverse(
                '{}_index'.format(resource or self.get_resource_name()),
                **default_kwargs
            )
        )

    def get_definition_url(self, resource=None, **kwargs):
        default_kwargs = self.default_kwargs_for_urls() \
            if resource is None else {}
        default_kwargs.update(kwargs)

        return self.get_full_url(
            self.app.reverse(
                '{}_definition'.format(resource or self.get_resource_name()),
                **default_kwargs
            )
        )

    def get_object_url(self, id, resource=None, **kwargs):
        default_kwargs = self.default_kwargs_for_urls() \
            if resource is None else {}
        default_kwargs.update(kwargs)

        return self.get_full_url(
            self.app.reverse(
                '{}_item'.format(resource or self.get_resource_name()),
                id=id,
                **default_kwargs
            )
        )

    def get_self_url(self):
        resource = self.get_resource_name()
        return self.get_index_url(
            resource,
            **self.default_kwargs_for_urls()) if self.is_collection() \
            else self.get_object_url(
            self.request.match_info.get('id', None),
            resource, **self.default_kwargs_for_urls()
        )

    def get_encoder_class(self):
        return getattr(self, 'encoder_class', None)

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

        def _nested_url(k, c):
            if issubclass(c, Resource):
                return self.get_index_url(c.__name__.lower(), **current_args)

            return self.get_full_url(
                self.app.reverse(
                    '{}'.format(c.__name__.lower()),
                    **current_args
                )
            )

        return {
            k: _nested_url(k, c)
            for k, c in self.get_nested_resources().items()
        }

    def get_parent(self):
        """Returns the url to the parent endpoint."""
        if self.is_entity():
            return self.get_index_url(**self.default_kwargs_for_urls())
        elif self._parent is not None:
            resource = self._parent.rsplit('_', 1)[0]
            parts = self.default_kwargs_for_urls()

            if '{}_id'.format(resource) in parts:
                id = parts.pop('{}_id'.format(resource))
                parts['id'] = id
            return self.get_full_url(
                self.app.reverse(
                    self._parent, **parts
                )
            )

    def resource_definition(self, **kwargs):
        definition = self.get_definition(**kwargs) \
            if hasattr(self, 'get_definition') \
            else getattr(self, 'definition', {})
        return JSONResponse(definition)


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

        if hasattr(resource, 'definition'):
            data['definition'] = resource.get_definition_url()

        data['parent'] = resource.get_parent() or None

        super(ResourceResponse, self).__init__(
            data, cls=resource.get_encoder_class(), **kwargs
        )


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
