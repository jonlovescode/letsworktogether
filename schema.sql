DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS groupC;
DROP TABLE IF EXISTS location;
DROP TABLE IF EXISTS groupMember;
DROP TABLE IF EXISTS Event;

CREATE TABLE groupC (
	gName VARCHAR(50) NOT NULL,
	gDescription VARCHAR(150) NOT NULL,
    PRIMARY KEY (gName)
);

CREATE TABLE location (
	lName VARCHAR(100) NOT NULL,
	lID INTEGER PRIMARY KEY NOT NULL,
	longitude VARCHAR(50) NOT NULL,
	latitude VARCHAR(50) NOT NULL
--     PRIMARY KEY (lID)
);
CREATE TABLE user (
	email VARCHAR(50) NOT NULL,
	password VARCHAR(200) NOT NULL,
	firstName VARCHAR(50) NOT NULL,
	lastName VARCHAR(50) NOT NULL,
    lID INTEGER NOT NULL,
	lastLogin timestamp default NULL,
	pChange VARCHAR(1) NOT NULL,
	PRIMARY KEY (email),
	FOREIGN KEY (lID)
		REFERENCES location (lID)
			ON DELETE CASCADE
			ON UPDATE CASCADE
);

CREATE TABLE groupMember (
	gName VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    userStatus VARCHAR(50) NOT NULL DEFAULT "Pending",
	PRIMARY KEY (gName, email),
	FOREIGN KEY (gName)
		REFERENCES groupC (gName)
			ON DELETE CASCADE
			ON UPDATE CASCADE,
	FOREIGN KEY (email)
		REFERENCES User (email)
			ON DELETE CASCADE
			ON UPDATE CASCADE
);

CREATE TABLE Event (
  	gName VARCHAR(50) NOT NULL,
    eventId INTEGER NOT NULL,
    lID INTEGER NOT NULL,
  	eventDescription VARCHAR(300) NOT NULL,
  	eventDate timestamp NOT NULL,
  	PRIMARY KEY (eventId),
      FOREIGN KEY (lID)
  		REFERENCES location (lID)
  			ON DELETE CASCADE
  			ON UPDATE CASCADE
);