CREATE USER IF NOT EXISTS 'mysql.infoschema'@'localhost' IDENTIFIED BY '12030919Wjm';
GRANT ALL PRIVILEGES ON *.* TO 'mysql.infoschema'@'localhost';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
