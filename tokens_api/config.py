from dataclasses import dataclass

@dataclass
class Config:
	domain_name: str
	users_db_conn_string: str
	stream_key_len: int
	stream_key_longevity: int # In seconds
	username_field: str
	view_update_url: str

DOMAIN = 'session.com'

config = Config(
		domain_name="session.com",
		users_db_conn_string=f"mongodb://session_user:session_pwd@users-db.{DOMAIN}:27017/session_auth",
		stream_key_len=10,
		stream_key_longevity=20,
		username_field="username",
		view_update_url=f'http://stream-registry.{DOMAIN}/continue_view'
		)

