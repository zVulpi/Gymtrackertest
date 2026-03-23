const fs = require('fs');
const path = require('path');
const mongoose = require('mongoose');
require('dotenv').config();

const userSchema = new mongoose.Schema({
  id: { type: String, required: true, unique: true },
  username: { type: String, required: true },
  email: { type: String, required: true },
  password: { type: String, required: true },
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

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/gymtracker';

async function migrate() {
  const DB_FILE = path.join(__dirname, 'database.json');
  if (!fs.existsSync(DB_FILE)) {
    console.log('Keine database.json gefunden. Nichts zu migrieren.');
    process.exit(0);
  }

  const dbData = JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
  
  if (!dbData.users || dbData.users.length === 0) {
    console.log('Keine Nutzer in database.json gefunden. Nichts zu migrieren.');
    process.exit(0);
  }

  try {
    await mongoose.connect(MONGODB_URI);
    console.log('✅ Verbunden mit MongoDB');

    for (const u of dbData.users) {
      const existing = await User.findOne({ id: u.id });
      if (!existing) {
        const userData = dbData.data[u.id] || { log: [], cycleStartIndex: 0, cycleStartDate: null, tips: {} };
        const newUser = new User({
          id: u.id,
          username: u.username,
          email: u.email,
          password: u.password,
          role: u.role || 'user',
          verified: u.verified || true,
          verificationToken: u.verificationToken || null,
          sessionToken: u.sessionToken || null,
          data: userData
        });
        await newUser.save();
        console.log(`User ${u.username} migriert.`);
      } else {
        console.log(`User ${u.username} existiert bereits, übersprungen.`);
      }
    }
    
    console.log('🎉 Migration abgeschlossen!');
    process.exit(0);
  } catch (error) {
    console.error('❌ Fehler bei der Migration:', error);
    process.exit(1);
  }
}

migrate();