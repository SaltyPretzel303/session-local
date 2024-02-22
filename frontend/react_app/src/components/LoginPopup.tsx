import Overlay from 'react-modal'
import { SuperTokensWrapper } from 'supertokens-auth-react'
import { EmailPasswordComponentsOverrideProvider } from 'supertokens-auth-react/recipe/emailpassword'
import { SignInAndUp } from "supertokens-auth-react/recipe/emailpassword/prebuiltui"

type LoginPopupProps = {
	loginVisible: boolean
	setLoginVisible: React.Dispatch<boolean>
}

export default function LoginPopup(props: LoginPopupProps) {
	// export default function LoginPopup() {

	return (
		<Overlay
			ariaHideApp={false}
			isOpen={props.loginVisible}
			shouldCloseOnEsc={true}
			onRequestClose={() => props.setLoginVisible(false)}>

			{/* This is purely cosmetical, for new functionalities, including 
			custom form fields goto init method, recipeList, chosenRecipe.init */}

			{/* <EmailPasswordComponentsOverrideProvider
				components={{
					EmailPasswordSignInForm_Override: ({ DefaultComponent, ...props }) => {
						return (
							<div>
								<div style={{
									display: "flex",
									flexDirection: "column",
									justifyContent: "center",
									alignItems: "left",
									alignContent: "left",
									textAlign: "left",
								}}>
									<label>Username</label>
									<input placeholder='username'></input>
								</div>
								<DefaultComponent {...props} />
							</div>)
					},
					EmailPasswordSignIn_Override: ({ DefaultComponent, ...props }) => {
						return (
							<div>
								<div>Heloo there</div>
								<DefaultComponent {...props} />
							</div>
						)
					}
				}}>

				<SignInAndUp redirectOnSessionExists={false} />
			</EmailPasswordComponentsOverrideProvider> */}

			<SignInAndUp redirectOnSessionExists={false} />

		</Overlay>

	);
}