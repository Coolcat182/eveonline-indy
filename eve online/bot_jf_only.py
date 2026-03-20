# EVE Jump Freighter Discord Bot - Simplified Version
# This bot only handles JF services - everything else is in the web dashboard

import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re
import aiohttp
import asyncio

load_dotenv()

# ESI Configuration
ESI_BASE_URL = "https://esi.evetech.net/latest"
JITA_REGION_ID = 10000002  # The Forge

# EVE Item Database (common items with volumes)
ITEM_DATABASE = {
    # Ships
    'drake': {'volume': 15000, 'type_id': 645},
    'raven': {'volume': 50000, 'type_id': 638},
    'rokh': {'volume': 50000, 'type_id': 642},
    'scorpion': {'volume': 50000, 'type_id': 640},
    'megathron': {'volume': 50000, 'type_id': 645},
    'dominix': {'volume': 50000, 'type_id': 645},
    'hyperion': {'volume': 50000, 'type_id': 643},
    'tempest': {'volume': 50000, 'type_id': 644},
    'typhoon': {'volume': 50000, 'type_id': 644},
    'maelstrom': {'volume': 50000, 'type_id': 646},
    'abaddon': {'volume': 50000, 'type_id': 641},
    'apocalypse': {'volume': 50000, 'type_id': 642},
    'armageddon': {'volume': 50000, 'type_id': 643},
    'vexor': {'volume': 10000, 'type_id': 626},
    'caracal': {'volume': 10000, 'type_id': 621},
    'stabber': {'volume': 10000, 'type_id': 622},
    'omni': {'volume': 10000, 'type_id': 640},
    
    # Battlecruisers
    'drake navy issue': {'volume': 15000, 'type_id': 33153},
    'hurricane': {'volume': 15000, 'type_id': 647},
    'brutix': {'volume': 15000, 'type_id': 633},
    'myrmidon': {'volume': 15000, 'type_id': 644},
    
    # Freighters
    'charon': {'volume': 20000000, 'type_id': 20183},
    'providence': {'volume': 20000000, 'type_id': 20187},
    'obelisk': {'volume': 20000000, 'type_id': 20185},
    'fenrir': {'volume': 20000000, 'type_id': 20189},
    
    # Modules
    'afterburner': {'volume': 5, 'type_id': 12058},
    'microwarpdrive': {'volume': 5, 'type_id': 12076},
    'shield booster': {'volume': 5, 'type_id': 12054},
    'armor repairer': {'volume': 5, 'type_id': 12055},
    'railgun': {'volume': 5, 'type_id': 12082},
    'missile launcher': {'volume': 5, 'type_id': 12084},
    'autocannon': {'volume': 5, 'type_id': 12083},
    'laser': {'volume': 5, 'type_id': 12080},
    
    # Capital Modules
    'capital shield booster': {'volume': 4000, 'type_id': 41475},
    'capital armor repairer': {'volume': 4000, 'type_id': 41483},
    'siege module': {'volume': 4000, 'type_id': 34266},
    
    # Ammo
    'missile': {'volume': 0.1, 'type_id': 209},  # Generic
    'charge': {'volume': 0.2, 'type_id': 209},   # Generic
    'torpedo': {'volume': 0.5, 'type_id': 209},  # Generic
    'drone': {'volume': 5, 'type_id': 245},      # Generic
    
    # Minerals
    'tritanium': {'volume': 0.01, 'type_id': 34},
    'pyerite': {'volume': 0.01, 'type_id': 35},
    'mexallon': {'volume': 0.01, 'type_id': 36},
    'isogen': {'volume': 0.01, 'type_id': 37},
    'nocxium': {'volume': 0.01, 'type_id': 38},
    'zydrine': {'volume': 0.01, 'type_id': 39},
    'megacyte': {'volume': 0.01, 'type_id': 40},
    
    # PLEX
    'plex': {'volume': 0.01, 'type_id': 44992},
    'multiple pilot training certificate': {'volume': 0.01, 'type_id': 34133},
    
    # Skill Injectors
    'large skill injector': {'volume': 0.01, 'type_id': 40520},
    'skill injector': {'volume': 0.01, 'type_id': 40520},
}

