const express = require('express');
const User = require('../models/User');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const router = express.Router();

// Register a new user
router.post('/register', async (req, res) => {
  try {
    const hashedPassword = await bcrypt.hash(req.body.password, 10);
    const user = await User.create({ ...req.body, password: hashedPassword });
    res.status(201).send(user);
  } catch (error) {
    console.error('Registration error:', error);
    res.status(400).send('Registration failed');
  }
});

// Login a user
router.post('/login', async (req, res) => {
  const user = await User.findOne({ where: { username: req.body.username } });
  if (!user || !await bcrypt.compare(req.body.password, user.password)) {
    return res.status(401).send('Invalid credentials');
  }
  const token = jwt.sign({ id: user.id }, 'secret');
  res.send({ token });
});

module.exports = router;