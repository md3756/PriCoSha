CHANGED

-- Creating tables

CREATE TABLE Person(
    email VARCHAR(20), 
    password CHAR(64), 
    fname VARCHAR(20),
    lname VARCHAR(20),
    PRIMARY KEY (email)
);

CREATE TABLE Friendgroup(
    owner_email VARCHAR(20), 
    fg_name VARCHAR(20), 
    description VARCHAR(1000), 
    PRIMARY KEY (owner_email, fg_name),
    FOREIGN KEY (owner_email) REFERENCES Person(email)
);

-- added status --
CREATE TABLE Belong (
    email VARCHAR(20), 
    owner_email VARCHAR(20),
    fg_name VARCHAR(20),
    status VARCHAR(20),
    PRIMARY KEY (email, owner_email, fg_name),
    FOREIGN KEY(email) REFERENCES Person(email),
    FOREIGN KEY(owner_email, fg_name) REFERENCES  Friendgroup(owner_email, fg_name)
);

CREATE TABLE ContentItem(
    item_id int AUTO_INCREMENT, 
    email_post VARCHAR(20),
    post_time Timestamp, 
    file_path VARCHAR(100), 
    item_name VARCHAR(20), 
    is_pub Boolean, 
    PRIMARY KEY(item_id),
    FOREIGN KEY(email_post) REFERENCES Person(email)
);

CREATE TABLE Rate (
    email VARCHAR(20), 
    item_id int, 
    rate_time Timestamp, 
    emoji VARCHAR(20) CHARACTER SET utf8mb4,
    PRIMARY KEY(email, item_id), 
    FOREIGN KEY(email) REFERENCES Person(email),
        FOREIGN KEY(item_id)REFERENCES ContentItem(item_id)
);        

CREATE TABLE Share ( 
    owner_email VARCHAR(20), 
    fg_name VARCHAR(20), 
    item_id int, 
    PRIMARY KEY(owner_email, fg_name, item_id),
    FOREIGN KEY(owner_email, fg_name) REFERENCES Friendgroup(owner_email, fg_name),                  
    FOREIGN KEY (item_id) REFERENCES ContentItem(item_id)
);

CREATE TABLE Tag (
    email_tagged VARCHAR(20), 
    email_tagger VARCHAR(20), 
    item_id int,
    status VARCHAR(20),
    tagtime Timestamp,
    PRIMARY KEY(email_tagged, email_tagger, item_id),
    FOREIGN KEY(email_tagged) REFERENCES Person(email),
    FOREIGN KEY(email_tagger) REFERENCES Person(email),
    FOREIGN KEY(item_id) REFERENCES ContentItem(item_id)
);


-- add comment table --
CREATE TABLE Comments (
    email VARCHAR(20), 
    item_id int, 
    comment_time Timestamp, 
    comment VARCHAR(140),
    PRIMARY KEY(email, item_id), 
    FOREIGN KEY(email) REFERENCES Person(email),
    FOREIGN KEY(item_id)REFERENCES ContentItem(item_id)
);




