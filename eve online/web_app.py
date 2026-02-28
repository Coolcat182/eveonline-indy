from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('data/eve_services.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    """Main dashboard showing all status information"""
    conn = get_db()
    
    # Get counts
    c = conn.cursor()
    
    # JF Contracts
    c.execute("SELECT COUNT(*) FROM jf_contracts WHERE status = 'pending'")
    pending_jf = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM jf_contracts WHERE status = 'in_progress'")
    active_jf = c.fetchone()[0]
    
    # Industry Jobs
    c.execute("SELECT COUNT(*) FROM industry_jobs WHERE status = 'pending'")
    pending_jobs = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM industry_jobs WHERE status = 'building'")
    building_jobs = c.fetchone()[0]
    
    c.execute("SELECT SUM(profit) FROM industry_jobs WHERE status = 'sold'")
    total_profit = c.fetchone()[0] or 0
    
    # PI Colonies
    c.execute("SELECT COUNT(*) FROM pi_colonies")
    total_colonies = c.fetchone()[0]
    
    c.execute("SELECT SUM(daily_profit) FROM pi_colonies")
    daily_pi_profit = c.fetchone()[0] or 0
    
    # Active Contracts
    c.execute("SELECT COUNT(*) FROM contracts WHERE status = 'active'")
    active_contracts = c.fetchone()[0]
    
    c.execute("SELECT SUM(total_value) FROM contracts WHERE status = 'active'")
    contract_value = c.fetchone()[0] or 0
    
    conn.close()
    
    return render_template('dashboard.html',
                         pending_jf=pending_jf,
                         active_jf=active_jf,
                         pending_jobs=pending_jobs,
                         building_jobs=building_jobs,
                         total_profit=total_profit,
                         total_colonies=total_colonies,
                         daily_pi_profit=daily_pi_profit,
                         active_contracts=active_contracts,
                         contract_value=contract_value)

@app.route('/api/jf-contracts')
def api_jf_contracts():
    """Get all JF contracts"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM jf_contracts 
        ORDER BY 
            CASE status 
                WHEN 'pending' THEN 1 
                WHEN 'in_progress' THEN 2 
                ELSE 3 
            END,
            created_at DESC
    """)
    contracts = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(contracts)

@app.route('/api/industry-jobs')
def api_industry_jobs():
    """Get all industry jobs"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM industry_jobs 
        ORDER BY 
            CASE status 
                WHEN 'building' THEN 1
                WHEN 'pending' THEN 2
                WHEN 'completed' THEN 3
                ELSE 4
            END,
            created_at DESC
    """)
    jobs = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(jobs)

