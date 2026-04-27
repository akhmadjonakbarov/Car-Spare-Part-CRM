from utils.response_messages import ResponseMessages


class ResponseType:
    @classmethod
    def response_list(lst, pagination={}, message=ResponseMessages.SUCCESS, ) -> dict:
        return {
            'data': {
                'message': message,
                'list': lst,
                'pagination': pagination
            }
        }


def response_list(lst, pagination={}, message=ResponseMessages.SUCCESS, ) -> dict:
    return {
        'data': {
            'message': message,
            'list': lst,
            'pagination': pagination
        }
    }


def response_item(item, message=ResponseMessages.SUCCESS) -> dict:
    return {
        'data': {
            'message': message,
            'item': item,

        }
    }


def res_error(error) -> dict:
    return {
        'data': {
            'error': error,
        }
    }


def res_message(message) -> dict:
    return {
        'data': {
            'message': message,
        }
    }


class Response:
    def __init__(self, total, pages, page, size, items):
        self.total = total
        self.pages = pages
        self.page = page
        self.size = size
        self.items = items

    def paginated_response(self) -> dict:
        return {
            "total": self.total,
            "pages": self.pages,
            "page": self.page,
            "size": self.size,
            "items": self.items
        }
