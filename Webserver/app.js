const express = require('express')
const fs = require('fs')
const PORT = process.env.PORT || 3000
const app = express()

app.set('view engine', 'ejs')
app.set('views', __dirname + '/views')

app.use(express.static(__dirname + "/public"))
app.use(express.json())
app.use(express.urlencoded())

app.get('/', (req, res) => {
    let server_id = req.query.server_id || get_server_id()[0]
    let channel_id = req.query.channel_id || get_channels(server_id)[0].id
    let messages = get_messages(server_id, channel_id)
    let servers = get_servers()

    let results = []
    let default_image = "https://www.freepnglogos.com/uploads/discord-logo-png/concours-discord-cartes-voeux-fortnite-france-6.png"
    Object.keys(servers).forEach((key) => {
        results.push({server_name: servers[key]["server_name"], server_image: servers[key]["server_image"] || default_image, server_id: key, channels: servers[key]["channels"]})
    })
    res.render('pages/index', {channel_id: channel_id, server_id: server_id, results: results, messages: messages})
})

app.get('/server/:id', (req, res) => {
    res.redirect("/?channel_id=" + get_channels(req.params.id)[0].id)
})

app.get('/channel/:server_id/:channel_id', (req, res) => {
    let channel_id = req.params.channel_id
    let server_id = req.params.server_id
    res.redirect(`/?channel_id=${channel_id}&server_id=${server_id}`)
})

app.post("/send_message", (req, res) => {
    send_message(req.body.server_id, req.body.channel_id, req.body.message)
    console.log("Sent to channel " + req.body.channel_id)
    res.redirect(`/?channel_id=${req.body.channel_id}&server_id=${req.body.server_id}`)
})

app.listen(PORT, () => {
    console.log(`Example app listening on port ${PORT}`)
})

function get_channels(server_id){
    let servers = JSON.parse(fs.readFileSync("../interface/servers.json", 'utf8'))
    // Structure Server list > channel list > channel dict > - name / - id
    if (server_id == 0){
        return servers[Object.keys(servers)[0]]["channels"]
    }
    return servers[server_id]["channels"]
}

function get_server_id(){
    let servers = JSON.parse(fs.readFileSync("../interface/servers.json", 'utf8'))
    return Object.keys(servers)
}

function get_servers(){
    return JSON.parse(fs.readFileSync("../interface/servers.json", 'utf8'))
}

function get_messages(server_id, channel_id){
    let messages = JSON.parse(fs.readFileSync("../interface/messages.json", 'utf8'))
    // Structure Server > channel > list of messages
    return messages[server_id][channel_id]
}

function send_message(server_id, channel_id, message){
    let to_send_path = "../interface/to_send.json"
    let newMessage = {server_id: server_id,
                      channel_id: channel_id,
                      message: message}
    fs.readFile(to_send_path, function (err, data) {
        let json = JSON.parse(data)
        json.push(newMessage)
  
        fs.writeFile(to_send_path, JSON.stringify(json), function(err, result) {
          if(err) console.log('error', err)})
    })
}