@app.route('/api/pi-colonies')
def api_pi_colonies():
    """Get all PI colonies"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM pi_colonies ORDER BY daily_profit DESC")
    colonies = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(colonies)

@app.route('/api/contracts')
def api_contracts():
    """Get all contracts"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM contracts 
        WHERE status = 'active'
        ORDER BY created_at DESC
    """)
    contracts = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(contracts)

@app.route('/api/stats')
def api_stats():
    """Get dashboard statistics"""
    conn = get_db()
    c = conn.cursor()
    
    stats = {}
    
    # JF Stats
    c.execute("SELECT COUNT(*), SUM(price) FROM jf_contracts WHERE status = 'completed'")
    row = c.fetchone()
    stats['jf_completed'] = row[0] or 0
    stats['jf_total_spent'] = row[1] or 0
    
    # Industry Stats
    c.execute("SELECT COUNT(*), SUM(profit) FROM industry_jobs WHERE status = 'sold'")
    row = c.fetchone()
    stats['jobs_sold'] = row[0] or 0
    stats['total_profit'] = row[1] or 0
    
    # PI Stats
    c.execute("SELECT COUNT(*), SUM(daily_profit) FROM pi_colonies")
    row = c.fetchone()
    stats['pi_colonies'] = row[0] or 0
    stats['pi_daily'] = row[1] or 0
    stats['pi_monthly'] = (row[1] or 0) * 30
    
    # Active counts
    c.execute("SELECT COUNT(*) FROM jf_contracts WHERE status = 'pending'")
    stats['jf_pending'] = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM industry_jobs WHERE status IN ('pending', 'building')")
    stats['jobs_active'] = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM contracts WHERE status = 'active'")
    stats['contracts_active'] = c.fetchone()[0]
    
    conn.close()
    return jsonify(stats)

# Market Pricing Data
BASE_PRICES = {
    'Tritanium': 6, 'Pyerite': 12, 'Mexallon': 85, 'Isogen': 120,
    'Nocxium': 450, 'Zydrine': 1200, 'Megacyte': 2800
}

LOCAL_MARKDOWNS = {
    'RD-G2R': 0.05,    # 5% markdown
    'VA6-ED': 0.08,    # 8% markdown
    'D-PN': 0.10,      # 10% markdown
    'O-BKJY': 0.12     # 12% markdown
}

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
    markdown = LOCAL_MARKDOWNS.get(location.upper(), 0.05)
    return {item: int(price * (1 - markdown)) for item, price in BASE_PRICES.items()}

def get_import_prices(from_loc, to_loc):
    """Get prices when importing from empire to nullsec (with markup)"""
    if from_loc.upper() != 'JITA':
        return get_local_prices(to_loc)
    markup = IMPORT_MARKUPS.get(to_loc.upper(), 0.15)
    return {item: int(price * (1 + markup)) for item, price in BASE_PRICES.items()}

@app.route('/api/prices')
def api_prices():
    """Get current market prices for all locations"""
    locations = ['Jita', 'D-PN', 'VA6-ED', 'RD-G2R', 'O-BKJY']
    prices = {}
    
    for loc in locations:
        if loc == 'Jita':
            prices[loc] = {
                'local': BASE_PRICES,
                'markdown': 0,
                'import_markup': 0,
                'type': 'empire'
            }
        else:
            prices[loc] = {
                'local': get_local_prices(loc),
                'markdown': LOCAL_MARKDOWNS.get(loc, 0.05),
                'import_markup': IMPORT_MARKUPS.get(loc, 0.15),
                'type': 'nullsec'
            }
    
    return jsonify({
        'base_prices': BASE_PRICES,
        'locations': prices,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/prices/update', methods=['POST'])
def api_update_prices():
    """Update base market prices"""
    data = request.get_json()
    
    if 'base_prices' in data:
        global BASE_PRICES
        BASE_PRICES.update(data['base_prices'])
        return jsonify({'status': 'success', 'message': 'Base prices updated'})
    
    if 'markdowns' in data:
        global LOCAL_MARKDOWNS
        LOCAL_MARKDOWNS.update(data['markdowns'])
        return jsonify({'status': 'success', 'message': 'Local markdowns updated'})
    
    if 'markups' in data:
        global IMPORT_MARKUPS
        IMPORT_MARKUPS.update(data['markups'])
        return jsonify({'status': 'success', 'message': 'Import markups updated'})
    
    return jsonify({'status': 'error', 'message': 'No valid data provided'}), 400

# ============================================================
# MARKETPLACE API
# ============================================================

@app.route('/api/marketplace')
def api_marketplace():
    """Get all marketplace listings"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM marketplace_listings 
        WHERE status = 'active'
        ORDER BY created_at DESC
        LIMIT 100
    """)
    listings = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(listings)

@app.route('/api/marketplace/search')
def api_marketplace_search():
    """Search marketplace listings"""
    query = request.args.get('q', '')
    listing_type = request.args.get('type', '')
    
    conn = get_db()
    c = conn.cursor()
    
    sql = """
        SELECT * FROM marketplace_listings 
        WHERE status = 'active' AND item_name LIKE ?
    """
    params = [f'%{query}%']
    
    if listing_type:
        sql += " AND listing_type = ?"
        params.append(listing_type)
    
    sql += " ORDER BY price_per_unit ASC LIMIT 50"
    
    c.execute(sql, params)
    listings = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(listings)

@app.route('/api/marketplace/create', methods=['POST'])
def api_marketplace_create():
    """Create a new marketplace listing"""
    data = request.get_json()
    
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO marketplace_listings 
        (discord_user_id, seller_name, listing_type, item_name, quantity, 
         price_per_unit, total_value, location, description, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
    """, (
        data.get('user_id', 'web'),
        data.get('seller_name', 'Anonymous'),
        data.get('listing_type', 'sell'),
        data['item_name'],
        data['quantity'],
        data['price_per_unit'],
        data['price_per_unit'] * data['quantity'],
        data.get('location', 'Unknown'),
        data.get('description', ''),
        datetime.now().isoformat()
    ))
    conn.commit()
    listing_id = c.lastrowid
    conn.close()
    
    return jsonify({'status': 'success', 'listing_id': listing_id})

