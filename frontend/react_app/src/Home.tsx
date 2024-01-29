import './style/Home.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react'
import { Explore } from './Explore';
import { Player } from './Player';
import { WithLogin } from './WIthLogin';
import User from './data_model/User';
import { HlsPlayer } from './components/HlsPlayer';
import QuickPlay from './QuickPlay';

export default function Home() {

	const [user, setUser] = useState<User | null>(null)
	const [loginDenied, setLoginDenied] = useState<boolean>(false)

	// useEffect(() => {
	// 	// TODO pretend I am reading user from ... localStorage / 
	// 	// TODO also read if login was already denied 
	// })

	return (

		<div className="Home">
			<QuickPlay/>
		</div>

	);
}
