--creating database schema

CREATE TABLE conference_user (
  id INTEGER NOT NULL,
  login VARCHAR(20) NOT NULL UNIQUE,
  password_hash CHAR(60) NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE organizer (
  id INTEGER NOT NULL,
  conference_user_id INTEGER NOT NULL UNIQUE,
  PRIMARY KEY (id)
);

CREATE TABLE participant (
  id INTEGER NOT NULL,
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
  id INTEGER NOT NULL,
  name VARCHAR(20) NOT NULL UNIQUE,
  speaker_id INTEGER NOT NULL,
  title VARCHAR(255) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  room INTEGER NOT NULL,
  organizer_rating INTEGER NOT NULL,
  conference_event_id INTEGER,
  organizer_id INTEGER NOT NULL,
  creation_date TIMESTAMP NOT NULL DEFAULT now,
  PRIMARY KEY (id),
  CHECK (room >= 0),
  CHECK (organizer_rating BETWEEN 0 AND 10)
);

CREATE TABLE talk_proposal (
  id INTEGER NOT NULL,
  name VARCHAR(20) NOT NULL UNIQUE,
  creator_id INTEGER NOT NULL,
  title VARCHAR(255) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  talk_id INTEGER UNIQUE DEFAULT NULL,
  talk_rejection_id INTEGER UNIQUE DEFAULT NULL,
  creation_date TIMESTAMP NOT NULL DEFAULT now,
  PRIMARY KEY (id)
);

CREATE TABLE talk_rejection (
  id INTEGER NOT NULL,
  rejection_date TIMESTAMP NOT NULL DEFAULT now,
  rejection_organizer_id INTEGER NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE conference_event (
  id INTEGER NOT NULL,
  name VARCHAR(255) NOT NULL UNIQUE,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  organizer_id INTEGER NOT NULL,
  PRIMARY KEY (id)
);

-- Creating indexes

CREATE INDEX talk_start_date ON talk (start_date);
CREATE INDEX talk_creation_date ON talk (creation_date);
CREATE INDEX talk_proposal_creator_id ON talk_proposal (creator_id);

-- creating views

CREATE VIEW participant_bilatelar_friend AS
SELECT * FROM participant_friend WHERE
  (participant_id2, participant_id1) IN
    (SELECT * FROM participant_friend);
