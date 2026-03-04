import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';
import { BPO_DATABASE } from '../data/bpoData';

export const data = new SlashCommandBuilder()
  .setName('bpodb')
  .setDescription('Complete BPO database with ownership tracking')
  .addSubcommand(sub =>
    sub
      .setName('add')
      .setDescription('Add a BPO to your collection')
      .addStringOption(opt => opt.setName('name').setDescription('Blueprint name').setRequired(true))
      .addStringOption(opt => opt.setName('category').setDescription('Category').setRequired(true).addChoices(
        { name: 'T1 Ships', value: 't1_ships' },
        { name: 'T1 Modules', value: 't1_modules' },
        { name: 'T1 Ammo', value: 't1_ammo' },
        { name: 'T1 Rigs', value: 't1_rigs' },
        { name: 'T2 Ships', value: 't2_ships' },
        { name: 'T2 Modules', value: 't2_modules' },
        { name: 'Capital Ships', value: 'capital_ships' },
        { name: 'Capital Modules', value: 'capital_modules' },
        { name: 'Components', value: 'components' },
        { name: 'Structures', value: 'structures' }
      ))
      .addIntegerOption(opt => opt.setName('me').setDescription('Material Efficiency (0-10)').setRequired(false))
      .addIntegerOption(opt => opt.setName('te').setDescription('Time Efficiency (0-20)').setRequired(false))
      .addStringOption(opt => opt.setName('location').setDescription('Storage location').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('list')
      .setDescription('List your BPO collection')
      .addStringOption(opt => opt.setName('category').setDescription('Filter by category').setRequired(false)))
  .addSubcommand(sub =>
    sub
      .setName('view')
      .setDescription('View all BPOs in database')
      .addStringOption(opt => opt.setName('category').setDescription('Filter by category').setRequired(false)))
  .addSubcommand(sub =>
    sub
      .setName('search')
      .setDescription('Search for a BPO')
      .addStringOption(opt => opt.setName('query').setDescription('Search term').setRequired(true)))
  .addSubcommand(sub =>
    sub
      .setName('update')
      .setDescription('Update your BPO')
      .addIntegerOption(opt => opt.setName('id').setDescription('Your BPO ID').setRequired(true))
      .addIntegerOption(opt => opt.setName('me').setDescription('New ME').setRequired(false))
      .addIntegerOption(opt => opt.setName('te').setDescription('New TE').setRequired(false)))
  .addSubcommand(sub =>
    sub
      .setName('materials')
      .setDescription('View materials needed for a BPO')
      .addStringOption(opt => opt.setName('name').setDescription('Blueprint name').setRequired(true))
      .addIntegerOption(opt => opt.setName('me').setDescription('ME level (0-10)').setRequired(false))
      .addIntegerOption(opt => opt.setName('runs').setDescription('Number of runs').setRequired(false)))
  .addSubcommand(sub =>
    sub
      .setName('buildtime')
      .setDescription('Calculate build time with TE')
      .addStringOption(opt => opt.setName('name').setDescription('Blueprint name').setRequired(true))
      .addIntegerOption(opt => opt.setName('te').setDescription('TE level (0-20)').setRequired(false))
      .addIntegerOption(opt => opt.setName('runs').setDescription('Number of runs').setRequired(false))
      .addIntegerOption(opt => opt.setName('industry_skill').setDescription('Industry skill level (0-5)').setRequired(false))
      .addIntegerOption(opt => opt.setName('adv_industry').setDescription('Advanced Industry skill (0-5)').setRequired(false)))
  .addSubcommand(sub =>
    sub
      .setName('calc')
      .setDescription('Full build calculation (materials + time + cost)')
      .addStringOption(opt => opt.setName('name').setDescription('Blueprint name').setRequired(true))
      .addIntegerOption(opt => opt.setName('me').setDescription('ME level (0-10)').setRequired(false))
      .addIntegerOption(opt => opt.setName('te').setDescription('TE level (0-20)').setRequired(false))
      .addIntegerOption(opt => opt.setName('runs').setDescription('Number of runs').setRequired(false)));

db.exec(`
  CREATE TABLE IF NOT EXISTS bpo_master (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    type_id INTEGER NOT NULL,
    image_url TEXT,
    base_cost REAL DEFAULT 0,
    build_time INTEGER DEFAULT 0,
    volume REAL DEFAULT 0
  );

  CREATE TABLE IF NOT EXISTS user_bpos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    bpo_id INTEGER NOT NULL,
    me INTEGER DEFAULT 0,
    te INTEGER DEFAULT 0,
    location TEXT,
    acquired_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bpo_id) REFERENCES bpo_master(id)
  );
`);

const insertBPO = db.prepare(`
  INSERT OR IGNORE INTO bpo_master (id, name, category, type_id, image_url, base_cost, build_time, volume)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?)
`);

for (const bpo of BPO_DATABASE) {
  insertBPO.run(bpo.id, bpo.name, bpo.category, bpo.type_id, bpo.image_url, bpo.base_cost, bpo.build_time, bpo.volume);
}

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'add': await handleAdd(interaction); break;
    case 'list': await handleList(interaction); break;
    case 'view': await handleView(interaction); break;
    case 'search': await handleSearch(interaction); break;
    case 'update': await handleUpdate(interaction); break;
    case 'materials': await handleMaterials(interaction); break;
    case 'buildtime': await handleBuildTime(interaction); break;
    case 'calc': await handleCalc(interaction); break;
  }
}

