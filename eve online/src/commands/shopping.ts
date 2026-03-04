import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';

export const data = new SlashCommandBuilder()
  .setName('shopping')
  .setDescription('Generate shopping lists for industry jobs')
  .addSubcommand(sub =>
    sub
      .setName('materials')
      .setDescription('Calculate materials needed for a job')
      .addStringOption(opt => opt.setName('product').setDescription('Product name').setRequired(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity to build').setRequired(true))
      .addIntegerOption(opt => opt.setName('me').setDescription('Blueprint ME (0-10)').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('piextract')
      .setDescription('Generate PI extraction schedule')
      .addIntegerOption(opt => opt.setName('colonies').setDescription('Number of colonies').setRequired(true))
      .addStringOption(opt => opt.setName('product').setDescription('Target P1 product').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('export')
      .setDescription('Export your shopping list')
      .addStringOption(opt => opt.setName('format').setDescription('Export format').addChoices(
        { name: 'Text', value: 'text' },
        { name: 'EVE Clipboard', value: 'eve' }
      ).setRequired(true)));

interface Material {
  name: string;
  quantity: number;
  price: number;
}

const COMMON_PRODUCTS: Record<string, { materials: Material[]; baseTime: number }> = {
  'Ishtar': {
    materials: [
      { name: 'Ishtar Blueprint', quantity: 1, price: 0 },
      { name: 'Fermionic Condensates', quantity: 25, price: 350000 },
      { name: 'Nanotransistors', quantity: 150, price: 12000 },
      { name: 'Sylramic Fibers', quantity: 300, price: 2200 },
      { name: 'Fullerides', quantity: 200, price: 15000 },
      { name: 'Hypersynaptic Fibers', quantity: 50, price: 55000 },
      { name: 'Phenolic Composites', quantity: 100, price: 18000 },
      { name: 'Construction Blocks', quantity: 500, price: 480 },
    ],
    baseTime: 72000
  },
  'Stratios': {
    materials: [
      { name: 'Stratios Blueprint', quantity: 1, price: 0 },
      { name: 'Fermionic Condensates', quantity: 45, price: 350000 },
      { name: 'Nanotransistors', quantity: 300, price: 12000 },
      { name: 'Sylramic Fibers', quantity: 600, price: 2200 },
      { name: 'Fullerides', quantity: 400, price: 15000 },
      { name: 'Hypersynaptic Fibers', quantity: 100, price: 55000 },
      { name: 'Phenolic Composites', quantity: 200, price: 18000 },
    ],
    baseTime: 120000
  },
  'Capacitor Recharger II': {
    materials: [
      { name: 'Capacitor Recharger II Blueprint', quantity: 1, price: 0 },
      { name: 'Particle Accelerator', quantity: 4, price: 8000 },
      { name: 'Magnetometric Sensor Cluster', quantity: 2, price: 3500 },
      { name: 'Current Pump', quantity: 2, price: 2500 },
    ],
    baseTime: 4500
  },
  '10MN Afterburner II': {
    materials: [
      { name: '10MN Afterburner II Blueprint', quantity: 1, price: 0 },
      { name: 'Particle Accelerator', quantity: 8, price: 8000 },
      { name: 'Fusion Reactor', quantity: 2, price: 12000 },
      { name: 'Photon Microprocessor', quantity: 4, price: 4500 },
    ],
    baseTime: 6000
  },
  'Drone Damage Amplifier II': {
    materials: [
      { name: 'DDA II Blueprint', quantity: 1, price: 0 },
      { name: 'Quantum Processor', quantity: 4, price: 6500 },
      { name: 'Neutron Flux', quantity: 2, price: 3500 },
    ],
    baseTime: 3600
  },
};

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'materials': await handleMaterials(interaction); break;
    case 'piextract': await handlePIExtract(interaction); break;
    case 'export': await handleExport(interaction); break;
  }
}

async function handleMaterials(interaction: CommandInteraction) {
  const product = interaction.options.get('product')?.value as string;
  const quantity = interaction.options.get('quantity')?.value as number;
  const me = (interaction.options.get('me')?.value as number) || 0;
  
  const productData = COMMON_PRODUCTS[product];
  if (!productData) {
    const available = Object.keys(COMMON_PRODUCTS).join(', ');
    await interaction.reply({ 
      content: `Unknown product. Available: ${available}`, 
      ephemeral: true 
    });
    return;
  }
  
  const meMultiplier = 1 - (me / 100);
  const materials = productData.materials.map(m => ({
    name: m.name,
    quantity: Math.ceil(m.quantity * quantity * meMultiplier),
    price: m.price,
    total: Math.ceil(m.quantity * quantity * meMultiplier) * m.price
  }));
  
  const totalCost = materials.reduce((sum, m) => sum + m.total, 0);
  const totalTime = productData.baseTime * quantity;
  
  const embed = new EmbedBuilder()
    .setTitle(`Shopping List: ${product} x${quantity}`)
    .setColor(0x3498db)
    .setDescription(
      materials.filter(m => m.quantity > 0).map(m => 
        `**${m.name}**: ${m.quantity.toLocaleString()}` +
        (m.price > 0 ? ` (${m.total.toLocaleString()} ISK)` : '')
      ).join('\n')
    )
    .addFields(
      { name: 'ME Level', value: `${me}%`, inline: true },
      { name: 'Total Material Cost', value: `${totalCost.toLocaleString()} ISK`, inline: true },
      { name: 'Build Time', value: formatTime(totalTime), inline: true }
    );
  
  await interaction.reply({ embeds: [embed] });
}

async function handlePIExtract(interaction: CommandInteraction) {
  const colonies = interaction.options.get('colonies')?.value as number;
  const product = interaction.options.get('product')?.value as string;
  
  const extractionPerHour = 5000;
  const processRatio = 6000;
  
  const p0PerHour = extractionPerHour * colonies;
  const p1PerHour = p0PerHour / processRatio;
  
  const p0PerDay = p0PerHour * 24;
  const p1PerDay = p1PerHour * 24;
  
  const embed = new EmbedBuilder()
    .setTitle(`PI Extraction Schedule: ${product}`)
    .setColor(0x00ff00)
    .addFields(
      { name: 'Colonies', value: colonies.toString(), inline: true },
      { name: 'P0 per Hour', value: p0PerHour.toLocaleString(), inline: true },
      { name: 'P1 per Hour', value: p1PerHour.toFixed(1), inline: true },
      { name: 'P0 per Day', value: p0PerDay.toLocaleString(), inline: true },
      { name: 'P1 per Day', value: p1PerDay.toFixed(0), inline: true },
      { name: 'P1 per Week', value: (p1PerDay * 7).toFixed(0), inline: true }
    )
    .addFields({ name: 'Extractors Needed', value: `${colonies} ECU with 2-3 extractors each` })
    .addFields({ name: 'Processors Needed', value: `${colonies * 2} Basic Industry Facilities` });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleExport(interaction: CommandInteraction) {
  const format = interaction.options.get('format')?.value as string;
  
  const pendingJobs = db.prepare(`
    SELECT product_name, quantity, material_cost 
    FROM industry_jobs 
    WHERE discord_user_id = ? AND status IN ('pending', 'building')
  `).all(interaction.user.id) as { product_name: string; quantity: number; material_cost: number }[];
  
  if (pendingJobs.length === 0) {
    await interaction.reply({ content: 'No pending jobs to export.', ephemeral: true });
    return;
  }
  
  let output = '';
  
  if (format === 'eve') {
    output = pendingJobs.map(j => `${j.product_name} x${j.quantity}`).join('\n');
  } else {
    output = 'Industry Jobs Shopping List\n';
    output += '='.repeat(40) + '\n\n';
    pendingJobs.forEach(j => {
      output += `${j.product_name} x${j.quantity}\n`;
      output += `  Cost: ${j.material_cost.toLocaleString()} ISK\n\n`;
    });
    
    const totalCost = pendingJobs.reduce((sum, j) => sum + j.material_cost, 0);
    output += '='.repeat(40) + '\n';
    output += `Total Investment: ${totalCost.toLocaleString()} ISK\n`;
  }
  
  await interaction.reply({ 
    content: '```\n' + output + '\n```', 
    ephemeral: true 
  });
}

function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours >= 24) {
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `${days}d ${remainingHours}h ${minutes}m`;
  }
  
  return `${hours}h ${minutes}m`;
}