# ESI Client for Jita price lookups
class ESIClient:
    def __init__(self):
        self.session = None
        self.price_cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 minutes
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_jita_price(self, type_id):
        """Get Jita buy price for item"""
        now = datetime.now()
        
        # Check cache
        if type_id in self.price_cache:
            cache_age = (now - self.cache_time[type_id]).total_seconds()
            if cache_age < self.cache_duration:
                return self.price_cache[type_id]
        
        try:
            session = await self.get_session()
            url = f"{ESI_BASE_URL}/markets/{JITA_REGION_ID}/orders/"
            params = {'type_id': type_id, 'order_type': 'buy'}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    orders = await response.json()
                    if orders:
                        # Get highest buy price
                        best_price = max(order['price'] for order in orders)
                        self.price_cache[type_id] = best_price
                        self.cache_time[type_id] = now
                        return best_price
        except Exception as e:
            print(f"ESI error: {e}")
        
        return None
    
    async def search_type(self, name):
        """Search for item type by name"""
        try:
            session = await self.get_session()
            url = f"{ESI_BASE_URL}/search/"
            params = {
                'categories': 'inventory_type',
                'search': name,
                'strict': 'false'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'inventory_type' in data:
                        return data['inventory_type'][0]
        except Exception as e:
            print(f"Search error: {e}")
        
        return None
    
    async def close(self):
        if self.session:
            await self.session.close()

esi_client = ESIClient()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Database setup
def get_db():
    conn = sqlite3.connect('data/eve_services.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with JF-specific tables only"""
    conn = get_db()
    c = conn.cursor()
    
    # JF Contracts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS jf_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL,
            discord_username TEXT NOT NULL,
            character_name TEXT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            volume_m3 REAL NOT NULL,
            collateral REAL NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accepted_by TEXT,
            accepted_at TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')
    
    # JF Rate Settings - kept for backwards compatibility
    c.execute('''
        CREATE TABLE IF NOT EXISTS jf_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route TEXT UNIQUE NOT NULL,
            base_rate REAL NOT NULL,
            min_collateral REAL DEFAULT 0,
            max_collateral REAL DEFAULT 5000000000,
            collateral_fee_rate REAL DEFAULT 0.01,
            active BOOLEAN DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# Distance-based pricing configuration
# Base rate: 200 ISK/m³ at RD-G2R (hub)
# Rate increases by 10 ISK/m³ per "jump distance" level from RD-G2R
SYSTEM_DISTANCE_TIERS = {
    # Hub - Tier 0 (200 ISK/m³)
    'RDG': 0,    # RD-G2R - Main WinterCo hub
    
    # Close systems - Tier 1 (210 ISK/m³) - 1 jump from hub
    'DPN': 1,    # D-PN
    'VA6': 1,    # VA6-ED
    'OBK': 2,    # O-BKJY
    '7RM': 2,    # 7RM-N0
    'C4C': 2,    # C4C-Z4
    
    # Medium distance - Tier 3 (230 ISK/m³)
    'MTO': 3,    # MTO-OK
    '2R6': 3,    # 2R-CRW
    'NHK': 3,    # NHKO-2
    
    # Far systems - Tier 4 (240 ISK/m³)
    'KQU': 4,    # KQU-WS
    '6Y8': 4,    # 6Y-WRM
    
    # Highsec/very far - Tier 5 (250 ISK/m³)
    'JITA': 5,   # Jita 4-4
}

BASE_RATE = 200  # ISK/m³ at hub
RATE_INCREMENT = 10  # ISK/m³ per distance tier
COLLATERAL_FEE_RATE = 0.01  # 1%

def calculate_jf_price(origin: str, destination: str, volume: float, collateral: float) -> dict:
    """Calculate JF shipping price with distance-based pricing"""
    origin_clean = origin.upper().replace('-', '').replace(' ', '')
    dest_clean = destination.upper().replace('-', '').replace(' ', '')
    
    # Normalize system names - All WinterCo hub systems
    system_map = {
        # Hub
        'RDG': 'RDG', 'RD-G2R': 'RDG', 'RDG2R': 'RDG', 'RD': 'RDG',
        
        # Tier 1 - Close systems
        'DPN': 'DPN', 'D-PN': 'DPN', 'DP': 'DPN',
        'VA6': 'VA6', 'VA6-ED': 'VA6', 'VA': 'VA6',
        
        # Tier 2 - Near systems  
        'OBK': 'OBK', 'O-BKJY': 'OBK', 'OB': 'OBK',
        '7RM': '7RM', '7RM-N0': '7RM', '7R': '7RM',
        'C4C': 'C4C', 'C4C-Z4': 'C4C', 'C4': 'C4C',
        
        # Tier 3 - Medium distance
        'MTO': 'MTO', 'MTO-OK': 'MTO', 'MT': 'MTO',
        '2R6': '2R6', '2R-CRW': '2R6', '2R': '2R6',
        'NHK': 'NHK', 'NHKO-2': 'NHK', 'NH': 'NHK',
        
        # Tier 4 - Far systems
        'KQU': 'KQU', 'KQU-WS': 'KQU', 'KQ': 'KQU',
        '6Y8': '6Y8', '6Y-WRM': '6Y8', '6Y': '6Y8',
        
        # Tier 5 - Highsec
        'JITA': 'JITA', 'JITA4': 'JITA', 'JIT': 'JITA'
    }
    
    origin_code = system_map.get(origin_clean, origin_clean[:3])
    dest_code = system_map.get(dest_clean, dest_clean[:3])
    
    # Check if both systems are valid
    if origin_code not in SYSTEM_DISTANCE_TIERS:
        return {
            'error': f"Origin system '{origin}' not recognized",
            'available_systems': [
                'Hub: RD-G2R',
                'Tier 1: D-PN, VA6-ED',
                'Tier 2: O-BKJY, 7RM-N0, C4C-Z4',
                'Tier 3: MTO-OK, 2R-CRW, NHKO-2',
                'Tier 4: KQU-WS, 6Y-WRM',
                'Highsec: Jita'
            ]
        }
    
    if dest_code not in SYSTEM_DISTANCE_TIERS:
        return {
            'error': f"Destination system '{destination}' not recognized",
            'available_systems': [
                'Hub: RD-G2R',
                'Tier 1: D-PN, VA6-ED',
                'Tier 2: O-BKJY, 7RM-N0, C4C-Z4',
                'Tier 3: MTO-OK, 2R-CRW, NHKO-2',
                'Tier 4: KQU-WS, 6Y-WRM',
                'Highsec: Jita'
            ]
        }
    
    # Calculate distance-based rate
    # Price is based on the FARTHEST point from RD-G2R in the route
    origin_distance = SYSTEM_DISTANCE_TIERS[origin_code]
    dest_distance = SYSTEM_DISTANCE_TIERS[dest_code]
    max_distance = max(origin_distance, dest_distance)
    
    # Calculate rate: base + (distance × increment)
    base_rate = BASE_RATE + (max_distance * RATE_INCREMENT)
    base_price = volume * base_rate
    
    # Collateral fee: 1% on entire collateral amount
    collateral_fee = collateral * COLLATERAL_FEE_RATE
    
    total_price = base_price + collateral_fee
    
    # Create route description
    if origin_distance == dest_distance:
        distance_desc = f"Tier {max_distance} (Same distance from hub)"
    else:
        distance_desc = f"Tier {max_distance} ({origin_code} T{origin_distance} → {dest_code} T{dest_distance})"
    
    return {
        'origin': origin_code,
        'destination': dest_code,
        'volume': volume,
        'collateral': collateral,
        'base_rate': base_rate,
        'base_price': base_price,
        'collateral_fee': collateral_fee,
        'total_price': total_price,
        'distance_tier': max_distance,
        'distance_desc': distance_desc
    }

# ============================================================
# JF COMMANDS ONLY
# ============================================================

@bot.tree.command(name="jf", description="Get a Jump Freighter shipping quote")
@app_commands.describe(
    origin="Origin system (e.g., Jita, D-PN, VA6-ED, RD-G2R)",
    destination="Destination system",
    volume="Total volume in m³",
    collateral="Collateral value in ISK"
)
async def jf_quote(
    interaction: discord.Interaction,
    origin: str,
    destination: str,
    volume: float,
    collateral: float
):
    """Get instant JF shipping quote"""
    
    # Calculate price
    result = calculate_jf_price(origin, destination, volume, collateral)
    
    if 'error' in result:
        await interaction.response.send_message(
            f"❌ {result['error']}\n\n"
            f"Available systems:\n" + "\n".join([f"• {s}" for s in result['available_systems']]),
            ephemeral=True
        )
        return
    
    embed = discord.Embed(
        title="🚀 Jump Freighter Quote",
        description=f"Route: **{result['origin']}** → **{result['destination']}**",
        color=discord.Color.green()
    )
    
    # Show calculation breakdown
    volume_text = f"{result['volume']:,.0f}m³ = {result['base_price']:,.0f} ISK (@{result['base_rate']:.0f} ISK/m³)"
    collateral_text = f"{result['collateral']:,.0f} = {result['collateral_fee']:,.0f} ISK (@1% collateral)"
    
    embed.add_field(
        name="📦 Volume Charge",
        value=f"```{volume_text}```",
        inline=False
    )
    
    embed.add_field(
        name="💰 Collateral Fee",
        value=f"```{collateral_text}```",
        inline=False
    )
    
    # Show distance tier info
    embed.add_field(
        name="📍 Distance Tier",
        value=f"```{result['distance_desc']}```\nRate: {result['base_rate']:.0f} ISK/m³",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Total Price",
        value=f"**{result['total_price']:,.0f} ISK**",
        inline=False
    )
    
    embed.set_footer(text="Quote valid for 24 hours | Use /jf_contract to book this shipment")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="jf_contract", description="Book a Jump Freighter contract")
@app_commands.describe(
    origin="Origin system",
    destination="Destination system",
    volume="Volume in m³",
    collateral="Collateral value",
    character_name="Your EVE character name",
    notes="Additional notes"
)
async def jf_contract(
    interaction: discord.Interaction,
    origin: str,
    destination: str,
    volume: float,
    collateral: float,
    character_name: str,
    notes: str = None
):
    """Book a JF contract"""
    
    # Calculate price
    result = calculate_jf_price(origin, destination, volume, collateral)
    
    if 'error' in result:
        await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
        return
    
    # Save to database
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO jf_contracts 
        (discord_user_id, discord_username, character_name, origin, destination, 
         volume_m3, collateral, price, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(interaction.user.id),
        interaction.user.name,
        character_name,
        result['origin'],
        result['destination'],
        volume,
        collateral,
        result['total_price'],
        notes
    ))
    conn.commit()
    contract_id = c.lastrowid
    conn.close()
    
    embed = discord.Embed(
        title="✅ JF Contract Created",
        description=f"Contract ID: **#{contract_id}**",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Character", value=character_name, inline=True)
    embed.add_field(name="Route", value=f"{result['origin']} → {result['destination']}", inline=True)
    embed.add_field(name="Volume", value=f"{volume:,.0f} m³", inline=True)
    embed.add_field(name="Price", value=f"{result['total_price']:,.0f} ISK", inline=True)
    
    if notes:
        embed.add_field(name="Notes", value=notes, inline=False)
    
    embed.add_field(
        name="📋 Next Steps",
        value="1. Create contract in-game to 'JF Services'\n"
              "2. Set collateral and reward as quoted\n"
              "3. Contract will be accepted within 24h\n"
              "4. Track with `/jf_status`",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="jf_status", description="Check your JF contract status")
@app_commands.describe(contract_id="Contract ID (optional - shows latest if not provided)")
async def jf_status(interaction: discord.Interaction, contract_id: int = None):
    """Check status of JF contracts"""
    
    conn = get_db()
    c = conn.cursor()
    
    if contract_id:
        c.execute('''
            SELECT * FROM jf_contracts 
            WHERE id = ? AND discord_user_id = ?
        ''', (contract_id, str(interaction.user.id)))
    else:
        c.execute('''
            SELECT * FROM jf_contracts 
            WHERE discord_user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        ''', (str(interaction.user.id),))
    
    contracts = c.fetchall()
    conn.close()
    
    if not contracts:
        await interaction.response.send_message(
            "📭 No contracts found. Create one with `/jf_contract`",
            ephemeral=True
        )
        return
    
    if contract_id:
        # Single contract detail view
        contract = contracts[0]
        status_emoji = {"pending": "⏳", "accepted": "🚛", "in_transit": "✈️", "completed": "✅", "cancelled": "❌"}.get(contract['status'], "❓")
        
        embed = discord.Embed(
            title=f"{status_emoji} Contract #{contract['id']}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Character", value=contract['character_name'], inline=True)
        embed.add_field(name="Route", value=f"{contract['origin']} → {contract['destination']}", inline=True)
        embed.add_field(name="Status", value=contract['status'].upper(), inline=True)
        embed.add_field(name="Volume", value=f"{contract['volume_m3']:,.0f} m³", inline=True)
        embed.add_field(name="Price", value=f"{contract['price']:,.0f} ISK", inline=True)
        embed.add_field(name="Created", value=contract['created_at'][:10], inline=True)
        
        if contract['accepted_by']:
            embed.add_field(name="Accepted By", value=contract['accepted_by'], inline=True)
        if contract['notes']:
            embed.add_field(name="Notes", value=contract['notes'], inline=False)
        
        await interaction.response.send_message(embed=embed)
    else:
        # List view
        embed = discord.Embed(
            title="📋 Your JF Contracts",
            color=discord.Color.blue()
        )
        
        for contract in contracts:
            status_emoji = {"pending": "⏳", "accepted": "🚛", "in_transit": "✈️", "completed": "✅"}.get(contract['status'], "❓")
            embed.add_field(
                name=f"{status_emoji} #{contract['id']} - {contract['origin']} → {contract['destination']}",
                value=f"Status: {contract['status']} | Price: {contract['price']:,.0f} ISK",
                inline=False
            )
        
        embed.set_footer(text="Use `/jf_status contract_id:ID` for detailed view")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="jf_rates", description="View current JF shipping rates")
async def jf_rates(interaction: discord.Interaction):
    """Display current JF rates with distance-based pricing"""
    
    embed = discord.Embed(
        title="💰 Jump Freighter Rates",
        description="Distance-based pricing - farther from hub = more fuel",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="⛽ Fuel Surcharge Tiers (All WinterCo Systems)",
        value="**Tier 0 - RD-G2R (Hub)**: 200 ISK/m³\n"
              "**Tier 1 - D-PN, VA6-ED**: 210 ISK/m³ (+10)\n"
              "**Tier 2 - O-BKJY, 7RM-N0, C4C-Z4**: 220 ISK/m³ (+20)\n"
              "**Tier 3 - MTO-OK, 2R-CRW, NHKO-2**: 230 ISK/m³ (+30)\n"
              "**Tier 4 - KQU-WS, 6Y-WRM**: 240 ISK/m³ (+40)\n"
              "**Tier 5 - Jita**: 250 ISK/m³ (+50)\n"
              "*Rate based on farthest point from hub*",
        inline=False
    )
    
    embed.add_field(
        name="💵 Collateral Fee",
        value="**1%** of total collateral amount",
        inline=False
    )
    
    embed.add_field(
        name="🧮 Example: RD-G2R → Jita",
        value="113,416m³ × 250 ISK = **28,354,000 ISK**\n"
              "13.4B collateral × 1% = **134,792,567 ISK**\n"
              "**Total: ~163.1M ISK**",
        inline=False
    )
    
    embed.add_field(
        name="🧮 Example: RD-G2R → D-PN",
        value="113,416m³ × 210 ISK = **23,817,360 ISK**\n"
              "13.4B collateral × 1% = **134,792,567 ISK**\n"
              "**Total: ~158.6M ISK** (saves 4.5M!)",
        inline=False
    )
    
    embed.add_field(
        name="🌐 All WinterCo Routes Supported",
        value="All hub systems ↔ All hub systems\n"
              "15+ systems across Pure Blind\n"
              "Automatic tier detection",
        inline=False
    )
    
    embed.add_field(
        name="💡 Tip",
        value="Ship to RD-G2R first for cheapest rates!\n"
              "Avoid Tier 5 (Jita) when possible",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="jf_cargo", description="Paste cargo from EVE to calculate JF cost")
@app_commands.describe(
    origin="Origin system",
    destination="Destination system",
    cargo="Paste your cargo here (copy from inventory/cargo scan)",
    use_jita_prices="Use Jita buy prices for valuation (default: yes)"
)
async def jf_cargo(
    interaction: discord.Interaction,
    origin: str,
    destination: str,
    cargo: str,
    use_jita_prices: bool = True
):
    """Parse pasted cargo and calculate JF shipping cost"""
    
    await interaction.response.defer(thinking=True)
    
    # Parse cargo data
    lines = cargo.strip().split('\n')
    items = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to parse: "Item Name" xQuantity or "Item Name"
        # Common formats from EVE copy:
        # - Drake x5
        # - 5x Drake
        # - Drake (5)
        
        parsed = False
        
        # Format: "Item Name" x5
        match = re.match(r'(.+?)\s*x\s*(\d+)', line, re.IGNORECASE)
        if match:
            item_name = match.group(1).strip()
            quantity = int(match.group(2))
            items.append({'name': item_name, 'quantity': quantity})
            parsed = True
        
        # Format: 5x "Item Name"
        if not parsed:
            match = re.match(r'(\d+)x\s*(.+)', line, re.IGNORECASE)
            if match:
                quantity = int(match.group(1))
                item_name = match.group(2).strip()
                items.append({'name': item_name, 'quantity': quantity})
                parsed = True
        
        # Format: "Item Name" (5)
        if not parsed:
            match = re.match(r'(.+?)\s*\((\d+)\)', line)
            if match:
                item_name = match.group(1).strip()
                quantity = int(match.group(2))
                items.append({'name': item_name, 'quantity': quantity})
                parsed = True
        
        # Single item
        if not parsed:
            items.append({'name': line, 'quantity': 1})
    
    if not items:
        await interaction.followup.send(
            "❌ Could not parse cargo. Please paste items in format:\n"
            "• Item Name x5\n"
            "• 5x Item Name\n"
            "• Item Name (5)",
            ephemeral=True
        )
        return
    
    # Calculate totals
    total_volume = 0
    total_value = 0
    item_details = []
    
    for item in items:
        name_lower = item['name'].lower()
        qty = item['quantity']
        
        # Find item in database
        matched_item = None
        for db_name, db_data in ITEM_DATABASE.items():
            if db_name in name_lower or name_lower in db_name:
                matched_item = db_data
                break
        
        if matched_item:
            volume = matched_item['volume'] * qty
            total_volume += volume
            
            # Get Jita price if requested
            jita_price = 0
            if use_jita_prices and matched_item['type_id']:
                try:
                    price = await esi_client.get_jita_price(matched_item['type_id'])
                    if price:
                        jita_price = price * qty
                        total_value += jita_price
                except:
                    pass
            
            item_details.append({
                'name': item['name'],
                'quantity': qty,
                'volume': volume,
                'value': jita_price,
                'found': True
            })
        else:
            # Unknown item - estimate volume
            item_details.append({
                'name': item['name'],
                'quantity': qty,
                'volume': 0,
                'value': 0,
                'found': False
            })
    
    # Calculate JF cost
    result = calculate_jf_price(origin, destination, total_volume, total_value)
    
    if 'error' in result:
        await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)
        return
    
    # Build response
    embed = discord.Embed(
        title="📦 Cargo Analysis & JF Quote",
        description=f"Route: **{result['origin']}** → **{result['destination']}**",
        color=discord.Color.blue()
    )
    
    # Show items (limit to first 10)
    items_text = ""
    for item in item_details[:10]:
        if item['found']:
            value_str = f" ({format_isk(item['value'])})" if item['value'] > 0 else ""
            items_text += f"• {item['name']} x{item['quantity']} - {item['volume']:,.1f}m³{value_str}\n"
        else:
            items_text += f"• {item['name']} x{item['quantity']} - ⚠️ Unknown item\n"
    
    if len(item_details) > 10:
        items_text += f"*... and {len(item_details) - 10} more items*"
    
    embed.add_field(
        name=f"Items ({len(items)} types, {sum(i['quantity'] for i in items)} total)",
        value=items_text or "No items parsed",
        inline=False
    )
    
    # Totals
    embed.add_field(
        name="📊 Totals",
        value=f"Total Volume: **{total_volume:,.1f} m³**\n"
              f"Total Value: **{format_isk(total_value)}**\n"
              f"Unknown Items: **{sum(1 for i in item_details if not i['found'])}**",
        inline=False
    )
    
    # JF Cost
    volume_text = f"{result['volume']:,.0f}m³ × {result['base_rate']:.0f} ISK = {format_isk(result['base_price'])}"
    collateral_text = f"{format_isk(result['collateral'])} × 1% = {format_isk(result['collateral_fee'])}"
    
    embed.add_field(
        name="🚀 JF Shipping Cost",
        value=f"**Volume Charge:**\n```{volume_text}```\n"
              f"**Collateral Fee:**\n```{collateral_text}```\n"
              f"**Total: {format_isk(result['total_price'])}**",
        inline=False
    )
    
    embed.add_field(
        name="📋 To Book This Shipment",
        value=f"Use:\n`/jf_contract origin:{origin} destination:{destination} volume:{int(total_volume)} collateral:{int(total_value)} character_name:YOUR_NAME`",
        inline=False
    )
    
    # Show distance tier
    embed.add_field(
        name="📍 Distance Tier",
        value=f"{result['distance_desc']}\nRate: {result['base_rate']:.0f} ISK/m³",
        inline=True
    )
    
    await interaction.followup.send(embed=embed)

def format_isk(num):
    """Format ISK numbers nicely"""
    if num >= 1000000000:
        return f"{num/1000000000:.2f}B ISK"
    if num >= 1000000:
        return f"{num/1000000:.2f}M ISK"
    if num >= 1000:
        return f"{num/1000:.1f}K ISK"
    return f"{num:.0f} ISK"

@bot.tree.command(name="jf_help", description="Show JF bot help")
async def jf_help(interaction: discord.Interaction):
    """Display help for JF bot"""
    
    embed = discord.Embed(
        title="🚀 Jump Freighter Services - Help",
        description="Quick commands for JF shipping",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📦 Analyze Cargo",
        value="`/jf_cargo origin destination cargo`\n"
              "Paste cargo from EVE inventory to auto-calculate\n"
              "Example: `/jf_cargo RD-G2R Jita Drake x5 Raven x2`",
        inline=False
    )
    
    embed.add_field(
        name="💰 Get a Quote",
        value="`/jf origin destination volume collateral`\n"
              "Example: `/jf Jita D-PN 50000 1000000000`",
        inline=False
    )
    
    embed.add_field(
        name="📝 Book a Contract",
        value="`/jf_contract origin destination volume collateral character_name`\n"
              "Creates a contract in the system for JF pilots to accept",
        inline=False
    )
    
    embed.add_field(
        name="📊 Check Status",
        value="`/jf_status` - List your contracts\n"
              "`/jf_status contract_id:123` - View specific contract",
        inline=False
    )
    
    embed.add_field(
        name="💵 View Rates",
        value="`/jf_rates` - Show all current shipping rates",
        inline=False
    )
    
    embed.add_field(
        name="🌐 Full Services",
        value="For industry, trading, BPOs, and more:\n"
              "Visit the web dashboard (link in server pins)",
        inline=False
    )
    
    embed.set_footer(text="WinterCo JF Services | Pure Blind Region")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Bot events
@bot.event
async def on_ready():
    print(f'✅ JF Bot logged in as {bot.user}')
    print(f'🚀 Bot ID: {bot.user.id}')
    print(f'📊 Guilds: {len(bot.guilds)}')
    
    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'❌ Failed to sync commands: {e}')
    
    print("\n🎯 Available commands:")
    print("  /jf_cargo - Paste cargo to calculate cost")
    print("  /jf - Get shipping quote")
    print("  /jf_contract - Book contract")
    print("  /jf_status - Check contract status")
    print("  /jf_rates - View rates")
    print("  /jf_help - Show help")

# Initialize
def setup():
    """Initialize bot components"""
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Initialize database
    init_db()
    
    print("\n" + "="*50)
    print("🚀 WinterCo JF Services Bot")
    print("="*50)
    print("Features:")
    print("  ✅ Cargo calculator (paste from EVE)")
    print("  ✅ Jita price lookups via ESI")
    print("  ✅ Distance-based pricing")
    print("  ✅ Contract booking")
    print("  ✅ Status tracking")
    print("  ✅ 15+ WinterCo hub systems")
    print("\nFor full services, use the web dashboard")
    print("="*50 + "\n")

if __name__ == "__main__":
    setup()
    
    # Run bot
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Error: DISCORD_TOKEN not found in .env")
        exit(1)
    
    bot.run(token)
