import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';
import axios from 'axios';

const ESI_BASE = 'https://esi.evetech.net/latest';

export const data = new SlashCommandBuilder()
  .setName('character')
  .setDescription('Character and skill management')
  .addSubcommand(sub =>
    sub
      .setName('add')
      .setDescription('Add a character manually')
      .addStringOption(opt => opt.setName('name').setDescription('Character name').setRequired(true))
      .addStringOption(opt => opt.setName('skills').setDescription('Key skills (comma-separated, e.g., "Industry 5, Production Eff 5")').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('list')
      .setDescription('List all your characters and their capabilities'))
  .addSubcommand(sub =>
    sub
      .setName('canbuild')
      .setDescription('Check if any character can build an item')
      .addStringOption(opt => opt.setName('item').setDescription('Item to check').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('compare')
      .setDescription('Compare two characters skills')
      .addStringOption(opt => opt.setName('char1').setDescription('First character').setRequired(true))
      .addStringOption(opt => opt.setName('char2').setDescription('Second character').setRequired(true)))
  .addSubcommand(sub =>
    sub
      .setName('bestfor')
      .setDescription('Find best character for a task')
      .addStringOption(opt => opt.setName('task').setDescription('Task type').addChoices(
        { name: 'Manufacturing', value: 'manufacturing' },
        { name: 'PI', value: 'pi' },
        { name: 'Research', value: 'research' },
        { name: 'Invention', value: 'invention' },
        { name: 'Reactions', value: 'reactions' }
      ).setRequired(true))
  .addSubcommand(sub =>
    sub
      .setName('delete')
      .setDescription('Remove a character')
      .addStringOption(opt => opt.setName('name').setDescription('Character name').setRequired(true)));

const INDUSTRY_SKILLS: Record<string, { skill: string; level: number; benefit: string }[]> = {
  'T1 Ships': [
    { skill: 'Industry', level: 5, benefit: '10% faster manufacturing' },
    { skill: 'Advanced Industry', level: 5, benefit: '10% faster manufacturing' },
  ],
  'T2 Ships': [
    { skill: 'Industry', level: 5, benefit: '10% faster manufacturing' },
    { skill: 'Advanced Industry', level: 5, benefit: '10% faster manufacturing' },
    { skill: 'Amarr/Caldari/Gallente/Minmatar Encryption', level: 1, benefit: 'Required for invention' },
  ],
  'T2 Modules': [
    { skill: 'Industry', level: 5, benefit: '10% faster manufacturing' },
    { skill: 'Advanced Industry', level: 5, benefit: '10% faster manufacturing' },
    { skill: 'Science', level: 5, benefit: 'Required for invention' },
  ],
  'Capital Ships': [
    { skill: 'Industry', level: 5, benefit: 'Required' },
    { skill: 'Advanced Industry', level: 5, benefit: 'Required' },
    { skill: 'Capital Ship Construction', level: 1, benefit: 'Required for caps' },
  ],
  'PI': [
    { skill: 'Interplanetary Consolidation', level: 5, benefit: '6 colonies' },
    { skill: 'Command Center Upgrades', level: 5, benefit: 'Best CC' },
    { skill: 'Planetology', level: 4, benefit: 'Better scans' },
    { skill: 'Advanced Planetology', level: 4, benefit: 'Much better scans' },
  ],
};

db.exec(`
  CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    character_id INTEGER,
    corporation TEXT,
    skills TEXT,
    manufacturing_bonus REAL DEFAULT 0,
    research_bonus REAL DEFAULT 0,
    pi_colonies INTEGER DEFAULT 6,
    can_invent INTEGER DEFAULT 0,
    can_build_capitals INTEGER DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(discord_user_id, name)
  );

  CREATE TABLE IF NOT EXISTS skill_imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    import_data TEXT,
    imported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id)
  );
`);

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'add': await handleAdd(interaction); break;
    case 'list': await handleList(interaction); break;
    case 'canbuild': await handleCanBuild(interaction); break;
    case 'compare': await handleCompare(interaction); break;
    case 'bestfor': await handleBestFor(interaction); break;
    case 'delete': await handleDelete(interaction); break;
  }
}

async function handleAdd(interaction: CommandInteraction) {
  const name = interaction.options.get('name')?.value as string;
  const skillsInput = interaction.options.get('skills')?.value as string;
  
  const skills = parseSkills(skillsInput);
  const bonuses = calculateBonuses(skills);
  
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO characters 
    (discord_user_id, name, skills, manufacturing_bonus, research_bonus, pi_colonies, can_invent, can_build_capitals)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  stmt.run(
    interaction.user.id,
    name,
    JSON.stringify(skills),
    bonuses.manufacturing,
    bonuses.research,
    bonuses.piColonies,
    bonuses.canInvent ? 1 : 0,
    bonuses.canBuildCapitals ? 1 : 0
  );
  
  const embed = new EmbedBuilder()
    .setTitle('Character Added')
    .setColor(0x00ff00)
    .addFields(
      { name: 'Name', value: name, inline: true },
      { name: 'Mfg Bonus', value: `${bonuses.manufacturing}%`, inline: true },
      { name: 'Research Bonus', value: `${bonuses.research}%`, inline: true },
      { name: 'PI Colonies', value: bonuses.piColonies.toString(), inline: true },
      { name: 'Can Invent', value: bonuses.canInvent ? 'Yes' : 'No', inline: true },
      { name: 'Can Build Caps', value: bonuses.canBuildCapitals ? 'Yes' : 'No', inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleList(interaction: CommandInteraction) {
  const chars = db.prepare(`
    SELECT * FROM characters WHERE discord_user_id = ?
  `).all(interaction.user.id) as {
    name: string;
    manufacturing_bonus: number;
    research_bonus: number;
    pi_colonies: number;
    can_invent: number;
    can_build_capitals: number;
    skills: string;
  }[];
  
  if (chars.length === 0) {
    await interaction.reply({ content: 'No characters added. Use `/character add` to add one.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Your Characters & Capabilities')
    .setColor(0x3498db)
    .setDescription(
      chars.map(c => {
        const capabilities: string[] = [];
        if (c.manufacturing_bonus >= 20) capabilities.push('T2 Production');
        if (c.can_invent) capabilities.push('Invention');
        if (c.can_build_capitals) capabilities.push('Capitals');
        if (c.pi_colonies >= 6) capabilities.push('Max PI');
        
        return `**${c.name}**\n` +
               `Mfg: ${c.manufacturing_bonus}% | Research: ${c.research}% | PI: ${c.pi_colonies} colonies\n` +
               `Capabilities: ${capabilities.join(', ') || 'T1 Production'}`;
      }).join('\n\n')
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleCanBuild(interaction: CommandInteraction) {
  const item = interaction.options.get('item')?.value as string;
  
  const chars = db.prepare(`
    SELECT name, manufacturing_bonus, can_invent, can_build_capitals, skills 
    FROM characters WHERE discord_user_id = ?
  `).all(interaction.user.id) as {
    name: string;
    manufacturing_bonus: number;
    can_invent: number;
    can_build_capitals: number;
    skills: string;
  }[];
  
  if (chars.length === 0) {
    await interaction.reply({ content: 'No characters on file.', ephemeral: true });
    return;
  }
  
  const itemLower = item.toLowerCase();
  let requiredSkills: string[] = [];
  let requiredType = 'T1 Module';
  
  if (itemLower.includes('ii')) {
    requiredType = 'T2 Item';
    requiredSkills = ['Industry 5', 'Science 5'];
  }
  if (itemLower.includes('dreadnought') || itemLower.includes('carrier') || itemLower.includes('fAX')) {
    requiredType = 'Capital Ship';
    requiredSkills = ['Capital Ship Construction'];
  }
  
  const canBuild: string[] = [];
  const cannotBuild: string[] = [];
  
  for (const char of chars) {
    const skills = JSON.parse(char.skills || '{}');
    let hasSkills = true;
    
    if (requiredType === 'T2 Item' && !char.can_invent) hasSkills = false;
    if (requiredType === 'Capital Ship' && !char.can_build_capitals) hasSkills = false;
    
    if (hasSkills) {
      canBuild.push(`**${char.name}** (${char.manufacturing_bonus}% bonus)`);
    } else {
      cannotBuild.push(char.name);
    }
  }
  
  const embed = new EmbedBuilder()
    .setTitle(`Can Build: ${item}`)
    .setColor(canBuild.length > 0 ? 0x00ff00 : 0xff0000)
    .addFields({ name: 'Required Type', value: requiredType, inline: true });
  
  if (canBuild.length > 0) {
    embed.addFields({ name: '✓ Can Build', value: canBuild.join('\n'), inline: false });
  }
  if (cannotBuild.length > 0) {
    embed.addFields({ name: '✗ Cannot Build', value: cannotBuild.join(', '), inline: false });
  }
  
  await interaction.reply({ embeds: [embed] });
}

async function handleCompare(interaction: CommandInteraction) {
  const char1Name = interaction.options.get('char1')?.value as string;
  const char2Name = interaction.options.get('char2')?.value as string;
  
  const char1 = db.prepare(`
    SELECT * FROM characters WHERE discord_user_id = ? AND name = ?
  `).get(interaction.user.id, char1Name) as {
    manufacturing_bonus: number;
    research_bonus: number;
    pi_colonies: number;
    can_invent: number;
    can_build_capitals: number;
  } | undefined;
  
  const char2 = db.prepare(`
    SELECT * FROM characters WHERE discord_user_id = ? AND name = ?
  `).get(interaction.user.id, char2Name) as {
    manufacturing_bonus: number;
    research_bonus: number;
    pi_colonies: number;
    can_invent: number;
    can_build_capitals: number;
  } | undefined;
  
  if (!char1 || !char2) {
    await interaction.reply({ content: 'One or both characters not found.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle(`Character Comparison: ${char1Name} vs ${char2Name}`)
    .setColor(0x9b59b6)
    .addFields(
      { name: '', value: `**${char1Name}**`, inline: true },
      { name: '', value: '**vs**', inline: true },
      { name: '', value: `**${char2Name}**`, inline: true },
      { name: 'Mfg Bonus', value: `${char1.manufacturing_bonus}%`, inline: true },
      { name: '', value: 'Manufacturing', inline: true },
      { name: 'Mfg Bonus', value: `${char2.manufacturing_bonus}%`, inline: true },
      { name: 'Research', value: `${char1.research_bonus}%`, inline: true },
      { name: '', value: 'Research', inline: true },
      { name: 'Research', value: `${char2.research_bonus}%`, inline: true },
      { name: 'PI Colonies', value: char1.pi_colonies.toString(), inline: true },
      { name: '', value: 'PI', inline: true },
      { name: 'PI Colonies', value: char2.pi_colonies.toString(), inline: true }
    );
  
  await interaction.reply({ embeds: [embed] });
}

async function handleBestFor(interaction: CommandInteraction) {
  const task = interaction.options.get('task')?.value as string;
  
  let orderBy = 'manufacturing_bonus DESC';
  let filter = '1=1';
  let taskName = '';
  
  switch (task) {
    case 'manufacturing':
      orderBy = 'manufacturing_bonus DESC';
      taskName = 'Manufacturing';
      break;
    case 'research':
      orderBy = 'research_bonus DESC';
      taskName = 'Research';
      break;
    case 'invention':
      filter = 'can_invent = 1';
      orderBy = 'manufacturing_bonus DESC';
      taskName = 'Invention';
      break;
    case 'pi':
      orderBy = 'pi_colonies DESC';
      taskName = 'PI';
      break;
    case 'reactions':
      filter = 'can_invent = 1';
      orderBy = 'manufacturing_bonus DESC';
      taskName = 'Reactions';
      break;
  }
  
  const chars = db.prepare(`
    SELECT name, manufacturing_bonus, research_bonus, pi_colonies, can_invent, can_build_capitals
    FROM characters 
    WHERE discord_user_id = ? AND ${filter}
    ORDER BY ${orderBy}
    LIMIT 1
  `).get(interaction.user.id) as {
    name: string;
    manufacturing_bonus: number;
    research_bonus: number;
    pi_colonies: number;
  } | undefined;
  
  if (!chars) {
    await interaction.reply({ content: `No characters capable of ${taskName}.`, ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle(`Best Character for ${taskName}`)
    .setColor(0x00ff00)
    .addFields(
      { name: 'Character', value: chars.name, inline: true },
      { name: 'Mfg Bonus', value: `${chars.manufacturing_bonus}%`, inline: true },
      { name: 'Research Bonus', value: `${chars.research_bonus}%`, inline: true },
      { name: 'PI Colonies', value: chars.pi_colonies.toString(), inline: true }
    );
  
  await interaction.reply({ embeds: [embed] });
}

async function handleDelete(interaction: CommandInteraction) {
  const name = interaction.options.get('name')?.value as string;
  
  const result = db.prepare('DELETE FROM characters WHERE discord_user_id = ? AND name = ?')
    .run(interaction.user.id, name);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'Character not found.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `Character "${name}" deleted.`, ephemeral: true });
}

function parseSkills(input: string): Record<string, number> {
  const skills: Record<string, number> = {};
  
  const pairs = input.split(',').map(s => s.trim());
  for (const pair of pairs) {
    const match = pair.match(/(.+?)\s*(\d+)/);
    if (match) {
      const name = match[1].trim();
      const level = parseInt(match[2]);
      skills[name] = level;
    }
  }
  
  return skills;
}

function calculateBonuses(skills: Record<string, number>): {
  manufacturing: number;
  research: number;
  piColonies: number;
  canInvent: boolean;
  canBuildCapitals: boolean;
} {
  const industry = skills['Industry'] || 0;
  const advIndustry = skills['Advanced Industry'] || 0;
  const science = skills['Science'] || 0;
  const metallurgy = skills['Metallurgy'] || 0;
  const research = skills['Research'] || 0;
  const piColonies = skills['Interplanetary Consolidation'] || 1;
  const ccUpgrades = skills['Command Center Upgrades'] || 0;
  const datacore = skills['Datacore'] || 0;
  const encryption = Math.max(
    skills['Amarr Encryption'] || 0,
    skills['Caldari Encryption'] || 0,
    skills['Gallente Encryption'] || 0,
    skills['Minmatar Encryption'] || 0
  );
  const capConstruction = skills['Capital Ship Construction'] || 0;
  
  return {
    manufacturing: (industry * 4) + (advIndustry * 3),
    research: (science * 1) + (metallurgy * 1) + (research * 1),
    piColonies: Math.min(piColonies + 1, 6),
    canInvent: science >= 5 && encryption >= 1 && datacore >= 1,
    canBuildCapitals: capConstruction >= 1,
  };
}
