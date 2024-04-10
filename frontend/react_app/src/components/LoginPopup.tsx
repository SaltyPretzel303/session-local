import Overlay from 'react-modal'
import { SignInAndUp } from "supertokens-auth-react/recipe/emailpassword/prebuiltui"

type LoginPopupProps = {
	loginVisible: boolean
	setLoginVisible: React.Dispatch<boolean>
	forcedLogin: boolean
}

export default function LoginPopup(props: LoginPopupProps) {
	return (
		<Overlay
			ariaHideApp={false}
			isOpen={props.loginVisible}
			shouldCloseOnEsc={!props.forcedLogin}
			onRequestClose={() => props.setLoginVisible(false)}>

			<SignInAndUp redirectOnSessionExists={false} />
		</Overlay>

	);
}