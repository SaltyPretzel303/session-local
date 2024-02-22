from dataclasses import dataclass

@dataclass
class Config:
	users_db_conn_string: str
	stream_key_len: int
	stream_key_longevity: int # In seconds
	username_field: str

config = Config(
		users_db_conn_string="mongodb://session_user:session_pwd@users-db.session:27017/session_auth",
		stream_key_len=10,
		stream_key_longevity=20,
		username_field="username"
		)

