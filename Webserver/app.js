const express = require('express')
const fs = require('fs')
const PORT = process.env.PORT || 3000
const app = express()

app.set('view engine', 'ejs')
app.set('views', __dirname + '/views')

app.use(express.static(__dirname + "/public"))
app.use(express.json())
app.use(express.urlencoded())

app.get('/', async (req, res) => {
    let servers = get_servers()
    let server_id = req.query.server_id || servers[0]
    let channels = await get_channels(server_id)
    let channel_id = req.query.channel_id || Object.keys(await channels[1])[0]
    let messages = await get_messages(channel_id)

    let results = []
    let default_image = "https://www.freepnglogos.com/uploads/discord-logo-png/concours-discord-cartes-voeux-fortnite-france-6.png"
    for (server_id_scope of servers) {
        let channels = await get_channels(server_id_scope)
            results.push(
                {   
                    server_name: get_server_name(server_id_scope) || "undefined",
                    server_image: get_server_image(server_id_scope) || default_image,
                    server_id: server_id, channels: channels[1]
                }
                )
    }
    res.render('pages/index', {channel_id: channel_id, server_id: server_id, results: results, messages: await messages})
})

app.get('/server/:id', (req, res) => {
    res.redirect(`/?channel_id=${get_channels(req.params.id)[0]}&server_id=${req.params.id}`)
})

app.get('/channel/:server_id/:channel_id', (req, res) => {
    let channel_id = req.params.channel_id
    let server_id = req.params.server_id
    res.redirect(`/?channel_id=${channel_id}&server_id=${server_id}`)
})

app.post("/send_message", (req, res) => {
    send_message(req.body.channel_id, req.body.message)
    console.log("Sent to channel " + req.body.channel_id)
    res.redirect(`/?channel_id=${req.body.channel_id}&server_id=${req.body.server_id}`)
})

app.listen(PORT, () => {
    console.log(`Example app listening on port ${PORT}`)
})

function get_servers(){
    return JSON.parse(fs.readFileSync("../interface/servers.json", 'utf8'))
}

/*function send_message(server_id, channel_id, message){
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
}*/

async function send_message(channel_id, message){
    let url = `https://discord.com/api/v9//channels/${channel_id}/messages`
    let bot_token = process.env.discord_token || JSON.parse(fs.readFileSync("../config/config.json", 'utf8')).Discord_token
    headers = {
        method: 'POST',
        headers: {Authorization: `Bot ${bot_token}`,
                "Content-Type":  "Application/json"},
        body: JSON.stringify({channel_id: channel_id, content: message})
    }
    let res = JSON.parse(await do_fetch(url, headers))
    console.log(res)
    return res
}

function get_server_name(server_id){
    return undefined
}

function get_server_image(server_id){
    return undefined
}

async function get_messages(channel_id){
    let url = `https://discord.com/api/v9/channels/${channel_id}/messages`
    let bot_token = process.env.discord_token || JSON.parse(fs.readFileSync("../config/config.json", 'utf8')).Discord_token
    headers = {
        Authorization: `Bot ${bot_token}`,
        "Content-Type":  "Application/json"
    }
    let res = JSON.parse(await do_fetch(url, {headers: headers}))
    return await treat_messages(res)
}

async function treat_messages(messages){
    let response_messages = []
    messages.forEach(element => {
        response_messages.push({
            author: element.author.username,
            content: element.content,
            timestamp: element.timestamp
        })
    })
    return response_messages
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  

async function do_fetch(url, headers){
    let res = await fetch(url, headers)
    if (res.status == 429){
        let req = await res.text()
        req = JSON.parse(req)
        await sleep(req.retry_after * 1000)
        return do_fetch(url, headers)
    }
    return res.text()
}

async function get_channels(guild_id){
    let url = `https://discord.com/api/v9/guilds/${guild_id}/channels`
    let bot_token = process.env.discord_token || JSON.parse(fs.readFileSync("../config/config.json", 'utf8')).Discord_token
    headers = {
        Authorization: `Bot ${bot_token}`,
        "Content-Type":  "Application/json"
    }
    let res = JSON.parse(await do_fetch(url, {headers: headers}))
    let categories = {}
    let text_channels = {}
    res.forEach(resi => {
        let temp_dic = {}
        if (resi.type == 4){
            temp_dic['name'] = resi.name
            temp_dic['childs'] = {}
            categories[resi.id] = temp_dic
        }
        else if (resi.type == 0){
            temp_dic['id'] = resi.id
            let parent_id = resi.parent_id
            temp_dic['parent'] = parent_id
            temp_dic['name'] = resi.name
            categories[parent_id].childs[resi.id] = {id: resi.id, name: resi.name}
            text_channels[resi.id] = temp_dic
        }
    })
    return [categories, text_channels]
}