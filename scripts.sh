docker run --name tuxon-test-database -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root mysql 
docker run --name myadmin -d --link tuxon-test-database:db -p 8080:80 phpmyadmin 
