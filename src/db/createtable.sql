CREATE TABLE `BucketList`.`tbl_user` (
  `player_id` VARCHAR(20) NOT NULL,
  `email` NVARCHAR(320) NOT NULL,
  `password` VARCHAR(64) NOT NULL,
  `mfa_key` CHAR(32),
  `timestamp` DATETIME DEFAULT LOCALTIME(),
  `login_counter` TINYINT DEFAULT 0,
  `verified` BOOLEAN NOT NULL DEFAULT FALSE,
  `total_points` INT DEFAULT 0,
  `session_id` CHAR(6),
  PRIMARY KEY (`player_id`));


