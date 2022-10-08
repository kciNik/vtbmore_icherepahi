require('dotenv').config()
const express = require('express');
const cors = require('cors'); 
const cookie_parser = require('cookie-parser');
const pg = require('pg');
const config = {
  host: 'localhost',
  user: 'postgres',     
  password: '123321',
  database: 'postgres',
  port: 5432,
  ssl: false
};
const router = require('./router/index')

const client = new pg.Client(config);

const PORT = process.env.PORT || 5000; 
const app = express()

app.use(express.json());
app.use(cookie_parser());
app.use(cors());
app.use('/api', router);

const start = async () => {
  try {
    await client.connect(err => {
      if (err) throw err;
    });
    app.listen(PORT, () => console.log(`Server started on port ${PORT}`));

  } catch (e) {
    console.log(e);
  }
}

start();