import { useEffect, Dispatch, useState } from "react";
import Overlay from 'react-modal'
import { signUp } from "supertokens-auth-react/lib/build/recipe/emailpassword";
import { SignInAndUp } from "supertokens-auth-react/recipe/thirdpartyemailpassword/prebuiltui"

type LoginPopupProps = {
	loginVisible: boolean
	setLoginVisible: Dispatch<boolean>
}

export default function LoginPopup(props: LoginPopupProps) {


	return (
		<Overlay
			ariaHideApp={false}
			isOpen={props.loginVisible}
			shouldCloseOnEsc={true}
			onRequestClose={() => props.setLoginVisible(false)}>

			<SignInAndUp redirectOnSessionExists={false} />

		</Overlay>

	);
}