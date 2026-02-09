Create this file:

**README.md**


# The Welcome Window

A customer service portal with real-time chat, visitor management, and interactive games to keep users engaged while they wait for support.

## Overview

The Welcome Window is a Flask-based web application designed for live customer support and service. It provides a professional interface where customers can request access, wait for approval, and chat with support staff in real-time. To improve the waiting experience, visitors can play interactive games (Word Search, Sudoku, Trivia) while they wait for assistance.

## Features

### For Customers/Visitors
- **Real-time availability status** - See when support is available, busy, or away
- **Access request system** - Submit name and email to request support. Access is via appointment only
- **Live chat support** - Real-time text communication with support staff
- **Interactive games** - Play while waiting for responses or during support sessions. Wordsearch. Sudoku and Trivia
- **Video option** - Optional Jitsi Meet video chat for visual support

### For Support Staff/Admins
- **Live chat dashboard** - Real-time communication with a visitor in one interface
- **Visitor queue management** - Approve/reject access requests, disconnect users
- **Availability controls** - Set status (available/busy/away) with custom messages
- **Active visitor monitoring** - See who's connected in real-time and disconnect visitors if needed

### Games

- **Word Search** - Multiple themes (general, Christmas) with customizable grid sizes
- **Sudoku** - Three difficulty levels (easy, medium, hard) with solution checking
- **Trivia Quiz** - Customizable categories and difficulty with scoring. Fetch trivia questions from Open Trivia Database

## Tech Stack

- **Backend:** Flask 3.1.0, Flask-SocketIO 5.4.1
- **Frontend:** Tailwind CSS, Alpine.js
- **Real-time:** Socket.IO (WebSocket communication)
- **Database:** SQLite with WAL mode
- **Video:** Jitsi Meet (embedded)
- **Deployment:** Caddy (reverse proxy + SSL), systemd service
- **Server:** VPS with Ubuntu

## Installation

### Prerequisites
- Python 3.8+
- pip and venv

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/welcome-window.git
cd welcome-window
```

2. **Run the start script**
```bash
chmod +x start.sh
./start.sh
```

The script will:
- Create a virtual environment
- Install dependencies
- Initialize the database
- Start the application at http://localhost:5000

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "import models; models.init_db()"

# Run the application
python app.py
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

### Admin Credentials

Default credentials (change in production):
- **Username:** admin
- **Password:** changeme123

Access the admin panel at: http://localhost:5000/admin/login

## Project Structure

```
welcome-window/
├── app.py                      # Main Flask application
├── models.py                   # Database models and functions
├── config.py                   # Application configuration
├── requirements.txt            # Python dependencies
├── start.sh                    # Local development script
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Landing page with availability status
│   ├── waiting_room.html      # Visitor approval waiting page
│   ├── choose.html            # Connection mode selection
│   ├── room_chat.html         # Chat & Games room
│   ├── room_video.html        # Video chat room
│   └── admin/
│       ├── login.html         # Admin login
│       └── dashboard.html     # Admin control panel
├── static/
│   └── js/
│       ├── wordsearch.js      # Word Search game implementation
│       └── sudoku.js          # Sudoku game implementation
├── games/
│   ├── wordsearch_generator.py
│   └── sudoku_generator.py
└── welcome_window.db          # SQLite database (auto-created)
```

## Usage

### For Customers

1. Visit the support portal and check availability status
2. If available, click "Request Access" and enter your name and email
3. Wait for approval in the waiting room (typically 1-2 minutes)
4. Once approved, choose "Chat & Games" mode
5. Chat with support staff and play games while waiting for responses
6. If unavailable, leave a message in the guest book

### For Support Staff

1. Log in at `/admin/login`
2. Set your availability status (Available/Busy/Away)
3. Monitor incoming access requests and approve/reject as needed
4. Chat with customers in real-time through the dashboard
5. Disconnect users when support session is complete
6. Review guest book messages and visitor analytics

## Database Schema

- **availability** - Current status and custom message
- **messages** - Guest book messages
- **visits** - Visit logs with duration tracking
- **pending_visitors** - Access requests awaiting approval
- **chat_messages** - Persistent chat history

## Deployment

The application is designed to be deployed on a VPS with:
- Caddy for reverse proxy and automatic SSL
- systemd for process management
- SQLite in WAL mode for concurrent access

See deployment script in `deploy.sh` for production deployment steps.

## API Endpoints

### Public Endpoints
- `GET /` - Landing page
- `POST /request-access` - Submit access request
- `GET /waiting-room` - Approval waiting page
- `GET /choose` - Connection mode selection
- `GET /room/chat` - Chat & Games room
- `GET /room/video` - Video chat room
- `GET /api/game/wordsearch` - Generate Word Search puzzle
- `GET /api/game/sudoku` - Generate Sudoku puzzle
- `POST /guestbook` - Submit guest book message

### Admin Endpoints
- `POST /admin/login` - Admin authentication
- `GET /admin` - Admin dashboard
- `POST /admin/status/update` - Update availability status
- `POST /admin/visitor/{id}/approve` - Approve visitor
- `POST /admin/visitor/{id}/reject` - Reject visitor
- `POST /admin/visitor/{id}/disconnect` - Disconnect visitor
- `POST /admin/chat/message/{id}/delete` - Delete chat message
- `POST /admin/chat/clear` - Clear chat history

## Socket.IO Events

### Client → Server
- `send_message` - Send chat message
- `join_admin` - Join admin room
- `request_game` - Request to start a game

### Server → Client
- `connection_established` - Connection confirmed
- `new_message` - New chat message received
- `status_changed` - Availability status updated
- `visitor_joined` - New visitor connected (admin only)
- `visitor_left` - Visitor disconnected (admin only)
- `approval_granted` - Access request approved
- `approval_rejected` - Access request rejected
- `force_disconnect` - Admin disconnected visitor
- `message_deleted` - Message removed from chat
- `chat_cleared` - Chat history cleared

## Security Considerations

- Admin credentials should be changed from defaults
- Use environment variables for sensitive configuration
- HTTPS is required for production (handled by Caddy)
- Session-based authentication for admin panel
- Input validation and sanitization on all user inputs
- Rate limiting recommended for production

## Browser Support

- Modern browsers with WebSocket support
- Chrome, Firefox, Safari, Edge (latest versions)
- Mobile browsers supported

## Contributing

This is a personal project, but feedback and suggestions are welcome! Please open an issue to discuss proposed changes.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with Flask and Socket.IO
- Video chat powered by Jitsi Meet
- Styled with Tailwind CSS
- Interactive elements with Alpine.js

## Author

**Diane** - UK-based Django/Flask developer
- GitHub: [@djangify](https://github.com/djangify)
- Website: [todiane.com](https://todiane.com)

---

**The Welcome Window** - Professional live chat support with games to keep customers engaged while they wait.
```

