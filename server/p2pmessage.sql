--
-- 由SQLiteStudio v3.2.1 产生的文件 周四 11月 15 23:50:20 2018
--
-- 文本编码：UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- 表：CONTACTS
CREATE TABLE CONTACTS (
    id         INTEGER REFERENCES USER (id),
    contact_id INTEGER REFERENCES USER (id) 
);


-- 表：MESSAGE
CREATE TABLE MESSAGE (
    id          INTEGER UNIQUE
                        PRIMARY KEY ASC AUTOINCREMENT,
    from_userid INTEGER REFERENCES USER (id) 
                        NOT NULL,
    to_userid   INTEGER REFERENCES USER (id) 
                        NOT NULL,
    status      INT     DEFAULT (1),
    content     TEXT,
    ts          INTEGER
);


-- 表：USER
CREATE TABLE USER (
    id          INTEGER      PRIMARY KEY ASC AUTOINCREMENT
                             UNIQUE
                             NOT NULL,
    name        TEXT (50)    NOT NULL
                             UNIQUE,
    address     TEXT (10),
    avatar      CHAR (50)    DEFAULT default_avatar,
    email       CHAR (20),
    password    VARCHAR (20) NOT NULL,
    last_online INTEGER,
    status      INTEGER
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
