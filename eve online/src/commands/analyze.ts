import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';
import { getTradeSettings } from './config';

export const data = new SlashCommandBuilder()
  .setName('analyze')
  .setDescription('Max profit analysis across all activities')
  .addSubcommand(sub =>
    sub
      .setName('best')
      .setDescription('Find the best ISK-making activity right now'))
  .addSubcommand(sub =>
    sub
      .setName('pi')
      .setDescription('Analyze PI profit - show best tier regardless of what it is')
      .addIntegerOption(opt => opt.setName('colonies').setDescription('Number of colonies available').setRequired(true)))
  .addSubcommand(sub =>
    sub
      .setName('industry')
      .setDescription('Analyze your industry jobs for best profit'))
  .addSubcommand(sub =>
    sub
      .setName('trading')
      .setDescription('Analyze trading opportunities'))
  .addSubcommand(sub =>
    sub
      .setName('all')
      .setDescription('Full profit analysis - everything you could be doing')));

const PURE_BLIND_SYSTEMS = [
  { system: 'D-PN', security: -0.5, stations: ['Solar Fleet'], piPlanets: 8 },
  { system: 'VA6-ED', security: -0.4, stations: ['Keepstar'], piPlanets: 7 },
  { system: 'RD-G2R', security: -0.6, stations: ['Industry Hub'], piPlanets: 9 },
  { system: 'O-BKJY', security: -0.5, stations: [], piPlanets: 6 },
  { system: '7-60QB', security: -0.4, stations: [], piPlanets: 5 },
  { system: 'X-7OMU', security: -0.5, stations: [], piPlanets: 7 },
  { system: 'E-YCML', security: -0.6, stations: [], piPlanets: 8 },
  { system: 'H-PA29', security: -0.5, stations: [], piPlanets: 6 },
  { system: 'F-9CZX', security: -0.4, stations: [], piPlanets: 5 },
  { system: 'FDZ4-A', security: -0.5, stations: [], piPlanets: 7 },
  { system: 'B-VIP9', security: -0.6, stations: [], piPlanets: 6 },
  { system: 'V7-MID', security: -0.5, stations: [], piPlanets: 5 },
];

const PI_PRODUCTS_WITH_PRICES = [
  { name: 'Plasmoids', tier: 'P1', price: 1400, dailyPerColony: 480000, effort: 'low' },
  { name: 'Superconductors', tier: 'P1', price: 1100, dailyPerColony: 420000, effort: 'low' },
  { name: 'Coolant', tier: 'P1', price: 950, dailyPerColony: 380000, effort: 'low' },
  { name: 'Oxidizing Compound', tier: 'P1', price: 380, dailyPerColony: 320000, effort: 'low' },
  { name: 'Gel-Matrix Biopaste', tier: 'P2', price: 4200, dailyPerColony: 580000, effort: 'medium' },
  { name: 'High-Tech Transmitters', tier: 'P2', price: 4200, dailyPerColony: 550000, effort: 'medium' },
  { name: 'Supercomputers', tier: 'P2', price: 4800, dailyPerColony: 520000, effort: 'medium' },
  { name: 'Ukomi Superconductor', tier: 'P2', price: 3900, dailyPerColony: 510000, effort: 'medium' },
  { name: 'Guidance System', tier: 'P3', price: 35000, dailyPerColony: 680000, effort: 'high' },
  { name: 'Nano-Factory', tier: 'P3', price: 45000, dailyPerColony: 720000, effort: 'high' },
  { name: 'Neural Network', tier: 'P3', price: 38000, dailyPerColony: 650000, effort: 'high' },
  { name: 'Broadcast Node', tier: 'P4', price: 1200000, dailyPerColony: 950000, effort: 'very_high' },
  { name: 'Recursive Computing Module', tier: 'P4', price: 1100000, dailyPerColony: 880000, effort: 'very_high' },
];

