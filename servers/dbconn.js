var mongoose = require('mongoose');

mongoose.connect('mongodb://localhost:27017/cptv');

var db = mongoose.connection;

db.on('error', function(){
    console.log('db connection Failed');
});

db.once('open', function(){

    console.log('db conneced');
});

var cptv_schema = mongoose.Schema({
    title: { type: String },
    num: { type: Number },
    lat: { type: Number },
    lng: { type: Number },
    dtime: { type: String },
    dform: { type: Number }
});

var cptv = mongoose.model('Schema', cptv_schema);

/*
cptv.find(function(error, cptv_list){
    console.log('gettig all data');

    if(error){
        console.log('getting D error');
    }else{
        console.log(cptv_list);
    }
});
*/


module.exports = cptv



