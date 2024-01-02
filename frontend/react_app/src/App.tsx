import './App.css';
import HlsPlayer from './HlsPlayer';
import Chat from './Chat';
import LoginPopup from './LoginPopup';

export default function App() {



	return (
		<div className="App">
			{/* <div className="VideoContainer">
				<HlsPlayer src={"http://localhost:10000/live/streamer_hd/index.m3u8"} />
			</div>

			<Chat visible={true}></Chat> */}

			<LoginPopup/>

		</div>

	);
}

// export default App;
