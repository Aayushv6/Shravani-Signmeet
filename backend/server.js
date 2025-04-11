const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const cors = require('cors');

// Setup
const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
  cors: {
    origin: "*", // Change this in production
    methods: ["GET", "POST"]
  }
});

app.use(cors());
app.use(express.json());

// Just a welcome route
app.get('/', (req, res) => {
  res.send('🟢 Socket Server Running!');
});

// Handle socket connections
io.on('connection', (socket) => {
  console.log('🔌 A user connected:', socket.id);

  // Handle receiving gesture messages
  socket.on('gestureMessage', (data) => {
    console.log('✋ Gesture Received:', data);

    // Broadcast to all clients except sender
    socket.broadcast.emit('gestureMessage', data);
  });

  // On disconnect
  socket.on('disconnect', () => {
    console.log('❌ User disconnected:', socket.id);
  });
});

// Start server
const PORT = process.env.PORT || 5001;
server.listen(PORT, () => {
  console.log(`🚀 Socket.IO server running at http://localhost:${PORT}`);
});
