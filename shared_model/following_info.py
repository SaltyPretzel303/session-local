from dataclasses import dataclass
from datetime import datetime
from typing import List

from shared_model.user import User

@dataclass
class FollowingInfo: 
	username: str
	following: str
	from_date: datetime