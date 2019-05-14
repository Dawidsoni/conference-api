from query_helper import QueryHelper


class TalkProposalController(object):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_talk_proposal(self, query, auth):
        name, title, start_date = query["talk"], query["title"], query["start_timestamp"]
        creator_id = auth["id"]
        db_query = "INSERT INTO talk_proposal (name, creator_id, title, start_date) " \
                   "VALUES ('%s', '%s', '%s', '%s')" % (name, creator_id, title, start_date)
        self.db_connection.execute_update(db_query)
        return QueryHelper.get_ok_response()

    def get_rejected_talk_proposals(self, query, auth):
        if auth["type"] == "O":
            db_query = "SELECT t.name, u.login, t.start_date, t.title FROM talk_proposal t " \
                       "JOIN talk_rejection tr ON (t.talk_rejection_id = tr.id) " \
                       "JOIN participant p ON (t.creator_id = p.id) JOIN conference_user u " \
                       "ON (p.conference_user_id = u.id)"
        elif auth["type"] == "U":
            participant_id = auth["id"]
            db_query = "SELECT t.name, u.login, t.start_date, t.title FROM talk_proposal t " \
                       "JOIN talk_rejection tr ON (t.talk_rejection_id = tr.id) " \
                       "JOIN participant p ON (t.creator_id = p.id) JOIN conference_user u " \
                       "ON (p.conference_user_id = u.id) WHERE t.creator_id = '%s'" % (participant_id,)
        else:
            raise ValueError("Invalid user type")
        query_response = self.db_connection.execute_query(db_query)
        return QueryHelper.get_ok_response(query_response)

    def get_talk_proposals(self, query, auth):
        db_query = "SELECT t.name, u.login, t.start_date, t.title FROM talk_proposal t " \
                   "JOIN participant p ON (t.creator_id = p.id) " \
                   "JOIN conference_user u ON (p.conference_user_id = u.id) " \
                   "WHERE talk_id IS NULL AND talk_rejection_id IS NULL"
        query_response = self.db_connection.execute_query(db_query)
        return QueryHelper.get_ok_response(query_response)
