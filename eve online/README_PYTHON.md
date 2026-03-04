# EVE Industry Services (Python)

Discord bot for WinterCo industry, PI, JF, and trading operations.

## Features

- **BPO Database**: 130+ blueprints with full material requirements
- **Build Calculations**: ME (0-10), TE (0-20), skill bonuses
- **PI Management**: All 15 regions with Pure Blind default
- **Jump Freighter**: Quotes and contracts
- **Trading**: Jita to WinterCo import analysis
- **Contracts**: Player buy/sell system
- **PLEX Arbitrage**: Store item analysis

## Setup

1. Install Python 3.8+ from https://python.org

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your Discord bot token:
```
DISCORD_TOKEN=your_token_here
```

4. Run the bot:
```bash
python bot.py
```

## Commands

- `/jf` - Jump Freighter quotes
- `/bpodb` - BPO database with materials/build time
- `/contract` - Buy/sell contracts
- `/pi` - PI colony management
- `/help` - Show all commands

## Dashboard

Open `dashboard.html` in your browser to see the full feature list.
