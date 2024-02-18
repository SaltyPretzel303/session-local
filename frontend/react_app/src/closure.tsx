import { useState } from "react"

type formState = {
	stateName: string
	clickHandler: () => void
}


function SomeForm() {

	const regularStateName = "regularState"
	const specialStateName = "specialState"

	const regularState: formState = {
		stateName: regularStateName,
		clickHandler: regularClickHandler
	}

	const specialState: formState = {
		stateName: specialStateName,
		clickHandler: specialClickHandler
	}

	const [formState, setFormState] = useState(regularState)

	const [userInput, setUserInput] = useState("")

	function mainClickHandler() {
		formState.clickHandler()
	}

	function regularClickHandler() {
		console.log("RegularClick")
		console.log("User input: " + userInput)
	}

	function specialClickHandler() {
		console.log("SpecialClick")
		console.log("User input: " + userInput)
	}

	function switchState() {
		if (formState.stateName == regularStateName) {
			setFormState(specialState)
		} else {
			setFormState(regularState)
		}

	}

	return (
		<div>
			<button onClick={switchState}>SwitchState</button>
			<input onChange={(e) => setUserInput(e.target.value)} />
			<button onClick={mainClickHandler}>ClickMe</button>
		</div>
	)
}