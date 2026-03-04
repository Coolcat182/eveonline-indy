# EVE Industry Bot - Architecture Overview

## 🏗️ New Architecture

This system is now split into two parts:

### 1. 🤖 Discord Bot (JF-Only)
**File**: `bot_jf_only.py`
**Purpose**: Jump Freighter services ONLY

**Commands**:
- `/jf` - Get shipping quotes
- `/jf_contract` - Book contracts
- `/jf_status` - Check contract status
- `/jf_rates` - View pricing
- `/jf_help` - Show help

**Usage**:
```bash
python bot_jf_only.py
```

### 2. 🌐 Web Dashboard (Comprehensive)
**File**: `web_app.py`
**URL**: http://localhost:5000

**Features**:
- 📊 Main Dashboard (JF, Industry, PI, Contracts)
- 🛒 **Marketplace** - Buy/sell items (moved from bot)
- 🏭 Industry tracking
- 📈 Trading analysis
- 💰 JF booking interface
- 📚 BPO database
- 🌍 PI management

**Pages**:
- `/` - Main dashboard
- `/marketplace` - Player marketplace
- `/jf-booking` - Book JF contracts via web

**Usage**:
```bash
python web_app.py
```

---

## 📦 File Structure

```
eve-online-bot/
├── bot_jf_only.py              # Discord bot (JF only)
├── web_app.py                  # Web dashboard
├── update.py                   # Auto-updater
│
├── data/                       # Database
│   └── eve_services.db
│
├── templates/                  # Web pages
│   ├── dashboard.html
│   ├── marketplace.html
│   └── jf_booking.html
│
├── capital_database.py         # Capital ships data
├── advanced_materials_database.py  # Materials data
├── org_commands.py             # Corp/Alliance commands (web only)
├── marketplace.py              # Marketplace logic (web only)
│
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── version.json               # Version tracking
```

---

## 🔄 Software Updater

**File**: `update.py`

Automatically checks for and installs updates.

### Usage:

```bash
# Check for updates
python update.py

# Force update
python update.py --force

# Rollback to previous version
python update.py --rollback

# Show version
python update.py --version
```

### Features:
- ✅ Automatic backup before updating
- ✅ Git-based updates
- ✅ Database migration support
- ✅ Rollback capability
- ✅ Changelog display

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DISCORD_TOKEN=your_token_here" > .env
```

### 2. Start Web Dashboard
```bash
python web_app.py
# Open http://localhost:5000
```

### 3. Start Discord Bot
```bash
python bot_jf_only.py
```

---

## 🗄️ Database Schema

### Core Tables (for JF):
- `jf_contracts` - JF shipping contracts
- `jf_rates` - Shipping rate configuration

### Web Dashboard Tables:
- `marketplace_listings` - Player marketplace
- `industry_jobs` - Industry job tracking
- `pi_colonies` - PI management
- `user_bpos` - BPO library
- `character_auth` - ESI authentication
- `corporations` - Corp management
- `alliances` - Alliance management
- `shared_assets` - Shared resources

---

## 🎯 Key Changes from Old System

| Feature | Old (Bot) | New (Web/Bot) |
|---------|-----------|---------------|
| JF Quotes | ✅ Bot `/jf` | ✅ Bot `/jf` |
| JF Booking | ✅ Bot `/jf_contract` | ✅ Both bot + web |
| Marketplace | ❌ Not available | ✅ Web dashboard |
| Industry | ✅ Bot commands | ✅ Web dashboard |
| BPO Database | ✅ Bot `/bpodb` | ✅ Web dashboard |
| PI Management | ✅ Bot `/pi` | ✅ Web dashboard |
| Corp/Alliance | ❌ Not available | ✅ Web dashboard |

---

## 🔐 Environment Variables

Create `.env` file:
```
DISCORD_TOKEN=your_discord_bot_token
UPDATE_URL=https://your-update-server.com
```

---

## 📱 Access Points

| Service | URL/Command |
|---------|-------------|
| Discord Bot | Use bot commands in Discord |
| Web Dashboard | http://localhost:5000 |
| Marketplace | http://localhost:5000/marketplace |
| JF Booking | http://localhost:5000/jf-booking |

---

## 🆘 Troubleshooting

### Bot won't start:
```bash
# Check token
python -c "import os; print(os.getenv('DISCORD_TOKEN'))"

# Verify requirements
pip install -r requirements.txt
```

### Database issues:
```bash
# Database is auto-created on first run
# Check data/ directory exists
mkdir -p data
```

### Update fails:
```bash
# Check git is installed
git --version

# Manual update
git pull
pip install -r requirements.txt
```

---

## 📝 Notes

- Discord bot is **JF-only** - all other features moved to web
- Web dashboard provides comprehensive industry tools
- Marketplace is **web-only** - players use browser to trade
- Auto-updater keeps software current
- All data stored in SQLite (data/eve_services.db)

---

## 🎮 WinterCo Pure Blind

**Primary Hub**: D-PN
**Secondary**: VA6-ED, RD-G2R
**Market**: Jita 4-4

For support, contact your corp directors or alliance leadership.
