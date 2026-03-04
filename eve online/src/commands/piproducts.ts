import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';

interface PIProduct {
  name: string;
  tier: string;
  basePrice: number;
  volume: number;
}

const PI_PRODUCTS: PIProduct[] = [
  { name: 'Nanites', tier: 'P1', basePrice: 450, volume: 0.38 },
  { name: 'Synthetic Oil', tier: 'P1', basePrice: 380, volume: 0.38 },
  { name: 'Polyaramids', tier: 'P1', basePrice: 520, volume: 0.38 },
  { name: 'Microfiber Shielding', tier: 'P1', basePrice: 600, volume: 0.38 },
  { name: 'Smartfab Units', tier: 'P1', basePrice: 420, volume: 0.38 },
  { name: 'Superconductors', tier: 'P1', basePrice: 1100, volume: 0.38 },
  { name: 'Biocells', tier: 'P1', basePrice: 550, volume: 0.38 },
  { name: 'Construction Blocks', tier: 'P1', basePrice: 480, volume: 0.38 },
  { name: 'Mechanical Parts', tier: 'P1', basePrice: 490, volume: 0.38 },
  { name: 'Coolant', tier: 'P1', basePrice: 950, volume: 0.38 },
  { name: 'Condensates', tier: 'P1', basePrice: 580, volume: 0.38 },
  { name: 'Water', tier: 'P1', basePrice: 320, volume: 0.38 },
  { name: 'Bacteria', tier: 'P1', basePrice: 290, volume: 0.38 },
  { name: 'Biomass', tier: 'P1', basePrice: 310, volume: 0.38 },
  { name: 'Proteins', tier: 'P1', basePrice: 350, volume: 0.38 },
  { name: 'Electrolytes', tier: 'P1', basePrice: 620, volume: 0.38 },
  { name: 'Industrial Fibers', tier: 'P1', basePrice: 440, volume: 0.38 },
  { name: 'Oxidizing Compound', tier: 'P1', basePrice: 380, volume: 0.38 },
  { name: 'Plasmoids', tier: 'P1', basePrice: 1400, volume: 0.38 },
  { name: 'Precious Metals', tier: 'P1', basePrice: 650, volume: 0.38 },
  { name: 'Reactive Metals', tier: 'P1', basePrice: 890, volume: 0.38 },
  { name: 'Silicon', tier: 'P1', basePrice: 410, volume: 0.38 },
  { name: 'Toxic Metals', tier: 'P1', basePrice: 720, volume: 0.38 },
  { name: 'Viral Agent', tier: 'P1', basePrice: 510, volume: 0.38 },
  { name: 'Felsic Magma', tier: 'P1', basePrice: 280, volume: 0.38 },
  { name: 'Heavier Metals', tier: 'P1', basePrice: 380, volume: 0.38 },
  { name: 'Ionic Solutions', tier: 'P1', basePrice: 290, volume: 0.38 },
  { name: 'Noble Gas', tier: 'P1', basePrice: 480, volume: 0.38 },
  { name: 'Noble Metals', tier: 'P1', basePrice: 780, volume: 0.38 },
  { name: 'Non-CS Crystals', tier: 'P1', basePrice: 260, volume: 0.38 },
  { name: 'Oxygen', tier: 'P1', basePrice: 420, volume: 0.38 },
  { name: 'Suspended Plasma', tier: 'P1', basePrice: 320, volume: 0.38 },
  { name: 'Base Metals', tier: 'P1', basePrice: 340, volume: 0.38 },
  { name: 'Chiral Structures', tier: 'P2', basePrice: 2800, volume: 1.5 },
  { name: 'Camera Drones', tier: 'P2', basePrice: 2200, volume: 1.5 },
  { name: 'Condensates P2', tier: 'P2', basePrice: 3100, volume: 1.5 },
  { name: 'Cryoprotectant Solution', tier: 'P2', basePrice: 2600, volume: 1.5 },
  { name: 'Data Chips', tier: 'P2', basePrice: 3800, volume: 1.5 },
  { name: 'Gel-Matrix Biopaste', tier: 'P2', basePrice: 4200, volume: 1.5 },
  { name: 'Genetic Modified Industrial Foods', tier: 'P2', basePrice: 2400, volume: 1.5 },
  { name: 'Hazmat Detection Systems', tier: 'P2', basePrice: 2900, volume: 1.5 },
  { name: 'Hermetic Membranes', tier: 'P2', basePrice: 3400, volume: 1.5 },
  { name: 'High-Tech Transmitters', tier: 'P2', basePrice: 4200, volume: 1.5 },
  { name: 'Industrial Explosives', tier: 'P2', basePrice: 3200, volume: 1.5 },
  { name: 'Neocoms', tier: 'P2', basePrice: 2800, volume: 1.5 },
  { name: 'Nuclear Detonators', tier: 'P2', basePrice: 3600, volume: 1.5 },
  { name: 'Planetary Vehicles', tier: 'P2', basePrice: 3100, volume: 1.5 },
  { name: 'Rocket Fuel', tier: 'P2', basePrice: 2500, volume: 1.5 },
  { name: 'Silicate Glass', tier: 'P2', basePrice: 2100, volume: 1.5 },
  { name: 'Supercomputers', tier: 'P2', basePrice: 4800, volume: 1.5 },
  { name: 'Synthetic Synapses', tier: 'P2', basePrice: 3500, volume: 1.5 },
  { name: 'Transmitter', tier: 'P2', basePrice: 2700, volume: 1.5 },
  { name: 'Ukomi Superconductor', tier: 'P2', basePrice: 3900, volume: 1.5 },
  { name: 'Vaccines', tier: 'P2', basePrice: 2300, volume: 1.5 },
  { name: 'Water-Cooled CPU', tier: 'P2', basePrice: 3000, volume: 1.5 },
  { name: 'Biotech Research Reports', tier: 'P3', basePrice: 18000, volume: 6 },
  { name: 'Capital Construction Parts', tier: 'P3', basePrice: 75000, volume: 6 },
  { name: 'Cryopreservation Unit', tier: 'P3', basePrice: 22000, volume: 6 },
  { name: 'Danube Cartridge', tier: 'P3', basePrice: 24000, volume: 6 },
  { name: 'Destructive Testing Script', tier: 'P3', basePrice: 19000, volume: 6 },
  { name: 'Fuel Block Formula', tier: 'P3', basePrice: 16000, volume: 6 },
  { name: 'Guidance System', tier: 'P3', basePrice: 35000, volume: 6 },
  { name: 'Hazmat Control Unit', tier: 'P3', basePrice: 21000, volume: 6 },
  { name: 'Incognito Processing', tier: 'P3', basePrice: 25000, volume: 6 },
  { name: 'Integrity Response Drones', tier: 'P3', basePrice: 28000, volume: 6 },
  { name: 'Mainframe Structure', tier: 'P3', basePrice: 32000, volume: 6 },
  { name: 'Molecular Analysis Tools', tier: 'P3', basePrice: 20000, volume: 6 },
  { name: 'Nano-Factory', tier: 'P3', basePrice: 45000, volume: 6 },
  { name: 'Neural Network', tier: 'P3', basePrice: 38000, volume: 6 },
  { name: 'Organic Mortar Apparatus', tier: 'P3', basePrice: 23000, volume: 6 },
  { name: 'Reconnaissance Photographic', tier: 'P3', basePrice: 19000, volume: 6 },
  { name: 'Sanitary Nanites', tier: 'P3', basePrice: 17000, volume: 6 },
  { name: 'Self-Harmonizing Power Core', tier: 'P3', basePrice: 55000, volume: 6 },
  { name: 'Situational Slaves', tier: 'P3', basePrice: 26000, volume: 6 },
  { name: 'Spatial Attunement Unit', tier: 'P3', basePrice: 21000, volume: 6 },
  { name: 'Sterile Conduits', tier: 'P3', basePrice: 18000, volume: 6 },
  { name: 'Structural Analysers', tier: 'P3', basePrice: 24000, volume: 6 },
  { name: 'Synthetic Power Core', tier: 'P3', basePrice: 30000, volume: 6 },
  { name: 'Tempered Nanites', tier: 'P3', basePrice: 27000, volume: 6 },
  { name: 'Telemetric Subprocessor', tier: 'P3', basePrice: 22000, volume: 6 },
  { name: 'Touch response Signals', tier: 'P3', basePrice: 20000, volume: 6 },
  { name: 'Ubiquitous Metal', tier: 'P3', basePrice: 15000, volume: 6 },
  { name: 'Wetware Mainframe', tier: 'P3', basePrice: 42000, volume: 6 },
  { name: 'Broadcast Node', tier: 'P4', basePrice: 1200000, volume: 100 },
  { name: 'Integrity Response Drones P4', tier: 'P4', basePrice: 900000, volume: 100 },
  { name: 'Nano-Factory P4', tier: 'P4', basePrice: 950000, volume: 100 },
  { name: 'Organic Mortar Apparatus P4', tier: 'P4', basePrice: 850000, volume: 100 },
  { name: 'Recursive Computing Module', tier: 'P4', basePrice: 1100000, volume: 100 },
  { name: 'Self-Harmonizing Power Core P4', tier: 'P4', basePrice: 1000000, volume: 100 },
  { name: 'Smartfab Units P4', tier: 'P4', basePrice: 800000, volume: 100 },
  { name: 'Sterile Conduits P4', tier: 'P4', basePrice: 750000, volume: 100 },
];

