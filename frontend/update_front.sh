#!/bin/bash 

# Will update only the content of the src dir. 
docker cp ./react_app/src frontend.session.com:/app/react_app

# This one will copy all the files except nodes_modules and git stuff,
# usefull when files in the project root are mofied as well. 
# ls -A react_app/ | grep -vE 'node|git' | xargs -I {} docker cp react_app/{} frontend.session.com:/app/react_app
