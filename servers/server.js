
const cptv = require('./dbconn');
const express = require('express');
const path = require('path');
const app = express();
const net = require('net');


app.listen(8080, function () {
    console.log('listening on 8080')
});


/*
app.use(express.static(path.join(__dirname, '../build')), function(req, res, next){
    res.header("Access-Control-Allow-Origin", "192.168.0.5.A"); // update to match the domain you will make the request from
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});
*/
app.get('/', function(req, res, next){
    res.sendFile( path.join(__dirname, '../build/index.html'))
});

app.use(express.static(path.join(__dirname, '../build')));

app.get('/', function(req, res){
    res.sendFile( path.join(__dirname, '../build/index.html'))
});

/*
app.get('*', function (req, res) {
    res.sendFile(path.join(__dirname, '../build/index.html'))
})
*/

app.get('/data', function(req, res){
    res.send(dbparsing())
});

app.get('/vid', function (req, res) {
    //res.render("test_img.jpg")
    res.sendfile(path.join(__dirname, '../src/Components/received.mp4'));
});

var dbparsing = function () {
    cptv.find(function (error, cptv_list) {
        console.log('getting all data');

        if (error) {
            console.log('getting D error');
        } else {
            console.log('db data received');
            return JSON.parse(JSON.stringify(cptv_list))
        }
    });
}

var server_log = net.createServer(function (socket) {
    // connection event
    console.log('connected: server_log');

    socket.on('data', function (data) {


        rcdata = data.toString();
        rcdata.replace(/\n/gi, '\\n');
        rcdata.replace(/\r/gi, '\\r');
        rcdata_splitted = rcdata.split('_');
        console.log('received : ', rcdata);

        var rcdata_json = [
            {
                dtime: rcdata_splitted[0],
                num: rcdata_splitted[1],
                dform: rcdata_splitted[2]
            }
        ]

        cptv.findOneAndUpdate({ num: rcdata_json.num }, { dtime:rcdata_json.dtime, dform:rcdata_json.dform }, { new: true }, function (err, tasks) {
            if (err) throw err;
            console.log(tasks);
        });
        

    });

});

server_log.on('listening', function () {
    console.log('log listening..');
});

server_log.on('close', function () {
    console.log('server closed');
});

server_log.on('error', function (err) {
    console.log('connection lost');
});

server_log.listen(22046);