import discord
from discord import app_commands
from discord.ext import commands, tasks
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import asyncio
import aiohttp
import math

load_dotenv()

# Import Capital Ships & Structures Database
try:
    from capital_database import ALL_CAPITAL_DATABASE, CAPITAL_COMPONENTS
    CAPITAL_DB_AVAILABLE = True
except ImportError:
    ALL_CAPITAL_DATABASE = []
    CAPITAL_COMPONENTS = []
    CAPITAL_DB_AVAILABLE = False
    print("Warning: capital_database.py not found. Capital ships will not be available.")

# Import Advanced Materials & Components
try:
    from advanced_materials_database import (
        ADVANCED_MATERIALS, REACTION_MATERIALS, T3_MATERIALS,
        SALVAGE_MATERIALS, ANCIENT_SALVAGE, ALL_COMPONENT_DATABASE
    )
    ADVANCED_DB_AVAILABLE = True
except ImportError:
    ADVANCED_MATERIALS = {}
    REACTION_MATERIALS = {}
    T3_MATERIALS = {}
    SALVAGE_MATERIALS = {}
    ANCIENT_SALVAGE = {}
    ALL_COMPONENT_DATABASE = []
    ADVANCED_DB_AVAILABLE = False
    print("Warning: advanced_materials_database.py not found. Advanced materials will not be available.")

# EVE ESI API Configuration
ESI_BASE_URL = "https://esi.evetech.net/latest"
JITA_SYSTEM_ID = 30000142  # Jita IV - Moon 4
MARKET_REGION_ID = 10000002  # The Forge

# ESI Client for API calls
class ESIClient:
    def __init__(self):
        self.session = None
        self.rate_limit_remaining = 100
        self.rate_limit_reset = datetime.now()
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def request(self, endpoint, params=None):
        """Make ESI API request with rate limiting"""
        await self._check_rate_limit()
        
        session = await self.get_session()
        url = f"{ESI_BASE_URL}{endpoint}"
        
        async with session.get(url, params=params) as response:
            # Update rate limit info
            self.rate_limit_remaining = int(response.headers.get('X-ESI-Error-Limit-Remain', 100))
            reset_time = int(response.headers.get('X-ESI-Error-Limit-Reset', 0))
            self.rate_limit_reset = datetime.now() + timedelta(seconds=reset_time)
            
            if response.status == 200:
                return await response.json()
            else:
                print(f"ESI API Error: {response.status} - {await response.text()}")
                return None
    
    async def _check_rate_limit(self):
        """Respect rate limits"""
        if self.rate_limit_remaining < 10:
            wait_time = (self.rate_limit_reset - datetime.now()).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
    
    # Character API
    async def get_character_info(self, character_id):
        """Get character public info"""
        return await self.request(f'/characters/{character_id}/')
    
    async def get_character_skills(self, character_id, access_token):
        """Get character skills (requires auth)"""
        session = await self.get_session()
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f"{ESI_BASE_URL}/characters/{character_id}/skills/"
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return None
    
    async def get_character_wallet(self, character_id, access_token):
        """Get character wallet balance (requires auth)"""
        session = await self.get_session()
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f"{ESI_BASE_URL}/characters/{character_id}/wallet/"
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return float(await response.text())
            return None
    
    async def get_character_location(self, character_id, access_token):
        """Get character current location (requires auth)"""
        session = await self.get_session()
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f"{ESI_BASE_URL}/characters/{character_id}/location/"
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return None
    
    async def get_character_ship(self, character_id, access_token):
        """Get character current ship (requires auth)"""
        session = await self.get_session()
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f"{ESI_BASE_URL}/characters/{character_id}/ship/"
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return None
    
    # Market API
    async def get_market_orders(self, region_id, type_id=None, order_type='all', page=1):
        """Get market orders for a region"""
        params = {'page': page}
        if type_id:
            params['type_id'] = type_id
        if order_type != 'all':
            params['order_type'] = order_type
        
        return await self.request(f'/markets/{region_id}/orders/', params)
    
    async def get_market_prices(self):
        """Get average market prices for all items"""
        return await self.request('/markets/prices/')
    
    async def get_type_info(self, type_id):
        """Get item type information"""
        return await self.request(f'/universe/types/{type_id}/')
    
    async def get_system_info(self, system_id):
        """Get system information"""
        return await self.request(f'/universe/systems/{system_id}/')
    
    async def search_character(self, name):
        """Search for character by name"""
        params = {'categories': 'character', 'search': name, 'strict': 'true'}
        result = await self.request('/search/', params)
        if result and 'character' in result:
            return result['character'][0]
        return None
    
    async def close(self):
        if self.session:
            await self.session.close()

# Initialize ESI client
esi_client = ESIClient()

# Market Cache for Jita prices
market_cache = {}
market_cache_time = {}
CACHE_DURATION = 300  # 5 minutes

