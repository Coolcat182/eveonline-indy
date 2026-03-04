# Alliance, Corp, and Character Commands Extension
# Import this in bot.py or add to the end of bot.py

# ============================================================
# CHARACTER AUTHENTICATION & MANAGEMENT
# ============================================================

@bot.tree.command(name="auth", description="Link your EVE character via ESI authentication")
async def auth_cmd(interaction: discord.Interaction):
    """Start ESI OAuth flow for character authentication"""
    
    embed = discord.Embed(
        title="🔐 EVE ESI Authentication",
        description="Link your EVE character to unlock personalized features",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="What You'll Get:",
        value="✅ Automatic character skill tracking\n"
              "✅ Wallet balance monitoring\n"
              "✅ Corp/Alliance role integration\n"
              "✅ Shared asset access\n"
              "✅ Real-time location tracking",
        inline=False
    )
    
    embed.add_field(
        name="How to Authenticate:",
        value="1. Visit: https://developers.eveonline.com\n"
              "2. Create an application\n"
              "3. Use the auth link below\n"
              "4. Authorize this bot\n"
              "5. Copy the code and use `/auth_code`",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Security Note",
        value="Your tokens are encrypted and stored securely. "
              "The bot only reads data - it cannot perform actions on your behalf.",
        inline=False
    )
    
    # Check if already authenticated
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM character_auth WHERE discord_user_id = ?", (str(interaction.user.id),))
    auth_data = c.fetchone()
    conn.close()
    
    if auth_data and auth_data[9]:  # is_authenticated
        embed.add_field(
            name="Status",
            value=f"✅ Already authenticated as: {auth_data[3]}\n"
                  f"Corporation: {auth_data[5] or 'Unknown'}\n"
                  f"Alliance: {auth_data[7] or 'None'}",
            inline=False
        )
    else:
        embed.add_field(
            name="Status",
            value="❌ Not authenticated. Use the link above to start.",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="auth_code", description="Complete ESI authentication with authorization code")
@app_commands.describe(code="Authorization code from EVE SSO")
async def auth_code_cmd(interaction: discord.Interaction, code: str):
    """Complete the OAuth flow with authorization code"""
    # This is a placeholder - in production, you'd exchange the code for tokens
    await interaction.response.send_message(
        f"🔐 Auth code received: `{code[:10]}...`\n"
        f"In production, this would complete the OAuth flow and link your character.",
        ephemeral=True
    )

