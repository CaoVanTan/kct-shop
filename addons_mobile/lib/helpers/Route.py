class Route(object):
    __ROOT_ENTRY_POINT = '/api/{0}'

    def __new__(cls, route):
        return cls.__route(route)

    @staticmethod
    def __route(route):
        return Route.__ROOT_ENTRY_POINT.format(route)
