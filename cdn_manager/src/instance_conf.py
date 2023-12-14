from dataclasses import dataclass


@dataclass
class InstanceConf:
	ip: str
	hls_port: int
	hc_port: int
	hls_path: str
	hc_path: str
