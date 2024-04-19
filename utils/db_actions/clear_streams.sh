docker exec registry-db.session.com mongosh mongodb://localhost/streams --eval 'db.stream_data.remove({})'
