from query_helper import QueryHelper


class EventController(object):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_event(self, query, auth):
        event_name = query["eventname"]
        start_date, end_date = query["start_timestamp"], query["end_timestamp"]
        organizer_id = auth["id"]
        db_query = "INSERT INTO conference_event " \
                   "(name, start_date, end_date, organizer_id) VALUES " \
                   "('%s', '%s', '%s', '%s')" % (event_name, start_date, end_date, organizer_id)
        self.db_connection.execute_update(db_query)
        return QueryHelper.get_ok_response()

    def register_for_event(self, query, auth):
        participant_id = auth["id"]
        event_name = query["eventname"]
        db_query = "INSERT INTO event_reg (participant_id, conference_event_id) " \
                   "VALUES (%s, (SELECT id FROM conference_event " \
                   "WHERE name = '%s'))" % (participant_id, event_name)
        self.db_connection.execute_update(db_query)
        return QueryHelper.get_ok_response()

    def get_friends_events(self, query, auth):
        login = auth["login"]
        participant_id = auth["id"]
        event_name = query["eventname"]
        db_query = "SELECT DISTINCT '%s', '%s', u.login FROM event_reg e JOIN conference_event ce " \
                   "ON (e.conference_event_id = ce.id) JOIN participant p " \
                   "ON (e.participant_id = p.id) JOIN conference_user u " \
                   "ON (p.conference_user_id = u.id) WHERE ce.name = '%s' AND e.participant_id IN (" \
                   "SELECT participant_id2 FROM participant_bilatelar_friend WHERE " \
                   "participant_id1 = '%s')" % (login, event_name, event_name, participant_id)
        query_response = self.db_connection.execute_query(db_query)
        return QueryHelper.get_ok_response(query_response)
