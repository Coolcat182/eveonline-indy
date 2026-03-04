# 📝 JF Cargo Calculator Usage Guide

## How to Use `/jf_cargo`

### Step 1: Copy Your Cargo
**From EVE Inventory:**
1. Open your ship cargo hold or hangar
2. Press `Ctrl+A` to select all items
3. Press `Ctrl+C` to copy

**From Cargo Scan:**
1. Cargo scan a target
2. Copy the results

### Step 2: Use the Command
```
/jf_cargo origin:RD-G2R destination:Jita cargo:[paste here]
```

### Example Inputs:

**Simple list:**
```
Drake x5
Raven x2
Shield Booster x10
Tritanium x50000
```

**From EVE copy (various formats accepted):**
```
Drake Navy Issue x5
Large Shield Booster II x10
Scourge Heavy Missile x10000
PLEX x100
```

### What the Bot Does:

1. **Parses Items**: Recognizes item names and quantities
2. **Looks Up Prices**: Fetches Jita buy prices via ESI
3. **Calculates Volume**: Sums up total m³
4. **Calculates Value**: Total collateral value
5. **Quotes JF Cost**: Shows shipping price with distance-based rates

### Output Example:

```
📦 Cargo Analysis & JF Quote
Route: RD-G2R → Jita

Items (3 types, 7 total):
• Drake Navy Issue x5 - 75,000.0m³ (475.00M ISK)
• Large Shield Booster II x10 - 50.0m³ (12.50M ISK)  
• Scourge Heavy Missile x10000 - 1,000.0m³ (8.00M ISK)

📊 Totals:
Total Volume: 76,050.0 m³
Total Value: 495.50M ISK
Unknown Items: 0

🚀 JF Shipping Cost:
Volume Charge:
76,050m³ × 250 ISK = 19.01M ISK

Collateral Fee:
495.50M × 1% = 4.96M ISK

Total: 23.97M ISK

📋 To Book This Shipment:
Use: /jf_contract origin:RD-G2R destination:Jita...
```

## Features:

✅ **Paste & Calculate** - Copy directly from EVE inventory  
✅ **Jita Prices** - Live market data via ESI  
✅ **Auto-Detection** - Recognizes 50+ common items  
✅ **Distance Pricing** - Tiered rates based on jump distance  
✅ **Quick Booking** - One-click to create JF contract  

## Tips:

- Works with any WinterCo hub system
- Unknown items will show ⚠️ but still count toward volume
- Jita prices update every 5 minutes
- Maximum cargo: Rhea capacity (~3.4M m³)

## Available Systems:

**Hub (Tier 0):** RD-G2R  
**Close (Tier 1):** D-PN, VA6-ED  
**Near (Tier 2):** O-BKJY, 7RM-N0, C4C-Z4  
**Medium (Tier 3):** MTO-OK, 2R-CRW, NHKO-2  
**Far (Tier 4):** KQU-WS, 6Y-WRM  
**Highsec (Tier 5):** Jita  

**Pro Tip:** Ship to RD-G2R first for cheapest rates!
