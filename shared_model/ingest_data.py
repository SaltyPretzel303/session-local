from dataclasses import dataclass

@dataclass
class IngestData:
	ip : str
	port: int
	ingest_path: str
	health_check_path: str
	streams_cnt: int
	max_streams: int	

	def form_id(self):
		return f"{self.ip}:{self.port}"