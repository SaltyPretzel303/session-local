import './Chat.css'

export default function Chat({ visible }: { visible: boolean }) {

	// TODO do some websocket connection with the backend ... ? 
	// or directly to message 'provider' some broker or something similar ... 

	return (
		<div className="Chat" hidden={!visible}>
			<div className="MsgContainer" >
				<p className="SingleMessage">this is message</p>
			</div>
			<input className="ChatMsgInput" type="text" />
		</div>
	);
};