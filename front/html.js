let express = require('express');
let app = express();
let http = require('http').createServer(app);
app.use(express.static(__dirname));

app.get('/', (req, res) => {
 
    res.sendFile(__dirname + '/auth.html');
 
});
http.listen(3000, () => {
    console.log('listening on *:3000');
});