@app.route('/api/marketplace/<int:listing_id>/cancel', methods=['POST'])
def api_marketplace_cancel(listing_id):
    """Cancel a marketplace listing"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        UPDATE marketplace_listings 
        SET status = 'cancelled'
        WHERE id = ?
    """, (listing_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# ============================================================
# JF CONTRACTS API (for web dashboard)
# ============================================================

@app.route('/api/jf/create', methods=['POST'])
def api_jf_create():
    """Create JF contract from web"""
    data = request.get_json()
    
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO jf_contracts 
        (discord_user_id, discord_username, character_name, origin, destination,
         volume_m3, collateral, price, status, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
    """, (
        data.get('user_id', 'web'),
        data.get('username', 'web_user'),
        data.get('character_name', 'Unknown'),
        data['origin'],
        data['destination'],
        data['volume'],
        data['collateral'],
        data['price'],
        data.get('notes', ''),
        datetime.now().isoformat()
    ))
    conn.commit()
    contract_id = c.lastrowid
    conn.close()
    
    return jsonify({'status': 'success', 'contract_id': contract_id})

@app.route('/api/jf/calculate', methods=['POST'])
def api_jf_calculate():
    """Calculate JF price"""
    data = request.get_json()
    origin = data.get('origin', '').upper()
    destination = data.get('destination', '').upper()
    volume = float(data.get('volume', 0))
    collateral = float(data.get('collateral', 0))
    
    # Normalize
    system_map = {
        'DPN': 'DPN', 'D-PN': 'DPN',
        'VA6': 'VA6', 'VA6-ED': 'VA6',
        'RDG': 'RDG', 'RD-G2R': 'RDG',
        'JITA': 'JITA'
    }
    
    origin_code = system_map.get(origin, origin[:3] if len(origin) > 3 else origin)
    dest_code = system_map.get(destination, destination[:3] if len(destination) > 3 else destination)
    
    route_key = f"{origin_code}-{dest_code}"
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM jf_rates WHERE route = ? AND active = 1", (route_key,))
    rate_data = c.fetchone()
    conn.close()
    
    if not rate_data:
        return jsonify({'error': 'Route not available'}), 400
    
    base_price = volume * rate_data['base_rate']
    collateral_fee = 0
    if collateral > rate_data['min_collateral']:
        collateral_fee = (collateral - rate_data['min_collateral']) * rate_data['collateral_fee_rate']
    
    return jsonify({
        'origin': origin_code,
        'destination': dest_code,
        'base_price': base_price,
        'collateral_fee': collateral_fee,
        'total_price': base_price + collateral_fee,
        'rate': rate_data['base_rate']
    })

# ============================================================
# MARKETPLACE PAGE
# ============================================================

@app.route('/marketplace')
def marketplace_page():
    """Marketplace web interface"""
    return render_template('marketplace.html')

@app.route('/jf-booking')
def jf_booking_page():
    """JF booking web interface"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM jf_rates WHERE active = 1 ORDER BY route")
    rates = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('jf_booking.html', rates=rates)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