async function handleAdd(interaction: CommandInteraction) {
  const name = interaction.options.get('name')?.value as string;
  const category = interaction.options.get('category')?.value as string;
  const me = (interaction.options.get('me')?.value as number) || 0;
  const te = (interaction.options.get('te')?.value as number) || 0;
  const location = (interaction.options.get('location')?.value as string) || 'Unknown';
  
  const bpo = BPO_DATABASE.find(b => b.name.toLowerCase().includes(name.toLowerCase()));
  
  if (!bpo) {
    await interaction.reply({ content: `BPO not found. Use "/bpodb search" to find BPOs.`, ephemeral: true });
    return;
  }
  
  const stmt = db.prepare(`
    INSERT INTO user_bpos (discord_user_id, bpo_id, me, te, location)
    VALUES (?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(interaction.user.id, bpo.id, me, te, location);
  
  const embed = new EmbedBuilder()
    .setTitle('BPO Added to Collection')
    .setColor(0x00ff00)
    .setThumbnail(bpo.image_url)
    .addFields(
      { name: 'Name', value: bpo.name, inline: true },
      { name: 'Category', value: bpo.category, inline: true },
      { name: 'ME', value: me.toString(), inline: true },
      { name: 'TE', value: te.toString(), inline: true },
      { name: 'Location', value: location, inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleList(interaction: CommandInteraction) {
  const category = interaction.options.get('category')?.value as string | undefined;
  
  let query = `
    SELECT ub.id, ub.me, ub.te, ub.location, bm.name, bm.category, bm.image_url
    FROM user_bpos ub
    JOIN bpo_master bm ON ub.bpo_id = bm.id
    WHERE ub.discord_user_id = ?
  `;
  const params: (string | number)[] = [interaction.user.id];
  
  if (category) {
    query += ' AND bm.category = ?';
    params.push(category);
  }
  
  query += ' ORDER BY bm.category, bm.name';
  
  const bpos = db.prepare(query).all(...params) as {
    id: number;
    me: number;
    te: number;
    location: string;
    name: string;
    category: string;
    image_url: string;
  }[];
  
  if (bpos.length === 0) {
    await interaction.reply({ content: 'No BPOs in your collection. Use `/bpodb add` to add some.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Your BPO Collection')
    .setColor(0x3498db)
    .setDescription(`Total: ${bpos.length} BPOs`)
    .addFields(
      bpos.slice(0, 20).map(b => ({
        name: b.name,
        value: `ME${b.me}/TE${b.te} | ${b.location}`,
        inline: true
      }))
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleView(interaction: CommandInteraction) {
  const category = interaction.options.get('category')?.value as string | undefined;
  
  let query = 'SELECT * FROM bpo_master';
  const params: string[] = [];
  
  if (category) {
    query += ' WHERE category = ?';
    params.push(category);
  }
  
  query += ' ORDER BY category, name LIMIT 25';
  
  const bpos = db.prepare(query).all(...params) as BPOEntry[];
  
  if (bpos.length === 0) {
    await interaction.reply({ content: 'No BPOs found.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Complete BPO Database')
    .setColor(0xf1c40f)
    .setDescription(`Total: ${BPO_DATABASE.length} BPOs`)
    .addFields(
      bpos.map(b => ({
        name: b.name,
        value: `${b.category} | ${b.base_cost.toLocaleString()} ISK`,
        inline: true
      }))
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleSearch(interaction: CommandInteraction) {
  const query = interaction.options.get('query')?.value as string;
  
  const results = BPO_DATABASE.filter(b => 
    b.name.toLowerCase().includes(query.toLowerCase()) ||
    b.category.toLowerCase().includes(query.toLowerCase())
  );
  
  if (results.length === 0) {
    await interaction.reply({ content: 'No BPOs found matching your search.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle(`Search Results: "${query}"`)
    .setColor(0x9b59b6)
    .setDescription(`Found ${results.length} BPOs`)
    .addFields(
      results.slice(0, 10).map(b => ({
        name: b.name,
        value: `${b.category} | ${b.base_cost.toLocaleString()} ISK`,
        inline: true
      }))
    );
  
  await interaction.reply({ embeds: [embed] });
}

async function handleUpdate(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  const me = interaction.options.get('me')?.value as number | undefined;
  const te = interaction.options.get('te')?.value as number | undefined;
  
  const updates: string[] = [];
  const values: (number | string)[] = [];
  
  if (me !== undefined) { updates.push('me = ?'); values.push(me); }
  if (te !== undefined) { updates.push('te = ?'); values.push(te); }
  
  if (updates.length === 0) {
    await interaction.reply({ content: 'No updates provided.', ephemeral: true });
    return;
  }
  
  values.push(id, interaction.user.id);
  
  const result = db.prepare(`
    UPDATE user_bpos SET ${updates.join(', ')} WHERE id = ? AND discord_user_id = ?
  `).run(...values);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'BPO not found or not yours.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `BPO #${id} updated.`, ephemeral: true });
}

async function handleMaterials(interaction: CommandInteraction) {
  const name = interaction.options.get('name')?.value as string;
  const me = (interaction.options.get('me')?.value as number) || 0;
  const runs = (interaction.options.get('runs')?.value as number) || 1;
  
  const bpo = BPO_DATABASE.find(b => b.name.toLowerCase().includes(name.toLowerCase()));
  
  if (!bpo) {
    await interaction.reply({ content: `BPO not found. Use "/bpodb search" to find BPOs.`, ephemeral: true });
    return;
  }
  
  // Calculate material efficiency bonus
  // ME 0 = 0% bonus, ME 10 = 10% reduction
  const meBonus = 1 - (me / 100);
  
  let totalMaterialCost = 0;
  const materialPrices: Record<string, number> = {
    'Tritanium': 6,
    'Pyerite': 12,
    'Mexallon': 85,
    'Isogen': 120,
    'Nocxium': 450,
    'Zydrine': 1200,
    'Megacyte': 2800,
    'Morphite': 8500,
    'Construction Blocks': 480,
    'Nanotransistors': 12000,
    'Sylramic Fibers': 2200,
    'Fullerides': 15000,
    'Fermionic Condensates': 350000,
    'Superconductors': 1100
  };
  
  const materialsList = bpo.materials.map(m => {
    const adjustedQty = Math.ceil(m.quantity * meBonus * runs);
    const price = materialPrices[m.name] || 0;
    const cost = adjustedQty * price;
    totalMaterialCost += cost;
    return {
      name: m.name,
      baseQty: m.quantity,
      adjustedQty,
      price,
      cost
    };
  });
  
  const embed = new EmbedBuilder()
    .setTitle(`Materials: ${bpo.name}`)
    .setColor(0x3498db)
    .setThumbnail(bpo.image_url)
    .addFields(
      { name: 'ME Level', value: `${me}% (saves ${me}%)`, inline: true },
      { name: 'Runs', value: runs.toString(), inline: true },
      { name: 'Total Material Cost', value: `${totalMaterialCost.toLocaleString()} ISK`, inline: true }
    )
    .addFields({ name: '\u200B', value: '\u200B' })
    .addFields(
      materialsList.slice(0, 20).map(m => ({
        name: m.name,
        value: `${m.adjustedQty.toLocaleString()} @ ${m.price.toLocaleString()} ISK = ${m.cost.toLocaleString()} ISK`,
        inline: true
      }))
    );
  
  await interaction.reply({ embeds: [embed] });
}

async function handleBuildTime(interaction: CommandInteraction) {
  const name = interaction.options.get('name')?.value as string;
  const te = (interaction.options.get('te')?.value as number) || 0;
  const runs = (interaction.options.get('runs')?.value as number) || 1;
  const industrySkill = (interaction.options.get('industry_skill')?.value as number) || 5;
  const advIndustry = (interaction.options.get('adv_industry')?.value as number) || 5;
  
  const bpo = BPO_DATABASE.find(b => b.name.toLowerCase().includes(name.toLowerCase()));
  
  if (!bpo) {
    await interaction.reply({ content: `BPO not found. Use "/bpodb search" to find BPOs.`, ephemeral: true });
    return;
  }
  
  // Calculate time bonuses
  // TE 0 = 0% reduction, TE 20 = 20% reduction
  const teBonus = 1 - (te / 100);
  
  // Industry skill: 4% per level (max 20%)
  const industryBonus = 1 - (industrySkill * 0.04);
  
  // Advanced Industry: 3% per level (max 15%)
  const advIndustryBonus = 1 - (advIndustry * 0.03);
  
  const baseTime = bpo.build_time * runs;
  const adjustedTime = Math.ceil(baseTime * teBonus * industryBonus * advIndustryBonus);
  
  // Convert seconds to readable format
  const hours = Math.floor(adjustedTime / 3600);
  const minutes = Math.floor((adjustedTime % 3600) / 60);
  const seconds = adjustedTime % 60;
  
  const baseHours = Math.floor(baseTime / 3600);
  const baseMinutes = Math.floor((baseTime % 3600) / 60);
  
  const embed = new EmbedBuilder()
    .setTitle(`Build Time: ${bpo.name}`)
    .setColor(0xe67e22)
    .setThumbnail(bpo.image_url)
    .addFields(
      { name: 'Base Time', value: `${baseHours}h ${baseMinutes}m`, inline: true },
      { name: 'Adjusted Time', value: `${hours}h ${minutes}m ${seconds}s`, inline: true },
      { name: 'Time Saved', value: `${(((baseTime - adjustedTime) / baseTime) * 100).toFixed(1)}%`, inline: true }
    )
    .addFields({ name: '\u200B', value: '\u200B' })
    .addFields(
      { name: 'TE Level', value: `${te}% reduction`, inline: true },
      { name: 'Industry Skill', value: `${industrySkill}/5 (${(industrySkill * 4)}% reduction)`, inline: true },
      { name: 'Adv Industry', value: `${advIndustry}/5 (${(advIndustry * 3)}% reduction)`, inline: true }
    )
    .addFields(
      { name: 'Runs', value: runs.toString(), inline: true },
      { name: 'Time per Run', value: `${Math.floor(adjustedTime / runs / 3600)}h ${Math.floor((adjustedTime / runs % 3600) / 60)}m`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed] });
}

