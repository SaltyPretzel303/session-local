#!/bin/bash

USERNAME="session_user"
PASSWORD="session_pwd"
DB_NAME="session_auth"

echo "Creating user: "
echo "User: $USERNAME"
echo "Password: $PASSWORD"
echo "Db_name: $DB_NAME"

mongosh localhost:27017/$DB_NAME --eval 'db.createUser({user: "'$USERNAME'", pwd: "'$PASSWORD'",roles:[{role:"readWrite", db: "'$DB_NAME'"}] })'