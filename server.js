const express = require('express');
const cors = require('cors');
const path = require('path');
const mongoose = require('mongoose');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json({ limit: '50mb' })); // Allow large sync payloads

// Mongoose Schema & Model
const userSchema = new mongoose.Schema({
  id: { type: String, required: true, unique: true },
  username: { type: String, required: true },
  email: { type: String, required: true },
  password: { type: String, required: true }, // In a real app, hash this!
  role: { type: String, default: 'user' },
  verified: { type: Boolean, default: true },
  verificationToken: { type: String, default: null },
  sessionToken: { type: String, default: null },
  data: {
    log: { type: Array, default: [] },
    cycleStartIndex: { type: Number, default: 0 },
    cycleStartDate: { type: String, default: null },
    tips: { type: Object, default: {} },
    lastSync: { type: Number, default: Date.now }
  }
});

const User = mongoose.model('User', userSchema);

// Connect to MongoDB
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/gymtracker';
mongoose.connect(MONGODB_URI)
  .then(() => console.log('✅ Verbunden mit MongoDB'))
  .catch(err => console.error('❌ MongoDB Verbindungsfehler:', err));

function generateToken() {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

// REGISTER
app.post('/api/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Alle Felder sind erforderlich.' });
    }

    const existingUser = await User.findOne({ $or: [{ email }, { username }] });
    if (existingUser) {
      return res.status(400).json({ error: 'Benutzername oder Email existiert bereits.' });
    }

    const newUser = new User({
      id: generateToken(),
      username,
      email,
      password,
      role: username.toLowerCase() === 'admin' ? 'admin' : 'user',
      verified: true
    });

    await newUser.save();
    res.json({ message: 'Registrierung erfolgreich. Du kannst dich jetzt einloggen.', autoLogin: true });
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler bei der Registrierung.' });
  }
});

// VERIFY EMAIL
app.post('/api/verify', async (req, res) => {
  try {
    const { email, token } = req.body;
    const user = await User.findOne({ email, verificationToken: token });

    if (!user) {
      return res.status(400).json({ error: 'Ungültige Email oder Token.' });
    }

    user.verified = true;
    user.verificationToken = null;
    await user.save();

    res.json({ message: 'Email erfolgreich bestätigt!' });
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler bei der Verifizierung.' });
  }
});

// LOGIN
app.post('/api/login', async (req, res) => {
  try {
    const { ident, password } = req.body;
    const user = await User.findOne({ 
      $or: [{ email: ident }, { username: ident }],
      password 
    });

    if (!user) {
      return res.status(401).json({ error: 'Ungültige Anmeldedaten.' });
    }

    const sessionToken = generateToken();
    user.sessionToken = sessionToken;
    await user.save();

    res.json({
      message: 'Login erfolgreich',
      token: sessionToken,
      user: { id: user.id, username: user.username, email: user.email, role: user.role || 'user' }
    });
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler beim Login.' });
  }
});

// SYNC (Upload & Download Data)
app.post('/api/sync', async (req, res) => {
  try {
    const token = req.headers['authorization'];
    if (!token) return res.status(401).json({ error: 'Nicht autorisiert.' });

    const user = await User.findOne({ sessionToken: token });
    if (!user) return res.status(401).json({ error: 'Ungültige Session.' });

    const { log, cycleStartIndex, cycleStartDate, tips } = req.body;

    user.data = {
      log: log || [],
      cycleStartIndex: cycleStartIndex || 0,
      cycleStartDate: cycleStartDate || null,
      tips: tips || {},
      lastSync: Date.now()
    };

    await user.save();
    res.json({ message: 'Daten erfolgreich auf dem Server gespeichert.' });
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler beim Synchronisieren.' });
  }
});

app.get('/api/sync', async (req, res) => {
  try {
    const token = req.headers['authorization'];
    if (!token) return res.status(401).json({ error: 'Nicht autorisiert.' });

    const user = await User.findOne({ sessionToken: token });
    if (!user) return res.status(401).json({ error: 'Ungültige Session.' });

    res.json({
      ...(user.data || { log: [], cycleStartIndex: 0, cycleStartDate: null, tips: {} }),
      user: { id: user.id, username: user.username, role: user.role || 'user' }
    });
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler beim Abrufen der Daten.' });
  }
});

