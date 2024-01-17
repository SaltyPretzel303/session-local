import './style/Home.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react'
import { Explore } from './Explore';
import { Player } from './Player';
import { WithLogin } from './WIthLogin';
import User from './data_model/User';

export default function Home() {

	const [user, setUser] = useState<User | null>(null)
	const [loginDenied, setLoginDenied] = useState<boolean>(false)

	useEffect(() => {
		// TODO pretend I am reading user from ... localStorage / 
		// TODO also read if login was already denied 
	})

	return (
		<div className="Home">
			<BrowserRouter>
				<Routes>

					<Route path="/" element={
						<WithLogin showLogin={!user && !loginDenied}
							setUser={setUser}
							setLoginDenied={setLoginDenied}>

							<Explore user={user} />

						</WithLogin>
					} />

					<Route path="/watch/:streamer" element={
						<WithLogin showLogin={!user && !loginDenied}
							setUser={setUser}
							setLoginDenied={setLoginDenied}>

							<Player user={user} />

						</WithLogin>
					} />

					{/* add user profile page  */}

					{/* extract streamer with:const {streamer} userParams() */}
				</Routes>
			</BrowserRouter>
		</div>

	);
}