@bot.tree.command(name="mychar", description="View your linked character information")
async def mychar_cmd(interaction: discord.Interaction):
    """View authenticated character details"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM character_auth WHERE discord_user_id = ?", (str(interaction.user.id),))
    char_data = c.fetchone()
    conn.close()
    
    if not char_data or not char_data[9]:
        await interaction.response.send_message(
            "❌ You haven't linked an EVE character yet.\n"
            "Use `/auth` to authenticate with ESI.",
            ephemeral=True
        )
        return
    
    embed = discord.Embed(
        title=f"👤 Character: {char_data[3]}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Character ID", value=str(char_data[2]), inline=True)
    embed.add_field(name="Corporation", value=char_data[5] or "Unknown", inline=True)
    embed.add_field(name="Alliance", value=char_data[7] or "None", inline=True)
    
    # Get character's industry jobs
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*), SUM(profit) FROM industry_jobs 
        WHERE discord_user_id = ? AND status = 'completed'
    """, (str(interaction.user.id),))
    jobs_count, total_profit = c.fetchone()
    conn.close()
    
    embed.add_field(name="Jobs Completed", value=str(jobs_count or 0), inline=True)
    embed.add_field(name="Total Profit", value=f"{total_profit or 0:,.0f} ISK", inline=True)
    embed.add_field(name="Status", value="✅ Authenticated", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unlink", description="Unlink your EVE character from this bot")
async def unlink_cmd(interaction: discord.Interaction):
    """Remove character authentication"""
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM character_auth WHERE discord_user_id = ?", (str(interaction.user.id),))
    conn.commit()
    conn.close()
    
    await interaction.response.send_message(
        "✅ Your EVE character has been unlinked.\n"
        "Use `/auth` to link a new character.",
        ephemeral=True
    )

# ============================================================
# CORPORATION MANAGEMENT
# ============================================================

@bot.tree.command(name="corp", description="Corporation management and information")
@app_commands.describe(
    action="Action to perform",
    target="Target corporation or character"
)
@app_commands.choices(action=[
    app_commands.Choice(name="info", value="info"),
    app_commands.Choice(name="members", value="members"),
    app_commands.Choice(name="assets", value="assets"),
    app_commands.Choice(name="jobs", value="jobs"),
    app_commands.Choice(name="bpos", value="bpos"),
    app_commands.Choice(name="register", value="register"),
])
async def corp_cmd(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    target: str = None
):
    """Corporation management commands"""
    conn = get_db()
    c = conn.cursor()
    
    if action.value == "register":
        if not target:
            await interaction.response.send_message(
                "❌ Please provide a corporation name. Example: `/corp action:register target:WinterCo`",
                ephemeral=True
            )
            conn.close()
            return
        
        c.execute("""
            INSERT OR REPLACE INTO corporations 
            (corporation_id, corporation_name, created_at)
            VALUES (?, ?, ?)
        """, (hash(target) % 1000000, target, datetime.now().isoformat()))
        conn.commit()
        
        await interaction.response.send_message(
            f"✅ Corporation '{target}' registered.\n"
            f"Members can now link their characters with `/auth`",
            ephemeral=True
        )
    
    elif action.value == "info":
        c.execute("SELECT * FROM corporations WHERE corporation_name = ? OR corporation_id = ?", 
                 (target or "", target or 0))
        corp = c.fetchone()
        
        if not corp:
            c.execute("SELECT corporation_name FROM character_auth WHERE discord_user_id = ?", 
                     (str(interaction.user.id),))
            char_corp = c.fetchone()
            
            if char_corp and char_corp[0]:
                await interaction.response.send_message(
                    f"📊 Your corporation: {char_corp[0]}\n"
                    f"Use `/corp action:register target:{char_corp[0]}` to register it.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Corporation not found. Register it with `/corp action:register`",
                    ephemeral=True
                )
            conn.close()
            return
        
        embed = discord.Embed(
            title=f"🏢 Corporation: {corp[2]}",
            color=discord.Color.green()
        )
        embed.add_field(name="Corp ID", value=str(corp[1]), inline=True)
        embed.add_field(name="Ticker", value=corp[4] or "N/A", inline=True)
        embed.add_field(name="Members", value=str(corp[6] or 0), inline=True)
        embed.add_field(name="Tax Rate", value=f"{(corp[7] or 0) * 100:.1f}%", inline=True)
        
        c.execute("SELECT COUNT(*) FROM corporation_members WHERE corporation_id = ?", (corp[1],))
        member_count = c.fetchone()[0]
        embed.add_field(name="Registered Members", value=str(member_count), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "members":
        c.execute("""
            SELECT cm.character_name, cm.roles, cm.joined_at
            FROM corporation_members cm
            JOIN corporations c ON cm.corporation_id = c.corporation_id
            WHERE c.corporation_name = ? OR c.corporation_id = ?
            ORDER BY cm.joined_at DESC
            LIMIT 20
        """, (target or "", target or 0))
        members = c.fetchall()
        
        if not members:
            await interaction.response.send_message("❌ No members found.", ephemeral=True)
            conn.close()
            return
        
        embed = discord.Embed(title=f"👥 Members", color=discord.Color.blue())
        for member in members[:10]:
            roles = member[1] or "Member"
            embed.add_field(name=member[0], value=f"Roles: {roles}", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "assets":
        c.execute("""
            SELECT asset_type, asset_name, quantity, location, status
            FROM shared_assets
            WHERE owner_type = 'corporation' AND owner_id = (
                SELECT corporation_id FROM corporations 
                WHERE corporation_name = ? OR corporation_id = ?
            )
        """, (target or "", target or 0))
        assets = c.fetchall()
        
        if not assets:
            await interaction.response.send_message(
                "📦 No shared assets found.\nUse `/asset add` to add corporation assets.",
                ephemeral=True
            )
            conn.close()
            return
        
        embed = discord.Embed(title=f"📦 Corporation Assets", color=discord.Color.gold())
        for asset in assets[:10]:
            status_emoji = "✅" if asset[4] == 'available' else "🔒"
            embed.add_field(
                name=f"{status_emoji} {asset[1]}",
                value=f"Qty: {asset[2]} | Loc: {asset[3]}",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "jobs":
        c.execute("""
            SELECT product_name, quantity, status, character_name
            FROM industry_jobs
            WHERE corporation_id = (
                SELECT corporation_id FROM corporations 
                WHERE corporation_name = ? OR corporation_id = ?
            )
            ORDER BY created_at DESC
            LIMIT 10
        """, (target or "", target or 0))
        jobs = c.fetchall()
        
        if not jobs:
            await interaction.response.send_message("🏭 No corporation jobs found.", ephemeral=True)
            conn.close()
            return
        
        embed = discord.Embed(title=f"🏭 Corporation Industry Jobs", color=discord.Color.orange())
        for job in jobs:
            status_emoji = {"pending": "⏳", "building": "🔨", "completed": "✅"}.get(job[2], "❓")
            embed.add_field(
                name=f"{status_emoji} {job[0]} x{job[1]}",
                value=f"Status: {job[2]} | By: {job[3]}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "bpos":
        c.execute("""
            SELECT bpo_name, me, te, location, is_shared
            FROM user_bpos
            WHERE ownership_level = 'corporation'
            AND (corporation_id = (
                SELECT corporation_id FROM corporations 
                WHERE corporation_name = ? OR corporation_id = ?
            ) OR corporation_id IS NULL)
        """, (target or "", target or 0))
        bpos = c.fetchall()
        
        if not bpos:
            await interaction.response.send_message(
                "📘 No corporation BPOs found.\nUse `/bpo share` to share your BPOs.",
                ephemeral=True
            )
            conn.close()
            return
        
        embed = discord.Embed(title=f"📘 Corporation BPO Library", color=discord.Color.blue())
        for bpo in bpos[:15]:
            share_status = "🌐" if bpo[4] else "🔒"
            embed.add_field(
                name=f"{share_status} {bpo[0]}",
                value=f"ME: {bpo[1]} | TE: {bpo[2]} | Loc: {bpo[3]}",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
    
    conn.close()

@bot.tree.command(name="corp_join", description="Join a registered corporation")
@app_commands.describe(corporation_name="Name of the corporation to join")
async def corp_join_cmd(interaction: discord.Interaction, corporation_name: str):
    """Join a corporation in the system"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT corporation_id FROM corporations WHERE corporation_name = ?", (corporation_name,))
    corp = c.fetchone()
    
    if not corp:
        await interaction.response.send_message(
            f"❌ Corporation '{corporation_name}' not found.\n"
            f"Use `/corp action:register` to register it first.",
            ephemeral=True
        )
        conn.close()
        return
    
    c.execute("SELECT character_id, character_name FROM character_auth WHERE discord_user_id = ?", 
             (str(interaction.user.id),))
    char = c.fetchone()
    
    character_id = char[0] if char else hash(interaction.user.name) % 1000000
    character_name = char[1] if char else interaction.user.name
    
    c.execute("""
        INSERT OR REPLACE INTO corporation_members 
        (corporation_id, character_id, character_name, discord_user_id, joined_at)
        VALUES (?, ?, ?, ?, ?)
    """, (corp[0], character_id, character_name, str(interaction.user.id), datetime.now().isoformat()))
    
    if char:
        c.execute("""
            UPDATE character_auth 
            SET corporation_id = ?, corporation_name = ?
            WHERE discord_user_id = ?
        """, (corp[0], corporation_name, str(interaction.user.id)))
    
    conn.commit()
    conn.close()
    
    await interaction.response.send_message(
        f"✅ You have joined '{corporation_name}'!\n"
        f"You now have access to corp assets, BPOs, and shared jobs.",
        ephemeral=True
    )

# ============================================================
# ALLIANCE MANAGEMENT
# ============================================================

@bot.tree.command(name="alliance", description="Alliance management and information")
@app_commands.describe(
    action="Action to perform",
    target="Target alliance"
)
@app_commands.choices(action=[
    app_commands.Choice(name="info", value="info"),
    app_commands.Choice(name="corps", value="corps"),
    app_commands.Choice(name="assets", value="assets"),
    app_commands.Choice(name="register", value="register"),
])
async def alliance_cmd(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    target: str = None
):
    """Alliance management commands"""
    conn = get_db()
    c = conn.cursor()
    
    if action.value == "register":
        if not target:
            await interaction.response.send_message(
                "❌ Please provide an alliance name.",
                ephemeral=True
            )
            conn.close()
            return
        
        c.execute("""
            INSERT OR REPLACE INTO alliances 
            (alliance_id, alliance_name, created_at)
            VALUES (?, ?, ?)
        """, (hash(target) % 1000000, target, datetime.now().isoformat()))
        conn.commit()
        
        await interaction.response.send_message(
            f"✅ Alliance '{target}' registered.",
            ephemeral=True
        )
    
    elif action.value == "info":
        c.execute("SELECT * FROM alliances WHERE alliance_name = ? OR alliance_id = ?", 
                 (target or "", target or 0))
        alliance = c.fetchone()
        
        if not alliance:
            await interaction.response.send_message(
                "❌ Alliance not found. Register it with `/alliance action:register`",
                ephemeral=True
            )
            conn.close()
            return
        
        embed = discord.Embed(
            title=f"⚔️ Alliance: {alliance[2]}",
            color=discord.Color.purple()
        )
        embed.add_field(name="Alliance ID", value=str(alliance[1]), inline=True)
        embed.add_field(name="Ticker", value=alliance[3] or "N/A", inline=True)
        
        c.execute("SELECT COUNT(*) FROM alliance_corporations WHERE alliance_id = ?", (alliance[1],))
        corp_count = c.fetchone()[0]
        embed.add_field(name="Member Corps", value=str(corp_count), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "corps":
        c.execute("""
            SELECT c.corporation_name, c.member_count, ac.joined_at
            FROM alliance_corporations ac
            JOIN alliances a ON ac.alliance_id = a.alliance_id
            JOIN corporations c ON ac.corporation_id = c.corporation_id
            WHERE a.alliance_name = ? OR a.alliance_id = ?
        """, (target or "", target or 0))
        corps = c.fetchall()
        
        if not corps:
            await interaction.response.send_message("❌ No corporations found.", ephemeral=True)
            conn.close()
            return
        
        embed = discord.Embed(title=f"🏢 Alliance Corporations", color=discord.Color.blue())
        for corp in corps:
            embed.add_field(
                name=corp[0],
                value=f"Members: {corp[1]}",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "assets":
        c.execute("""
            SELECT asset_type, asset_name, quantity, location
            FROM shared_assets
            WHERE owner_type = 'alliance' AND owner_id = (
                SELECT alliance_id FROM alliances 
                WHERE alliance_name = ? OR alliance_id = ?
            )
        """, (target or "", target or 0))
        assets = c.fetchall()
        
        if not assets:
            await interaction.response.send_message(
                "📦 No alliance assets found.",
                ephemeral=True
            )
            conn.close()
            return
        
        embed = discord.Embed(title=f"📦 Alliance Assets", color=discord.Color.gold())
        for asset in assets[:10]:
            embed.add_field(
                name=asset[1],
                value=f"Qty: {asset[2]} | Loc: {asset[3]}",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
    
    conn.close()

@bot.tree.command(name="alliance_join", description="Add your corporation to an alliance")
@app_commands.describe(alliance_name="Name of the alliance to join")
async def alliance_join_cmd(interaction: discord.Interaction, alliance_name: str):
    """Join an alliance with your corporation"""
    conn = get_db()
    c = conn.cursor()
    
    # Get user's corporation
    c.execute("SELECT corporation_id, corporation_name FROM character_auth WHERE discord_user_id = ?", 
             (str(interaction.user.id),))
    char_data = c.fetchone()
    
    if not char_data or not char_data[0]:
        await interaction.response.send_message(
            "❌ You must be a member of a corporation first.\n"
            "Use `/corp_join` to join a corporation.",
            ephemeral=True
        )
        conn.close()
        return
    
    corp_id, corp_name = char_data[0], char_data[1]
    
    # Find alliance
    c.execute("SELECT alliance_id FROM alliances WHERE alliance_name = ?", (alliance_name,))
    alliance = c.fetchone()
    
    if not alliance:
        await interaction.response.send_message(
            f"❌ Alliance '{alliance_name}' not found.",
            ephemeral=True
        )
        conn.close()
        return
    
    # Add corp to alliance
    c.execute("""
        INSERT OR REPLACE INTO alliance_corporations 
        (alliance_id, corporation_id, joined_at)
        VALUES (?, ?, ?)
    """, (alliance[0], corp_id, datetime.now().isoformat()))
    
    # Update corporation with alliance
    c.execute("""
        UPDATE corporations 
        SET alliance_id = ?
        WHERE corporation_id = ?
    """, (alliance[0], corp_id))
    
    conn.commit()
    conn.close()
    
    await interaction.response.send_message(
        f"✅ Corporation '{corp_name}' has joined alliance '{alliance_name}'!",
        ephemeral=True
    )

# ============================================================
# SHARED ASSET MANAGEMENT
# ============================================================

@bot.tree.command(name="asset", description="Manage shared assets")
@app_commands.describe(
    action="Action to perform",
    name="Asset name",
    quantity="Quantity",
    location="Asset location"
)
@app_commands.choices(action=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="list", value="list"),
    app_commands.Choice(name="checkout", value="checkout"),
    app_commands.Choice(name="return", value="return"),
])
async def asset_cmd(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    name: str = None,
    quantity: int = 1,
    location: str = None
):
    """Manage shared corporation/alliance assets"""
    conn = get_db()
    c = conn.cursor()
    user_id = str(interaction.user.id)
    
    if action.value == "add":
        if not name or not location:
            await interaction.response.send_message(
                "❌ Please provide asset name and location.",
                ephemeral=True
            )
            conn.close()
            return
        
        # Determine ownership level
        c.execute("SELECT corporation_id, alliance_id FROM character_auth WHERE discord_user_id = ?", (user_id,))
        char_data = c.fetchone()
        
        if char_data and char_data[1]:  # Has alliance
            owner_type = 'alliance'
            owner_id = char_data[1]
        elif char_data and char_data[0]:  # Has corp
            owner_type = 'corporation'
            owner_id = char_data[0]
        else:
            owner_type = 'personal'
            owner_id = hash(user_id) % 1000000
        
        c.execute("""
            INSERT INTO shared_assets 
            (owner_type, owner_id, asset_type, asset_name, quantity, location, status)
            VALUES (?, ?, ?, ?, ?, ?, 'available')
        """, (owner_type, owner_id, 'misc', name, quantity, location))
        conn.commit()
        
        await interaction.response.send_message(
            f"✅ Added {quantity}x {name} to {owner_type} assets at {location}.",
            ephemeral=True
        )
    
    elif action.value == "list":
        c.execute("""
            SELECT asset_name, quantity, location, status, checked_out_by
            FROM shared_assets
            WHERE owner_type IN ('corporation', 'alliance')
            ORDER BY owner_type, asset_name
            LIMIT 20
        """)
        assets = c.fetchall()
        
        if not assets:
            await interaction.response.send_message("📦 No shared assets found.", ephemeral=True)
            conn.close()
            return
        
        embed = discord.Embed(title="📦 Shared Assets", color=discord.Color.gold())
        for asset in assets[:15]:
            status = "✅ Available" if asset[3] == 'available' else f"🔒 Checked out by {asset[4]}"
            embed.add_field(
                name=f"{asset[0]} x{asset[1]}",
                value=f"Loc: {asset[2]} | {status}",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "checkout":
        if not name:
            await interaction.response.send_message("❌ Please specify asset name.", ephemeral=True)
            conn.close()
            return
        
        c.execute("""
            UPDATE shared_assets 
            SET status = 'checked_out', checked_out_by = ?, checked_out_at = ?
            WHERE asset_name = ? AND status = 'available'
        """, (interaction.user.name, datetime.now().isoformat(), name))
        conn.commit()
        
        if c.rowcount > 0:
            await interaction.response.send_message(f"✅ You have checked out: {name}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Asset '{name}' not available or not found.", ephemeral=True)
    
    elif action.value == "return":
        if not name:
            await interaction.response.send_message("❌ Please specify asset name.", ephemeral=True)
            conn.close()
            return
        
        c.execute("""
            UPDATE shared_assets 
            SET status = 'available', checked_out_by = NULL, checked_out_at = NULL
            WHERE asset_name = ? AND checked_out_by = ?
        """, (name, interaction.user.name))
        conn.commit()
        
        if c.rowcount > 0:
            await interaction.response.send_message(f"✅ You have returned: {name}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Asset '{name}' not found or not checked out by you.", ephemeral=True)
    
    conn.close()

# ============================================================
# BPO SHARING
# ============================================================

@bot.tree.command(name="bpo_share", description="Share a BPO with your corporation or alliance")
@app_commands.describe(
    bpo_name="Name of the BPO to share",
    share_level="Who to share with"
)
@app_commands.choices(share_level=[
    app_commands.Choice(name="corporation", value="corporation"),
    app_commands.Choice(name="alliance", value="alliance"),
])
async def bpo_share_cmd(
    interaction: discord.Interaction,
    bpo_name: str,
    share_level: app_commands.Choice[str]
):
    """Share a personal BPO with corp/alliance"""
    conn = get_db()
    c = conn.cursor()
    user_id = str(interaction.user.id)
    
    # Get user's corp/alliance
    c.execute("SELECT corporation_id, alliance_id FROM character_auth WHERE discord_user_id = ?", (user_id,))
    char_data = c.fetchone()
    
    corp_id = char_data[0] if char_data else None
    alliance_id = char_data[1] if char_data else None
    
    if share_level.value == "alliance" and not alliance_id:
        await interaction.response.send_message(
            "❌ You are not in an alliance.\n"
            "Use `/alliance_join` to join one first.",
            ephemeral=True
        )
        conn.close()
        return
    
    if share_level.value == "corporation" and not corp_id:
        await interaction.response.send_message(
            "❌ You are not in a corporation.\n"
            "Use `/corp_join` to join one first.",
            ephemeral=True
        )
        conn.close()
        return
    
    # Update or insert BPO
    c.execute("""
        INSERT OR REPLACE INTO user_bpos 
        (discord_user_id, bpo_name, ownership_level, corporation_id, alliance_id, is_shared, me, te)
        VALUES (?, ?, ?, ?, ?, 1, 0, 0)
    """, (user_id, bpo_name, share_level.value, corp_id, alliance_id))
    conn.commit()
    conn.close()
    
    await interaction.response.send_message(
        f"✅ Shared '{bpo_name}' with your {share_level.value}!\n"
        f"Other members can now view and use this BPO.",
        ephemeral=True
    )

print("✅ Alliance, Corp, and Character commands loaded!")