async def get_jita_price(type_id):
    """Get Jita buy/sell prices with caching"""
    now = datetime.now()
    
    # Check cache
    if type_id in market_cache:
        cache_time = market_cache_time.get(type_id)
        if cache_time and (now - cache_time).seconds < CACHE_DURATION:
            return market_cache[type_id]
    
    # Fetch from ESI
    orders = await esi_client.get_market_orders(MARKET_REGION_ID, type_id)
    if not orders:
        return None
    
    buy_orders = [o for o in orders if o['is_buy_order']]
    sell_orders = [o for o in orders if not o['is_buy_order']]
    
    best_buy = max(buy_orders, key=lambda x: x['price']) if buy_orders else None
    best_sell = min(sell_orders, key=lambda x: x['price']) if sell_orders else None
    
    price_data = {
        'buy': best_buy['price'] if best_buy else 0,
        'sell': best_sell['price'] if best_sell else 0,
        'volume': sum(o['volume_remain'] for o in orders)
    }
    
    # Update cache
    market_cache[type_id] = price_data
    market_cache_time[type_id] = now
    
    return price_data

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Database setup
def init_db():
    conn = sqlite3.connect('data/eve_services.db')
    c = conn.cursor()
    
    # JF Contracts
    c.execute('''
        CREATE TABLE IF NOT EXISTS jf_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            volume_m3 REAL NOT NULL,
            collateral REAL NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')
    
    # Industry Jobs
    c.execute('''
        CREATE TABLE IF NOT EXISTS industry_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            material_cost REAL NOT NULL,
            sell_price REAL,
            profit REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # PI Colonies
    c.execute('''
        CREATE TABLE IF NOT EXISTS pi_colonies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            planet_name TEXT NOT NULL,
            planet_type TEXT NOT NULL,
            system TEXT NOT NULL,
            daily_profit REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # BPOs - Enhanced with ownership levels
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_bpos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL,
            character_name TEXT,
            bpo_name TEXT NOT NULL,
            me INTEGER DEFAULT 0,
            te INTEGER DEFAULT 0,
            location TEXT,
            ownership_level TEXT DEFAULT 'personal',
            corporation_id INTEGER,
            alliance_id INTEGER,
            is_shared BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Character ESI Authentication
    c.execute('''
        CREATE TABLE IF NOT EXISTS character_auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL UNIQUE,
            character_id INTEGER,
            character_name TEXT,
            corporation_id INTEGER,
            corporation_name TEXT,
            alliance_id INTEGER,
            alliance_name TEXT,
            access_token TEXT,
            refresh_token TEXT,
            token_expires_at TIMESTAMP,
            is_authenticated BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Corporations
    c.execute('''
        CREATE TABLE IF NOT EXISTS corporations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            corporation_id INTEGER UNIQUE NOT NULL,
            corporation_name TEXT NOT NULL,
            alliance_id INTEGER,
            ticker TEXT,
            ceo_character_id INTEGER,
            member_count INTEGER DEFAULT 0,
            tax_rate REAL DEFAULT 0.0,
            discord_guild_id TEXT,
            settings TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Corporation Members
    c.execute('''
        CREATE TABLE IF NOT EXISTS corporation_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            corporation_id INTEGER NOT NULL,
            character_id INTEGER NOT NULL,
            character_name TEXT,
            discord_user_id TEXT,
            roles TEXT,
            joined_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            UNIQUE(corporation_id, character_id)
        )
    ''')
    
    # Alliances
    c.execute('''
        CREATE TABLE IF NOT EXISTS alliances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alliance_id INTEGER UNIQUE NOT NULL,
            alliance_name TEXT NOT NULL,
            ticker TEXT,
            executor_corp_id INTEGER,
            member_count INTEGER DEFAULT 0,
            discord_guild_id TEXT,
            settings TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Alliance Corporations
    c.execute('''
        CREATE TABLE IF NOT EXISTS alliance_corporations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alliance_id INTEGER NOT NULL,
            corporation_id INTEGER NOT NULL,
            joined_at TIMESTAMP,
            UNIQUE(alliance_id, corporation_id)
        )
    ''')
    
    # Shared Assets (Corp/Alliance level)
    c.execute('''
        CREATE TABLE IF NOT EXISTS shared_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_type TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            asset_type TEXT NOT NULL,
            asset_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            location TEXT,
            status TEXT DEFAULT 'available',
            checked_out_by TEXT,
            checked_out_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Industry Jobs - Enhanced with corp/alliance tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS industry_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL,
            character_id INTEGER,
            character_name TEXT NOT NULL,
            corporation_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            material_cost REAL NOT NULL,
            sell_price REAL,
            profit REAL,
            status TEXT DEFAULT 'pending',
            job_type TEXT DEFAULT 'personal',
            facility_location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Access Control / Permissions
    c.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            permission_name TEXT NOT NULL,
            granted_by TEXT,
            granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(entity_type, entity_id, permission_name)
        )
    ''')
    
    # Activity Log
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,
            character_id INTEGER,
            action TEXT,
            entity_type TEXT,
            entity_id INTEGER,
            details TEXT,
            ip_address TEXT
        )
    ''')
    
    # Contracts
    c.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL,
            contract_type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            total_value REAL NOT NULL,
            station TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect('data/eve_services.db')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Player Locations
player_locations = {}

# WinterCo Systems
WINTERCO_SYSTEMS = {
    'D-PN': {'region': 'Pure Blind', 'stations': ['D-PN Solar Fleet']},
    'VA6-ED': {'region': 'Pure Blind', 'stations': ['VA6-ED Keepstar']},
    'RD-G2R': {'region': 'Pure Blind', 'stations': ['RD-G2R Industry Hub']},
    'O-BKJY': {'region': 'Pure Blind', 'stations': []},
    'Jita': {'region': 'The Forge', 'stations': ['Jita IV - Moon 4']}
}

# Base Market Prices (Jita baseline)
BASE_PRICES = {
    'Tritanium': 6, 'Pyerite': 12, 'Mexallon': 85, 'Isogen': 120,
    'Nocxium': 450, 'Zydrine': 1200, 'Megacyte': 2800
}

# Local Markdowns for buying IN nullsec (discounts)
# Format: location -> markdown percentage (negative = discount)
LOCAL_MARKDOWNS = {
    'RD-G2R': 0.05,    # 5% markdown (95% of Jita price)
    'VA6-ED': 0.08,    # 8% markdown (92% of Jita price)
    'D-PN': 0.10,      # 10% markdown (90% of Jita price)
    'O-BKJY': 0.12     # 12% markdown (88% of Jita price)
}

# Import Markups for shipping FROM empire TO nullsec
IMPORT_MARKUPS = {
    'RD-G2R': 0.10,    # 10% markup
    'VA6-ED': 0.15,    # 15% markup
    'D-PN': 0.20,      # 20% markup
    'O-BKJY': 0.25     # 25% markup
}

def get_local_prices(location):
    """Get prices when buying locally in nullsec (with markdown)"""
    if location.upper() == 'Jita':
        return BASE_PRICES.copy()
    
    markdown = LOCAL_MARKDOWNS.get(location.upper(), 0.05)  # Default 5%
    return {item: int(price * (1 - markdown)) for item, price in BASE_PRICES.items()}

def get_import_prices(from_loc, to_loc):
    """Get prices when importing from empire to nullsec (with markup)"""
    if from_loc.upper() != 'JITA':
        # Not importing from Jita, use local prices
        return get_local_prices(to_loc)
    
    markup = IMPORT_MARKUPS.get(to_loc.upper(), 0.15)  # Default 15%
    return {item: int(price * (1 + markup)) for item, price in BASE_PRICES.items()}

# Backwards compatibility alias
MARKET_PRICES = {loc: get_local_prices(loc) for loc in ['Jita', 'D-PN', 'VA6-ED', 'RD-G2R', 'O-BKJY']}

@bot.tree.command(name="iam", description="Set your current location in EVE")
@app_commands.describe(system="System name (e.g., D-PN, VA6-ED, Jita)")
async def iam_cmd(interaction: discord.Interaction, system: str):
    """Player sets their current location"""
    system_upper = system.upper()
    
    if system_upper not in WINTERCO_SYSTEMS and system_upper != 'JITA':
        available = ', '.join(WINTERCO_SYSTEMS.keys())
        await interaction.response.send_message(
            f"❌ System not recognized. Available: {available}, Jita",
            ephemeral=True
        )
        return
    
    player_locations[str(interaction.user.id)] = {
        'system': system_upper,
        'set_at': datetime.now().isoformat()
    }
    
    system_info = WINTERCO_SYSTEMS.get(system_upper, {'region': 'Unknown', 'stations': []})
    stations_text = '\n'.join([f"• {s}" for s in system_info['stations']]) if system_info['stations'] else "• No stations"
    
    embed = discord.Embed(
        title=f"📍 Location Set: {system_upper}",
        color=discord.Color.green()
    )
    embed.add_field(name="Region", value=system_info['region'], inline=True)
    embed.add_field(name="Stations", value=stations_text, inline=False)
    embed.set_footer(text="Your location is used for price quotes and JF calculations")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="whereami", description="Check your current location")
async def whereami_cmd(interaction: discord.Interaction):
    """Check where the player is currently located"""
    user_id = str(interaction.user.id)
    
    if user_id not in player_locations:
        await interaction.response.send_message(
            "❌ You haven't set your location. Use `/iam system:NAME` to set it.\n\n"
            "Example: `/iam system:D-PN`",
            ephemeral=True
        )
        return
    
    location = player_locations[user_id]
    system_info = WINTERCO_SYSTEMS.get(location['system'], {'region': 'Unknown', 'stations': []})
    
    embed = discord.Embed(
        title=f"📍 You are in: {location['system']}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Region", value=system_info['region'], inline=True)
    embed.add_field(name="Set at", value=location['set_at'][:19], inline=True)
    
    if system_info['stations']:
        embed.add_field(
            name="Local Stations",
            value='\n'.join([f"• {s}" for s in system_info['stations']]),
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="price", description="Check prices at your location or Jita")
@app_commands.describe(
    item="Item to check prices for",
    location="Check prices at specific location (default: your location)"
)
async def price_cmd(interaction: discord.Interaction, item: str, location: str = None):
    """Get price quotes for items at player's location"""
    user_id = str(interaction.user.id)
    
    # Determine location
    if location:
        loc = location.upper()
    elif user_id in player_locations:
        loc = player_locations[user_id]['system']
    else:
        loc = 'Jita'
    
    if loc not in MARKET_PRICES:
        await interaction.response.send_message(
            f"❌ No price data for {loc}. Available: {', '.join(MARKET_PRICES.keys())}",
            ephemeral=True
        )
        return
    
    # Get appropriate pricing based on location
    if loc == 'Jita':
        prices = BASE_PRICES
        jita_prices = BASE_PRICES
        loc_label = "Jita (Base Prices)"
    else:
        prices = get_local_prices(loc)
        jita_prices = BASE_PRICES
        markdown = LOCAL_MARKDOWNS.get(loc, 0.05)
        loc_label = f"{loc} ({markdown*100:.0f}% Local Markdown)"
    
    embed = discord.Embed(
        title=f"💰 Prices: {item}",
        description=f"Location: **{loc_label}**",
        color=discord.Color.gold()
    )
    
    # Show material prices comparison
    for mat in ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium', 'Zydrine']:
        if mat in prices:
            loc_price = prices[mat]
            jita_price = jita_prices.get(mat, 0)
            diff = loc_price - jita_price
            diff_pct = (diff / jita_price * 100) if jita_price > 0 else 0
            
            if loc == 'Jita':
                arrow = "➡️"
                status = "Baseline"
            elif diff < 0:
                arrow = "✅"
                status = f"{abs(diff_pct):.1f}% cheaper"
            else:
                arrow = "📈"
                status = f"{diff_pct:+.1f}% vs Jita"
            
            embed.add_field(
                name=f"{mat}",
                value=f"{loc_price:,} ISK\n{arrow} {status}",
                inline=True
            )
    
    # Show pricing context
    if loc != 'Jita':
        markdown = LOCAL_MARKDOWNS.get(loc, 0.05)
        import_markup = IMPORT_MARKUPS.get(loc, 0.15)
        jf_cost_per_m3 = 1500  # Jita to nullsec rate
        
        embed.add_field(
            name="💡 Pricing Info",
            value=f"✅ **Local Buy:** {markdown*100:.0f}% markdown (shown above)\n"
                  f"📦 **Import from Jita:** {import_markup*100:.0f}% markup\n"
                  f"🚀 **JF Rate:** {jf_cost_per_m3:,} ISK/m³",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="find", description="Search for items and where to buy them")
@app_commands.describe(item="Item you're looking for")
async def find_cmd(interaction: discord.Interaction, item: str):
    """Search for items and show where to buy them"""
    user_id = str(interaction.user.id)
    user_location = player_locations.get(user_id, {}).get('system', 'Jita')
    
    # Search BPO database
    matching_bpos = [b for b in BPO_DATABASE if item.lower() in b['name'].lower()]
    
    embed = discord.Embed(
        title=f"🔍 Search Results: {item}",
        color=discord.Color.blue()
    )
    
    # Show player's location context
    embed.add_field(
        name="Your Location",
        value=user_location,
        inline=False
    )
    
    if matching_bpos:
        for bpo in matching_bpos[:3]:  # Show first 3 matches
            # Calculate costs for both local and import
            if user_location == 'Jita':
                material_cost_jita = sum(
                    m['quantity'] * BASE_PRICES.get(m['name'], 0)
                    for m in bpo['materials']
                )
                value_text = f"Base Cost: {bpo['base_cost']:,.0f} ISK\n" \
                           f"Material Cost (Jita): {material_cost_jita:,.0f} ISK\n" \
                           f"Build Time: {bpo['build_time']//3600}h"
            else:
                # Local prices (markdown)
                local_prices = get_local_prices(user_location)
                material_cost_local = sum(
                    m['quantity'] * local_prices.get(m['name'], 0)
                    for m in bpo['materials']
                )
                
                # Import prices (markup from Jita)
                import_prices = get_import_prices('Jita', user_location)
                material_cost_import = sum(
                    m['quantity'] * import_prices.get(m['name'], 0)
                    for m in bpo['materials']
                )
                
                markdown_pct = LOCAL_MARKDOWNS.get(user_location, 0.05) * 100
                import_pct = IMPORT_MARKUPS.get(user_location, 0.15) * 100
                savings = material_cost_import - material_cost_local
                
                value_text = f"Base Cost: {bpo['base_cost']:,.0f} ISK\n" \
                           f"✅ Local ({user_location}): {material_cost_local:,.0f} ISK (-{markdown_pct:.0f}%)\n" \
                           f"📦 Import (Jita→{user_location}): {material_cost_import:,.0f} ISK (+{import_pct:.0f}%)\n" \
                           f"💰 **Save {savings:,.0f} ISK locally!**\n" \
                           f"Build Time: {bpo['build_time']//3600}h"
            
            embed.add_field(
                name=f"📘 {bpo['name']}",
                value=value_text,
                inline=False
            )
    else:
        embed.add_field(
            name="No BPOs found",
            value="Try searching for a different item name",
            inline=False
        )
    
    # Show purchase recommendations
    if user_location != 'Jita':
        markdown = LOCAL_MARKDOWNS.get(user_location, 0.05)
        embed.add_field(
            name="💡 Recommendation",
            value=f"✅ Buy locally in {user_location} for {markdown*100:.0f}% discount vs Jita prices!\n"
                  f"📦 Only import if item not available locally\n"
                  f"Use `/buyquote` for complete shipping quotes!",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="buyquote", description="Get a quote to buy and ship an item")
@app_commands.describe(
    item="Item to buy",
    quantity="How many",
    from_location="Where to buy from (default: Jita)",
    to_location="Where to deliver (default: your location)"
)
async def buyquote_cmd(
    interaction: discord.Interaction,
    item: str,
    quantity: int = 1,
    from_location: str = "Jita",
    to_location: str = None
):
    """Get complete quote: item cost + shipping"""
    user_id = str(interaction.user.id)
    
    # Determine destination
    if to_location:
        dest = to_location.upper()
    elif user_id in player_locations:
        dest = player_locations[user_id]['system']
    else:
        await interaction.response.send_message(
            "❌ Please set your location with `/iam system:NAME` first!",
            ephemeral=True
        )
        return
    
    from_loc = from_location.upper()
    
    # Find item in database
    bpo = next((b for b in BPO_DATABASE if item.lower() in b['name'].lower()), None)
    
    if not bpo:
        await interaction.response.send_message(
            f"❌ Item '{item}' not found in database. Try `/find item:{item}`",
            ephemeral=True
        )
        return
    
    # Calculate costs
    volume = bpo.get('volume', 1) * quantity
    is_jita = from_loc == 'JITA' or 'jita' in from_loc.lower()
    
    # Shipping calculation
    if is_jita and dest != 'JITA':
        shipping_rate = 1500  # Jita to null
    elif dest == 'JITA':
        shipping_rate = 1200  # Null to Jita
    else:
        shipping_rate = 800  # Null to null
    
    shipping_cost = volume * shipping_rate
    
    # Calculate material cost based on location and import status
    base_item_cost = bpo['base_cost'] * quantity
    
    if is_jita and dest != 'JITA':
        # Importing from Jita to nullsec - use import markup
        import_prices = get_import_prices('Jita', dest)
        markup_pct = IMPORT_MARKUPS.get(dest, 0.15)
        item_cost = int(base_item_cost * (1 + markup_pct))
        price_type = f"Import Price (+{markup_pct*100:.0f}% markup)"
    elif dest == 'Jita':
        # Buying in Jita - base price
        item_cost = base_item_cost
        price_type = "Jita Price"
    else:
        # Buying locally in nullsec - use local markdown
        local_prices = get_local_prices(dest)
        markdown_pct = LOCAL_MARKDOWNS.get(dest, 0.05)
        item_cost = int(base_item_cost * (1 - markdown_pct))
        price_type = f"Local Price (-{markdown_pct*100:.0f}% markdown)"
    
    total_cost = item_cost + shipping_cost
    
    embed = discord.Embed(
        title=f"💰 Buy & Ship Quote: {item}",
        description=f"Route: **{from_loc}** → **{dest}**",
        color=discord.Color.green()
    )
    embed.add_field(name="Item", value=item, inline=True)
    embed.add_field(name="Quantity", value=f"{quantity:,}", inline=True)
    embed.add_field(name="Volume", value=f"{volume:,.0f} m³", inline=True)
    
    embed.add_field(name=price_type, value=f"{item_cost:,.0f} ISK", inline=True)
    embed.add_field(name="Shipping", value=f"{shipping_cost:,.0f} ISK", inline=True)
    embed.add_field(name="Total Cost", value=f"**{total_cost:,.0f} ISK**", inline=True)
    
    # Show comparison
    if dest != 'Jita':
        local_cost = int(base_item_cost * (1 - LOCAL_MARKDOWNS.get(dest, 0.05)))
        import_cost = int(base_item_cost * (1 + IMPORT_MARKUPS.get(dest, 0.15)))
        savings = import_cost - local_cost
        
        embed.add_field(
            name="📊 Price Comparison",
            value=f"Local buy: {local_cost:,.0f} ISK ({LOCAL_MARKDOWNS.get(dest, 0.05)*100:.0f}% off)\n"
                  f"Import buy: {import_cost:,.0f} ISK ({IMPORT_MARKUPS.get(dest, 0.15)*100:.0f}% markup)\n"
                  f"💰 **Save {savings:,.0f} ISK buying locally!**",
            inline=False
        )
    
    # Context-aware advice
    if dest == 'D-PN':
        embed.add_field(
            name="💡 WinterCo Tip",
            value="D-PN is the primary hub. Check local contracts first for best prices!",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

# BPO Database with Materials
BPO_DATABASE = [
    # T1 FRIGATES
    {'id': 1, 'name': 'Atron Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 850000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 28000}, {'name': 'Pyerite', 'quantity': 8500}, {'name': 'Mexallon', 'quantity': 2000}]},
    {'id': 2, 'name': 'Incursus Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 900000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 30000}, {'name': 'Pyerite', 'quantity': 9000}, {'name': 'Mexallon', 'quantity': 2200}]},
    {'id': 3, 'name': 'Tristan Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 920000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 31000}, {'name': 'Pyerite', 'quantity': 9200}, {'name': 'Mexallon', 'quantity': 2300}]},
    {'id': 4, 'name': 'Navitas Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 850000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 28000}, {'name': 'Pyerite', 'quantity': 8500}, {'name': 'Mexallon', 'quantity': 2000}]},
    {'id': 5, 'name': 'Imicus Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 880000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 29000}, {'name': 'Pyerite', 'quantity': 8800}, {'name': 'Mexallon', 'quantity': 2100}]},
    
    # CALDARI FRIGATES
    {'id': 10, 'name': 'Merlin Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 870000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 29000}, {'name': 'Pyerite', 'quantity': 8700}, {'name': 'Mexallon', 'quantity': 2150}]},
    {'id': 11, 'name': 'Kestrel Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 860000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 28500}, {'name': 'Pyerite', 'quantity': 8600}, {'name': 'Mexallon', 'quantity': 2100}]},
    {'id': 12, 'name': 'Condor Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 830000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 27500}, {'name': 'Pyerite', 'quantity': 8300}, {'name': 'Mexallon', 'quantity': 1950}]},
    {'id': 13, 'name': 'Bantam Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 840000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 28000}, {'name': 'Pyerite', 'quantity': 8400}, {'name': 'Mexallon', 'quantity': 2000}]},
    {'id': 14, 'name': 'Griffin Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 890000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 29500}, {'name': 'Pyerite', 'quantity': 8900}, {'name': 'Mexallon', 'quantity': 2200}]},
    
    # MINMATAR FRIGATES
    {'id': 20, 'name': 'Rifter Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 890000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 29600}, {'name': 'Pyerite', 'quantity': 8900}, {'name': 'Mexallon', 'quantity': 2250}]},
    {'id': 21, 'name': 'Slasher Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 850000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 28200}, {'name': 'Pyerite', 'quantity': 8500}, {'name': 'Mexallon', 'quantity': 2000}]},
    {'id': 22, 'name': 'Breacher Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 860000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 28600}, {'name': 'Pyerite', 'quantity': 8600}, {'name': 'Mexallon', 'quantity': 2050}]},
    {'id': 23, 'name': 'Probe Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 880000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 29200}, {'name': 'Pyerite', 'quantity': 8800}, {'name': 'Mexallon', 'quantity': 2150}]},
    {'id': 24, 'name': 'Vigil Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 910000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 30200}, {'name': 'Pyerite', 'quantity': 9100}, {'name': 'Mexallon', 'quantity': 2300}]},
    
    # AMARR FRIGATES
    {'id': 30, 'name': 'Punisher Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 900000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 30000}, {'name': 'Pyerite', 'quantity': 9000}, {'name': 'Mexallon', 'quantity': 2250}]},
    {'id': 31, 'name': 'Executioner Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 860000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 28600}, {'name': 'Pyerite', 'quantity': 8600}, {'name': 'Mexallon', 'quantity': 2050}]},
    {'id': 32, 'name': 'Tormentor Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 880000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 29200}, {'name': 'Pyerite', 'quantity': 8800}, {'name': 'Mexallon', 'quantity': 2150}]},
    {'id': 33, 'name': 'Magnate Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 870000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 29000}, {'name': 'Pyerite', 'quantity': 8700}, {'name': 'Mexallon', 'quantity': 2100}]},
    {'id': 34, 'name': 'Crucifier Blueprint', 'category': 't1_ships', 'group': 'Frigates', 'volume': 2500, 'base_cost': 920000, 'build_time': 18000, 'materials': [
        {'name': 'Tritanium', 'quantity': 30500}, {'name': 'Pyerite', 'quantity': 9200}, {'name': 'Mexallon', 'quantity': 2350}]},
    
    # T1 DESTROYERS
    {'id': 50, 'name': 'Algos Blueprint', 'category': 't1_ships', 'group': 'Destroyers', 'volume': 5000, 'base_cost': 3200000, 'build_time': 36000, 'materials': [
        {'name': 'Tritanium', 'quantity': 85000}, {'name': 'Pyerite', 'quantity': 28000}, {'name': 'Mexallon', 'quantity': 6500}, {'name': 'Isogen', 'quantity': 1200}]},
    {'id': 51, 'name': 'Catalyst Blueprint', 'category': 't1_ships', 'group': 'Destroyers', 'volume': 5000, 'base_cost': 3100000, 'build_time': 36000, 'materials': [
        {'name': 'Tritanium', 'quantity': 82000}, {'name': 'Pyerite', 'quantity': 27500}, {'name': 'Mexallon', 'quantity': 6300}, {'name': 'Isogen', 'quantity': 1150}]},
    {'id': 52, 'name': 'Cormorant Blueprint', 'category': 't1_ships', 'group': 'Destroyers', 'volume': 5000, 'base_cost': 3300000, 'build_time': 36000, 'materials': [
        {'name': 'Tritanium', 'quantity': 88000}, {'name': 'Pyerite', 'quantity': 29000}, {'name': 'Mexallon', 'quantity': 6800}, {'name': 'Isogen', 'quantity': 1250}]},
    {'id': 53, 'name': 'Thrasher Blueprint', 'category': 't1_ships', 'group': 'Destroyers', 'volume': 5000, 'base_cost': 3250000, 'build_time': 36000, 'materials': [
        {'name': 'Tritanium', 'quantity': 86000}, {'name': 'Pyerite', 'quantity': 28500}, {'name': 'Mexallon', 'quantity': 6600}, {'name': 'Isogen', 'quantity': 1200}]},
    {'id': 54, 'name': 'Coercer Blueprint', 'category': 't1_ships', 'group': 'Destroyers', 'volume': 5000, 'base_cost': 3350000, 'build_time': 36000, 'materials': [
        {'name': 'Tritanium', 'quantity': 89000}, {'name': 'Pyerite', 'quantity': 29500}, {'name': 'Mexallon', 'quantity': 6900}, {'name': 'Isogen', 'quantity': 1300}]},
    
    # T1 CRUISERS
    {'id': 60, 'name': 'Vexor Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 12500000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 320000}, {'name': 'Pyerite', 'quantity': 105000}, {'name': 'Mexallon', 'quantity': 25000}, {'name': 'Isogen', 'quantity': 5200}, {'name': 'Nocxium', 'quantity': 850}]},
    {'id': 61, 'name': 'Thorax Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 11800000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 305000}, {'name': 'Pyerite', 'quantity': 100000}, {'name': 'Mexallon', 'quantity': 23800}, {'name': 'Isogen', 'quantity': 4950}, {'name': 'Nocxium', 'quantity': 800}]},
    {'id': 62, 'name': 'Celestis Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 11500000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 298000}, {'name': 'Pyerite', 'quantity': 98000}, {'name': 'Mexallon', 'quantity': 23200}, {'name': 'Isogen', 'quantity': 4850}, {'name': 'Nocxium', 'quantity': 780}]},
    {'id': 63, 'name': 'Exequror Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 12200000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 312000}, {'name': 'Pyerite', 'quantity': 103000}, {'name': 'Mexallon', 'quantity': 24500}, {'name': 'Isogen', 'quantity': 5100}, {'name': 'Nocxium', 'quantity': 820}]},
    
    # CALDARI CRUISERS
    {'id': 70, 'name': 'Caracal Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 12800000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 325000}, {'name': 'Pyerite', 'quantity': 108000}, {'name': 'Mexallon', 'quantity': 25500}, {'name': 'Isogen', 'quantity': 5300}, {'name': 'Nocxium', 'quantity': 870}]},
    {'id': 71, 'name': 'Osprey Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 12400000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 315000}, {'name': 'Pyerite', 'quantity': 104000}, {'name': 'Mexallon', 'quantity': 24800}, {'name': 'Isogen', 'quantity': 5150}, {'name': 'Nocxium', 'quantity': 840}]},
    {'id': 72, 'name': 'Blackbird Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 12000000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 310000}, {'name': 'Pyerite', 'quantity': 102000}, {'name': 'Mexallon', 'quantity': 24000}, {'name': 'Isogen', 'quantity': 5000}, {'name': 'Nocxium', 'quantity': 820}]},
    {'id': 73, 'name': 'Moa Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 13000000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 330000}, {'name': 'Pyerite', 'quantity': 110000}, {'name': 'Mexallon', 'quantity': 26000}, {'name': 'Isogen', 'quantity': 5400}, {'name': 'Nocxium', 'quantity': 890}]},
    
    # MINMATAR CRUISERS
    {'id': 80, 'name': 'Stabber Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 12600000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 322000}, {'name': 'Pyerite', 'quantity': 106000}, {'name': 'Mexallon', 'quantity': 25200}, {'name': 'Isogen', 'quantity': 5250}, {'name': 'Nocxium', 'quantity': 860}]},
    {'id': 81, 'name': 'Scythe Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 12300000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 314000}, {'name': 'Pyerite', 'quantity': 103500}, {'name': 'Mexallon', 'quantity': 24600}, {'name': 'Isogen', 'quantity': 5125}, {'name': 'Nocxium', 'quantity': 835}]},
    {'id': 82, 'name': 'Bellicose Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 11900000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 306000}, {'name': 'Pyerite', 'quantity': 101000}, {'name': 'Mexallon', 'quantity': 23800}, {'name': 'Isogen', 'quantity': 4975}, {'name': 'Nocxium', 'quantity': 805}]},
    {'id': 83, 'name': 'Rupture Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 12900000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 328000}, {'name': 'Pyerite', 'quantity': 109000}, {'name': 'Mexallon', 'quantity': 25800}, {'name': 'Isogen', 'quantity': 5350}, {'name': 'Nocxium', 'quantity': 880}]},
    
    # AMARR CRUISERS
    {'id': 90, 'name': 'Maller Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 13100000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 332000}, {'name': 'Pyerite', 'quantity': 111000}, {'name': 'Mexallon', 'quantity': 26200}, {'name': 'Isogen', 'quantity': 5450}, {'name': 'Nocxium', 'quantity': 895}]},
    {'id': 91, 'name': 'Augoror Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 12700000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 324000}, {'name': 'Pyerite', 'quantity': 107000}, {'name': 'Mexallon', 'quantity': 25400}, {'name': 'Isogen', 'quantity': 5280}, {'name': 'Nocxium', 'quantity': 865}]},
    {'id': 92, 'name': 'Arbitrator Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 12100000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 308000}, {'name': 'Pyerite', 'quantity': 102000}, {'name': 'Mexallon', 'quantity': 24200}, {'name': 'Isogen', 'quantity': 5050}, {'name': 'Nocxium', 'quantity': 810}]},
    {'id': 93, 'name': 'Omen Blueprint', 'category': 't1_ships', 'group': 'Cruisers', 'volume': 10000, 'base_cost': 13200000, 'build_time': 54000, 'materials': [
        {'name': 'Tritanium', 'quantity': 335000}, {'name': 'Pyerite', 'quantity': 112000}, {'name': 'Mexallon', 'quantity': 26500}, {'name': 'Isogen', 'quantity': 5500}, {'name': 'Nocxium', 'quantity': 900}]},
    
    # T1 BATTLECRUISERS
    {'id': 100, 'name': 'Drake Blueprint', 'category': 't1_ships', 'group': 'Battlecruisers', 'volume': 15000, 'base_cost': 58000000, 'build_time': 108000, 'materials': [
        {'name': 'Tritanium', 'quantity': 850000}, {'name': 'Pyerite', 'quantity': 280000}, {'name': 'Mexallon', 'quantity': 68000}, 
        {'name': 'Isogen', 'quantity': 15000}, {'name': 'Nocxium', 'quantity': 2800}, {'name': 'Zydrine', 'quantity': 700}]},
    {'id': 101, 'name': 'Ferox Blueprint', 'category': 't1_ships', 'group': 'Battlecruisers', 'volume': 15000, 'base_cost': 57000000, 'build_time': 108000, 'materials': [
        {'name': 'Tritanium', 'quantity': 840000}, {'name': 'Pyerite', 'quantity': 275000}, {'name': 'Mexallon', 'quantity': 67000}, 
        {'name': 'Isogen', 'quantity': 14800}, {'name': 'Nocxium', 'quantity': 2750}, {'name': 'Zydrine', 'quantity': 680}]},
    {'id': 102, 'name': 'Brutix Blueprint', 'category': 't1_ships', 'group': 'Battlecruisers', 'volume': 15000, 'base_cost': 56000000, 'build_time': 108000, 'materials': [
        {'name': 'Tritanium', 'quantity': 830000}, {'name': 'Pyerite', 'quantity': 270000}, {'name': 'Mexallon', 'quantity': 66000}, 
        {'name': 'Isogen', 'quantity': 14500}, {'name': 'Nocxium', 'quantity': 2700}, {'name': 'Zydrine', 'quantity': 660}]},
    {'id': 103, 'name': 'Myrmidon Blueprint', 'category': 't1_ships', 'group': 'Battlecruisers', 'volume': 15000, 'base_cost': 55000000, 'build_time': 108000, 'materials': [
        {'name': 'Tritanium', 'quantity': 820000}, {'name': 'Pyerite', 'quantity': 265000}, {'name': 'Mexallon', 'quantity': 65000}, 
        {'name': 'Isogen', 'quantity': 14200}, {'name': 'Nocxium', 'quantity': 2650}, {'name': 'Zydrine', 'quantity': 640}]},
    {'id': 104, 'name': 'Hurricane Blueprint', 'category': 't1_ships', 'group': 'Battlecruisers', 'volume': 15000, 'base_cost': 57500000, 'build_time': 108000, 'materials': [
        {'name': 'Tritanium', 'quantity': 845000}, {'name': 'Pyerite', 'quantity': 278000}, {'name': 'Mexallon', 'quantity': 67500}, 
        {'name': 'Isogen', 'quantity': 14900}, {'name': 'Nocxium', 'quantity': 2780}, {'name': 'Zydrine', 'quantity': 690}]},
    {'id': 105, 'name': 'Cyclone Blueprint', 'category': 't1_ships', 'group': 'Battlecruisers', 'volume': 15000, 'base_cost': 56500000, 'build_time': 108000, 'materials': [
        {'name': 'Tritanium', 'quantity': 835000}, {'name': 'Pyerite', 'quantity': 272000}, {'name': 'Mexallon', 'quantity': 66500}, 
        {'name': 'Isogen', 'quantity': 14600}, {'name': 'Nocxium', 'quantity': 2720}, {'name': 'Zydrine', 'quantity': 670}]},
    {'id': 106, 'name': 'Harbinger Blueprint', 'category': 't1_ships', 'group': 'Battlecruisers', 'volume': 15000, 'base_cost': 58500000, 'build_time': 108000, 'materials': [
        {'name': 'Tritanium', 'quantity': 860000}, {'name': 'Pyerite', 'quantity': 285000}, {'name': 'Mexallon', 'quantity': 69000}, 
        {'name': 'Isogen', 'quantity': 15200}, {'name': 'Nocxium', 'quantity': 2850}, {'name': 'Zydrine', 'quantity': 710}]},
    {'id': 107, 'name': 'Prophecy Blueprint', 'category': 't1_ships', 'group': 'Battlecruisers', 'volume': 15000, 'base_cost': 59000000, 'build_time': 108000, 'materials': [
        {'name': 'Tritanium', 'quantity': 870000}, {'name': 'Pyerite', 'quantity': 290000}, {'name': 'Mexallon', 'quantity': 70000}, 
        {'name': 'Isogen', 'quantity': 15500}, {'name': 'Nocxium', 'quantity': 2900}, {'name': 'Zydrine', 'quantity': 720}]},
    
    # T1 BATTLESHIPS
    {'id': 120, 'name': 'Raven Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 285000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3200000}, {'name': 'Pyerite', 'quantity': 1100000}, {'name': 'Mexallon', 'quantity': 280000}, 
        {'name': 'Isogen', 'quantity': 65000}, {'name': 'Nocxium', 'quantity': 13500}, {'name': 'Zydrine', 'quantity': 3800}, {'name': 'Megacyte', 'quantity': 850}]},
    {'id': 121, 'name': 'Scorpion Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 290000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3250000}, {'name': 'Pyerite', 'quantity': 1120000}, {'name': 'Mexallon', 'quantity': 285000}, 
        {'name': 'Isogen', 'quantity': 66000}, {'name': 'Nocxium', 'quantity': 13800}, {'name': 'Zydrine', 'quantity': 3900}, {'name': 'Megacyte', 'quantity': 870}]},
    {'id': 122, 'name': 'Rokh Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 280000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3150000}, {'name': 'Pyerite', 'quantity': 1080000}, {'name': 'Mexallon', 'quantity': 275000}, 
        {'name': 'Isogen', 'quantity': 64000}, {'name': 'Nocxium', 'quantity': 13200}, {'name': 'Zydrine', 'quantity': 3700}, {'name': 'Megacyte', 'quantity': 830}]},
    {'id': 123, 'name': 'Megathron Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 275000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3100000}, {'name': 'Pyerite', 'quantity': 1050000}, {'name': 'Mexallon', 'quantity': 268000}, 
        {'name': 'Isogen', 'quantity': 62500}, {'name': 'Nocxium', 'quantity': 12800}, {'name': 'Zydrine', 'quantity': 3600}, {'name': 'Megacyte', 'quantity': 800}]},
    {'id': 124, 'name': 'Dominix Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 270000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3050000}, {'name': 'Pyerite', 'quantity': 1020000}, {'name': 'Mexallon', 'quantity': 260000}, 
        {'name': 'Isogen', 'quantity': 61000}, {'name': 'Nocxium', 'quantity': 12500}, {'name': 'Zydrine', 'quantity': 3500}, {'name': 'Megacyte', 'quantity': 780}]},
    {'id': 125, 'name': 'Hyperion Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 278000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3120000}, {'name': 'Pyerite', 'quantity': 1060000}, {'name': 'Mexallon', 'quantity': 270000}, 
        {'name': 'Isogen', 'quantity': 63000}, {'name': 'Nocxium', 'quantity': 13000}, {'name': 'Zydrine', 'quantity': 3650}, {'name': 'Megacyte', 'quantity': 820}]},
    {'id': 126, 'name': 'Tempest Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 277000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3110000}, {'name': 'Pyerite', 'quantity': 1055000}, {'name': 'Mexallon', 'quantity': 269000}, 
        {'name': 'Isogen', 'quantity': 62800}, {'name': 'Nocxium', 'quantity': 12900}, {'name': 'Zydrine', 'quantity': 3620}, {'name': 'Megacyte', 'quantity': 815}]},
    {'id': 127, 'name': 'Typhoon Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 272000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3060000}, {'name': 'Pyerite', 'quantity': 1025000}, {'name': 'Mexallon', 'quantity': 262000}, 
        {'name': 'Isogen', 'quantity': 61500}, {'name': 'Nocxium', 'quantity': 12600}, {'name': 'Zydrine', 'quantity': 3550}, {'name': 'Megacyte', 'quantity': 790}]},
    {'id': 128, 'name': 'Maelstrom Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 282000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3180000}, {'name': 'Pyerite', 'quantity': 1090000}, {'name': 'Mexallon', 'quantity': 276000}, 
        {'name': 'Isogen', 'quantity': 64500}, {'name': 'Nocxium', 'quantity': 13400}, {'name': 'Zydrine', 'quantity': 3750}, {'name': 'Megacyte', 'quantity': 840}]},
    {'id': 129, 'name': 'Abaddon Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 288000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3220000}, {'name': 'Pyerite', 'quantity': 1110000}, {'name': 'Mexallon', 'quantity': 282000}, 
        {'name': 'Isogen', 'quantity': 65500}, {'name': 'Nocxium', 'quantity': 13600}, {'name': 'Zydrine', 'quantity': 3820}, {'name': 'Megacyte', 'quantity': 860}]},
    {'id': 130, 'name': 'Apocalypse Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 286000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3200000}, {'name': 'Pyerite', 'quantity': 1100000}, {'name': 'Mexallon', 'quantity': 280000}, 
        {'name': 'Isogen', 'quantity': 65000}, {'name': 'Nocxium', 'quantity': 13500}, {'name': 'Zydrine', 'quantity': 3800}, {'name': 'Megacyte', 'quantity': 855}]},
    {'id': 131, 'name': 'Armageddon Blueprint', 'category': 't1_ships', 'group': 'Battleships', 'volume': 50000, 'base_cost': 274000000, 'build_time': 216000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3080000}, {'name': 'Pyerite', 'quantity': 1030000}, {'name': 'Mexallon', 'quantity': 265000}, 
        {'name': 'Isogen', 'quantity': 62000}, {'name': 'Nocxium', 'quantity': 12700}, {'name': 'Zydrine', 'quantity': 3580}, {'name': 'Megacyte', 'quantity': 805}]},
    
    # HAULERS & INDUSTRIALS
    {'id': 150, 'name': 'Iteron Mark V Blueprint', 'category': 't1_ships', 'group': 'Haulers', 'volume': 20000, 'base_cost': 25000000, 'build_time': 72000, 'materials': [
        {'name': 'Tritanium', 'quantity': 450000}, {'name': 'Pyerite', 'quantity': 150000}, {'name': 'Mexallon', 'quantity': 35000}, 
        {'name': 'Isogen', 'quantity': 8000}, {'name': 'Nocxium', 'quantity': 1200}, {'name': 'Zydrine', 'quantity': 400}]},
    {'id': 151, 'name': 'Badger Blueprint', 'category': 't1_ships', 'group': 'Haulers', 'volume': 20000, 'base_cost': 23000000, 'build_time': 72000, 'materials': [
        {'name': 'Tritanium', 'quantity': 420000}, {'name': 'Pyerite', 'quantity': 140000}, {'name': 'Mexallon', 'quantity': 32500}, 
        {'name': 'Isogen', 'quantity': 7500}, {'name': 'Nocxium', 'quantity': 1100}, {'name': 'Zydrine', 'quantity': 360}]},
    {'id': 152, 'name': 'Mammoth Blueprint', 'category': 't1_ships', 'group': 'Haulers', 'volume': 20000, 'base_cost': 24000000, 'build_time': 72000, 'materials': [
        {'name': 'Tritanium', 'quantity': 435000}, {'name': 'Pyerite', 'quantity': 145000}, {'name': 'Mexallon', 'quantity': 33800}, 
        {'name': 'Isogen', 'quantity': 7800}, {'name': 'Nocxium', 'quantity': 1150}, {'name': 'Zydrine', 'quantity': 380}]},
    {'id': 153, 'name': 'Sigil Blueprint', 'category': 't1_ships', 'group': 'Haulers', 'volume': 20000, 'base_cost': 24500000, 'build_time': 72000, 'materials': [
        {'name': 'Tritanium', 'quantity': 440000}, {'name': 'Pyerite', 'quantity': 147000}, {'name': 'Mexallon', 'quantity': 34200}, 
        {'name': 'Isogen', 'quantity': 7900}, {'name': 'Nocxium', 'quantity': 1180}, {'name': 'Zydrine', 'quantity': 390}]},
    {'id': 154, 'name': 'Tayra Blueprint', 'category': 't1_ships', 'group': 'Haulers', 'volume': 20000, 'base_cost': 23500000, 'build_time': 72000, 'materials': [
        {'name': 'Tritanium', 'quantity': 425000}, {'name': 'Pyerite', 'quantity': 142000}, {'name': 'Mexallon', 'quantity': 33000}, 
        {'name': 'Isogen', 'quantity': 7600}, {'name': 'Nocxium', 'quantity': 1120}, {'name': 'Zydrine', 'quantity': 370}]},
    
    # MINING BARGES & EXHUMERS
    {'id': 160, 'name': 'Venture Blueprint', 'category': 't1_ships', 'group': 'Mining', 'volume': 2500, 'base_cost': 1800000, 'build_time': 25000, 'materials': [
        {'name': 'Tritanium', 'quantity': 52000}, {'name': 'Pyerite', 'quantity': 18000}, {'name': 'Mexallon', 'quantity': 4500}, {'name': 'Isogen', 'quantity': 900}]},
    {'id': 161, 'name': 'Procurer Blueprint', 'category': 't1_ships', 'group': 'Mining', 'volume': 15000, 'base_cost': 22000000, 'build_time': 55000, 'materials': [
        {'name': 'Tritanium', 'quantity': 380000}, {'name': 'Pyerite', 'quantity': 125000}, {'name': 'Mexallon', 'quantity': 30000}, 
        {'name': 'Isogen', 'quantity': 6800}, {'name': 'Nocxium', 'quantity': 980}]},
    {'id': 162, 'name': 'Retriever Blueprint', 'category': 't1_ships', 'group': 'Mining', 'volume': 15000, 'base_cost': 23000000, 'build_time': 55000, 'materials': [
        {'name': 'Tritanium', 'quantity': 395000}, {'name': 'Pyerite', 'quantity': 130000}, {'name': 'Mexallon', 'quantity': 31200}, 
        {'name': 'Isogen', 'quantity': 7050}, {'name': 'Nocxium', 'quantity': 1020}]},
    {'id': 163, 'name': 'Covetor Blueprint', 'category': 't1_ships', 'group': 'Mining', 'volume': 15000, 'base_cost': 24000000, 'build_time': 55000, 'materials': [
        {'name': 'Tritanium', 'quantity': 410000}, {'name': 'Pyerite', 'quantity': 135000}, {'name': 'Mexallon', 'quantity': 32500}, 
        {'name': 'Isogen', 'quantity': 7300}, {'name': 'Nocxium', 'quantity': 1050}]},
    
    # T1 MODULES - AFTERBURNERS
    {'id': 200, 'name': '1MN Afterburner I Blueprint', 'category': 't1_modules', 'group': 'Propulsion', 'volume': 5, 'base_cost': 8500, 'build_time': 1200, 'materials': [
        {'name': 'Tritanium', 'quantity': 8500}, {'name': 'Pyerite', 'quantity': 2000}, {'name': 'Mexallon', 'quantity': 480}]},
    {'id': 201, 'name': '10MN Afterburner I Blueprint', 'category': 't1_modules', 'group': 'Propulsion', 'volume': 10, 'base_cost': 15000, 'build_time': 3000, 'materials': [
        {'name': 'Tritanium', 'quantity': 15000}, {'name': 'Pyerite', 'quantity': 3500}, {'name': 'Mexallon', 'quantity': 800}, {'name': 'Isogen', 'quantity': 200}, {'name': 'Nocxium', 'quantity': 40}]},
    {'id': 202, 'name': '100MN Afterburner I Blueprint', 'category': 't1_modules', 'group': 'Propulsion', 'volume': 25, 'base_cost': 45000, 'build_time': 8000, 'materials': [
        {'name': 'Tritanium', 'quantity': 45000}, {'name': 'Pyerite', 'quantity': 10500}, {'name': 'Mexallon', 'quantity': 2400}, 
        {'name': 'Isogen', 'quantity': 600}, {'name': 'Nocxium', 'quantity': 120}, {'name': 'Zydrine', 'quantity': 30}]},
    
    # T1 MODULES - MICROWARPDRIVES
    {'id': 210, 'name': '5MN Microwarpdrive I Blueprint', 'category': 't1_modules', 'group': 'Propulsion', 'volume': 5, 'base_cost': 12000, 'build_time': 1500, 'materials': [
        {'name': 'Tritanium', 'quantity': 12000}, {'name': 'Pyerite', 'quantity': 2800}, {'name': 'Mexallon', 'quantity': 650}, {'name': 'Isogen', 'quantity': 150}]},
    {'id': 211, 'name': '50MN Microwarpdrive I Blueprint', 'category': 't1_modules', 'group': 'Propulsion', 'volume': 10, 'base_cost': 22000, 'build_time': 4000, 'materials': [
        {'name': 'Tritanium', 'quantity': 22000}, {'name': 'Pyerite', 'quantity': 5200}, {'name': 'Mexallon', 'quantity': 1200}, 
        {'name': 'Isogen', 'quantity': 300}, {'name': 'Nocxium', 'quantity': 60}]},
    {'id': 212, 'name': '500MN Microwarpdrive I Blueprint', 'category': 't1_modules', 'group': 'Propulsion', 'volume': 25, 'base_cost': 65000, 'build_time': 10000, 'materials': [
        {'name': 'Tritanium', 'quantity': 65000}, {'name': 'Pyerite', 'quantity': 15000}, {'name': 'Mexallon', 'quantity': 3500}, 
        {'name': 'Isogen', 'quantity': 850}, {'name': 'Nocxium', 'quantity': 170}, {'name': 'Zydrine', 'quantity': 40}]},
    
    # T1 MODULES - SHIELDS
    {'id': 220, 'name': 'Small Shield Booster I Blueprint', 'category': 't1_modules', 'group': 'Shields', 'volume': 5, 'base_cost': 9500, 'build_time': 1400, 'materials': [
        {'name': 'Tritanium', 'quantity': 9500}, {'name': 'Pyerite', 'quantity': 2200}, {'name': 'Mexallon', 'quantity': 520}]},
    {'id': 221, 'name': 'Medium Shield Booster I Blueprint', 'category': 't1_modules', 'group': 'Shields', 'volume': 10, 'base_cost': 18000, 'build_time': 3500, 'materials': [
        {'name': 'Tritanium', 'quantity': 18000}, {'name': 'Pyerite', 'quantity': 4200}, {'name': 'Mexallon', 'quantity': 980}, {'name': 'Isogen', 'quantity': 240}, {'name': 'Nocxium', 'quantity': 48}]},
    {'id': 222, 'name': 'Large Shield Booster I Blueprint', 'category': 't1_modules', 'group': 'Shields', 'volume': 25, 'base_cost': 52000, 'build_time': 9000, 'materials': [
        {'name': 'Tritanium', 'quantity': 52000}, {'name': 'Pyerite', 'quantity': 12000}, {'name': 'Mexallon', 'quantity': 2800}, 
        {'name': 'Isogen', 'quantity': 680}, {'name': 'Nocxium', 'quantity': 136}, {'name': 'Zydrine', 'quantity': 34}]},
    {'id': 223, 'name': 'Small Shield Extender I Blueprint', 'category': 't1_modules', 'group': 'Shields', 'volume': 5, 'base_cost': 7200, 'build_time': 1100, 'materials': [
        {'name': 'Tritanium', 'quantity': 7200}, {'name': 'Pyerite', 'quantity': 1700}, {'name': 'Mexallon', 'quantity': 400}]},
    {'id': 224, 'name': 'Medium Shield Extender I Blueprint', 'category': 't1_modules', 'group': 'Shields', 'volume': 10, 'base_cost': 13500, 'build_time': 2800, 'materials': [
        {'name': 'Tritanium', 'quantity': 13500}, {'name': 'Pyerite', 'quantity': 3200}, {'name': 'Mexallon', 'quantity': 750}, {'name': 'Isogen', 'quantity': 180}]},
    {'id': 225, 'name': 'Large Shield Extender I Blueprint', 'category': 't1_modules', 'group': 'Shields', 'volume': 25, 'base_cost': 38000, 'build_time': 7200, 'materials': [
        {'name': 'Tritanium', 'quantity': 38000}, {'name': 'Pyerite', 'quantity': 8800}, {'name': 'Mexallon', 'quantity': 2050}, 
        {'name': 'Isogen', 'quantity': 500}, {'name': 'Nocxium', 'quantity': 100}]},
    
    # T1 MODULES - ARMOR
    {'id': 230, 'name': 'Small Armor Repairer I Blueprint', 'category': 't1_modules', 'group': 'Armor', 'volume': 5, 'base_cost': 8800, 'build_time': 1300, 'materials': [
        {'name': 'Tritanium', 'quantity': 8800}, {'name': 'Pyerite', 'quantity': 2050}, {'name': 'Mexallon', 'quantity': 480}]},
    {'id': 231, 'name': 'Medium Armor Repairer I Blueprint', 'category': 't1_modules', 'group': 'Armor', 'volume': 10, 'base_cost': 16800, 'build_time': 3200, 'materials': [
        {'name': 'Tritanium', 'quantity': 16800}, {'name': 'Pyerite', 'quantity': 3900}, {'name': 'Mexallon', 'quantity': 920}, {'name': 'Isogen', 'quantity': 220}, {'name': 'Nocxium', 'quantity': 44}]},
    {'id': 232, 'name': 'Large Armor Repairer I Blueprint', 'category': 't1_modules', 'group': 'Armor', 'volume': 25, 'base_cost': 48000, 'build_time': 8200, 'materials': [
        {'name': 'Tritanium', 'quantity': 48000}, {'name': 'Pyerite', 'quantity': 11200}, {'name': 'Mexallon', 'quantity': 2600}, 
        {'name': 'Isogen', 'quantity': 620}, {'name': 'Nocxium', 'quantity': 124}, {'name': 'Zydrine', 'quantity': 31}]},
    {'id': 233, 'name': 'Small Armor Plate I Blueprint', 'category': 't1_modules', 'group': 'Armor', 'volume': 5, 'base_cost': 6500, 'build_time': 1000, 'materials': [
        {'name': 'Tritanium', 'quantity': 6500}, {'name': 'Pyerite', 'quantity': 1550}, {'name': 'Mexallon', 'quantity': 360}]},
    {'id': 234, 'name': 'Medium Armor Plate I Blueprint', 'category': 't1_modules', 'group': 'Armor', 'volume': 10, 'base_cost': 12200, 'build_time': 2600, 'materials': [
        {'name': 'Tritanium', 'quantity': 12200}, {'name': 'Pyerite', 'quantity': 2900}, {'name': 'Mexallon', 'quantity': 680}, {'name': 'Isogen', 'quantity': 160}]},
    {'id': 235, 'name': 'Large Armor Plate I Blueprint', 'category': 't1_modules', 'group': 'Armor', 'volume': 25, 'base_cost': 35000, 'build_time': 6800, 'materials': [
        {'name': 'Tritanium', 'quantity': 35000}, {'name': 'Pyerite', 'quantity': 8200}, {'name': 'Mexallon', 'quantity': 1900}, 
        {'name': 'Isogen', 'quantity': 460}, {'name': 'Nocxium', 'quantity': 92}]},
    
    # T1 MODULES - WEAPONS (HYBRID)
    {'id': 240, 'name': '125mm Railgun I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 5, 'base_cost': 11000, 'build_time': 1600, 'materials': [
        {'name': 'Tritanium', 'quantity': 11000}, {'name': 'Pyerite', 'quantity': 2600}, {'name': 'Mexallon', 'quantity': 610}]},
    {'id': 241, 'name': '150mm Railgun I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 5, 'base_cost': 12500, 'build_time': 1800, 'materials': [
        {'name': 'Tritanium', 'quantity': 12500}, {'name': 'Pyerite', 'quantity': 2950}, {'name': 'Mexallon', 'quantity': 690}]},
    {'id': 242, 'name': '200mm Railgun I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 10, 'base_cost': 21000, 'build_time': 4200, 'materials': [
        {'name': 'Tritanium', 'quantity': 21000}, {'name': 'Pyerite', 'quantity': 4900}, {'name': 'Mexallon', 'quantity': 1150}, {'name': 'Isogen', 'quantity': 280}, {'name': 'Nocxium', 'quantity': 56}]},
    {'id': 243, 'name': '250mm Railgun I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 10, 'base_cost': 28500, 'build_time': 5600, 'materials': [
        {'name': 'Tritanium', 'quantity': 28500}, {'name': 'Pyerite', 'quantity': 6700}, {'name': 'Mexallon', 'quantity': 1560}, 
        {'name': 'Isogen', 'quantity': 380}, {'name': 'Nocxium', 'quantity': 76}]},
    {'id': 244, 'name': '425mm Railgun I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 25, 'base_cost': 78000, 'build_time': 14500, 'materials': [
        {'name': 'Tritanium', 'quantity': 78000}, {'name': 'Pyerite', 'quantity': 18200}, {'name': 'Mexallon', 'quantity': 4250}, 
        {'name': 'Isogen', 'quantity': 1020}, {'name': 'Nocxium', 'quantity': 204}, {'name': 'Zydrine', 'quantity': 51}]},
    
    # T1 MODULES - WEAPONS (MISSILES)
    {'id': 250, 'name': 'Light Missile Launcher I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 5, 'base_cost': 9200, 'build_time': 1400, 'materials': [
        {'name': 'Tritanium', 'quantity': 9200}, {'name': 'Pyerite', 'quantity': 2150}, {'name': 'Mexallon', 'quantity': 500}]},
    {'id': 251, 'name': 'Heavy Missile Launcher I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 10, 'base_cost': 17500, 'build_time': 3400, 'materials': [
        {'name': 'Tritanium', 'quantity': 17500}, {'name': 'Pyerite', 'quantity': 4100}, {'name': 'Mexallon', 'quantity': 960}, {'name': 'Isogen', 'quantity': 230}, {'name': 'Nocxium', 'quantity': 46}]},
    {'id': 252, 'name': 'Cruise Missile Launcher I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 25, 'base_cost': 50000, 'build_time': 8800, 'materials': [
        {'name': 'Tritanium', 'quantity': 50000}, {'name': 'Pyerite', 'quantity': 11600}, {'name': 'Mexallon', 'quantity': 2700}, 
        {'name': 'Isogen', 'quantity': 650}, {'name': 'Nocxium', 'quantity': 130}, {'name': 'Zydrine', 'quantity': 32}]},
    {'id': 253, 'name': 'Torpedo Launcher I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 25, 'base_cost': 58000, 'build_time': 10200, 'materials': [
        {'name': 'Tritanium', 'quantity': 58000}, {'name': 'Pyerite', 'quantity': 13500}, {'name': 'Mexallon', 'quantity': 3150}, 
        {'name': 'Isogen', 'quantity': 760}, {'name': 'Nocxium', 'quantity': 152}, {'name': 'Zydrine', 'quantity': 38}]},
    {'id': 254, 'name': 'Rocket Launcher I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 5, 'base_cost': 5800, 'build_time': 900, 'materials': [
        {'name': 'Tritanium', 'quantity': 5800}, {'name': 'Pyerite', 'quantity': 1350}, {'name': 'Mexallon', 'quantity': 315}]},
    
    # T1 MODULES - WEAPONS (PROJECTILE)
    {'id': 260, 'name': '125mm Autocannon I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 5, 'base_cost': 10200, 'build_time': 1500, 'materials': [
        {'name': 'Tritanium', 'quantity': 10200}, {'name': 'Pyerite', 'quantity': 2400}, {'name': 'Mexallon', 'quantity': 560}]},
    {'id': 261, 'name': '150mm Autocannon I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 5, 'base_cost': 11800, 'build_time': 1750, 'materials': [
        {'name': 'Tritanium', 'quantity': 11800}, {'name': 'Pyerite', 'quantity': 2780}, {'name': 'Mexallon', 'quantity': 650}]},
    {'id': 262, 'name': '200mm Autocannon I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 10, 'base_cost': 19800, 'build_time': 4000, 'materials': [
        {'name': 'Tritanium', 'quantity': 19800}, {'name': 'Pyerite', 'quantity': 4650}, {'name': 'Mexallon', 'quantity': 1080}, {'name': 'Isogen', 'quantity': 260}, {'name': 'Nocxium', 'quantity': 52}]},
    {'id': 263, 'name': '425mm Autocannon I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 25, 'base_cost': 72000, 'build_time': 13500, 'materials': [
        {'name': 'Tritanium', 'quantity': 72000}, {'name': 'Pyerite', 'quantity': 16800}, {'name': 'Mexallon', 'quantity': 3920}, 
        {'name': 'Isogen', 'quantity': 940}, {'name': 'Nocxium', 'quantity': 188}, {'name': 'Zydrine', 'quantity': 47}]},
    {'id': 264, 'name': '650mm Artillery Cannon I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 25, 'base_cost': 85000, 'build_time': 15800, 'materials': [
        {'name': 'Tritanium', 'quantity': 85000}, {'name': 'Pyerite', 'quantity': 19800}, {'name': 'Mexallon', 'quantity': 4620}, 
        {'name': 'Isogen', 'quantity': 1100}, {'name': 'Nocxium', 'quantity': 220}, {'name': 'Zydrine', 'quantity': 55}]},
    {'id': 265, 'name': '1400mm Howitzer Artillery I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 50, 'base_cost': 185000, 'build_time': 32000, 'materials': [
        {'name': 'Tritanium', 'quantity': 185000}, {'name': 'Pyerite', 'quantity': 43200}, {'name': 'Mexallon', 'quantity': 10080}, 
        {'name': 'Isogen', 'quantity': 2400}, {'name': 'Nocxium', 'quantity': 480}, {'name': 'Zydrine', 'quantity': 120}]},
    
    # T1 MODULES - WEAPONS (LASER)
    {'id': 270, 'name': 'Dual Light Beam Laser I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 5, 'base_cost': 10500, 'build_time': 1550, 'materials': [
        {'name': 'Tritanium', 'quantity': 10500}, {'name': 'Pyerite', 'quantity': 2450}, {'name': 'Mexallon', 'quantity': 570}]},
    {'id': 271, 'name': 'Small Focused Pulse Laser I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 5, 'base_cost': 12200, 'build_time': 1800, 'materials': [
        {'name': 'Tritanium', 'quantity': 12200}, {'name': 'Pyerite', 'quantity': 2850}, {'name': 'Mexallon', 'quantity': 665}]},
    {'id': 272, 'name': 'Heavy Beam Laser I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 10, 'base_cost': 20500, 'build_time': 4100, 'materials': [
        {'name': 'Tritanium', 'quantity': 20500}, {'name': 'Pyerite', 'quantity': 4800}, {'name': 'Mexallon', 'quantity': 1120}, {'name': 'Isogen', 'quantity': 270}, {'name': 'Nocxium', 'quantity': 54}]},
    {'id': 273, 'name': 'Mega Pulse Laser I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 25, 'base_cost': 75000, 'build_time': 14000, 'materials': [
        {'name': 'Tritanium', 'quantity': 75000}, {'name': 'Pyerite', 'quantity': 17500}, {'name': 'Mexallon', 'quantity': 4080}, 
        {'name': 'Isogen', 'quantity': 980}, {'name': 'Nocxium', 'quantity': 196}, {'name': 'Zydrine', 'quantity': 49}]},
    {'id': 274, 'name': 'Tachyon Beam Laser I Blueprint', 'category': 't1_modules', 'group': 'Weapons', 'volume': 50, 'base_cost': 195000, 'build_time': 33500, 'materials': [
        {'name': 'Tritanium', 'quantity': 195000}, {'name': 'Pyerite', 'quantity': 45500}, {'name': 'Mexallon', 'quantity': 10600}, 
        {'name': 'Isogen', 'quantity': 2550}, {'name': 'Nocxium', 'quantity': 510}, {'name': 'Zydrine', 'quantity': 127}]},
    
    # T1 DRONES
    {'id': 300, 'name': 'Hobgoblin I Blueprint', 'category': 't1_modules', 'group': 'Drones', 'volume': 5, 'base_cost': 6500, 'build_time': 1000, 'materials': [
        {'name': 'Tritanium', 'quantity': 6500}, {'name': 'Pyerite', 'quantity': 1550}, {'name': 'Mexallon', 'quantity': 360}]},
    {'id': 301, 'name': 'Warrior I Blueprint', 'category': 't1_modules', 'group': 'Drones', 'volume': 5, 'base_cost': 6800, 'build_time': 1050, 'materials': [
        {'name': 'Tritanium', 'quantity': 6800}, {'name': 'Pyerite', 'quantity': 1620}, {'name': 'Mexallon', 'quantity': 378}]},
    {'id': 302, 'name': 'Acolyte I Blueprint', 'category': 't1_modules', 'group': 'Drones', 'volume': 5, 'base_cost': 7000, 'build_time': 1080, 'materials': [
        {'name': 'Tritanium', 'quantity': 7000}, {'name': 'Pyerite', 'quantity': 1660}, {'name': 'Mexallon', 'quantity': 388}]},
    {'id': 303, 'name': 'Hornet I Blueprint', 'category': 't1_modules', 'group': 'Drones', 'volume': 5, 'base_cost': 7200, 'build_time': 1100, 'materials': [
        {'name': 'Tritanium', 'quantity': 7200}, {'name': 'Pyerite', 'quantity': 1710}, {'name': 'Mexallon', 'quantity': 398}]},
    {'id': 304, 'name': 'Hammerhead I Blueprint', 'category': 't1_modules', 'group': 'Drones', 'volume': 10, 'base_cost': 12500, 'build_time': 2400, 'materials': [
        {'name': 'Tritanium', 'quantity': 12500}, {'name': 'Pyerite', 'quantity': 2950}, {'name': 'Mexallon', 'quantity': 688}, {'name': 'Isogen', 'quantity': 165}, {'name': 'Nocxium', 'quantity': 33}]},
    {'id': 305, 'name': 'Valkyrie I Blueprint', 'category': 't1_modules', 'group': 'Drones', 'volume': 10, 'base_cost': 13000, 'build_time': 2500, 'materials': [
        {'name': 'Tritanium', 'quantity': 13000}, {'name': 'Pyerite', 'quantity': 3070}, {'name': 'Mexallon', 'quantity': 715}, {'name': 'Isogen', 'quantity': 172}, {'name': 'Nocxium', 'quantity': 34}]},
    {'id': 306, 'name': 'Infiltrator I Blueprint', 'category': 't1_modules', 'group': 'Drones', 'volume': 10, 'base_cost': 13200, 'build_time': 2550, 'materials': [
        {'name': 'Tritanium', 'quantity': 13200}, {'name': 'Pyerite', 'quantity': 3120}, {'name': 'Mexallon', 'quantity': 728}, {'name': 'Isogen', 'quantity': 175}, {'name': 'Nocxium', 'quantity': 35}]},
    {'id': 307, 'name': 'Vespa I Blueprint', 'category': 't1_modules', 'group': 'Drones', 'volume': 10, 'base_cost': 12800, 'build_time': 2450, 'materials': [
        {'name': 'Tritanium', 'quantity': 12800}, {'name': 'Pyerite', 'quantity': 3020}, {'name': 'Mexallon', 'quantity': 704}, {'name': 'Isogen', 'quantity': 169}, {'name': 'Nocxium', 'quantity': 33}]},
    {'id': 308, 'name': 'Ogre I Blueprint', 'category': 't1_modules', 'group': 'Drones', 'volume': 25, 'base_cost': 35000, 'build_time': 6800, 'materials': [
        {'name': 'Tritanium', 'quantity': 35000}, {'name': 'Pyerite', 'quantity': 8200}, {'name': 'Mexallon', 'quantity': 1910}, 
        {'name': 'Isogen', 'quantity': 460}, {'name': 'Nocxium', 'quantity': 92}, {'name': 'Zydrine', 'quantity': 23}]},
    {'id': 309, 'name': 'Berserker I Blueprint', 'category': 't1_modules', 'group': 'Drones', 'volume': 25, 'base_cost': 36800, 'build_time': 7100, 'materials': [
        {'name': 'Tritanium', 'quantity': 36800}, {'name': 'Pyerite', 'quantity': 8620}, {'name': 'Mexallon', 'quantity': 2008}, 
        {'name': 'Isogen', 'quantity': 483}, {'name': 'Nocxium', 'quantity': 96}, {'name': 'Zydrine', 'quantity': 24}]},
    
    # T1 AMMO
    {'id': 350, 'name': 'Antimatter Charge S Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.1, 'base_cost': 120, 'build_time': 50, 'materials': [
        {'name': 'Tritanium', 'quantity': 120}]},
    {'id': 351, 'name': 'Iron Charge S Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.1, 'base_cost': 100, 'build_time': 45, 'materials': [
        {'name': 'Tritanium', 'quantity': 100}]},
    {'id': 352, 'name': 'Antimatter Charge M Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.2, 'base_cost': 240, 'build_time': 90, 'materials': [
        {'name': 'Tritanium', 'quantity': 240}]},
    {'id': 353, 'name': 'Iron Charge M Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.2, 'base_cost': 200, 'build_time': 80, 'materials': [
        {'name': 'Tritanium', 'quantity': 200}]},
    {'id': 354, 'name': 'Antimatter Charge L Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.5, 'base_cost': 600, 'build_time': 200, 'materials': [
        {'name': 'Tritanium', 'quantity': 600}]},
    {'id': 355, 'name': 'Caldari Navy Antimatter Charge M Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.2, 'base_cost': 480, 'build_time': 160, 'materials': [
        {'name': 'Tritanium', 'quantity': 480}]},
    {'id': 356, 'name': 'Nova Light Missile Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.2, 'base_cost': 220, 'build_time': 85, 'materials': [
        {'name': 'Tritanium', 'quantity': 220}]},
    {'id': 357, 'name': 'Scourge Heavy Missile Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.5, 'base_cost': 550, 'build_time': 190, 'materials': [
        {'name': 'Tritanium', 'quantity': 550}]},
    {'id': 358, 'name': 'Nova Cruise Missile Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 1, 'base_cost': 1500, 'build_time': 480, 'materials': [
        {'name': 'Tritanium', 'quantity': 1500}]},
    {'id': 359, 'name': 'EMP S Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.2, 'base_cost': 180, 'build_time': 70, 'materials': [
        {'name': 'Tritanium', 'quantity': 180}]},
    {'id': 360, 'name': 'EMP M Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.5, 'base_cost': 360, 'build_time': 130, 'materials': [
        {'name': 'Tritanium', 'quantity': 360}]},
    {'id': 361, 'name': 'EMP L Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 1, 'base_cost': 900, 'build_time': 300, 'materials': [
        {'name': 'Tritanium', 'quantity': 900}]},
    {'id': 362, 'name': 'Multifrequency S Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.2, 'base_cost': 200, 'build_time': 75, 'materials': [
        {'name': 'Tritanium', 'quantity': 200}]},
    {'id': 363, 'name': 'Multifrequency M Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 0.5, 'base_cost': 400, 'build_time': 140, 'materials': [
        {'name': 'Tritanium', 'quantity': 400}]},
    {'id': 364, 'name': 'Multifrequency L Blueprint', 'category': 't1_modules', 'group': 'Ammo', 'volume': 1, 'base_cost': 1000, 'build_time': 320, 'materials': [
        {'name': 'Tritanium', 'quantity': 1000}]},
    
    # CAPACITOR MODULES
    {'id': 370, 'name': 'Small Capacitor Booster I Blueprint', 'category': 't1_modules', 'group': 'Capacitor', 'volume': 5, 'base_cost': 8500, 'build_time': 1250, 'materials': [
        {'name': 'Tritanium', 'quantity': 8500}, {'name': 'Pyerite', 'quantity': 2000}, {'name': 'Mexallon', 'quantity': 470}]},
    {'id': 371, 'name': 'Medium Capacitor Booster I Blueprint', 'category': 't1_modules', 'group': 'Capacitor', 'volume': 10, 'base_cost': 16200, 'build_time': 3100, 'materials': [
        {'name': 'Tritanium', 'quantity': 16200}, {'name': 'Pyerite', 'quantity': 3780}, {'name': 'Mexallon', 'quantity': 882}, {'name': 'Isogen', 'quantity': 210}, {'name': 'Nocxium', 'quantity': 42}]},
    {'id': 372, 'name': 'Heavy Capacitor Booster I Blueprint', 'category': 't1_modules', 'group': 'Capacitor', 'volume': 25, 'base_cost': 46500, 'build_time': 7950, 'materials': [
        {'name': 'Tritanium', 'quantity': 46500}, {'name': 'Pyerite', 'quantity': 10800}, {'name': 'Mexallon', 'quantity': 2520}, 
        {'name': 'Isogen', 'quantity': 600}, {'name': 'Nocxium', 'quantity': 120}, {'name': 'Zydrine', 'quantity': 30}]},
    {'id': 373, 'name': 'Cap Recharger I Blueprint', 'category': 't1_modules', 'group': 'Capacitor', 'volume': 5, 'base_cost': 7200, 'build_time': 1100, 'materials': [
        {'name': 'Tritanium', 'quantity': 7200}, {'name': 'Pyerite', 'quantity': 1690}, {'name': 'Mexallon', 'quantity': 395}]},
    {'id': 374, 'name': 'Capacitor Power Relay I Blueprint', 'category': 't1_modules', 'group': 'Capacitor', 'volume': 5, 'base_cost': 6800, 'build_time': 1050, 'materials': [
        {'name': 'Tritanium', 'quantity': 6800}, {'name': 'Pyerite', 'quantity': 1600}, {'name': 'Mexallon', 'quantity': 375}]},
    
    # ELECTRONIC WARFARE
    {'id': 380, 'name': 'Small Remote Capacitor Transmitter I Blueprint', 'category': 't1_modules', 'group': 'EWAR', 'volume': 5, 'base_cost': 7800, 'build_time': 1150, 'materials': [
        {'name': 'Tritanium', 'quantity': 7800}, {'name': 'Pyerite', 'quantity': 1830}, {'name': 'Mexallon', 'quantity': 428}]},
    {'id': 381, 'name': 'Medium Remote Capacitor Transmitter I Blueprint', 'category': 't1_modules', 'group': 'EWAR', 'volume': 10, 'base_cost': 14800, 'build_time': 2850, 'materials': [
        {'name': 'Tritanium', 'quantity': 14800}, {'name': 'Pyerite', 'quantity': 3450}, {'name': 'Mexallon', 'quantity': 805}, {'name': 'Isogen', 'quantity': 192}, {'name': 'Nocxium', 'quantity': 38}]},
    {'id': 382, 'name': 'Small Remote Shield Booster I Blueprint', 'category': 't1_modules', 'group': 'EWAR', 'volume': 5, 'base_cost': 8000, 'build_time': 1200, 'materials': [
        {'name': 'Tritanium', 'quantity': 8000}, {'name': 'Pyerite', 'quantity': 1870}, {'name': 'Mexallon', 'quantity': 437}]},
    {'id': 383, 'name': 'Medium Remote Shield Booster I Blueprint', 'category': 't1_modules', 'group': 'EWAR', 'volume': 10, 'base_cost': 15200, 'build_time': 2900, 'materials': [
        {'name': 'Tritanium', 'quantity': 15200}, {'name': 'Pyerite', 'quantity': 3550}, {'name': 'Mexallon', 'quantity': 828}, {'name': 'Isogen', 'quantity': 198}, {'name': 'Nocxium', 'quantity': 39}]},
    
    # RIGS
    {'id': 400, 'name': 'Small Core Defense Field Extender I Blueprint', 'category': 't1_modules', 'group': 'Rigs', 'volume': 5, 'base_cost': 15000, 'build_time': 2500, 'materials': [
        {'name': 'Tritanium', 'quantity': 15000}, {'name': 'Pyerite', 'quantity': 3500}, {'name': 'Mexallon', 'quantity': 820}]},
    {'id': 401, 'name': 'Medium Core Defense Field Extender I Blueprint', 'category': 't1_modules', 'group': 'Rigs', 'volume': 10, 'base_cost': 28500, 'build_time': 6000, 'materials': [
        {'name': 'Tritanium', 'quantity': 28500}, {'name': 'Pyerite', 'quantity': 6650}, {'name': 'Mexallon', 'quantity': 1550}, {'name': 'Isogen', 'quantity': 370}, {'name': 'Nocxium', 'quantity': 74}]},
    {'id': 402, 'name': 'Small Anti-EM Screen Reinforcer I Blueprint', 'category': 't1_modules', 'group': 'Rigs', 'volume': 5, 'base_cost': 13200, 'build_time': 2200, 'materials': [
        {'name': 'Tritanium', 'quantity': 13200}, {'name': 'Pyerite', 'quantity': 3080}, {'name': 'Mexallon', 'quantity': 718}]},
    {'id': 403, 'name': 'Medium Anti-EM Screen Reinforcer I Blueprint', 'category': 't1_modules', 'group': 'Rigs', 'volume': 10, 'base_cost': 25000, 'build_time': 5300, 'materials': [
        {'name': 'Tritanium', 'quantity': 25000}, {'name': 'Pyerite', 'quantity': 5830}, {'name': 'Mexallon', 'quantity': 1360}, {'name': 'Isogen', 'quantity': 325}, {'name': 'Nocxium', 'quantity': 65}]},
    {'id': 404, 'name': 'Small Nanobot Accelerator I Blueprint', 'category': 't1_modules', 'group': 'Rigs', 'volume': 5, 'base_cost': 14500, 'build_time': 2400, 'materials': [
        {'name': 'Tritanium', 'quantity': 14500}, {'name': 'Pyerite', 'quantity': 3380}, {'name': 'Mexallon', 'quantity': 790}]},
    {'id': 405, 'name': 'Medium Nanobot Accelerator I Blueprint', 'category': 't1_modules', 'group': 'Rigs', 'volume': 10, 'base_cost': 27500, 'build_time': 5800, 'materials': [
        {'name': 'Tritanium', 'quantity': 27500}, {'name': 'Pyerite', 'quantity': 6410}, {'name': 'Mexallon', 'quantity': 1495}, {'name': 'Isogen', 'quantity': 358}, {'name': 'Nocxium', 'quantity': 71}]},
    
    # INDUSTRIAL MATERIALS
    {'id': 500, 'name': 'Construction Blocks Blueprint', 'category': 'materials', 'group': 'Components', 'volume': 5, 'base_cost': 2500, 'build_time': 600, 'materials': [
        {'name': 'Tritanium', 'quantity': 2500}, {'name': 'Pyerite', 'quantity': 580}]},
    {'id': 501, 'name': 'Mechanical Parts Blueprint', 'category': 'materials', 'group': 'Components', 'volume': 5, 'base_cost': 3500, 'build_time': 800, 'materials': [
        {'name': 'Tritanium', 'quantity': 3500}, {'name': 'Pyerite', 'quantity': 820}, {'name': 'Mexallon', 'quantity': 190}]},
    {'id': 502, 'name': 'Rocket Fuel Blueprint', 'category': 'materials', 'group': 'Components', 'volume': 5, 'base_cost': 4200, 'build_time': 950, 'materials': [
        {'name': 'Tritanium', 'quantity': 4200}, {'name': 'Pyerite', 'quantity': 980}, {'name': 'Mexallon', 'quantity': 228}]},
    {'id': 503, 'name': 'Sensor Components Blueprint', 'category': 'materials', 'group': 'Components', 'volume': 5, 'base_cost': 4800, 'build_time': 1100, 'materials': [
        {'name': 'Tritanium', 'quantity': 4800}, {'name': 'Pyerite', 'quantity': 1120}, {'name': 'Mexallon', 'quantity': 262}]},
    {'id': 504, 'name': 'Microfiber Shielding Blueprint', 'category': 'materials', 'group': 'Components', 'volume': 5, 'base_cost': 5200, 'build_time': 1200, 'materials': [
        {'name': 'Tritanium', 'quantity': 5200}, {'name': 'Pyerite', 'quantity': 1210}, {'name': 'Mexallon', 'quantity': 283}]},
    {'id': 505, 'name': 'Coolant Blueprint', 'category': 'materials', 'group': 'Components', 'volume': 5, 'base_cost': 5800, 'build_time': 1350, 'materials': [
        {'name': 'Tritanium', 'quantity': 5800}, {'name': 'Pyerite', 'quantity': 1350}, {'name': 'Mexallon', 'quantity': 315}]},
    {'id': 506, 'name': 'Guidance Systems Blueprint', 'category': 'materials', 'group': 'Components', 'volume': 5, 'base_cost': 6500, 'build_time': 1500, 'materials': [
        {'name': 'Tritanium', 'quantity': 6500}, {'name': 'Pyerite', 'quantity': 1520}, {'name': 'Mexallon', 'quantity': 355}]},
    {'id': 507, 'name': 'Miniature Electronics Blueprint', 'category': 'materials', 'group': 'Components', 'volume': 5, 'base_cost': 7200, 'build_time': 1650, 'materials': [
        {'name': 'Tritanium', 'quantity': 7200}, {'name': 'Pyerite', 'quantity': 1680}, {'name': 'Mexallon', 'quantity': 392}]},
    {'id': 508, 'name': 'Superconductors Blueprint', 'category': 'materials', 'group': 'Components', 'volume': 5, 'base_cost': 8000, 'build_time': 1850, 'materials': [
        {'name': 'Tritanium', 'quantity': 8000}, {'name': 'Pyerite', 'quantity': 1870}, {'name': 'Mexallon', 'quantity': 437}]},
]

# Merge capital ships and structures database
if CAPITAL_DB_AVAILABLE:
    BPO_DATABASE.extend(ALL_CAPITAL_DATABASE)
    print(f"✅ Loaded {len(BPO_DATABASE)} total blueprints (including {len(ALL_CAPITAL_DATABASE)} capital ships & structures)")
else:
    print(f"✅ Loaded {len(BPO_DATABASE)} T1 blueprints")

# Merge advanced materials and capital components with BPO database
if ADVANCED_DB_AVAILABLE:
    # Add capital component blueprints
    BPO_DATABASE.extend(ALL_COMPONENT_DATABASE)
    print(f"✅ Added {len(ALL_COMPONENT_DATABASE)} capital component blueprints")
    print(f"✅ Advanced materials database loaded: {len(ADVANCED_MATERIALS)} moon, {len(REACTION_MATERIALS)} reactions, {len(T3_MATERIALS)} T3, {len(SALVAGE_MATERIALS)} salvage, {len(ANCIENT_SALVAGE)} ancient")
    print(f"📊 Total blueprints: {len(BPO_DATABASE)}")

# Type ID mappings for ESI lookups
TYPE_IDS = {
    # Minerals
    'Tritanium': 34,
    'Pyerite': 35,
    'Mexallon': 36,
    'Isogen': 37,
    'Nocxium': 38,
    'Zydrine': 39,
    'Megacyte': 40,
    'Morphite': 11399,
    
    # Ships - Frigates
    'Atron': 608,
    'Incursus': 591,
    'Tristan': 607,
    'Navitas': 592,
    'Imicus': 601,
    'Merlin': 603,
    'Kestrel': 602,
    'Condor': 599,
    'Bantam': 598,
    'Griffin': 597,
    'Rifter': 587,
    'Slasher': 586,
    'Breacher': 594,
    'Probe': 596,
    'Vigil': 588,
    'Punisher': 597,
    'Executioner': 589,
    'Tormentor': 590,
    'Magnate': 600,
    'Crucifier': 601,
    
    # Destroyers
    'Algos': 32872,
    'Catalyst': 16236,
    'Cormorant': 16238,
    'Thrasher': 16240,
    'Coercer': 16242,
    
    # Cruisers
    'Vexor': 626,
    'Thorax': 625,
    'Celestis': 619,
    'Exequror': 634,
    'Caracal': 621,
    'Osprey': 631,
    'Blackbird': 632,
    'Moa': 623,
    'Stabber': 622,
    'Scythe': 630,
    'Bellicose': 627,
    'Rupture': 624,
    'Maller': 636,
    'Augoror': 634,
    'Arbitrator': 628,
    'Omen': 640,
    
    # Battlecruisers
    'Drake': 645,
    'Ferox': 641,
    'Brutix': 633,
    'Myrmidon': 644,
    'Hurricane': 647,
    'Cyclone': 643,
    'Harbinger': 638,
    'Prophecy': 637,
    
    # Battleships
    'Raven': 638,
    'Scorpion': 640,
    'Rokh': 642,
    'Megathron': 645,
    'Dominix': 645,
    'Hyperion': 643,
    'Tempest': 644,
    'Typhoon': 644,
    'Maelstrom': 646,
    'Abaddon': 641,
    'Apocalypse': 642,
    'Armageddon': 643,
    
    # Capital Ships - Carriers
    'Thanatos': 23911,
    'Archon': 23915,
    'Chimera': 23913,
    'Nidhoggur': 23917,
    
    # Capital Ships - Dreadnoughts
    'Moros': 19720,
    'Revelation': 19722,
    'Phoenix': 19724,
    'Naglfar': 19726,
    
    # Capital Ships - Force Auxiliaries
    'Apostle': 37605,
    'Minokawa': 37607,
    'Lif': 37606,
    'Ninazu': 37604,
    
    # Capital Ships - Supercarriers
    'Nyx': 23919,
    'Aeon': 23911,  # Using placeholder, update with correct ID
    'Wyvern': 23915,  # Using placeholder, update with correct ID
    'Hel': 23917,  # Using placeholder, update with correct ID
    
    # Capital Ships - Titans
    'Erebus': 671,
    'Avatar': 11567,
    'Ragnarok': 45649,
    'Leviathan': 3764,
    
    # Freighters
    'Charon': 20183,
    'Providence': 20187,
    'Obelisk': 20185,
    'Fenrir': 20189,
    
    # Jump Freighters
    'Rhea': 28844,
    'Anshar': 28846,
    'Ark': 28848,
    'Nomad': 28850,
    
    # Capital Industrial
    'Orca': 28606,
    'Rorqual': 28352,
    
    # Structures
    'Astrahus': 35825,
    'Fortizar': 35826,
    'Keepstar': 35827,
    'Raitaru': 35835,
    'Azbel': 35836,
    'Sotiyo': 35837,
    'Athanor': 35840,
    'Tatara': 35841,
}

MATERIAL_PRICES = {
    'Tritanium': 6,
    'Pyerite': 12,
    'Mexallon': 85,
    'Isogen': 120,
    'Nocxium': 450,
    'Zydrine': 1200,
    'Megacyte': 2800,
    'Morphite': 8500,
    'Construction Blocks': 480,
    'Mechanical Parts': 650,
    'Rocket Fuel': 780,
    'Sensor Components': 890,
    'Microfiber Shielding': 960,
    'Coolant': 1080,
    'Guidance Systems': 1200,
    'Miniature Electronics': 1320,
    'Superconductors': 1480,
}

# Merge advanced materials prices if available
if ADVANCED_DB_AVAILABLE:
    for material_name, material_data in {**ADVANCED_MATERIALS, **REACTION_MATERIALS, **T3_MATERIALS, **SALVAGE_MATERIALS, **ANCIENT_SALVAGE}.items():
        if isinstance(material_data, dict) and 'base_price' in material_data:
            MATERIAL_PRICES[material_name] = material_data['base_price']
    print(f"✅ Added advanced material prices. Total: {len(MATERIAL_PRICES)} materials")

# JF Commands
@bot.tree.command(name="jf", description="Jump Freighter services")
@app_commands.describe(
    origin="Origin station",
    destination="Destination station",
    volume="Volume in m3",
    collateral="Collateral value in ISK"
)
async def jf_quote(interaction: discord.Interaction, origin: str, destination: str, volume: float, collateral: float):
    # Calculate JF price
    jita_to_null = 1500
    null_to_jita = 1200
    null_to_null = 800
    
    is_jita_origin = 'jita' in origin.lower()
    is_jita_dest = 'jita' in destination.lower()
    
    if is_jita_origin or is_jita_dest:
        rate = jita_to_null if is_jita_origin else null_to_jita
    else:
        rate = null_to_null
    
    price = volume * rate
    if collateral > 500000000:
        price += (collateral - 500000000) * 0.01
    
    embed = discord.Embed(
        title="Jump Freighter Quote",
        color=discord.Color.green()
    )
    embed.add_field(name="Route", value=f"{origin} → {destination}", inline=False)
    embed.add_field(name="Volume", value=f"{volume:,.0f} m³", inline=True)
    embed.add_field(name="Collateral", value=f"{collateral:,.0f} ISK", inline=True)
    embed.add_field(name="Shipping Cost", value=f"{price:,.0f} ISK", inline=True)
    embed.set_footer(text="Quote valid for 24 hours")
    
    await interaction.response.send_message(embed=embed)

# BPO Commands
@bot.tree.command(name="bpodb", description="BPO database with materials and calculations")
@app_commands.describe(
    action="Action to perform",
    blueprint="Blueprint name",
    me="Material Efficiency level (0-10)",
    te="Time Efficiency level (0-20)",
    runs="Number of runs"
)
@app_commands.choices(action=[
    app_commands.Choice(name="materials", value="materials"),
    app_commands.Choice(name="buildtime", value="buildtime"),
    app_commands.Choice(name="calc", value="calc"),
    app_commands.Choice(name="search", value="search"),
    app_commands.Choice(name="list", value="list")
])
async def bpodb(
    interaction: discord.Interaction, 
    action: app_commands.Choice[str],
    blueprint: str = None,
    me: int = 0,
    te: int = 0,
    runs: int = 1
):
    if action.value == "search":
        results = [b for b in BPO_DATABASE if blueprint.lower() in b['name'].lower()]
        if not results:
            await interaction.response.send_message("No blueprints found.", ephemeral=True)
            return
        
        embed = discord.Embed(title=f"Search Results: {blueprint}", color=discord.Color.blue())
        for b in results[:5]:
            embed.add_field(name=b['name'], value=f"{b['category']} | {b['base_cost']:,.0f} ISK", inline=True)
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "materials":
        bpo = next((b for b in BPO_DATABASE if blueprint.lower() in b['name'].lower()), None)
        if not bpo:
            await interaction.response.send_message("BPO not found.", ephemeral=True)
            return
        
        me_bonus = 1 - (me / 100)
        total_cost = 0
        
        embed = discord.Embed(title=f"Materials: {bpo['name']}", color=discord.Color.blue())
        embed.add_field(name="ME Level", value=f"{me}%", inline=True)
        embed.add_field(name="Runs", value=str(runs), inline=True)
        
        materials_text = ""
        for m in bpo['materials']:
            adjusted_qty = int(m['quantity'] * me_bonus * runs)
            price = MATERIAL_PRICES.get(m['name'], 0)
            cost = adjusted_qty * price
            total_cost += cost
            materials_text += f"{m['name']}: {adjusted_qty:,} @ {price:,} ISK = {cost:,.0f} ISK\n"
        
        embed.add_field(name="Total Cost", value=f"{total_cost:,.0f} ISK", inline=True)
        embed.add_field(name="Materials", value=materials_text[:1024], inline=False)
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "buildtime":
        bpo = next((b for b in BPO_DATABASE if blueprint.lower() in b['name'].lower()), None)
        if not bpo:
            await interaction.response.send_message("BPO not found.", ephemeral=True)
            return
        
        te_bonus = 1 - (te / 100)
        industry_bonus = 0.8  # Industry 5
        adv_industry_bonus = 0.85  # Advanced Industry 5
        
        base_time = bpo['build_time'] * runs
        adjusted_time = int(base_time * te_bonus * industry_bonus * adv_industry_bonus)
        
        hours = adjusted_time // 3600
        minutes = (adjusted_time % 3600) // 60
        
        embed = discord.Embed(title=f"Build Time: {bpo['name']}", color=discord.Color.orange())
        embed.add_field(name="Base Time", value=f"{base_time // 3600}h {(base_time % 3600) // 60}m", inline=True)
        embed.add_field(name="Adjusted Time", value=f"{hours}h {minutes}m", inline=True)
        embed.add_field(name="Time Saved", value=f"{((base_time - adjusted_time) / base_time * 100):.1f}%", inline=True)
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "calc":
        bpo = next((b for b in BPO_DATABASE if blueprint.lower() in b['name'].lower()), None)
        if not bpo:
            await interaction.response.send_message("BPO not found.", ephemeral=True)
            return
        
        # Material calc
        me_bonus = 1 - (me / 100)
        material_cost = sum(
            int(m['quantity'] * me_bonus * runs) * MATERIAL_PRICES.get(m['name'], 0)
            for m in bpo['materials']
        )
        
        # Time calc
        te_bonus = 1 - (te / 100)
        adjusted_time = int(bpo['build_time'] * runs * te_bonus * 0.8 * 0.85)
        hours = adjusted_time // 3600
        minutes = (adjusted_time % 3600) // 60
        
        # Profit calc
        sell_price = bpo['base_cost'] * 1.5 * runs
        profit = sell_price - material_cost
        margin = (profit / material_cost * 100) if material_cost > 0 else 0
        
        color = discord.Color.green() if profit > 0 else discord.Color.red()
        embed = discord.Embed(title=f"Build Calculation: {bpo['name']}", color=color)
        embed.add_field(name="Material Cost", value=f"{material_cost:,.0f} ISK", inline=True)
        embed.add_field(name="Build Time", value=f"{hours}h {minutes}m", inline=True)
        embed.add_field(name="Est. Sell", value=f"{sell_price:,.0f} ISK", inline=True)
        embed.add_field(name="Profit", value=f"{profit:,.0f} ISK", inline=True)
        embed.add_field(name="Margin", value=f"{margin:.1f}%", inline=True)
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "list":
        embed = discord.Embed(title="BPO Database", color=discord.Color.gold())
        for b in BPO_DATABASE[:10]:
            embed.add_field(name=b['name'], value=f"{b['category']} | {b['base_cost']:,.0f} ISK", inline=True)
        await interaction.response.send_message(embed=embed)

# Contract Commands
@bot.tree.command(name="contract", description="Create buy/sell contracts")
@app_commands.describe(
    action="Action",
    item="Item name",
    quantity="Quantity",
    price="Price per unit",
    station="Station"
)
@app_commands.choices(action=[
    app_commands.Choice(name="buy", value="buy"),
    app_commands.Choice(name="sell", value="sell"),
    app_commands.Choice(name="list", value="list")
])
async def contract_cmd(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    item: str = None,
    quantity: int = None,
    price: float = None,
    station: str = None
):
    conn = get_db()
    c = conn.cursor()
    
    if action.value in ["buy", "sell"]:
        total = price * quantity
        c.execute('''
            INSERT INTO contracts 
            (discord_user_id, contract_type, item_name, quantity, price_per_unit, total_value, station)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (str(interaction.user.id), action.value, item, quantity, price, total, station))
        conn.commit()
        contract_id = c.lastrowid
        
        embed = discord.Embed(
            title=f"{action.value.upper()} Contract Created",
            color=discord.Color.green() if action.value == "buy" else discord.Color.blue()
        )
        embed.add_field(name="Contract ID", value=str(contract_id), inline=True)
        embed.add_field(name="Item", value=item, inline=True)
        embed.add_field(name="Quantity", value=f"{quantity:,}", inline=True)
        embed.add_field(name="Price/Unit", value=f"{price:,.0f} ISK", inline=True)
        embed.add_field(name="Total", value=f"{total:,.0f} ISK", inline=True)
        embed.add_field(name="Station", value=station, inline=True)
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "list":
        c.execute("SELECT * FROM contracts WHERE status = 'active' ORDER BY created_at DESC LIMIT 20")
        contracts = c.fetchall()
        
        if not contracts:
            await interaction.response.send_message("No active contracts.", ephemeral=True)
            conn.close()
            return
        
        embed = discord.Embed(title="Active Contracts", color=discord.Color.gold())
        for contract in contracts:
            embed.add_field(
                name=f"#{contract[0]} | {contract[2].upper()}",
                value=f"{contract[3]} x{contract[4]:,} @ {contract[5]:,.0f} ISK | {contract[7]}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)
    
    conn.close()

# PI Commands
@bot.tree.command(name="pi", description="Planetary Interaction management")
@app_commands.describe(
    action="Action",
    planet="Planet name",
    planet_type="Planet type",
    system="System name"
)
@app_commands.choices(action=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="list", value="list"),
    app_commands.Choice(name="stats", value="stats")
])
@app_commands.choices(planet_type=[
    app_commands.Choice(name="Barren", value="barren"),
    app_commands.Choice(name="Gas", value="gas"),
    app_commands.Choice(name="Lava", value="lava"),
    app_commands.Choice(name="Plasma", value="plasma"),
    app_commands.Choice(name="Temperate", value="temperate")
])
async def pi_cmd(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    planet: str = None,
    planet_type: app_commands.Choice[str] = None,
    system: str = None
):
    conn = get_db()
    c = conn.cursor()
    
    if action.value == "add":
        c.execute('''
            INSERT INTO pi_colonies (discord_user_id, character_name, planet_name, planet_type, system)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(interaction.user.id), interaction.user.name, planet, planet_type.value, system))
        conn.commit()
        await interaction.response.send_message(f"PI colony added: {planet} ({planet_type.value}) in {system}")
    
    elif action.value == "list":
        c.execute("SELECT * FROM pi_colonies WHERE discord_user_id = ?", (str(interaction.user.id),))
        colonies = c.fetchall()
        
        if not colonies:
            await interaction.response.send_message("No PI colonies found.", ephemeral=True)
            conn.close()
            return
        
        embed = discord.Embed(title="Your PI Colonies", color=discord.Color.blue())
        for colony in colonies:
            embed.add_field(
                name=f"#{colony[0]} | {colony[3]} ({colony[4]})",
                value=f"{colony[5]} | Daily: {colony[6]:,.0f} ISK",
                inline=True
            )
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "stats":
        c.execute("SELECT COUNT(*), SUM(daily_profit) FROM pi_colonies WHERE discord_user_id = ?", 
                  (str(interaction.user.id),))
        count, daily = c.fetchone()
        daily = daily or 0
        
        embed = discord.Embed(title="PI Statistics", color=discord.Color.purple())
        embed.add_field(name="Colonies", value=str(count), inline=True)
        embed.add_field(name="Daily Profit", value=f"{daily:,.0f} ISK", inline=True)
        embed.add_field(name="Monthly Profit", value=f"{daily * 30:,.0f} ISK", inline=True)
        await interaction.response.send_message(embed=embed)
    
    conn.close()

# ESI Character Commands
@bot.tree.command(name="charinfo", description="Look up character information via ESI")
@app_commands.describe(character_name="Character name to lookup")
async def charinfo_cmd(interaction: discord.Interaction, character_name: str):
    """Get character public info from ESI"""
    await interaction.response.defer()
    
    # Search for character
    char_id = await esi_client.search_character(character_name)
    if not char_id:
        await interaction.followup.send(f"❌ Character '{character_name}' not found.", ephemeral=True)
        return
    
    # Get character info
    char_info = await esi_client.get_character_info(char_id)
    if not char_info:
        await interaction.followup.send(f"❌ Could not fetch info for '{character_name}'.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"👤 Character: {char_info.get('name', character_name)}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Character ID", value=str(char_id), inline=True)
    embed.add_field(name="Security Status", value=f"{char_info.get('security_status', 0):.2f}", inline=True)
    embed.add_field(name="Corporation", value="Use ESI auth for corp info", inline=True)
    embed.add_field(
        name="Born", 
        value=char_info.get('birthday', 'Unknown')[:10],
        inline=True
    )
    embed.set_footer(text="Data from EVE ESI API")
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="jita", description="Get real-time Jita market prices from ESI")
@app_commands.describe(item_name="Item name to check (e.g., 'Tritanium', 'Drake')")
async def jita_cmd(interaction: discord.Interaction, item_name: str):
    """Get real-time Jita prices via ESI"""
    await interaction.response.defer()
    
    # Try to find type ID
    type_id = TYPE_IDS.get(item_name)
    
    # If not in our mapping, try to search via ESI
    if not type_id:
        await interaction.followup.send(
            f"❌ Item '{item_name}' not found in database.\n"
            f"Try searching for: Tritanium, Pyerite, Drake, Raven, etc.",
            ephemeral=True
        )
        return
    
    # Get Jita prices
    price_data = await get_jita_price(type_id)
    
    if not price_data:
        await interaction.followup.send(f"❌ Could not fetch market data for '{item_name}'.", ephemeral=True)
        return
    
    # Get type info
    type_info = await esi_client.get_type_info(type_id)
    
    embed = discord.Embed(
        title=f"💰 Jita Market: {type_info.get('name', item_name) if type_info else item_name}",
        description=f"Type ID: {type_id}",
        color=discord.Color.gold()
    )
    
    embed.add_field(name="Best Buy", value=f"{price_data['buy']:,.2f} ISK", inline=True)
    embed.add_field(name="Best Sell", value=f"{price_data['sell']:,.2f} ISK", inline=True)
    embed.add_field(name="Spread", value=f"{price_data['sell'] - price_data['buy']:,.2f} ISK", inline=True)
    embed.add_field(name="Market Volume", value=f"{price_data['volume']:,} units", inline=False)
    
    # Calculate potential profit for traders
    if price_data['sell'] > 0:
        margin = ((price_data['sell'] - price_data['buy']) / price_data['buy'] * 100) if price_data['buy'] > 0 else 0
        embed.add_field(name="Margin", value=f"{margin:.2f}%", inline=True)
    
    embed.set_footer(text="Real-time data from ESI | Prices update every 5 min")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="profit", description="Calculate profit margins for trading")
@app_commands.describe(
    item="Item to analyze",
    quantity="Quantity to trade",
    buy_location="Where to buy",
    sell_location="Where to sell"
)
async def profit_cmd(
    interaction: discord.Interaction,
    item: str,
    quantity: int = 1,
    buy_location: str = "Jita",
    sell_location: str = "D-PN"
):
    """Calculate trading profit margins"""
    
    # Get base prices
    if buy_location.upper() == 'JITA':
        buy_prices = BASE_PRICES
    else:
        buy_prices = get_local_prices(buy_location)
    
    if sell_location.upper() == 'JITA':
        sell_prices = BASE_PRICES
    else:
        # For selling, we need to check if there's a markup for imports
        sell_prices = get_import_prices(buy_location, sell_location)
    
    # Find item in BPO database
    bpo = next((b for b in BPO_DATABASE if item.lower() in b['name'].lower()), None)
    
    if bpo:
        # Calculate material costs
        buy_cost = sum(
            m['quantity'] * buy_prices.get(m['name'], 0) * quantity
            for m in bpo['materials']
        )
        
        # Estimate sell price (could be improved with real market data)
        sell_price = bpo['base_cost'] * 1.2 * quantity  # 20% markup
        
        # JF shipping cost
        volume = bpo.get('volume', 1) * quantity
        shipping = volume * 1500 if buy_location.upper() == 'JITA' and sell_location.upper() != 'JITA' else 0
        
        total_cost = buy_cost + shipping
        profit = sell_price - total_cost
        margin = (profit / total_cost * 100) if total_cost > 0 else 0
        
        embed = discord.Embed(
            title=f"📊 Profit Analysis: {bpo['name']}",
            color=discord.Color.green() if profit > 0 else discord.Color.red()
        )
        embed.add_field(name="Buy Location", value=buy_location.upper(), inline=True)
        embed.add_field(name="Sell Location", value=sell_location.upper(), inline=True)
        embed.add_field(name="Quantity", value=f"{quantity:,}", inline=True)
        embed.add_field(name="Material Cost", value=f"{buy_cost:,.0f} ISK", inline=True)
        embed.add_field(name="Shipping", value=f"{shipping:,.0f} ISK", inline=True)
        embed.add_field(name="Total Cost", value=f"{total_cost:,.0f} ISK", inline=True)
        embed.add_field(name="Est. Sell Price", value=f"{sell_price:,.0f} ISK", inline=True)
        embed.add_field(name="Profit", value=f"{profit:,.0f} ISK", inline=True)
        embed.add_field(name="Margin", value=f"{margin:.1f}%", inline=True)
        
        if profit > 0:
            embed.add_field(
                name="💡 Recommendation",
                value="✅ Profitable trade! Consider buying and shipping.",
                inline=False
            )
        else:
            embed.add_field(
                name="⚠️ Warning",
                value="This trade would result in a loss. Check market prices first.",
                inline=False
            )
    else:
        # Simple material trading
        if item in BASE_PRICES:
            buy_price = buy_prices.get(item, BASE_PRICES[item])
            sell_price = sell_prices.get(item, BASE_PRICES[item])
            
            cost = buy_price * quantity
            revenue = sell_price * quantity
            profit = revenue - cost
            
            embed = discord.Embed(
                title=f"📊 Material Trading: {item}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Buy @", value=f"{buy_price:,} ISK/unit", inline=True)
            embed.add_field(name="Sell @", value=f"{sell_price:,} ISK/unit", inline=True)
            embed.add_field(name="Profit", value=f"{profit:,.0f} ISK", inline=True)
        else:
            embed = discord.Embed(
                title="❌ Item Not Found",
                description=f"'{item}' not found in database. Try `/find item:{item}`",
                color=discord.Color.red()
            )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="industry", description="Industry job management and queue")
@app_commands.describe(
    action="Action to perform",
    blueprint="Blueprint name",
    runs="Number of runs",
    me="Material Efficiency (0-10)",
    te="Time Efficiency (0-20)"
)
@app_commands.choices(action=[
    app_commands.Choice(name="queue", value="queue"),
    app_commands.Choice(name="list", value="list"),
    app_commands.Choice(name="status", value="status"),
    app_commands.Choice(name="complete", value="complete")
])
async def industry_cmd(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    blueprint: str = None,
    runs: int = 1,
    me: int = 0,
    te: int = 0
):
    """Industry job management"""
    conn = get_db()
    c = conn.cursor()
    user_id = str(interaction.user.id)
    
    if action.value == "queue":
        if not blueprint:
            await interaction.response.send_message("❌ Please specify a blueprint name.", ephemeral=True)
            conn.close()
            return
        
        # Find blueprint
        bpo = next((b for b in BPO_DATABASE if blueprint.lower() in b['name'].lower()), None)
        if not bpo:
            await interaction.response.send_message(f"❌ Blueprint '{blueprint}' not found.", ephemeral=True)
            conn.close()
            return
        
        # Calculate job details
        me_bonus = 1 - (me / 100)
        te_bonus = 1 - (te / 100)
        material_cost = sum(
            int(m['quantity'] * me_bonus * runs) * MATERIAL_PRICES.get(m['name'], 0)
            for m in bpo['materials']
        )
        build_time = int(bpo['build_time'] * runs * te_bonus * 0.8 * 0.85)
        
        # Add to queue
        c.execute('''
            INSERT INTO industry_jobs 
            (discord_user_id, character_name, product_name, quantity, material_cost, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, interaction.user.name, bpo['name'], runs, material_cost, 'pending'))
        conn.commit()
        job_id = c.lastrowid
        
        hours = build_time // 3600
        minutes = (build_time % 3600) // 60
        
        embed = discord.Embed(
            title="🏭 Job Queued",
            description=f"Job #{job_id}",
            color=discord.Color.green()
        )
        embed.add_field(name="Blueprint", value=bpo['name'], inline=True)
        embed.add_field(name="Runs", value=str(runs), inline=True)
        embed.add_field(name="Material Cost", value=f"{material_cost:,.0f} ISK", inline=True)
        embed.add_field(name="Build Time", value=f"{hours}h {minutes}m", inline=True)
        embed.add_field(name="ME", value=f"{me}%", inline=True)
        embed.add_field(name="TE", value=f"{te}%", inline=True)
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "list":
        c.execute("""
            SELECT * FROM industry_jobs 
            WHERE discord_user_id = ? 
            ORDER BY 
                CASE status 
                    WHEN 'pending' THEN 1 
                    WHEN 'building' THEN 2 
                    WHEN 'completed' THEN 3 
                    ELSE 4 
                END,
                created_at DESC
            LIMIT 20
        """, (user_id,))
        jobs = c.fetchall()
        
        if not jobs:
            await interaction.response.send_message("No industry jobs found.", ephemeral=True)
            conn.close()
            return
        
        embed = discord.Embed(title="🏭 Your Industry Jobs", color=discord.Color.orange())
        for job in jobs:
            status_emoji = {"pending": "⏳", "building": "🔨", "completed": "✅"}.get(job[7], "❓")
            profit_str = f" | Profit: {job[6]:,.0f} ISK" if job[6] else ""
            embed.add_field(
                name=f"#{job[0]} {status_emoji} {job[3]}",
                value=f"Qty: {job[4]:,} | Status: {job[7]}{profit_str}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "status":
        c.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'building' THEN 1 END) as building,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                SUM(material_cost) as total_invested,
                SUM(profit) as total_profit
            FROM industry_jobs 
            WHERE discord_user_id = ?
        """, (user_id,))
        stats = c.fetchone()
        
        embed = discord.Embed(title="📊 Industry Statistics", color=discord.Color.blue())
        embed.add_field(name="Pending", value=str(stats[0] or 0), inline=True)
        embed.add_field(name="Building", value=str(stats[1] or 0), inline=True)
        embed.add_field(name="Completed", value=str(stats[2] or 0), inline=True)
        embed.add_field(name="Total Invested", value=f"{stats[3] or 0:,.0f} ISK", inline=True)
        embed.add_field(name="Total Profit", value=f"{stats[4] or 0:,.0f} ISK", inline=True)
        embed.add_field(name="ROI", 
                       value=f"{((stats[4] or 0) / (stats[3] or 1) * 100):.1f}%" if stats[3] else "N/A", 
                       inline=True)
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "complete":
        await interaction.response.send_message(
            "Use `/bpodb action:calc` to calculate sell price, then update the job manually in the database.",
            ephemeral=True
        )
    
    conn.close()

@bot.tree.command(name="pioptimizer", description="PI Colony optimization recommendations")
@app_commands.describe(
    planet_type="Type of planet",
    target_product="What you want to produce"
)
@app_commands.choices(planet_type=[
    app_commands.Choice(name="Barren", value="barren"),
    app_commands.Choice(name="Gas", value="gas"),
    app_commands.Choice(name="Ice", value="ice"),
    app_commands.Choice(name="Lava", value="lava"),
    app_commands.Choice(name="Oceanic", value="oceanic"),
    app_commands.Choice(name="Plasma", value="plasma"),
    app_commands.Choice(name="Storm", value="storm"),
    app_commands.Choice(name="Temperate", value="temperate")
])
async def pioptimizer_cmd(
    interaction: discord.Interaction,
    planet_type: app_commands.Choice[str],
    target_product: str = None
):
    """Get PI colony optimization recommendations"""
    
    # PI product recommendations by planet type
    pi_recommendations = {
        'barren': {
            'resources': ['Noble Metals', 'Reactive Metals'],
            'good_products': ['Mechanical Parts', 'Consumer Electronics'],
            'profit_per_hour': 850000
        },
        'gas': {
            'resources': ['Noble Gas', 'Reactive Gas'],
            'good_products': ['Coolant', 'Oxygen'],
            'profit_per_hour': 920000
        },
        'ice': {
            'resources': ['Heavy Water', 'Liquid Ozone'],
            'good_products': ['Coolant', 'Strontium Clathrates'],
            'profit_per_hour': 780000
        },
        'lava': {
            'resources': ['Base Metals', 'Felsic Magma'],
            'good_products': ['Construction Blocks', 'Mechanical Parts'],
            'profit_per_hour': 880000
        },
        'oceanic': {
            'resources': ['Planktic Colonies', 'Biomass'],
            'good_products': ['Nanites', 'Test Cultures'],
            'profit_per_hour': 750000
        },
        'plasma': {
            'resources': ['Suspended Plasma', 'Ionic Solutions'],
            'good_products': ['Enriched Uranium', 'Coolant'],
            'profit_per_hour': 950000
        },
        'storm': {
            'resources': ['Ionic Solutions', 'Noble Gas'],
            'good_products': ['Superconductors', 'Water'],
            'profit_per_hour': 820000
        },
        'temperate': {
            'resources': ['Autotrophs', 'Complex Organisms'],
            'good_products': ['Livestock', 'Biofuels'],
            'profit_per_hour': 800000
        }
    }
    
    planet_info = pi_recommendations.get(planet_type.value, {})
    
    if not planet_info:
        await interaction.response.send_message(
            f"❌ Unknown planet type: {planet_type.value}",
            ephemeral=True
        )
        return
    
    embed = discord.Embed(
        title=f"🌍 PI Optimization: {planet_type.value.title()} Planet",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="Available Resources",
        value="\n".join([f"• {r}" for r in planet_info['resources']]),
        inline=False
    )
    
    embed.add_field(
        name="Recommended Products",
        value="\n".join([f"✅ {p}" for p in planet_info['good_products']]),
        inline=False
    )
    
    daily_profit = planet_info['profit_per_hour'] * 24
    monthly_profit = daily_profit * 30
    
    embed.add_field(name="Est. Hourly Profit", value=f"{planet_info['profit_per_hour']:,.0f} ISK", inline=True)
    embed.add_field(name="Est. Daily Profit", value=f"{daily_profit:,.0f} ISK", inline=True)
    embed.add_field(name="Est. Monthly Profit", value=f"{monthly_profit:,.0f} ISK", inline=True)
    
    embed.add_field(
        name="💡 Setup Tips",
        value="• Use 1 extractor per resource\n"
              "• 4-6 basic industry facilities\n"
              "• 1 advanced industry facility\n"
              "• 1 storage facility\n"
              "• 1 launchpad",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="volume", description="Calculate cargo volumes for ships")
@app_commands.describe(
    ship="Ship type",
    cargo_type="What you're hauling"
)
@app_commands.choices(ship=[
    app_commands.Choice(name="Iteron Mark V", value="itv"),
    app_commands.Choice(name="Badger", value="badger"),
    app_commands.Choice(name="Mammoth", value="mammoth"),
    app_commands.Choice(name="Sigil", value="sigil"),
    app_commands.Choice(name="Providence", value="providence"),
    app_commands.Choice(name="Charon", value="charon"),
    app_commands.Choice(name="Obelisk", value="obelisk"),
    app_commands.Choice(name="Fenrir", value="fenrir"),
    app_commands.Choice(name="Rhea", value="rhea"),
    app_commands.Choice(name="Anshar", value="anshar")
])
async def volume_cmd(
    interaction: discord.Interaction,
    ship: app_commands.Choice[str],
    cargo_type: str = None
):
    """Calculate cargo volumes for different ships"""
    
    ship_volumes = {
        'itv': {'name': 'Iteron Mark V', 'cargo': 38000, 'special': 50000},
        'badger': {'name': 'Badger', 'cargo': 5250, 'special': 0},
        'mammoth': {'name': 'Mammoth', 'cargo': 6500, 'special': 0},
        'sigil': {'name': 'Sigil', 'cargo': 13000, 'special': 0},
        'providence': {'name': 'Providence', 'cargo': 435000, 'special': 3000000},
        'charon': {'name': 'Charon', 'cargo': 465000, 'special': 3000000},
        'obelisk': {'name': 'Obelisk', 'cargo': 400000, 'special': 3000000},
        'fenrir': {'name': 'Fenrir', 'cargo': 420000, 'special': 3000000},
        'rhea': {'name': 'Rhea', 'cargo': 400000, 'special': 3000000},
        'anshar': {'name': 'Anshar', 'cargo': 420000, 'special': 3000000}
    }
    
    ship_info = ship_volumes.get(ship.value)
    
    if not ship_info:
        await interaction.response.send_message("❌ Unknown ship type.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"📦 Cargo Capacity: {ship_info['name']}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Standard Cargo", value=f"{ship_info['cargo']:,} m³", inline=True)
    if ship_info['special'] > 0:
        embed.add_field(name="Fleet Hangar", value=f"{ship_info['special']:,} m³", inline=True)
        embed.add_field(name="Total Capacity", value=f"{ship_info['cargo'] + ship_info['special']:,} m³", inline=True)
    
    # Calculate how many items fit
    if cargo_type:
        bpo = next((b for b in BPO_DATABASE if cargo_type.lower() in b['name'].lower()), None)
        if bpo:
            item_volume = bpo.get('volume', 1)
            items_fit = int(ship_info['cargo'] / item_volume)
            
            embed.add_field(
                name=f"{bpo['name']} Capacity",
                value=f"{items_fit:,} units @ {item_volume} m³ each",
                inline=False
            )
            
            # Calculate JF shipping cost
            jf_cost = ship_info['cargo'] * 1500
            embed.add_field(
                name="JF Shipping Cost (Jita→Null)",
                value=f"{jf_cost:,.0f} ISK",
                inline=False
            )
    
    embed.add_field(
        name="💡 Tips",
        value="• Fit Expanded Cargohold II for +27.5% capacity\n"
              "• Use cargo rigs for additional space\n"
              "• Consider implant: Zainou 'Gnome' CX-8\n"
              "• Max skills: Hull Upgrades V",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="jfoptimize", description="Jump Freighter route optimization")
@app_commands.describe(
    origin="Starting system",
    destination="Target system",
    max_collateral="Maximum ISK value",
    prefer_isk_per_m3="Optimize for ISK per m3 instead of total profit"
)
async def jfoptimize_cmd(
    interaction: discord.Interaction,
    origin: str,
    destination: str,
    max_collateral: float = 5000000000,
    prefer_isk_per_m3: bool = False
):
    """Optimize JF routes for maximum profit"""
    
    # WinterCo route data
    routes = {
        ('JITA', 'D-PN'): {'distance': 42, 'base_rate': 1500, 'avg_contracts': 15},
        ('JITA', 'VA6-ED'): {'distance': 38, 'base_rate': 1500, 'avg_contracts': 12},
        ('JITA', 'RD-G2R'): {'distance': 45, 'base_rate': 1500, 'avg_contracts': 8},
        ('D-PN', 'JITA'): {'distance': 42, 'base_rate': 1200, 'avg_contracts': 20},
        ('VA6-ED', 'JITA'): {'distance': 38, 'base_rate': 1200, 'avg_contracts': 18},
        ('RD-G2R', 'JITA'): {'distance': 45, 'base_rate': 1200, 'avg_contracts': 10}
    }
    
    origin_upper = origin.upper()
    dest_upper = destination.upper()
    
    route_key = (origin_upper, dest_upper)
    reverse_route = (dest_upper, origin_upper)
    
    route_info = routes.get(route_key)
    
    if not route_info:
        # Check if reversed route exists
        if routes.get(reverse_route):
            await interaction.response.send_message(
                f"❌ Route {origin} → {destination} not typically run.\n"
                f"However, {destination} → {origin} is a common route.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Unknown route: {origin} → {destination}\n"
                f"Common routes: Jita ↔ D-PN, Jita ↔ VA6-ED, Jita ↔ RD-G2R",
                ephemeral=True
            )
        return
    
    # Calculate optimal load
    rhea_capacity = 420000 + 3000000  # Standard + Fleet hangar
    optimal_collateral = min(max_collateral, 5000000000)
    
    # Calculate revenue
    base_revenue = rhea_capacity * route_info['base_rate']
    if optimal_collateral > 500000000:
        extra_fee = (optimal_collateral - 500000000) * 0.01
        total_revenue = base_revenue + extra_fee
    else:
        total_revenue = base_revenue
    
    # Calculate ISK per m3
    isk_per_m3 = total_revenue / rhea_capacity
    
    # Estimate time (4 jumps per hour with JF)
    jumps = route_info['distance']
    travel_time = jumps * 15  # 15 min per jump including cyno
    
    embed = discord.Embed(
        title=f"🚀 JF Route Optimization: {origin_upper} → {dest_upper}",
        color=discord.Color.gold()
    )
    
    embed.add_field(name="Distance", value=f"{route_info['distance']} jumps", inline=True)
    embed.add_field(name="Base Rate", value=f"{route_info['base_rate']:,} ISK/m³", inline=True)
    embed.add_field(name="Avg Contracts", value=str(route_info['avg_contracts']), inline=True)
    
    embed.add_field(name="Rhea Capacity", value=f"{rhea_capacity:,} m³", inline=True)
    embed.add_field(name="Max Collateral", value=f"{optimal_collateral:,.0f} ISK", inline=True)
    embed.add_field(name="Est. Revenue", value=f"{total_revenue:,.0f} ISK", inline=True)
    
    embed.add_field(name="ISK per m³", value=f"{isk_per_m3:,.0f} ISK", inline=True)
    embed.add_field(name="Travel Time", value=f"~{travel_time} minutes", inline=True)
    embed.add_field(name="Contracts/Hour", value=f"~{60//travel_time}", inline=True)
    
    # Weekly projection
    daily_revenue = total_revenue * 3  # 3 trips per day
    weekly_revenue = daily_revenue * 7
    
    embed.add_field(
        name="💰 Revenue Projections",
        value=f"Daily (3 trips): {daily_revenue:,.0f} ISK\n"
              f"Weekly: {weekly_revenue:,.0f} ISK\n"
              f"Monthly: {weekly_revenue * 4:,.0f} ISK",
        inline=False
    )
    
    embed.add_field(
        name="📋 Recommended Contract Settings",
        value=f"• Volume: {rhea_capacity:,} m³ max\n"
              f"• Collateral: {optimal_collateral:,.0f} ISK max\n"
              f"• Reward: {total_revenue:,.0f} ISK (or higher)\n"
              f"• Expiration: 3 days\n"
              f"• Days to Complete: 1 day",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="skills", description="Track your industry skills (requires ESI auth)")
@app_commands.describe(
    action="Action to take"
)
@app_commands.choices(action=[
    app_commands.Choice(name="check", value="check"),
    app_commands.Choice(name="optimize", value="optimize")
])
async def skills_cmd(interaction: discord.Interaction, action: app_commands.Choice[str]):
    """Track and optimize industry skills"""
    
    # Important industry skills
    industry_skills = {
        'Industry': {
            'levels': [4, 3, 2, 1],
            'bonus': '4% faster manufacturing per level',
            'time_impact': True
        },
        'Advanced Industry': {
            'levels': [5, 4, 3, 2, 1],
            'bonus': '3% faster manufacturing per level',
            'time_impact': True
        },
        'Mechanical Engineering': {
            'levels': [5, 4, 3, 2, 1],
            'bonus': '1% ME bonus per level for ships',
            'time_impact': False
        },
        'Electronic Engineering': {
            'levels': [5, 4, 3, 2, 1],
            'bonus': '1% ME bonus per level for modules',
            'time_impact': False
        },
        'Mass Production': {
            'levels': [5, 4, 3, 2, 1],
            'bonus': '+1 manufacturing slot per level',
            'time_impact': False
        },
        'Advanced Mass Production': {
            'levels': [5, 4, 3, 2, 1],
            'bonus': '+1 manufacturing slot per level',
            'time_impact': False
        },
        'Laboratory Operation': {
            'levels': [5, 4, 3, 2, 1],
            'bonus': '+1 research slot per level',
            'time_impact': False
        }
    }
    
    if action.value == "check":
        embed = discord.Embed(
            title="🏭 Industry Skills Checklist",
            description="Track your skill progression for maximum efficiency",
            color=discord.Color.blue()
        )
        
        for skill, info in industry_skills.items():
            levels_text = " → ".join([f"{l}" for l in info['levels']])
            embed.add_field(
                name=f"{skill}",
                value=f"Levels: {levels_text}\nBonus: {info['bonus']}",
                inline=False
            )
        
        embed.add_field(
            name="💡 Priority Skills",
            value="1. **Industry V** - Essential for all manufacturing\n"
                  "2. **Advanced Industry V** - Significant time savings\n"
                  "3. **Mechanical/Electronic Engineering V** - Material savings\n"
                  "4. **Mass Production** - More parallel jobs",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "optimize":
        # Calculate time savings
        base_time = 100
        
        # With max skills
        industry_bonus = 0.80  # 20% faster at level 5
        adv_industry_bonus = 0.85  # 15% faster at level 5
        optimized_time = base_time * industry_bonus * adv_industry_bonus
        
        embed = discord.Embed(
            title="⚡ Skill Optimization Analysis",
            description="Maximize your industry efficiency",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="Time Savings with Max Skills",
            value=f"Base time: {base_time}h\n"
                  f"With Industry V: {base_time * 0.80:.1f}h (-20%)\n"
                  f"With Industry V + Adv Industry V: {optimized_time:.1f}h (-32%)\n"
                  f"**Total time saved: {base_time - optimized_time:.1f}h per job**",
            inline=False
        )
        
        embed.add_field(
            name="Material Savings with Max Skills",
            value="• ME 0 → ME 10: 10% material reduction\n"
                  "• With Engineering skills V: Up to 15% additional reduction\n"
                  "• Example: Drake build saves ~15M ISK in materials",
            inline=False
        )
        
        embed.add_field(
            name="Training Plan",
            value="**Phase 1 (Essential):**\n"
                  "• Industry I-V (2 days)\n"
                  "• Advanced Industry I-V (5 days)\n\n"
                  "**Phase 2 (Optimization):**\n"
                  "• Mechanical Engineering I-V (8 days)\n"
                  "• Electronic Engineering I-V (8 days)\n\n"
                  "**Phase 3 (Scale):**\n"
                  "• Mass Production I-V (5 days)\n"
                  "• Advanced Mass Production I-V (15 days)",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

# Help Command
@bot.tree.command(name="help", description="Show all commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="EVE Industry Services - Commands", color=discord.Color.blue())
    
    commands_text = """
