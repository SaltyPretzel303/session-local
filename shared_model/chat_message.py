from dataclasses import dataclass
from enum import Enum
from typing import Union

class MsgType(Enum): 
	text = "text"
	url = "url"
	other = "other"

@dataclass
class ChatMessage: 
	sender: str
	type: MsgType
	txtContent: str
	# other type of content and I guess url to it ? 
