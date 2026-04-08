#!/bin/bash
# ============================================================================
# DayTradeAgents - Ubuntu Setup Script
# ============================================================================
# Run this on your Ubuntu server:
#   chmod +x setup_ubuntu.sh && ./setup_ubuntu.sh
# ============================================================================

set -e

echo "========================================="
echo " DayTradeAgents - Ubuntu Setup"
echo "========================================="

# ── 1. System packages ──
echo ""
echo "[1/6] Installing system packages..."
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git curl

# ── 2. Project directory ──
echo ""
echo "[2/6] Setting up project directory..."
PROJECT_DIR="$HOME/DayTradeAgents"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating $PROJECT_DIR..."
    mkdir -p "$PROJECT_DIR"
    echo "Copy your project files to $PROJECT_DIR first, then re-run this script."
    echo "Example: scp -r ./DayTradeAgents/* user@server:~/DayTradeAgents/"
    exit 1
fi

cd "$PROJECT_DIR"

# ── 3. Python virtual environment ──
echo ""
echo "[3/6] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# ── 4. Environment file ──
echo ""
echo "[4/6] Setting up .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "  IMPORTANT: Edit .env with your API keys:"
    echo "    nano $PROJECT_DIR/.env"
    echo ""
    echo "  You need to set:"
    echo "    - OPENAI_API_KEY (or ANTHROPIC_API_KEY)"
    echo "    - TELEGRAM_BOT_TOKEN"
    echo "    - TELEGRAM_CHAT_ID"
    echo ""
else
    echo "  .env already exists, skipping."
fi

# ── 5. Systemd service ──
echo ""
echo "[5/6] Installing systemd service..."
SERVICE_FILE="/etc/systemd/system/daytradeagents.service"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
USER=$(whoami)

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=DayTradeAgents Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PYTHON_PATH $PROJECT_DIR/telegram_bot.py
Restart=always
RestartSec=10
StandardOutput=append:$PROJECT_DIR/bot.log
StandardError=append:$PROJECT_DIR/bot.log
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable daytradeagents

# ── 6. Done ──
echo ""
echo "========================================="
echo " Setup complete!"
echo "========================================="
echo ""
echo " Next steps:"
echo "   1. Edit your .env file:"
echo "      nano $PROJECT_DIR/.env"
echo ""
echo "   2. Test the bot manually first:"
echo "      cd $PROJECT_DIR"
echo "      source venv/bin/activate"
echo "      python telegram_bot.py"
echo ""
echo "   3. Once working, start as a service:"
echo "      sudo systemctl start daytradeagents"
echo ""
echo "   4. Check status:"
echo "      sudo systemctl status daytradeagents"
echo ""
echo "   5. View logs:"
echo "      tail -f $PROJECT_DIR/bot.log"
echo ""
echo "========================================="