const TRADE_OPPORTUNITIES = [
  { item: 'Nanite Repair Paste', category: 'Consumables', margin: 30, effort: 'low', capital: 'low' },
  { item: 'Ogre II', category: 'Drones', margin: 18, effort: 'low', capital: 'medium' },
  { item: 'Capacitor Recharger II', category: 'Modules', margin: 20, effort: 'low', capital: 'low' },
  { item: 'Ishtar', category: 'Ships', margin: 15, effort: 'medium', capital: 'high' },
  { item: 'Stratios', category: 'Ships', margin: 12, effort: 'medium', capital: 'high' },
  { item: 'T2 Rigs (Medium)', category: 'Rigs', margin: 25, effort: 'medium', capital: 'medium' },
  { item: 'Fuel Blocks', category: 'Fuel', margin: 25, effort: 'low', capital: 'medium' },
];

db.exec(`
  CREATE TABLE IF NOT EXISTS profit_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    analysis_type TEXT NOT NULL,
    recommendations TEXT,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS pure_blind_systems (
    system TEXT PRIMARY KEY,
    security REAL,
    stations TEXT,
    pi_planets INTEGER
  );
`);

for (const system of PURE_BLIND_SYSTEMS) {
  db.prepare(`
    INSERT OR REPLACE INTO pure_blind_systems (system, security, stations, pi_planets)
    VALUES (?, ?, ?, ?)
  `).run(system.system, system.security, JSON.stringify(system.stations), system.piPlanets);
}

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'best': await handleBest(interaction); break;
    case 'pi': await handlePI(interaction); break;
    case 'industry': await handleIndustry(interaction); break;
    case 'trading': await handleTrading(interaction); break;
    case 'all': await handleAll(interaction); break;
  }
}

async function handleBest(interaction: CommandInteraction) {
  const settings = getTradeSettings(interaction.user.id);
  
  const bestPI = PI_PRODUCTS_WITH_PRICES.reduce((best, p) => 
    p.dailyPerColony > best.dailyPerColony ? p : best
  );
  
  const bestTrade = TRADE_OPPORTUNITIES.reduce((best, t) => 
    t.margin > best.margin ? t : best
  );
  
  const pendingJobs = db.prepare(`
    SELECT product_name, quantity, material_cost, 
           (SELECT MAX(sell_price) FROM industry_jobs WHERE status = 'sold') as avg_sell
    FROM industry_jobs 
    WHERE discord_user_id = ? AND status IN ('pending', 'building')
    LIMIT 5
  `).all(interaction.user.id) as { product_name: string; quantity: number; material_cost: number }[];
  
  const embed = new EmbedBuilder()
    .setTitle('Best ISK-Making Activities Right Now')
    .setColor(0x00ff00)
    .addFields(
      { 
        name: 'PI - Best Profit', 
        value: `**${bestPI.name}** (${bestPI.tier})\n${bestPI.dailyPerColony.toLocaleString()} ISK/day per colony\nEffort: ${bestPI.effort}`, 
        inline: true 
      },
      { 
        name: 'Trading - Best Margin', 
        value: `**${bestTrade.item}**\n${bestTrade.margin}% margin\nEffort: ${bestTrade.effort}`, 
        inline: true 
      }
    );
  
  if (pendingJobs.length > 0) {
    embed.addFields({ 
      name: 'Your Pending Jobs', 
      value: pendingJobs.map(j => `${j.product_name} x${j.quantity}`).join('\n') 
    });
  }
  
  embed.addFields({ 
    name: 'Recommendation', 
    value: `1. Focus PI on **${bestPI.name}** - ${bestPI.dailyPerColony.toLocaleString()} ISK/day\n` +
           `2. Import **${bestTrade.item}** from Jita - ${bestTrade.margin}% margin\n` +
           `3. Check sell orders at D-PN daily`
  });
  
  await interaction.reply({ embeds: [embed] });
}

