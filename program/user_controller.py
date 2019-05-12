import bcrypt
from query_helper import QueryHelper


class UserController(object):
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.ORGANIZER_SECRET = "d8578edf8458ce06fbc5bb76a58c5ca4"

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def add_organizer(self, query, auth):
        login, password, secret = query["newlogin"], query["newpassword"], query["secret"]
        password = str(self.hash_password(password))[2:-1]
        if secret != self.ORGANIZER_SECRET:
            return QueryHelper.get_error_response()
        db_query = "SELECT add_organizer('%s', '%s');" % (login, password)
        self.db_connection.execute_update(db_query)
        return QueryHelper.get_ok_response()

    def add_participant(self, query, auth):
        login, password = query["newlogin"], query["newpassword"]
        password = self.hash_password(password)
        db_query = "SELECT add_participant('%s', '%s')" % (login, password)
        self.db_connection.execute_update(db_query)
        return QueryHelper.get_ok_response()

    def invite_to_friends(self, query, auth):
        participant_id1 = auth["id"]
        login2 = query["login2"]
        db_query = "INSERT INTO participant_friend (participant_id1, participant_id2) " \
                   "VALUES (%s, (SELECT p.id FROM conference_user u JOIN participant p " \
                   "ON (u.id = p.conference_user_id) WHERE u.login = '%s'))" % (participant_id1, login2)
        self.db_connection.execute_update(db_query)
        return QueryHelper.get_ok_response()

    def get_participant_plan(self, query, auth):
        login = query["login"]
        row_limit = query["limit"]
        if int(row_limit) == 0:
            row_limit = "ALL"
        db_query = "SELECT us.login, t.name, t.start_date, t.title, t.room FROM event_reg e " \
                   "JOIN talk t USING (conference_event_id) JOIN participant p ON " \
                   "(e.participant_id = p.id) JOIN conference_user u ON (p.conference_user_id = u.id) " \
                   "JOIN participant ps ON (t.speaker_id = ps.id) JOIN conference_user us ON " \
                   "(ps.conference_user_id = us.id) WHERE t.start_date >= now() AND " \
                   "u.login = '%s' ORDER BY t.start_date LIMIT %s" % (login, row_limit)
        query_response = self.db_connection.execute_query(db_query)
        return QueryHelper.get_ok_response(query_response)

    def get_attended_talks(self, query, auth):
        participant_id = auth["id"]
        db_query = "SELECT t.name, t.start_date, t.title FROM talk t " \
                   "JOIN talk_part p ON (t.id = p.talk_id) " \
                   "WHERE p.participant_id = '%s'" % (participant_id,)
        query_response = self.db_connection.execute_query(db_query)
        return QueryHelper.get_ok_response(query_response)