// ADMIN MIDDLEWARE
async function isAdminOrWatcher(req, res, next) {
  try {
    const token = req.headers['authorization'];
    if (!token) return res.status(401).json({ error: 'Nicht autorisiert.' });
    
    const user = await User.findOne({ sessionToken: token });
    if (!user) return res.status(401).json({ error: 'Ungültige Session.' });
    
    if (user.role !== 'admin' && user.role !== 'watcher') return res.status(403).json({ error: 'Keine Rechte.' });
    
    req.user = user;
    next();
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler bei der Autorisierung.' });
  }
}

async function isAdmin(req, res, next) {
  try {
    const token = req.headers['authorization'];
    if (!token) return res.status(401).json({ error: 'Nicht autorisiert.' });
    
    const user = await User.findOne({ sessionToken: token });
    if (!user) return res.status(401).json({ error: 'Ungültige Session.' });
    
    if (user.role !== 'admin') return res.status(403).json({ error: 'Keine Admin-Rechte.' });
    
    req.user = user;
    next();
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler bei der Autorisierung.' });
  }
}

// ADMIN ROUTES
app.get('/api/admin/users', isAdminOrWatcher, async (req, res) => {
  try {
    const users = await User.find({}, 'id username email role');
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler beim Abrufen der Benutzer.' });
  }
});

app.get('/api/admin/users/:id', isAdminOrWatcher, async (req, res) => {
  try {
    const userId = req.params.id;
    const user = await User.findOne({ id: userId });
    if(!user) return res.status(404).json({error: 'User not found'});
    
    res.json({ 
      user: {id: user.id, username: user.username, email: user.email, role: user.role}, 
      data: user.data || { log: [], cycleStartIndex: 0, cycleStartDate: null, tips: {} } 
    });
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler beim Abrufen des Benutzers.' });
  }
});

app.put('/api/admin/users/:id', isAdmin, async (req, res) => {
  try {
    const userId = req.params.id;
    const { username, email, role, data } = req.body;
    
    const user = await User.findOne({ id: userId });
    if(!user) return res.status(404).json({error: 'User not found'});
    
    if(username) user.username = username;
    if(email) user.email = email;
    if(role) user.role = role;
    if(data) user.data = data;
    
    await user.save();
    res.json({ message: 'User updated' });
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler beim Aktualisieren des Benutzers.' });
  }
});

app.delete('/api/admin/users/:id', isAdmin, async (req, res) => {
  try {
    const userId = req.params.id;
    if (userId === req.user.id) {
        return res.status(400).json({ error: 'Kann sich nicht selbst löschen' });
    }
    
    await User.deleteOne({ id: userId });
    res.json({ message: 'User deleted' });
  } catch (error) {
    res.status(500).json({ error: 'Serverfehler beim Löschen des Benutzers.' });
  }
});

// Static files (serve the HTML)
app.use(express.static(__dirname));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'gym_tracker_website.html'));
});

const PORT = process.env.PORT || 3001;
const os = require('os');

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Gym Tracker Server läuft lokal auf http://localhost:${PORT}`);
  
  const interfaces = os.networkInterfaces();
  for (const devName in interfaces) {
    const iface = interfaces[devName];
    for (let i = 0; i < iface.length; i++) {
      const alias = iface[i];
      if (alias.family === 'IPv4' && alias.address !== '127.0.0.1' && !alias.internal) {
        console.log(`Für dein Handy (im selben WLAN): http://${alias.address}:${PORT}`);
      }
    }
  }
}).on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`Fehler: Port ${PORT} ist bereits in Benutzung.`);
    console.error(`Beende zuerst den anderen Prozess oder ändere den Port in server.js`);
    process.exit(1);
  } else {
    console.error('Server Fehler:', err);
  }
});
