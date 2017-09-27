from query_helper import QueryHelper


class TalkController(object):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def confirm_if_proposal(self, talk_name):
        db_query = "UPDATE talk_proposal SET talk_id = " \
                   "(SELECT id FROM talk WHERE name = '%s') " \
                   "WHERE name = '%s'" % (talk_name, talk_name)
        self.db_connection.execute_update(db_query)

    def create_talk(self, query, auth):
        speaker, name, title = query["speakerlogin"], query["talk"], query["title"]
        start_date, room = query["start_timestamp"], query["room"]
        org_id = auth["id"]
        org_rating, event_name = query["initial_evaluation"], query["eventname"]
        db_query = "INSERT INTO talk (name, speaker_id, title, start_date, room, " \
                   "organizer_rating, conference_event_id, organizer_id) VALUES " \
                   "('%s', (SELECT p.id FROM conference_user u JOIN participant p " \
                   "ON (u.id = p.conference_user_id) WHERE u.login = '%s'), '%s', '%s', " \
                   "'%s', '%s', (SELECT id FROM conference_event WHERE name = '%s'), '%s')" % \
                (name, speaker, title, start_date, room, org_rating, event_name, org_id)
        self.db_connection.execute_update(db_query)
        self.confirm_if_proposal(name)
        return QueryHelper.get_ok_response()

    def register_attendance(self, query, auth):
        name = query["talk"]
        participant_id = auth["id"]
        db_query = "INSERT INTO talk_part (participant_id, talk_id) VALUES " \
                   "('%s', (SELECT id FROM talk WHERE name = '%s'))" % (participant_id, name)
        self.db_connection.execute_update(db_query)
        return QueryHelper.get_ok_response()

    def register_rating(self, query, auth):
        name, rating = query["talk"], query["rating"]
        participant_id = auth["id"]
        db_query = "INSERT INTO talk_rating (participant_id, talk_id, rating) VALUES " \
                   "('%s', (SELECT id FROM talk WHERE name = '%s')," \
                   "'%s')" % (participant_id, name, rating)
        self.db_connection.execute_update(db_query)
        return QueryHelper.get_ok_response()

    def get_day_plan(self, query, auth):
        talk_day = query["timestamp"]
        db_query = "SELECT name, start_date, title, room FROM talk WHERE start_date " \
                   "BETWEEN ('%s'::date) AND ('%s'::date + INTERVAL '23:59' HOUR TO MINUTE) " \
                   "ORDER BY room, start_date" % (talk_day, talk_day)
        query_response = self.db_connection.execute_query(db_query)
        return QueryHelper.get_ok_response(query_response)

    def get_best_talks(self, query, auth):
        start_date, end_date = query["start_timestamp"], query["end_timestamp"]
        row_limit, is_all = query["limit"], query["all"]
        if int(row_limit) == 0:
            row_limit = "ALL"
        if int(is_all):
            db_query = "SELECT t.name, t.start_date, t.title, t.room FROM talk t " \
                       "LEFT JOIN talk_rating tr ON (t.id = tr.talk_id) " \
                       "WHERE t.start_date BETWEEN '%s' AND '%s' " \
                       "GROUP BY t.id, t.name, t.start_date, t.title, t.room ORDER BY " \
                       "((COALESCE(SUM(tr.rating), 0) + t.organizer_rating)::float " \
                       "/ (COUNT(tr.rating) + 1)) DESC LIMIT %s" % (start_date, end_date, row_limit)
        else:
            db_query = "SELECT t.name, t.start_date, t.title, t.room FROM talk_rating tr " \
                       "JOIN talk_part tp USING (talk_id, participant_id) RIGHT JOIN talk t " \
                       "ON (tr.talk_id = t.id) WHERE t.start_date BETWEEN '%s' AND '%s' " \
                       "GROUP BY t.id, t.name, t.start_date, t.title, t.room " \
                       "ORDER BY ((COALESCE(SUM(tr.rating), 0) + t.organizer_rating)::float " \
                       "/ (COUNT(tr.rating) + 1)) DESC LIMIT %s" % (start_date, end_date, row_limit)
        query_response = self.db_connection.execute_query(db_query)
        return QueryHelper.get_ok_response(query_response)

    def get_most_popular_talks(self, query, auth):
        start_date, end_date = query["start_timestamp"], query["end_timestamp"]
        row_limit = query["limit"]
        if int(row_limit) == 0:
            row_limit = "ALL"
        db_query = "SELECT t.name, t.start_date, t.title, t.room FROM talk t " \
                   "LEFT JOIN talk_part p ON (t.id = p.talk_id) WHERE t.start_date " \
                   "BETWEEN '%s' AND '%s' GROUP BY t.id, t.name, t.start_date, t.title, t.room " \
                   "ORDER BY COUNT(p.participant_id) DESC LIMIT %s" % (start_date, end_date, row_limit)
        query_response = self.db_connection.execute_query(db_query)
        return QueryHelper.get_ok_response(query_response)

    def get_abandoned_talks(self, query, auth):
        row_limit = query["limit"]
        if int(row_limit) == 0:
            row_limit = "ALL"
        db_query = "WITH part_count AS (SELECT t.id AS id, COUNT(tp.participant_id) AS p_count " \
                   "FROM talk t JOIN talk_part tp ON (t.id = tp.talk_id) " \
                   "JOIN conference_event ce ON (t.conference_event_id = ce.id) " \
                   "JOIN event_reg USING (participant_id, conference_event_id) GROUP BY t.id), " \
                   "total_count AS (SELECT t.id AS id, COUNT(DISTINCT er.participant_id) " \
                   "AS t_count FROM talk t JOIN conference_event ce ON (t.conference_event_id = ce.id) " \
                   "JOIN event_reg er ON (er.conference_event_id = ce.id) GROUP BY t.id) " \
                   "SELECT name, start_date, title, room, t_count - p_count FROM talk " \
                   "JOIN total_count USING (id) JOIN part_count USING (id) " \
                   "ORDER BY (t_count - p_count) DESC LIMIT %s" % (row_limit,)
        query_response = self.db_connection.execute_query(db_query)
        return QueryHelper.get_ok_response(query_response)

    def get_recently_added_talks(self, query, auth):
        row_limit = query["limit"]
        if int(row_limit) == 0:
            row_limit = "ALL"
        db_query = "SELECT t.name, u.login, t.start_date, t.title, t.room FROM talk t " \
                   "JOIN participant p ON (t.speaker_id = p.id) JOIN conference_user u " \
                   "ON (p.conference_user_id = u.id) ORDER BY t.creation_date DESC " \
                   "LIMIT %s" % (row_limit,)
        query_response = self.db_connection.execute_query(db_query)
        return QueryHelper.get_ok_response(query_response)
