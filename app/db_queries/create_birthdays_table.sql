CREATE TABLE Birthdays (
	user_id VARCHAR(255) NOT NULL,
	username VARCHAR(255) NOT NULL,
	birthday DATE NOT NULL,
	server_id VARCHAR(255) NOT NULL,
	FOREIGN KEY(server_id) REFERENCES Servers(server_id)
);