CREATE DATABASE IF NOT EXISTS `The Curious Case Of Cosmetics` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `The Curious Case Of Cosmetics`;

CREATE TABLE `Member User` (
	username	VARCHAR(30)	NOT NULL,
    first_name	VARCHAR(30),
    last_name 	VARCHAR(30),
    gender		CHAR(1) CHECK (gender IN ('F', 'M')),
    `password`	VARCHAR(30)	NOT NULL,
    email		VARCHAR(50),
    PRIMARY KEY (username),
    UNIQUE (username, email));
    
CREATE TABLE `Admin User` (
	admin_username	VARCHAR(30)	NOT NULL,
    first_name		VARCHAR(30),
    last_name 		VARCHAR(30),
    gender			CHAR(1) CHECK (gender IN ('F', 'M')),
    `password`		VARCHAR(30)	NOT NULL,
    email			VARCHAR(50),
    PRIMARY KEY (admin_username),
    UNIQUE (admin_username, email));
    
CREATE TABLE Product (
	product_name		VARCHAR(150)	NOT NULL,
    brand				VARCHAR(50),
    skincare_or_makeup	VARCHAR(8) NOT NULL CHECK (skincare_or_makeup IN ('Skincare', 'Makeup')),
    average_rating		DECIMAL(3,2) CHECK (average_rating <= 5.00),
    photo				LONGBLOB,
    PRIMARY KEY (product_name),
    UNIQUE (product_name));
    
CREATE TABLE Review (
	rating			INT NOT NULL CHECK (rating <= 5),
    username		VARCHAR(30) NOT NULL,
    product_name	VARCHAR(150) NOT NULL,
    FOREIGN KEY (username) REFERENCES `Member User`(username) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (product_name) REFERENCES Product(product_name) ON DELETE CASCADE ON UPDATE CASCADE);
    
CREATE TABLE `Forum Thread` (
	thread_ID		INT NOT NULL CHECK (thread_ID > 0),
    username		VARCHAR(30) NOT NULL,
    title			VARCHAR(150) NOT NULL,
    `description`	TEXT(40000),
    PRIMARY KEY (thread_ID),
    FOREIGN KEY (username) REFERENCES `Member User`(username) ON DELETE NO ACTION ON UPDATE CASCADE,
    UNIQUE (thread_ID));
    
CREATE TABLE `Forum Reply` (
	reply_ID		INT NOT NULL CHECK (reply_ID > 0),
    thread_ID		INT NOT NULL,
    username		VARCHAR(30) NOT NULL,
    text_content	TEXT(40000) NOT NULL,
    PRIMARY KEY (reply_ID, thread_ID, username),
    FOREIGN KEY (thread_ID) REFERENCES `Forum Thread`(thread_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (username) REFERENCES `Member User`(username) ON DELETE NO ACTION ON UPDATE CASCADE);
    
CREATE TABLE Uses (
    username			VARCHAR(30) NOT NULL,
    product_name		VARCHAR(150) NOT NULL,
	`frequency_type`	VARCHAR(7) CHECK (`frequency_type` IN ('Daily', 'Weekly', 'Monthly')),
    frequency 			INT DEFAULT 1,
    CONSTRAINT check_frequency_type_match CHECK ((frequency < 31 AND `frequency_type` = 'Monthly') OR 
												(frequency < 7 AND `frequency_type` = 'Weekly') OR
												(frequency = 1 AND `frequency_type` = 'Daily')),
    specific_days 		VARCHAR(100) DEFAULT 0,
    expiry_date 		DATE,
    routine_category 	VARCHAR(5) CHECK (routine_category IN ('Day', 'Night', 'Both')) DEFAULT 'Both',
    used_date 			DATE NOT NULL,
    PRIMARY KEY (username, product_name),
    FOREIGN KEY (username) REFERENCES `Member User`(username) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (product_name) REFERENCES Product(product_name) ON DELETE CASCADE ON UPDATE CASCADE);
    
CREATE TABLE Shelves (
    username			VARCHAR(30) NOT NULL,
    product_name		VARCHAR(150) NOT NULL,
    shelved_date 		DATE NOT NULL,
    PRIMARY KEY (username, product_name),
    FOREIGN KEY (username) REFERENCES `Member User`(username) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (product_name) REFERENCES Product(product_name) ON DELETE CASCADE ON UPDATE CASCADE);
    
CREATE TABLE Wishes (
    username			VARCHAR(30) NOT NULL,
    product_name		VARCHAR(150) NOT NULL,
    wished_date 		DATE NOT NULL,
    PRIMARY KEY (username, product_name),
    FOREIGN KEY (username) REFERENCES `Member User`(username) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (product_name) REFERENCES Product(product_name) ON DELETE CASCADE ON UPDATE CASCADE);
    
    
INSERT INTO `Member User` VALUES('kx_ein', 'ke xin', 'xie', 'F', 'bleh', 'gmail');
INSERT INTO `Member User` VALUES('lyntanrambutan', 'Lyn', 'Tan', 'F', 'jeno', 'gmail.com');
INSERT INTO `Member User` VALUES('vicki', 'Vicki', 'Tan', 'F', 'bicki', 'vicki@gmail.com');
SELECT * FROM `Member User` WHERE username = 'lyntanrambutan';

INSERT INTO `Forum Thread` VALUES(1, 'kx_ein', 'TEST', null);
INSERT INTO `Forum Reply` VALUES(1, 1, 'kx_ein', 'hello');
DELETE FROM `Forum Thread` WHERE thread_ID = 1;

INSERT INTO `Product` VALUES('Auto Eyebrow Pencil', 'Innisfree', 'Makeup', 0.00, null);
INSERT INTO `Product` VALUES('Jeju Cherry Blossom Tone-up Cream', 'Innisfree', 'Skincare', 0.00, null);
INSERT INTO `Product` VALUES('Born This Way The Natural Nudes Eye Shadow Palette', 'Too Faced', 'Makeup', 0.00, null);
INSERT INTO `Product` VALUES('Play Color Eyes Rose Wine', 'Etude House', 'Makeup', 0.00, null);
INSERT INTO `Product` VALUES('Rose Deep Hydration Facial Toner', 'Fresh', 'Skincare', 0.00, null);

INSERT INTO `Review` VALUES(4, 'lyntanrambutan', 'Auto Eyebrow Pencil');
INSERT INTO `Review` VALUES(5, 'kx_ein', 'Auto Eyebrow Pencil');
INSERT INTO `Review` VALUES(5, 'lyntanrambutan', 'Jeju Cherry Blossom Tone-up Cream');
INSERT INTO `Review` VALUES(3, 'kx_ein', 'Jeju Cherry Blossom Tone-up Cream');
INSERT INTO `Review` VALUES(5, 'lyntanrambutan', 'Born This Way The Natural Nudes Eye Shadow Palette');
INSERT INTO `Review` VALUES(2, 'kx_ein', 'Born This Way The Natural Nudes Eye Shadow Palette');
INSERT INTO `Review` VALUES(5, 'lyntanrambutan', 'Play Color Eyes Rose Wine');
INSERT INTO `Review` VALUES(3, 'kx_ein', 'Play Color Eyes Rose Wine');
INSERT INTO `Review` VALUES(5, 'kx_ein', 'Rose Deep Hydration Facial Toner');
SELECT product_name, rating FROM `Review` WHERE username = 'lyntanrambutan';