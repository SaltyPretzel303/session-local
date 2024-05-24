import Overlay from 'react-modal'
import { SignInAndUp } from "supertokens-auth-react/recipe/emailpassword/prebuiltui"


export default function LoginPopup({
	loginVisible,
	setLoginVisible,
	forcedLogin
}: {
	loginVisible: boolean
	setLoginVisible: React.Dispatch<boolean>
	forcedLogin: boolean
}) {
	return (
		<Overlay
			ariaHideApp={false}
			isOpen={loginVisible}
			shouldCloseOnEsc={!forcedLogin}
			onRequestClose={() => setLoginVisible(false)}>

			<SignInAndUp redirectOnSessionExists={false} />
		</Overlay>

	);
}