const path = require('path')
const express = require('express')
const favicon = require('serve-favicon')
const app = express()

app.use(express.static('client_build'));
app.use(favicon(path.join(__dirname, "client_build", "favicon.ico")))

app.get("*", (req, res) => {
	// Not sure what this is ...
	res.sendFile(path.resolve(__dirname, 'client_build', 'index.html'))
});

port = process.env.PORT
if (!port) {
	console.log("Will use default port.")
	port = 80 // default value 
}
app.listen(port, () => {
	console.log("Server started on port: " + port)
})