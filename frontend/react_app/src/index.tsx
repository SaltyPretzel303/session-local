import React from 'react';
import ReactDOM from 'react-dom/client';
import './style/index.css';
import Home from './Home';

import SuperTokens from "supertokens-auth-react";
import EmailPassword, { OnHandleEventContext } from 'supertokens-auth-react/recipe/emailpassword'
import Session from 'supertokens-auth-react/recipe/session'

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

root.render(
	// <React.StrictMode>
	<Home />
	// </React.StrictMode>
);