async function handleCalc(interaction: CommandInteraction) {
  const name = interaction.options.get('name')?.value as string;
  const me = (interaction.options.get('me')?.value as number) || 0;
  const te = (interaction.options.get('te')?.value as number) || 0;
  const runs = (interaction.options.get('runs')?.value as number) || 1;
  
  const bpo = BPO_DATABASE.find(b => b.name.toLowerCase().includes(name.toLowerCase()));
  
  if (!bpo) {
    await interaction.reply({ content: `BPO not found. Use "/bpodb search" to find BPOs.`, ephemeral: true });
    return;
  }
  
  // Material calculations
  const meBonus = 1 - (me / 100);
  const materialPrices: Record<string, number> = {
    'Tritanium': 6,
    'Pyerite': 12,
    'Mexallon': 85,
    'Isogen': 120,
    'Nocxium': 450,
    'Zydrine': 1200,
    'Megacyte': 2800,
    'Morphite': 8500,
    'Construction Blocks': 480,
    'Nanotransistors': 12000,
    'Sylramic Fibers': 2200,
    'Fullerides': 15000,
    'Fermionic Condensates': 350000,
    'Superconductors': 1100
  };
  
  let totalMaterialCost = 0;
  bpo.materials.forEach(m => {
    const adjustedQty = Math.ceil(m.quantity * meBonus * runs);
    const price = materialPrices[m.name] || 0;
    totalMaterialCost += adjustedQty * price;
  });
  
  // Time calculations
  const teBonus = 1 - (te / 100);
  const industryBonus = 0.8; // Industry 5
  const advIndustryBonus = 0.85; // Advanced Industry 5
  const baseTime = bpo.build_time * runs;
  const adjustedTime = Math.ceil(baseTime * teBonus * industryBonus * advIndustryBonus);
  const hours = Math.floor(adjustedTime / 3600);
  const minutes = Math.floor((adjustedTime % 3600) / 60);
  
  // Profit calculation (rough estimate)
  const estimatedSellPrice = bpo.base_cost * 1.5 * runs; // Assume 50% markup
  const profit = estimatedSellPrice - totalMaterialCost;
  const profitMargin = (profit / totalMaterialCost) * 100;
  
  const embed = new EmbedBuilder()
    .setTitle(`Build Calculation: ${bpo.name}`)
    .setColor(profit > 0 ? 0x00ff00 : 0xff0000)
    .setThumbnail(bpo.image_url)
    .addFields(
      { name: 'Runs', value: runs.toString(), inline: true },
      { name: 'ME Level', value: `${me}%`, inline: true },
      { name: 'TE Level', value: `${te}%`, inline: true }
    )
    .addFields({ name: '\u200B', value: '\u200B' })
    .addFields(
      { name: 'Material Cost', value: `${totalMaterialCost.toLocaleString()} ISK`, inline: true },
      { name: 'Build Time', value: `${hours}h ${minutes}m`, inline: true },
      { name: 'Est. Sell Price', value: `${estimatedSellPrice.toLocaleString()} ISK`, inline: true }
    )
    .addFields(
      { name: 'Est. Profit', value: `${profit.toLocaleString()} ISK`, inline: true },
      { name: 'Profit Margin', value: `${profitMargin.toFixed(1)}%`, inline: true },
      { name: 'Cost per Unit', value: `${(totalMaterialCost / runs).toLocaleString()} ISK`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed] });
}

export { BPO_DATABASE };
