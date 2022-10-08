const {Schema, model} = require('pg');

const token_schema = new Schema({
    user: {type: Schema.Types.OblectId, ref: 'User'},
    refresh_token: {type: String, required: true},
})

module.exports = model('Token', token_schema);

