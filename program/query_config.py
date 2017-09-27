class QueryConfig(object):

    def get_auth_type_from_config(self, config):
        if "auth" in config:
            return config["auth"]
        else:
            return None

    def get_login_field_from_config(self, config):
        if "login-field" in config:
            return config["login-field"]
        else:
            return "login"

    def get_password_field_from_config(self, config):
        if "password-field" in config:
            return config["password-field"]
        else:
            return "password"

    def get_response_labels(self, config):
        if "response" not in config:
            return []
        labels_list = config["response"].split(',')
        return map(lambda x: x.strip(), labels_list)

    def __init__(self, query_function, config):
        self.query_function = query_function
        self.auth_type = self.get_auth_type_from_config(config)
        self.login_field = self.get_login_field_from_config(config)
        self.password_field = self.get_password_field_from_config(config)
        self.response_labels = self.get_response_labels(config)

    def get_processed_row(self, row):
        processed_row = {}
        for ind, it in enumerate(row):
            label = self.response_labels[ind]
            processed_row[label] = it
        return processed_row

    def get_processed_query_response(self, query_response):
        processed_response = dict()
        processed_response["status"] = query_response["status"]
        if "data" not in query_response:
            return processed_response
        processed_response["data"] = []
        for row in query_response["data"]:
            processed_row = self.get_processed_row(row)
            processed_response["data"].append(processed_row)
        return processed_response
