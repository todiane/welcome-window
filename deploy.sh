#!/bin/bash

# The Welcome Window - Deployment Script
# This script backs up existing files and deploys the complete updated application

set -e  # Exit on error

echo "========================================="
echo "The Welcome Window - Deployment Script"
echo "========================================="
echo ""

# Configuration
APP_DIR="/home/welcome-window"
BACKUP_DIR="/home/welcome-window-backup-$(date +%Y%m%d-%H%M%S)"

# Check if running on the server
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Application directory $APP_DIR not found"
    echo "Are you on the correct server?"
    exit 1
fi

echo "Step 1: Creating backup..."
echo "Backup location: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$APP_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true
echo "✓ Backup created"
echo ""

echo "Step 2: Stopping the application..."
sudo systemctl stop welcome-window || echo "Service not running"
echo "✓ Application stopped"
echo ""

echo "Step 3: Installing updated files..."

# Copy Python files
echo "  - Updating Python files..."
cp models_updated.py "$APP_DIR/models.py"
cp app_updated.py "$APP_DIR/app.py"

# Create static directories if they don't exist
mkdir -p "$APP_DIR/static/js"
mkdir -p "$APP_DIR/templates/admin"

# Copy JavaScript game files
echo "  - Installing game files..."
cp wordsearch.js "$APP_DIR/static/js/"
cp sudoku.js "$APP_DIR/static/js/"

# Copy template files
echo "  - Updating templates..."
cp index_updated.html "$APP_DIR/templates/index.html"
cp waiting_room.html "$APP_DIR/templates/waiting_room.html"
cp dashboard_updated.html "$APP_DIR/templates/admin/dashboard.html"
cp room_chat_updated.html "$APP_DIR/templates/room_chat.html"

echo "✓ Files installed"
echo ""

echo "Step 4: Updating database schema..."
cd "$APP_DIR"
source venv/bin/activate
python3 << 'PYEOF'
import models
models.init_db()
print("✓ Database updated")
PYEOF
echo ""

echo "Step 5: Restarting the application..."
sudo systemctl start welcome-window
sleep 3
sudo systemctl status welcome-window --no-pager
echo "✓ Application restarted"
echo ""

echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "✓ Backup saved to: $BACKUP_DIR"
echo "✓ Application running at: https://welcome.todiane.com"
echo ""
echo "New Features Deployed:"
echo "  1. Admin Chat Interface - Real-time chat with visitors"
echo "  2. Visitor Approval System - Name + email required, manual approval"
echo "  3. Word Search Game - Fully functional with multiple themes"
echo "  4. Sudoku Game - Three difficulty levels with validation"
echo ""
echo "Next Steps:"
echo "  1. Test the application: https://welcome.todiane.com"
echo "  2. Login to admin: https://welcome.todiane.com/admin/login"
echo "  3. Check logs if needed: sudo journalctl -u welcome-window -f"
echo ""
echo "To rollback if needed:"
echo "  sudo systemctl stop welcome-window"
echo "  cp -r $BACKUP_DIR/* $APP_DIR/"
echo "  sudo systemctl start welcome-window"
echo ""