const PLANET_YIELDS: Record<string, Record<string, number>> = {
  plasma: { 'Plasmoids': 100, 'Superconductors': 95, 'Noble Gas': 85 },
  gas: { 'Noble Gas': 100, 'Coolant': 90, 'Oxidizing Compound': 80 },
  lava: { 'Toxic Metals': 100, 'Felsic Magma': 95, 'Non-CS Crystals': 85 },
  storm: { 'Noble Gas': 100, 'Ionic Solutions': 95, 'Suspended Plasma': 90 },
  oceanic: { 'Water': 100, 'Bacteria': 90, 'Biomass': 85 },
  ice: { 'Water': 100, 'Oxygen': 95, 'Coolant': 85 },
  temperate: { 'Industrial Fibers': 100, 'Proteins': 90, 'Biomass': 85 },
  barren: { 'Base Metals': 100, 'Silicon': 90, 'Precious Metals': 80 },
};

export const data = new SlashCommandBuilder()
  .setName('piproducts')
  .setDescription('PI product prices and best setups')
  .addSubcommand(sub =>
    sub
      .setName('prices')
      .setDescription('Show PI product prices by tier')
      .addStringOption(opt => opt.setName('tier').setDescription('PI tier').addChoices(
        { name: 'P1 (Basic)', value: 'P1' },
        { name: 'P2 (Refined)', value: 'P2' },
        { name: 'P3 (Specialized)', value: 'P3' },
        { name: 'P4 (Advanced)', value: 'P4' }
      ).setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('best')
      .setDescription('Best PI products to make by profit')
      .addStringOption(opt => opt.setName('tier').setDescription('Target tier').addChoices(
        { name: 'P1', value: 'P1' },
        { name: 'P2', value: 'P2' },
        { name: 'P3', value: 'P3' }
      ).setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('planet')
      .setDescription('Best products for a planet type')
      .addStringOption(opt => opt.setName('type').setDescription('Planet type').addChoices(
        { name: 'Plasma', value: 'plasma' },
        { name: 'Gas', value: 'gas' },
        { name: 'Lava', value: 'lava' },
        { name: 'Storm', value: 'storm' },
        { name: 'Oceanic', value: 'oceanic' },
        { name: 'Ice', value: 'ice' },
        { name: 'Temperate', value: 'temperate' },
        { name: 'Barren', value: 'barren' }
      ).setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('setup')
      .setDescription('Recommended PI setup for profit')
      .addIntegerOption(opt => opt.setName('colonies').setDescription('Number of colonies (3-6 per char)').setRequired(true))
      .addStringOption(opt => opt.setName('focus').setDescription('Production focus').addChoices(
        { name: 'P1 Extraction', value: 'p1' },
        { name: 'P2 Production', value: 'p2' },
        { name: 'P3 Factory', value: 'p3' },
        { name: 'P4 High-Tech', value: 'p4' }
      ).setRequired(true)));

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'prices': await handlePrices(interaction); break;
    case 'best': await handleBest(interaction); break;
    case 'planet': await handlePlanet(interaction); break;
    case 'setup': await handleSetup(interaction); break;
  }
}

async function handlePrices(interaction: CommandInteraction) {
  const tier = interaction.options.get('tier')?.value as string;
  const products = PI_PRODUCTS.filter(p => p.tier === tier);
  
  const sorted = [...products].sort((a, b) => b.basePrice - a.basePrice);
  
  const embed = new EmbedBuilder()
    .setTitle(`${tier} Product Prices`)
    .setColor(0x3498db)
    .setDescription(
      sorted.slice(0, 20).map(p => 
        `**${p.name}**: ${p.basePrice.toLocaleString()} ISK (${p.volume} m³)`
      ).join('\n')
    )
    .setFooter({ text: 'Prices are estimates - check Jita for current prices' });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleBest(interaction: CommandInteraction) {
  const tier = interaction.options.get('tier')?.value as string;
  const products = PI_PRODUCTS.filter(p => p.tier === tier);
  
  const withScores = products.map(p => {
    const dailyVolume = getDailyVolume(tier);
    const dailyRevenue = p.basePrice * dailyVolume;
    return { ...p, dailyVolume, dailyRevenue };
  }).sort((a, b) => b.dailyRevenue - a.dailyRevenue);
  
  const embed = new EmbedBuilder()
    .setTitle(`Best ${tier} Products by Daily Revenue`)
    .setColor(0x00ff00)
    .setDescription(
      withScores.slice(0, 15).map((p, i) => 
        `**${i + 1}. ${p.name}**\n` +
        `   Price: ${p.basePrice.toLocaleString()} ISK | Daily: ${p.dailyRevenue.toLocaleString()} ISK`
      ).join('\n')
    );
  
  await interaction.reply({ embeds: [embed] });
}

function getDailyVolume(tier: string): number {
  switch (tier) {
    case 'P1': return 20 * 24;
    case 'P2': return 5 * 6;
    case 'P3': return 3;
    default: return 1;
  }
}

async function handlePlanet(interaction: CommandInteraction) {
  const type = interaction.options.get('type')?.value as string;
  const yields = PLANET_YIELDS[type];
  
  if (!yields) {
    await interaction.reply({ content: 'Unknown planet type.', ephemeral: true });
    return;
  }
  
  const products = Object.entries(yields)
    .map(([name, yield_]) => {
      const product = PI_PRODUCTS.find(p => p.name === name);
      return { name, yield: yield_, price: product?.basePrice || 0 };
    })
    .sort((a, b) => (b.yield * b.price) - (a.yield * a.price));
  
  const embed = new EmbedBuilder()
    .setTitle(`Best Products for ${type.charAt(0).toUpperCase() + type.slice(1)} Planets`)
    .setColor(0xf1c40f)
    .setDescription(
      products.map(p => 
        `**${p.name}**: ${p.yield}% yield @ ${p.price.toLocaleString()} ISK`
      ).join('\n')
    )
    .addFields({ name: 'Recommendation', value: `Focus on ${products[0].name} for best profit` });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleSetup(interaction: CommandInteraction) {
  const colonies = interaction.options.get('colonies')?.value as number;
  const focus = interaction.options.get('focus')?.value as string;
  
  let dailyRevenue = 0;
  let setup = '';
  
  switch (focus) {
    case 'p1':
      dailyRevenue = colonies * 500000;
      setup = `${colonies} extraction colonies\n` +
              `Extract P0 → Process to P1\n` +
              `Best: Plasmoids, Coolant, Superconductors\n` +
              `Time: 15-20 min/day`;
      break;
    case 'p2':
      dailyRevenue = colonies * 800000;
      setup = `${Math.ceil(colonies * 0.7)} extraction + ${Math.floor(colonies * 0.3)} factory\n` +
              `Extract P0/P1 → Produce P2\n` +
              `Best: Coolant, Mechanical Parts → P2\n` +
              `Time: 20-30 min/day`;
      break;
    case 'p3':
      dailyRevenue = colonies * 1200000;
      setup = `${Math.ceil(colonies * 0.5)} extraction + ${Math.floor(colonies * 0.5)} factory\n` +
              `Import P1 → P2 → P3 chain\n` +
              `Best: Guidance Systems, Nanite Repair Paste\n` +
              `Time: 30-45 min/day`;
      break;
    case 'p4':
      dailyRevenue = colonies * 2000000;
      setup = `1 High-Tech (PI) + ${colonies - 1} extraction\n` +
              `P1/P2 → P3 → P4 (on temperate/plasma)\n` +
              `Best: Broadcast Node, Recursive Computing\n` +
              `Time: 45-60 min/day`;
      break;
  }
  
  const monthlyRevenue = dailyRevenue * 30;
  const yearlyRevenue = dailyRevenue * 365;
  
  const embed = new EmbedBuilder()
    .setTitle(`PI Setup Recommendation: ${focus.toUpperCase()} Focus`)
    .setColor(0x9b59b6)
    .addFields(
      { name: 'Setup', value: setup, inline: false },
      { name: 'Daily Revenue', value: `${dailyRevenue.toLocaleString()} ISK`, inline: true },
      { name: 'Monthly', value: `${monthlyRevenue.toLocaleString()} ISK`, inline: true },
      { name: 'Yearly', value: `${yearlyRevenue.toLocaleString()} ISK`, inline: true }
    )
    .setFooter({ text: 'Revenue estimates based on average prices. Actual results vary.' });
  
  await interaction.reply({ embeds: [embed] });
}