async function handlePI(interaction: CommandInteraction) {
  const colonies = interaction.options.get('colonies')?.value as number;
  
  const sorted = [...PI_PRODUCTS_WITH_PRICES].sort((a, b) => b.dailyPerColony - a.dailyPerColony);
  
  const best = sorted[0];
  const totalDaily = best.dailyPerColony * colonies;
  const totalMonthly = totalDaily * 30;
  
  const embed = new EmbedBuilder()
    .setTitle('PI Max Profit Analysis')
    .setColor(0x00ff00)
    .setDescription('**Showing the BEST profit regardless of tier**')
    .addFields(
      { 
        name: `BEST: ${best.name} (${best.tier})`, 
        value: `${best.dailyPerColony.toLocaleString()} ISK/day per colony\nEffort: ${best.effort}`, 
        inline: false 
      },
      { name: 'With Your Colonies', value: colonies.toString(), inline: true },
      { name: 'Daily Profit', value: `${totalDaily.toLocaleString()} ISK`, inline: true },
      { name: 'Monthly Profit', value: `${totalMonthly.toLocaleString()} ISK`, inline: true }
    )
    .addFields({ 
      name: 'Top 5 PI Products (Any Tier)', 
      value: sorted.slice(0, 5).map((p, i) => 
        `**${i + 1}. ${p.name}** (${p.tier})\n` +
        `   ${p.dailyPerColony.toLocaleString()} ISK/day | ${p.effort} effort`
      ).join('\n')
    })
    .addFields({ 
      name: 'Pure Blind - Best Systems', 
      value: PURE_BLIND_SYSTEMS.filter(s => s.piPlanets >= 7)
        .map(s => `**${s.system}**: ${s.piPlanets} planets`)
        .join('\n')
    });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleIndustry(interaction: CommandInteraction) {
  const jobs = db.prepare(`
    SELECT id, product_name, quantity, material_cost, status, started_at
    FROM industry_jobs 
    WHERE discord_user_id = ?
    ORDER BY started_at DESC
    LIMIT 20
  `).all(interaction.user.id) as {
    id: number;
    product_name: string;
    quantity: number;
    material_cost: number;
    status: string;
    started_at: string;
  }[];
  
  const soldJobs = jobs.filter(j => j.status === 'sold');
  const totalProfit = soldJobs.reduce((sum, j) => {
    const avgMargin = 0.2;
    return sum + (j.material_cost * avgMargin);
  }, 0);
  
  const pendingJobs = jobs.filter(j => j.status === 'pending' || j.status === 'building');
  const pendingValue = pendingJobs.reduce((sum, j) => sum + j.material_cost, 0);
  
  const embed = new EmbedBuilder()
    .setTitle('Industry Profit Analysis')
    .setColor(0x3498db);
  
  if (pendingJobs.length > 0) {
    embed.addFields({
      name: 'Pending Jobs',
      value: pendingJobs.slice(0, 5).map(j => 
        `**${j.product_name}** x${j.quantity}\n` +
        `   Invested: ${j.material_cost.toLocaleString()} ISK`
      ).join('\n'),
      inline: false
    });
  }
  
  embed.addFields(
    { name: 'Total Jobs', value: jobs.length.toString(), inline: true },
    { name: 'Sold', value: soldJobs.length.toString(), inline: true },
    { name: 'Pending', value: pendingJobs.length.toString(), inline: true },
    { name: 'Capital Tied Up', value: `${pendingValue.toLocaleString()} ISK`, inline: true },
    { name: 'Est. Profit (Sold)', value: `${totalProfit.toLocaleString()} ISK`, inline: true }
  );
  
  embed.addFields({
    name: 'Recommendations',
    value: '• Focus on T2 modules for best margins\n• Build capital components if you have BPOs\n• Check market before starting new jobs'
  });
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleTrading(interaction: CommandInteraction) {
  const settings = getTradeSettings(interaction.user.id);
  
  const opportunities = TRADE_OPPORTUNITIES.map(t => ({
    ...t,
    score: t.margin / (t.effort === 'low' ? 1 : t.effort === 'medium' ? 2 : 3)
  })).sort((a, b) => b.score - a.score);
  
  const embed = new EmbedBuilder()
    .setTitle('Trading Opportunities Analysis')
    .setColor(0xf1c40f)
    .setDescription(`Using ${settings.nullsec_discount * 100}% nullsec discount, ${settings.jf_rate_per_m3} ISK/m³ JF rate`)
    .addFields({
      name: 'Best Imports from Jita',
      value: opportunities.slice(0, 7).map((t, i) => 
        `**${i + 1}. ${t.item}** (${t.category})\n` +
        `   ${t.margin}% margin | ${t.effort} effort | ${t.capital} capital`
      ).join('\n')
    })
    .addFields({
      name: 'Quick Flips',
      value: '• Buy salvage at RD-G2R (5% discount)\n• Flip T2 modules at D-PN\n• Resell PI products from colonies'
    });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleAll(interaction: CommandInteraction) {
  const settings = getTradeSettings(interaction.user.id);
  
  const bestPI = PI_PRODUCTS_WITH_PRICES.reduce((best, p) => 
    p.dailyPerColony > best.dailyPerColony ? p : best
  );
  
  const bestTrade = TRADE_OPPORTUNITIES.reduce((best, t) => 
    t.margin > best.margin ? t : best
  );
  
  const chars = db.prepare(`
    SELECT name, pi_colonies, manufacturing_bonus FROM characters WHERE discord_user_id = ?
  `).all(interaction.user.id) as { name: string; pi_colonies: number; manufacturing_bonus: number }[];
  
  const totalPIColonies = chars.reduce((sum, c) => sum + c.pi_colonies, 0);
  const piDaily = bestPI.dailyPerColony * totalPIColonies;
  const piMonthly = piDaily * 30;
  
  const tradingMonthly = 50000000;
  
  const industryJobs = db.prepare(`
    SELECT COUNT(*) as count FROM industry_jobs WHERE discord_user_id = ?
  `).get(interaction.user.id) as { count: number };
  
  const embed = new EmbedBuilder()
    .setTitle('Complete ISK-Making Analysis')
    .setColor(0x9b59b6)
    .addFields(
      { 
        name: 'PI Income', 
        value: `**${bestPI.name}** (${bestPI.tier})\n` +
               `${totalPIColonies} colonies across ${chars.length} chars\n` +
               `Daily: ${piDaily.toLocaleString()} ISK\n` +
               `Monthly: ${piMonthly.toLocaleString()} ISK`,
        inline: true 
      },
      { 
        name: 'Trading Income', 
        value: `**${bestTrade.item}**\n` +
               `${bestTrade.margin}% margin\n` +
               `Est. Monthly: ${tradingMonthly.toLocaleString()} ISK`,
        inline: true 
      }
    );
  
  const totalMonthly = piMonthly + tradingMonthly;
  
  embed.addFields(
    { name: 'Total Potential Monthly', value: `**${totalMonthly.toLocaleString()} ISK**`, inline: false },
    { name: 'Characters', value: chars.length.toString(), inline: true },
    { name: 'Industry Jobs', value: industryJobs.count.toString(), inline: true },
    { name: 'PI Colonies', value: totalPIColonies.toString(), inline: true }
  );
  
  embed.addFields({
    name: 'Action Plan',
    value: `1. **PI**: All colonies on ${bestPI.name} - ${piMonthly.toLocaleString()} ISK/month\n` +
           `2. **Trading**: Import ${bestTrade.item} from Jita weekly\n` +
           `3. **Industry**: Build T2 modules for local sale\n` +
           `4. **Market**: Check D-PN prices daily`
  });
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}
