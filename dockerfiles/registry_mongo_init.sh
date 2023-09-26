#!/bin/bash

USERNAME="registry_user"
PASSWORD="registry_password"
COLLECTION="streams"

echo "Creating user: "
echo "User: $USERNAME"
echo "Password: $PASSWORD"
echo "Colllection: $COLLECTION"

# export USERNAME
# export PASSWORD
# export COLLECTION

mongosh localhost:27017/$COLLECTION --eval 'db.createUser({user: "'$USERNAME'", pwd: "'$PASSWORD'", roles:[{role:"readWrite", db: "'$COLLECTION'"}] })'