**📍 LOCATION & TRACKING**
`/iam system:NAME` - Set your current location
`/whereami` - Check where you are

**🚀 JUMP FREIGHTER & LOGISTICS**
`/jf origin destination volume collateral` - Get shipping quote
`/jfoptimize origin destination` - Optimize JF routes for profit
`/volume ship:cargo_type` - Calculate cargo capacity

**💰 PRICES & MARKET**
`/price item:NAME location:SYSTEM` - Check local prices
`/jita item:NAME` - Get real-time Jita prices from ESI
`/find item:NAME` - Search BPO database
`/buyquote item:NAME quantity:N` - Full quote with shipping
`/profit item:NAME quantity:N` - Calculate trading profit

**🏭 INDUSTRY & MANUFACTURING**
`/bpodb action:SEARCH/... blueprint:NAME me:N te:N runs:N` - BPO database
`/industry action:QUEUE/LIST/STATUS` - Industry job management
`/skills action:CHECK/OPTIMIZE` - Track and optimize skills

**🌍 PLANETARY INTERACTION**
`/pi action:ADD/LIST/STATS` - PI colony management
`/pioptimizer planet_type:TYPE` - PI optimization guide

**👤 CHARACTER & ESI**
`/charinfo character_name:NAME` - Look up character via ESI

