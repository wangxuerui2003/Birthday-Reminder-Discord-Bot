CREATE TABLE Birthdays (
	user_id VARCHAR(255) NOT NULL,
	username VARCHAR(255) NOT NULL,
	birthday DATE NOT NULL,
	server_id INT NOT NULL,
	PRIMARY KEY(user_id),
	FOREIGN KEY(server_id) REFERENCES Servers(server_id)
);