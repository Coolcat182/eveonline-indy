import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';

export const data = new SlashCommandBuilder()
  .setName('blueprint')
  .setDescription('Blueprint management and tracking')
  .addSubcommand(sub =>
    sub
      .setName('add')
      .setDescription('Add a blueprint to your collection')
      .addStringOption(opt => opt.setName('name').setDescription('Blueprint name').setRequired(true))
      .addStringOption(opt => opt.setName('type').setDescription('BPO or BPC').addChoices(
        { name: 'BPO (Original)', value: 'BPO' },
        { name: 'BPC (Copy)', value: 'BPC' }
      ).setRequired(true))
      .addIntegerOption(opt => opt.setName('me').setDescription('Material Efficiency (0-10)').setRequired(true))
      .addIntegerOption(opt => opt.setName('te').setDescription('Time Efficiency (0-20)').setRequired(true))
      .addIntegerOption(opt => opt.setName('runs').setDescription('Max runs (BPC only)').setRequired(false))
      .addStringOption(opt => opt.setName('location').setDescription('Where is it stored').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('list')
      .setDescription('List your blueprints')
      .addStringOption(opt => opt.setName('type').setDescription('Filter by type').addChoices(
        { name: 'BPO', value: 'BPO' },
        { name: 'BPC', value: 'BPC' },
        { name: 'All', value: 'all' }
      ).setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('update')
      .setDescription('Update a blueprint')
      .addIntegerOption(opt => opt.setName('id').setDescription('Blueprint ID').setRequired(true))
      .addIntegerOption(opt => opt.setName('me').setDescription('New ME').setRequired(false))
      .addIntegerOption(opt => opt.setName('te').setDescription('New TE').setRequired(false))
      .addIntegerOption(opt => opt.setName('runs').setDescription('Remaining runs').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('delete')
      .setDescription('Remove a blueprint')
      .addIntegerOption(opt => opt.setName('id').setDescription('Blueprint ID').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('research')
      .setDescription('Calculate research costs and time')
      .addIntegerOption(opt => opt.setName('current_me').setDescription('Current ME').setRequired(true))
      .addIntegerOption(opt => opt.setName('target_me').setDescription('Target ME').setRequired(true))
      .addIntegerOption(opt => opt.setName('current_te').setDescription('Current TE').setRequired(true))
      .addIntegerOption(opt => opt.setName('target_te').setDescription('Target TE').setRequired(true)));

db.exec(`
  CREATE TABLE IF NOT EXISTS blueprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    me INTEGER DEFAULT 0,
    te INTEGER DEFAULT 0,
    max_runs INTEGER,
    remaining_runs INTEGER,
    location TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
  )
`);

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'add': await handleAdd(interaction); break;
    case 'list': await handleList(interaction); break;
    case 'update': await handleUpdate(interaction); break;
    case 'delete': await handleDelete(interaction); break;
    case 'research': await handleResearch(interaction); break;
  }
}

async function handleAdd(interaction: CommandInteraction) {
  const name = interaction.options.get('name')?.value as string;
  const type = interaction.options.get('type')?.value as string;
  const me = interaction.options.get('me')?.value as number;
  const te = interaction.options.get('te')?.value as number;
  const runs = interaction.options.get('runs')?.value as number | undefined;
  const location = (interaction.options.get('location')?.value as string) || 'Unknown';
  
  const stmt = db.prepare(`
    INSERT INTO blueprints (discord_user_id, name, type, me, te, max_runs, remaining_runs, location)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(
    interaction.user.id,
    name,
    type,
    me,
    te,
    type === 'BPC' ? runs : null,
    type === 'BPC' ? runs : null,
    location
  );
  
  const embed = new EmbedBuilder()
    .setTitle('Blueprint Added')
    .setColor(0x00ff00)
    .addFields(
      { name: 'ID', value: result.lastInsertRowid.toString(), inline: true },
      { name: 'Name', value: name, inline: true },
      { name: 'Type', value: type, inline: true },
      { name: 'ME', value: me.toString(), inline: true },
      { name: 'TE', value: te.toString(), inline: true },
      { name: 'Location', value: location, inline: true }
    );
  
  if (type === 'BPC' && runs) {
    embed.addFields({ name: 'Runs', value: runs.toString(), inline: true });
  }
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleList(interaction: CommandInteraction) {
  const type = (interaction.options.get('type')?.value as string) || 'all';
  
  let query = 'SELECT * FROM blueprints WHERE discord_user_id = ?';
  const params: string[] = [interaction.user.id];
  
  if (type !== 'all') {
    query += ' AND type = ?';
    params.push(type);
  }
  
  query += ' ORDER BY name';
  
  const bps = db.prepare(query).all(...params) as {
    id: number;
    name: string;
    type: string;
    me: number;
    te: number;
    remaining_runs: number | null;
    location: string;
  }[];
  
  if (bps.length === 0) {
    await interaction.reply({ content: 'No blueprints found.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Your Blueprints')
    .setColor(0x3498db)
    .setDescription(
      bps.map(bp => 
        `**#${bp.id}** | ${bp.name} | ${bp.type} | ME${bp.me}/TE${bp.te}` +
        (bp.type === 'BPC' && bp.remaining_runs ? ` | ${bp.remaining_runs} runs` : '')
      ).join('\n')
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleUpdate(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  const me = interaction.options.get('me')?.value as number | undefined;
  const te = interaction.options.get('te')?.value as number | undefined;
  const runs = interaction.options.get('runs')?.value as number | undefined;
  
  const updates: string[] = [];
  const values: number[] = [];
  
  if (me !== undefined) { updates.push('me = ?'); values.push(me); }
  if (te !== undefined) { updates.push('te = ?'); values.push(te); }
  if (runs !== undefined) { updates.push('remaining_runs = ?'); values.push(runs); }
  
  if (updates.length === 0) {
    await interaction.reply({ content: 'No updates provided.', ephemeral: true });
    return;
  }
  
  values.push(id, interaction.user.id as unknown as number);
  
  const result = db.prepare(`UPDATE blueprints SET ${updates.join(', ')} WHERE id = ? AND discord_user_id = ?`)
    .run(...values);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'Blueprint not found.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `Blueprint #${id} updated.`, ephemeral: true });
}

async function handleDelete(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  
  const result = db.prepare('DELETE FROM blueprints WHERE id = ? AND discord_user_id = ?')
    .run(id, interaction.user.id);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'Blueprint not found.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `Blueprint #${id} deleted.`, ephemeral: true });
}

async function handleResearch(interaction: CommandInteraction) {
  const currentME = interaction.options.get('current_me')?.value as number;
  const targetME = interaction.options.get('target_me')?.value as number;
  const currentTE = interaction.options.get('current_te')?.value as number;
  const targetTE = interaction.options.get('target_te')?.value as number;
  
  function getMECost(from: number, to: number): number {
    let cost = 0;
    for (let i = from; i < to; i++) {
      cost += Math.pow(2, i) * 105;
    }
    return cost;
  }
  
  function getTECost(from: number, to: number): number {
    let cost = 0;
    for (let i = from; i < to; i++) {
      cost += Math.pow(2, Math.floor(i / 2)) * 105;
    }
    return cost;
  }
  
  const meCost = currentME < targetME ? getMECost(currentME, targetME) : 0;
  const teCost = currentTE < targetTE ? getTECost(currentTE, targetTE) : 0;
  const totalCost = meCost + teCost;
  
  const meSavings = targetME * 1;
  const teSavings = targetTE * 1;
  
  const embed = new EmbedBuilder()
    .setTitle('Blueprint Research Calculator')
    .setColor(0xf1c40f)
    .addFields(
      { name: 'ME Research', value: `${currentME}% → ${targetME}%`, inline: true },
      { name: 'ME Cost', value: meCost > 0 ? `${meCost.toLocaleString()} ISK` : 'N/A', inline: true },
      { name: 'Material Savings', value: `${meSavings}%`, inline: true },
      { name: 'TE Research', value: `${currentTE}% → ${targetTE}%`, inline: true },
      { name: 'TE Cost', value: teCost > 0 ? `${teCost.toLocaleString()} ISK` : 'N/A', inline: true },
      { name: 'Time Savings', value: `${teSavings}%`, inline: true },
      { name: 'Total Research Cost', value: `${totalCost.toLocaleString()} ISK`, inline: false }
    );
  
  await interaction.reply({ embeds: [embed] });
}
