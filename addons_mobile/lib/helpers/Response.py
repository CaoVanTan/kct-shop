class Response(object):
    SUCCESS = 200
    ERROR = 400

    __STATUS = ''
    __CODE = ''
    __MESSAGE = ''
    __DATA = {}
    __DEFAULT_ERROR_MESSAGE = 'Có lỗi hệ thống xảy ra, vui lòng thử lại sau.'
    __instance = None

    def __init__(self):
        if not Response.__instance:
            Response.__instance = self

    @staticmethod
    def success(message, data):
        Response.__CODE = Response.SUCCESS
        Response.__STATUS = 'Success'
        Response.__set_message_data(message, data)
        return Response

    @staticmethod
    def error(message=False, data={}, code=False):
        Response.__CODE = code or Response.ERROR
        Response.__STATUS = 'Error'
        Response.__set_message_data(message or Response.__DEFAULT_ERROR_MESSAGE, data)
        return Response

    @staticmethod
    def to_json():
        return Response.__generate_template()

    @staticmethod
    def __set_message_data(message, data):
        Response.__MESSAGE = message
        Response.__DATA = data

    @staticmethod
    def __generate_template():
        return {
            "code": Response.__CODE,
            "status": Response.__STATUS,
            "message": Response.__MESSAGE,
            "data": Response.__DATA
        }
