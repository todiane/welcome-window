# The Welcome Window - Quick Start

## What This Is

A personal connection portal where you signal availability and people can drop by for:
- **Chat & Games** (text chat + Word Search + Sudoku) - YOUR MAIN MODE
- **Video Chat** (Jitsi video + chat + games) - For new people/online groups

## Get Started NOW
```bash
cd welcome-window-v2
./start.sh
```

Visit: http://localhost:5000

## Admin Login

URL: http://localhost:5000/admin/login
- Username: admin
- Password: changeme123

## Two Connection Modes

**Chat & Games** - What you prefer most of the time
- Text chat only
- Play Word Search or Sudoku together
- Low pressure, relaxed

**Video Chat** - When you want to see someone
- Jitsi video (reliable, professional)
- Text chat sidebar
- Games still available

## Tech Stack

- Flask 3.x + Socket.IO
- Jitsi Meet (embedded)
- SQLite database
- Tailwind CSS + Alpine.js

## Deploy to VPS

Recommended domain: welcome.todiane.com

Basic steps:
1. Copy files to server
2. Install dependencies
3. Set up systemd service
4. Configure Caddy

## Next Steps

1. Test locally (./start.sh)
2. Try both Chat & Games and Video modes
3. Login to admin panel
4. Deploy when ready
5. Share link with friends