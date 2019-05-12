import bcrypt


class AuthController(object):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    @staticmethod
    def is_password_correct(password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def is_auth_correctly(self, password, query_response):
        if len(query_response) != 1:
            return False
        return self.is_password_correct(password, query_response[0][2])

    @staticmethod
    def create_auth_info(tup, user_type):
        return {"user_id": tup[0], "login": tup[1], "id": tup[3], "type": user_type}

    def auth_organizer(self, login, password):
        query = "SELECT * FROM conference_user u JOIN organizer o " \
                "ON (u.id = o.conference_user_id) WHERE u.login = '%s'" % (login,)
        query_response = self.db_connection.execute_query(query)
        if self.is_auth_correctly(password, query_response) is False:
            return {}
        return self.create_auth_info(query_response[0], "O")

    def auth_participant(self, login, password):
        query = "SELECT * FROM conference_user u JOIN participant p " \
                "ON (u.id = p.conference_user_id) WHERE u.login = '%s'" % (login,)
        query_response = self.db_connection.execute_query(query)
        if self.is_auth_correctly(password, query_response) is False:
            return {}
        return self.create_auth_info(query_response[0], "U")

    def auth_arbitrary_user(self, login, password):
        auth_response = self.auth_organizer(login, password)
        if len(auth_response) > 0:
            return auth_response
        return self.auth_participant(login, password)

    def try_auth_user(self, login, password, user_type):
        if user_type == "O":
            return self.auth_organizer(login, password)
        elif user_type == "U":
            return self.auth_participant(login, password)
        elif user_type == "U/O" or user_type == "O/U":
            return self.auth_arbitrary_user(login, password)
        else:
            raise ValueError("Invalid user type")

    def auth_user(self, login, password, user_type):
        auth = self.try_auth_user(login, password, user_type)
        if len(auth) == 0:
            raise Exception("Error during authentication")
        return auth
