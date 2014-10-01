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
