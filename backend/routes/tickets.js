const express = require('express');
const Ticket = require('../models/Ticket');
const router = express.Router();

// Create a new ticket
router.post('/', async (req, res) => {
  const ticket = await Ticket.create(req.body);
  res.status(201).send(ticket);
});

// Get all tickets
router.get('/', async (req, res) => {
  const tickets = await Ticket.findAll();
  res.send(tickets);
});

// Update a ticket
router.put('/:id', async (req, res) => {
  const ticket = await Ticket.findByPk(req.params.id);
  if (ticket) {
    await ticket.update(req.body);
    res.send(ticket);
  } else {
    res.status(404).send('Ticket not found');
  }
});

module.exports = router;