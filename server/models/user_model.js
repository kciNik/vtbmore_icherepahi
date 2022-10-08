const {Schema, model} = require('pg');

const user_schema = new Schema({
    email: {type: String, unique: true, required: true},
    password: {type: String, required: true},
    is_activated: {type: Boolean, default: false},
    activation_link: {type: String},
})

module.exports = model('User', user_schema);

