DROP DATABASE IF EXISTS WhatDoIDo;
CREATE DATABASE WhatDoIDo;
SET storage_engine = INNODB;
Use WhatDoIDo;

CREATE TABLE Users
(
    user_id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    username varchar(100) BINARY UNIQUE NOT NULL,
    email varchar(100) UNIQUE NOT NULL,
    password char(100) NOT NULL, -- truncate passwords at 100 characters
    salt char(36) NOT NULL -- From what I can tell, salts are just GUIDs which should be 32 meaningful characters
);

CREATE TABLE User_Sessions
(
    user_id int,
    session_token varchar(100),
    CONSTRAINT PRIMARY KEY (user_id, session_token),
    CONSTRAINT FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Locations
(
    location_id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    latitude FLOAT,
    longitude FLOAT,
    address VARCHAR(1000),
    place VARCHAR(1000)
);

CREATE TABLE Users_Locations
(
    user_id int,
    location_id int,
    time DATETIME,
    is_Route BOOLEAN,
    CONSTRAINT FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT FOREIGN KEY (location_id) REFERENCES Locations(location_id) ON DELETE CASCADE,
    CONSTRAINT PRIMARY KEY (user_id, location_id, time)
);

CREATE TABLE Events
(
    event_id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    event_type VARCHAR(30),
    user_id int,
    location_id int,
    name VARCHAR(100),
    locked BOOLEAN,
    deleted BOOLEAN,
    CONSTRAINT FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT FOREIGN KEY (location_id) REFERENCES Locations(location_id) ON DELETE CASCADE
);

CREATE TABLE Cyclical_Events
(
    cyclical_event_id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    event_id int,
    cycle_type ENUM("daily", "weekly", "monthly"),
    occurances VARCHAR(10000),
    CONSTRAINT FOREIGN KEY (event_id) REFERENCES Events(event_id) ON DELETE CASCADE
);

CREATE TABLE Spanning_Events
(
    spanning_event_id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    event_id int,
    min_time_between DATETIME,
    range_of_span DATETIME,
    avg_length_of_event DATETIME,
    CONSTRAINT FOREIGN KEY (event_id) REFERENCES Events(event_id) ON DELETE CASCADE
);

INSERT INTO `Users` (`user_id`, `username`, `emquitail`, `password`, `salt`) 
VALUES ('1', 'mobile', 'mobile@summary.com', SHA1(CONCAT('mobile', 'bec7f06710081143365387b79aeb59ad')), 'bec7f06710081143365387b79aeb59ad');