**📦 CONTRACTS**
`/contract action:BUY/SELL/LIST` - Manage buy/sell contracts

**❓ HELP**
`/help` - This help message
    """
    
    embed.add_field(name="Available Commands", value=commands_text, inline=False)
    embed.add_field(
        name="💡 Quick Start Examples",
        value="```\n"
              "1. Set location:      /iam system:D-PN\n"
              "2. Check Jita prices: /jita item:Drake\n"
              "3. Get JF quote:      /jf D-PN Jita 50000 1000000000\n"
              "4. Queue industry:    /industry action:queue blueprint:Drake runs:5\n"
              "5. Calculate profit:  /profit item:Drake quantity:10\n"
              "6. Optimize PI:       /pioptimizer planet_type:plasma\n"
              "7. Optimize JF:       /jfoptimize Jita D-PN\n"
              "```",
        inline=False
    )
    embed.add_field(
        name="🔧 Advanced Features",
        value="• **ESI Integration**: Real-time Jita prices via `/jita`\n"
              "• **100+ BPOs**: Comprehensive blueprint database\n"
              "• **Profit Analysis**: Trading margin calculations\n"
              "• **Route Optimization**: Maximize JF profits\n"
              "• **PI Optimization**: Planet-specific recommendations\n"
              "• **Skill Tracking**: Industry skill optimization",
        inline=False
    )
    embed.set_footer(text="WinterCo Industry Services - Pure Blind Region | 100+ BPOs | Real-time ESI Data")
    await interaction.response.send_message(embed=embed)

# Import Alliance, Corp, and Character commands
try:
    import org_commands
    print("✅ Organization commands loaded (auth, corp, alliance, asset sharing)")
except ImportError as e:
    print(f"⚠️ Could not load organization commands: {e}")

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
