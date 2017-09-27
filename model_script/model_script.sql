--creating database schema

CREATE TABLE conference_user (
  id SERIAL NOT NULL,
  login VARCHAR(20) NOT NULL UNIQUE,
  password_hash CHAR(60) NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE organizer (
  id SERIAL NOT NULL,
  conference_user_id INTEGER NOT NULL UNIQUE,
  PRIMARY KEY (id)
);

CREATE TABLE participant (
  id SERIAL NOT NULL,
  conference_user_id INTEGER NOT NULL UNIQUE,
  PRIMARY KEY (id)
);

CREATE TABLE participant_friend (
  participant_id1 INTEGER NOT NULL,
  participant_id2 INTEGER NOT NULL,
  PRIMARY KEY (participant_id1, participant_id2)
);

CREATE TABLE talk_rating (
  participant_id INTEGER NOT NULL,
  talk_id INTEGER NOT NULL,
  rating INTEGER NOT NULL,
  PRIMARY KEY (participant_id, talk_id),
  CHECK (rating BETWEEN 0 AND 10)
);

CREATE TABLE talk_part (
  participant_id INTEGER NOT NULL,
  talk_id INTEGER NOT NULL,
  PRIMARY KEY (participant_id, talk_id)
);

CREATE TABLE event_reg (
  participant_id INTEGER NOT NULL,
  conference_event_id INTEGER NOT NULL,
  PRIMARY KEY (participant_id, conference_event_id)
);

CREATE TABLE talk (
  id SERIAL NOT NULL,
  name VARCHAR(20) NOT NULL UNIQUE,
  speaker_id INTEGER NOT NULL,
  title VARCHAR(255) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  room INTEGER NOT NULL,
  organizer_rating INTEGER NOT NULL,
  conference_event_id INTEGER,
  organizer_id INTEGER NOT NULL,
  creation_date TIMESTAMP NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  CHECK (room >= 0),
  CHECK (organizer_rating BETWEEN 0 AND 10)
);

CREATE TABLE talk_proposal (
  id SERIAL NOT NULL,
  name VARCHAR(20) NOT NULL UNIQUE,
  creator_id INTEGER NOT NULL,
  title VARCHAR(255) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  talk_id INTEGER UNIQUE DEFAULT NULL,
  talk_rejection_id INTEGER UNIQUE DEFAULT NULL,
  creation_date TIMESTAMP NOT NULL DEFAULT now(),
  PRIMARY KEY (id)
);

CREATE TABLE talk_rejection (
  id SERIAL NOT NULL,
  rejection_date TIMESTAMP NOT NULL DEFAULT now(),
  rejection_organizer_id INTEGER NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE conference_event (
  id SERIAL NOT NULL,
  name VARCHAR(255) NOT NULL UNIQUE,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  organizer_id INTEGER NOT NULL,
  PRIMARY KEY (id)
);

--adding foreign key constraints

ALTER TABLE organizer
ADD CONSTRAINT organizer_conference_user_id_fk FOREIGN KEY (conference_user_id)
REFERENCES conference_user (id) ON DELETE CASCADE;

ALTER TABLE participant
ADD CONSTRAINT participant_conference_user_id_fk FOREIGN KEY (conference_user_id)
REFERENCES conference_user (id) ON DELETE CASCADE;

ALTER TABLE participant_friend
ADD CONSTRAINT participant_friend_id1_fk FOREIGN KEY (participant_id1)
REFERENCES participant (id) ON DELETE CASCADE;

ALTER TABLE participant_friend
ADD CONSTRAINT participant_friend_id2_fk FOREIGN KEY (participant_id2)
REFERENCES participant (id) ON DELETE CASCADE;

ALTER TABLE talk_rating
ADD CONSTRAINT talk_rating_talk_id_fk FOREIGN KEY (talk_id)
REFERENCES talk (id) ON DELETE CASCADE;

ALTER TABLE talk_rating
ADD CONSTRAINT talk_rating_participant_id_fk FOREIGN KEY (participant_id)
REFERENCES participant (id) ON DELETE CASCADE;

ALTER TABLE talk_part
ADD CONSTRAINT talk_part_talk_id_fk FOREIGN KEY (talk_id)
REFERENCES talk (id) ON DELETE CASCADE;

ALTER TABLE talk_part
ADD CONSTRAINT talk_part_participant_id_fk FOREIGN KEY (participant_id)
REFERENCES participant (id) ON DELETE CASCADE;

ALTER TABLE event_reg
ADD CONSTRAINT event_reg_conference_event_id_fk FOREIGN KEY (conference_event_id)
REFERENCES conference_event (id) ON DELETE CASCADE;

ALTER TABLE event_reg
ADD CONSTRAINT event_reg_participant_id_fk FOREIGN KEY (participant_id)
REFERENCES participant (id) ON DELETE CASCADE;

ALTER TABLE talk
ADD CONSTRAINT talk_speaker_id_fk FOREIGN KEY (speaker_id)
REFERENCES participant (id) ON DELETE CASCADE;

ALTER TABLE talk
ADD CONSTRAINT talk_conference_event_id_fk FOREIGN KEY (conference_event_id)
REFERENCES conference_event (id) ON DELETE CASCADE;

ALTER TABLE talk
ADD CONSTRAINT talk_organizer_id_fk FOREIGN KEY (organizer_id)
REFERENCES organizer (id) ON DELETE CASCADE;

ALTER TABLE conference_event
ADD CONSTRAINT conference_event_organizer_id_fk FOREIGN KEY (organizer_id)
REFERENCES organizer (id) ON DELETE CASCADE;

ALTER TABLE talk_proposal
ADD CONSTRAINT talk_proposal_creator_id_fk FOREIGN KEY (creator_id)
REFERENCES participant (id) ON DELETE CASCADE;

ALTER TABLE talk_proposal
ADD CONSTRAINT talk_proposal_talk_id_fk FOREIGN KEY (talk_id)
REFERENCES talk (id) ON DELETE CASCADE;

ALTER TABLE talk_proposal
ADD CONSTRAINT talk_proposal_talk_rejection_id_fk FOREIGN KEY (talk_rejection_id)
REFERENCES talk_rejection (id) ON DELETE CASCADE;

ALTER TABLE talk_rejection
ADD CONSTRAINT talk_rejection_organizer_id_fk FOREIGN KEY (rejection_organizer_id)
REFERENCES organizer (id) ON DELETE CASCADE;

-- Creating indexes

CREATE INDEX talk_start_date ON talk (start_date);
CREATE INDEX talk_creation_date ON talk (creation_date);
CREATE INDEX talk_proposal_creator_id ON talk_proposal (creator_id);

-- creating views

CREATE VIEW participant_bilatelar_friend AS
SELECT * FROM participant_friend WHERE
  (participant_id2, participant_id1) IN
    (SELECT * FROM participant_friend);

--creating functions and triggers

CREATE FUNCTION ensure_talk_proposal_status()
RETURNS TRIGGER AS
$$
  BEGIN
    IF NEW.talk_id IS NOT NULL AND NEW.talk_rejection_id IS NOT NULL THEN
      RAISE EXCEPTION 'Invalid talk proposal status';
    END IF;
    IF TG_OP <> 'UPDATE' THEN
      RETURN NEW;
    END IF;
    IF OLD.talk_id IS NOT NULL AND NEW.talk_id <> OLD.talk_id THEN
      RAISE EXCEPTION 'Proposal status cannot be changed';
    END IF;
    IF OLD.talk_rejection_id IS NOT NULL AND NEW.talk_rejection_id <> OLD.talk_rejection_id THEN
      RAISE EXCEPTION 'Proposal status cannot be changed';
    END IF;
    RETURN NEW;
  END;
$$ LANGUAGE PLpgSQL SECURITY DEFINER;

CREATE TRIGGER ensure_talk_proposal_status BEFORE INSERT OR UPDATE ON talk_proposal
FOR EACH ROW EXECUTE PROCEDURE ensure_talk_proposal_status();

CREATE FUNCTION ensure_correct_friendship()
RETURNS TRIGGER AS
$$
  BEGIN
    IF NEW.participant_id1 = NEW.participant_id2 THEN
      RAISE EXCEPTION 'Participant cannot be friend with yourself';
    END IF;
    RETURN NEW;
  END;
$$ LANGUAGE PLpgSQL SECURITY DEFINER;

CREATE TRIGGER ensure_correct_friendship BEFORE INSERT OR UPDATE ON participant_friend
FOR EACH ROW EXECUTE PROCEDURE ensure_correct_friendship();

CREATE FUNCTION add_organizer(user_login VARCHAR(255), pass_hash CHAR(128))
RETURNS VOID AS
$$
  DECLARE
    user_id INTEGER;
  BEGIN
    INSERT INTO conference_user (login, password_hash)
      VALUES (user_login, pass_hash) RETURNING id INTO user_id;
    INSERT INTO organizer (conference_user_id) VALUES (user_id);
  END;
$$ LANGUAGE PLpgSQL SECURITY DEFINER;

CREATE FUNCTION add_participant(user_login VARCHAR(255), pass_hash CHAR(128))
RETURNS VOID AS
$$
  DECLARE
    user_id INTEGER;
  BEGIN
    INSERT INTO conference_user (login, password_hash)
      VALUES (user_login, pass_hash) RETURNING id INTO user_id;
    INSERT INTO participant (conference_user_id) VALUES (user_id);
  END;
$$ LANGUAGE PLpgSQL SECURITY DEFINER;

CREATE FUNCTION remove_organizer(organizer_id INTEGER)
RETURNS VOID AS
$$
  BEGIN
    DELETE FROM conference_user WHERE id IN
      (SELECT conference_user_id FROM organizer WHERE id = organizer_id);
    DELETE FROM organizer WHERE id = organizer_id;
  END;
$$ LANGUAGE PLpgSQL SECURITY DEFINER;

CREATE FUNCTION remove_participant(participant_id INTEGER)
RETURNS VOID AS
$$
  BEGIN
    DELETE FROM conference_user WHERE id IN
      (SELECT conference_user_id FROM participant WHERE id = participant_id);
    DELETE FROM participant WHERE id = participant_id;
  END;
$$ LANGUAGE PLpgSQL SECURITY DEFINER;

CREATE FUNCTION reject_talk_proposal(prop_id INTEGER, rej_date TIMESTAMP, org_id INTEGER)
RETURNS VOID AS
$$
  DECLARE
    added_rejection_id INTEGER;
  BEGIN
    INSERT INTO talk_rejection (rejection_date, rejection_organizer_id)
      VALUES (rej_date, org_id) RETURNING id INTO added_rejection_id;
    UPDATE talk_proposal SET talk_rejection_id = added_rejection_id
      WHERE id = prop_id;
  END;
$$ LANGUAGE PLpgSQL SECURITY DEFINER;

CREATE FUNCTION confirm_talk_proposal(prop_id INTEGER, added_talk_id INTEGER)
RETURNS VOID AS
$$
  BEGIN
    UPDATE talk_proposal SET talk_id = added_talk_id WHERE id = prop_id;
  END;
$$ LANGUAGE PLpgSQL SECURITY DEFINER;

-- setting grants for application user

GRANT SELECT, UPDATE ON conference_user TO application_user;
GRANT SELECT ON SEQUENCE conference_user_id_seq TO application_user;
GRANT SELECT, UPDATE ON organizer TO application_user;
GRANT SELECT ON SEQUENCE organizer_id_seq TO application_user;
GRANT SELECT, UPDATE ON participant TO application_user;
GRANT SELECT ON SEQUENCE participant_id_seq TO application_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON participant_friend TO application_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON talk_rating TO application_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON talk_part TO application_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON event_reg TO application_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON talk TO application_user;
GRANT SELECT, USAGE ON SEQUENCE talk_id_seq TO application_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON talk_proposal TO application_user;
GRANT SELECT, USAGE ON SEQUENCE talk_proposal_id_seq TO application_user;
GRANT SELECT, UPDATE ON talk_rejection TO application_user;
GRANT SELECT ON SEQUENCE talk_rejection_id_seq TO application_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON conference_event TO application_user;
GRANT SELECT, USAGE ON SEQUENCE conference_event_id_seq TO application_user;
GRANT SELECT ON participant_bilatelar_friend TO application_user;
GRANT EXECUTE ON FUNCTION add_organizer(VARCHAR(255), CHAR(128)) TO application_user;
GRANT EXECUTE ON FUNCTION add_participant(VARCHAR(255), CHAR(128)) TO application_user;
GRANT EXECUTE ON FUNCTION reject_talk_proposal(INTEGER, TIMESTAMP, INTEGER) TO application_user;
GRANT EXECUTE ON FUNCTION confirm_talk_proposal(INTEGER, INTEGER) TO application_user;
