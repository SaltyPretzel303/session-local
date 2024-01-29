export default function doRequest(url: string = "http://localhost:10000/live/user_0_subsd/index.m3u8") {

	console.log(`Doing send cookie request at: ${url}`)

	fetch(url,
		{
			method: "GET",
			credentials: "include"
			// credentials: "same-origin"
		})
		.then(res => {
			if (res.status != 200) {
				console.log("Send cookie request failed.")
			} else {
				console.log("Send cookie request successfull.")
			}
		})
		.catch(err => {
			console.log("Err in send cookie request.")
			console.log(err)
		})

}
