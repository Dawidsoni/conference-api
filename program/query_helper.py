class QueryHelper(object):

    @staticmethod
    def get_ok_response(data=None):
        if data is None:
            return {"status": "OK"}
        else:
            return {"status": "OK", "data": data}

    @staticmethod
    def get_error_response():
        return {"status": "ERROR"}

    @staticmethod
    def get_not_implemented_response():
        return {"status": "NOT IMPLEMENTED"}
