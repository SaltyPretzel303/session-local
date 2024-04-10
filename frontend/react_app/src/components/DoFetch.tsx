export default function DoFetch() {

	async function doFetch() {
		let url = 'http://session.com/user/fetch'
		// let url = "http://cdn.session.com/live/streamer-0_subsd/index.m3u8"
		// let url = "http://172.19.0.10/live/streamer-0_subsd/index.m3u8"
		// let url = "http://session.com/live/streamer-0_subsd/index.m3u8"
		// let url = "http://some.domain.com/live/streamer-0_subsd/index.m3u8"

		try {
			let res = await fetch(url)

			if (res && res.status != 200) {
				throw Error("non 200: " + res.status + "mess: " + await res.text())
			}

			console.log("SUCCESS for: " + url)
			console.log(res.headers)

		} catch (e) {
			console.log("FAILED for: " + url)
			console.log("reason: " + e)
		}
	}

	return (
		<div>
			<button onClick={doFetch}>Click to fetch</button>
		</div>
	)
}