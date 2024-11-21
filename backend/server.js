const express = require('express');
const bodyParser = require('body-parser');
const { Sequelize, DataTypes } = require('sequelize');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
app.use(bodyParser.json());

const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: './database.sqlite'
});

const User = sequelize.define('User', {
  username: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true
  },
  password: {
    type: DataTypes.STRING,
    allowNull: false
  }
});

// Register a new user
app.post('/api/users/register', async (req, res) => {
  try {
    const hashedPassword = await bcrypt.hash(req.body.password, 10);
    const user = await User.create({ username: req.body.username, password: hashedPassword });
    res.status(201).send(user);
  } catch (error) {
    console.error('Registration error:', error);
    res.status(400).send('Registration failed');
  }
});

// Login a user
app.post('/api/users/login', async (req, res) => {
  const user = await User.findOne({ where: { username: req.body.username } });
  if (!user || !await bcrypt.compare(req.body.password, user.password)) {
    return res.status(401).send('Invalid credentials');
  }
  const token = jwt.sign({ id: user.id }, 'secret');
  res.send({ token });
});

// Add this route to handle the root URL
app.get('/', (req, res) => {
  res.send('Welcome to the Techmonium Ticketing System API');
});

sequelize.sync().then(async () => {
  // Create a default user
  const defaultUsername = 'admin';
  const defaultPassword = 'password';
  const hashedPassword = await bcrypt.hash(defaultPassword, 10);
  await User.findOrCreate({
    where: { username: defaultUsername },
    defaults: { password: hashedPassword }
  });

  app.listen(3000, () => {
    console.log('Server is running on port 3000');
  });
});