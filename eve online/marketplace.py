# Player Marketplace Module

@bot.tree.command(name="market", description="Player marketplace - buy, sell, and trade")
@app_commands.describe(
    action="Action to perform",
    item="Item name",
    quantity="Quantity available",
    price="Price per unit",
    location="Location/Station",
    description="Additional details"
)
@app_commands.choices(action=[
    app_commands.Choice(name="sell", value="sell"),
    app_commands.Choice(name="buy", value="buy"),
    app_commands.Choice(name="list", value="list"),
    app_commands.Choice(name="search", value="search"),
    app_commands.Choice(name="mylistings", value="mylistings"),
    app_commands.Choice(name="remove", value="remove"),
])
async def market_cmd(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    item: str = None,
    quantity: int = None,
    price: float = None,
    location: str = None,
    description: str = None
):
    """Player marketplace for items and services"""
    conn = get_db()
    c = conn.cursor()
    user_id = str(interaction.user.id)
    
    if action.value == "sell":
        if not all([item, quantity, price, location]):
            await interaction.response.send_message(
                "❌ Please provide: item name, quantity, price, and location.",
                ephemeral=True
            )
            conn.close()
            return
        
        total_value = price * quantity
        
        c.execute("""
            INSERT INTO marketplace_listings 
            (discord_user_id, seller_name, listing_type, item_name, quantity, price_per_unit, 
             total_value, location, description, status, created_at)
            VALUES (?, ?, 'sell', ?, ?, ?, ?, ?, ?, 'active', ?)
        """, (user_id, interaction.user.name, item, quantity, price, total_value, 
              location, description or '', datetime.now().isoformat()))
        conn.commit()
        listing_id = c.lastrowid
        
        embed = discord.Embed(
            title="✅ Listing Created",
            description=f"Your item is now for sale!",
            color=discord.Color.green()
        )
        embed.add_field(name="Listing ID", value=f"#{listing_id}", inline=True)
        embed.add_field(name="Item", value=item, inline=True)
        embed.add_field(name="Quantity", value=f"{quantity:,}", inline=True)
        embed.add_field(name="Price/Unit", value=f"{price:,.0f} ISK", inline=True)
        embed.add_field(name="Total Value", value=f"{total_value:,.0f} ISK", inline=True)
        embed.add_field(name="Location", value=location, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "buy":
        if not all([item, quantity, price, location]):
            await interaction.response.send_message(
                "❌ Please provide: item name, quantity, price, and location.",
                ephemeral=True
            )
            conn.close()
            return
        
        total_value = price * quantity
        
        c.execute("""
            INSERT INTO marketplace_listings 
            (discord_user_id, seller_name, listing_type, item_name, quantity, price_per_unit, 
             total_value, location, description, status, created_at)
            VALUES (?, ?, 'buy', ?, ?, ?, ?, ?, ?, 'active', ?)
        """, (user_id, interaction.user.name, item, quantity, price, total_value, 
              location, description or '', datetime.now().isoformat()))
        conn.commit()
        listing_id = c.lastrowid
        
        embed = discord.Embed(
            title="✅ Buy Order Created",
            description=f"You are now looking to buy:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Order ID", value=f"#{listing_id}", inline=True)
        embed.add_field(name="Item", value=item, inline=True)
        embed.add_field(name="Quantity Wanted", value=f"{quantity:,}", inline=True)
        embed.add_field(name="Price/Unit", value=f"{price:,.0f} ISK", inline=True)
        embed.add_field(name="Total Budget", value=f"{total_value:,.0f} ISK", inline=True)
        embed.add_field(name="Location", value=location, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "list":
        c.execute("""
            SELECT * FROM marketplace_listings 
            WHERE status = 'active'
            ORDER BY created_at DESC
            LIMIT 25
        """)
        listings = c.fetchall()
        
        if not listings:
            await interaction.response.send_message(
                "📭 No active listings found.",
                ephemeral=True
            )
            conn.close()
            return
        
        embed = discord.Embed(
            title="🛒 Player Marketplace",
            description=f"Active Listings: {len(listings)}",
            color=discord.Color.gold()
        )
        
        for listing in listings[:20]:
            listing_id = listing[0]
            listing_type = listing[3]
            item_name = listing[4]
            qty = listing[5]
            price = listing[6]
            total = listing[7]
            location = listing[8]
            seller = listing[2]
            
            type_emoji = "💰" if listing_type == 'sell' else "📥"
            
            embed.add_field(
                name=f"#{listing_id} {type_emoji} {item_name} x{qty:,}",
                value=f"💵 {price:,.0f} ISK/ea | 📍 {location}\n"
                      f"💰 Total: {total:,.0f} ISK | 👤 {seller}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "search":
        if not item:
            await interaction.response.send_message(
                "❌ Please provide an item name to search for.",
                ephemeral=True
            )
            conn.close()
            return
        
        c.execute("""
            SELECT * FROM marketplace_listings 
            WHERE status = 'active' AND item_name LIKE ?
            ORDER BY price_per_unit ASC
            LIMIT 20
        """, (f'%{item}%',))
        listings = c.fetchall()
        
        if not listings:
            await interaction.response.send_message(
                f"🔍 No listings found for '{item}'.",
                ephemeral=True
            )
            conn.close()
            return
        
        embed = discord.Embed(
            title=f"🔍 Search Results: {item}",
            description=f"Found {len(listings)} listing(s)",
            color=discord.Color.blue()
        )
        
        for listing in listings[:15]:
            listing_id = listing[0]
            listing_type = listing[3]
            item_name = listing[4]
            qty = listing[5]
            price = listing[6]
            loc = listing[8]
            seller = listing[2]
            
            type_emoji = "💰 SELL" if listing_type == 'sell' else "📥 BUY"
            
            embed.add_field(
                name=f"#{listing_id} {type_emoji}",
                value=f"{item_name} x{qty:,} @ {price:,.0f} ISK\n"
                      f"📍 {loc} | 👤 {seller}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    elif action.value == "mylistings":
        c.execute("""
            SELECT id, listing_type, item_name, quantity, price_per_unit, total_value, location, status
            FROM marketplace_listings 
            WHERE discord_user_id = ?
            ORDER BY created_at DESC
            LIMIT 20
        """, (user_id,))
        listings = c.fetchall()
        
        if not listings:
            await interaction.response.send_message(
                "📭 You have no active listings.",
                ephemeral=True
            )
            conn.close()
            return
        
        embed = discord.Embed(title="📋 Your Listings", color=discord.Color.purple())
        
        for listing in listings:
            listing_id, l_type, item_name, qty, price, total, location, status = listing
            type_emoji = "💰" if l_type == 'sell' else "📥"
            status_emoji = "✅" if status == 'active' else "❌"
            
            embed.add_field(
                name=f"{status_emoji} #{listing_id} {type_emoji} {item_name} x{qty:,}",
                value=f"💵 {price:,.0f} ISK/ea | 📍 {location}\n"
                      f"💰 Total: {total:,.0f} ISK",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    elif action.value == "remove":
        if not item:
            await interaction.response.send_message(
                "❌ Please provide the listing ID to remove.",
                ephemeral=True
            )
            conn.close()
            return
        
        try:
            listing_id = int(item)
        except ValueError:
            await interaction.response.send_message(
                "❌ Please provide a numeric listing ID.",
                ephemeral=True
            )
            conn.close()
            return
        
        c.execute("""
            UPDATE marketplace_listings 
            SET status = 'cancelled'
            WHERE id = ? AND discord_user_id = ? AND status = 'active'
        """, (listing_id, user_id))
        conn.commit()
        
        if c.rowcount > 0:
            await interaction.response.send_message(
                f"✅ Listing #{listing_id} has been cancelled.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Listing #{listing_id} not found or not yours.",
                ephemeral=True
            )
    
    conn.close()

print("✅ Marketplace commands loaded!")
