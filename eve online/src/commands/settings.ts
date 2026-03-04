import { SlashCommandBuilder, CommandInteraction, EmbedBuilder, AutocompleteInteraction } from 'discord.js';
import db from '../database/setup';

export const data = new SlashCommandBuilder()
  .setName('settings')
  .setDescription('Configure your preferences')
  .addSubcommand(sub =>
    sub
      .setName('set')
      .setDescription('Set your default settings')
      .addStringOption(opt => opt.setName('character').setDescription('Default character name').setRequired(false))
      .addStringOption(opt => opt.setName('location').setDescription('Default location').setRequired(false))
      .addBooleanOption(opt => opt.setName('notifications').setDescription('Enable notifications').setRequired(false))
      .addNumberOption(opt => opt.setName('profit_threshold').setDescription('Min profit threshold for alerts').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('view')
      .setDescription('View your current settings'))
  .addSubcommand(sub =>
    sub
      .setName('locations')
      .setDescription('List available WinterCo locations'));

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  if (subcommand === 'set') {
    await handleSet(interaction);
  } else if (subcommand === 'view') {
    await handleView(interaction);
  } else if (subcommand === 'locations') {
    await handleLocations(interaction);
  }
}

async function handleSet(interaction: CommandInteraction) {
  const character = interaction.options.get('character')?.value as string | undefined;
  const location = interaction.options.get('location')?.value as string | undefined;
  const notifications = interaction.options.get('notifications')?.value as boolean | undefined;
  const profitThreshold = interaction.options.get('profit_threshold')?.value as number | undefined;
  
  const existing = db.prepare('SELECT * FROM user_settings WHERE discord_user_id = ?')
    .get(interaction.user.id) as { discord_user_id: string } | undefined;
  
  if (existing) {
    const updates: string[] = [];
    const values: (string | number | boolean)[] = [];
    
    if (character) { updates.push('default_character = ?'); values.push(character); }
    if (location) { updates.push('default_location = ?'); values.push(location); }
    if (notifications !== undefined) { updates.push('notification_enabled = ?'); values.push(notifications ? 1 : 0); }
    if (profitThreshold !== undefined) { updates.push('profit_threshold = ?'); values.push(profitThreshold); }
    
    if (updates.length === 0) {
      await interaction.reply({ content: 'No settings provided to update.', ephemeral: true });
      return;
    }
    
    values.push(interaction.user.id);
    db.prepare(`UPDATE user_settings SET ${updates.join(', ')} WHERE discord_user_id = ?`).run(...values);
  } else {
    db.prepare(`
      INSERT INTO user_settings (discord_user_id, default_character, default_location, notification_enabled, profit_threshold)
      VALUES (?, ?, ?, ?, ?)
    `).run(
      interaction.user.id,
      character || null,
      location || null,
      notifications !== undefined ? (notifications ? 1 : 0) : 1,
      profitThreshold || 0
    );
  }
  
  await interaction.reply({ content: 'Settings updated.', ephemeral: true });
}

async function handleView(interaction: CommandInteraction) {
  const settings = db.prepare('SELECT * FROM user_settings WHERE discord_user_id = ?')
    .get(interaction.user.id) as { 
      default_character: string; 
      default_location: string; 
      notification_enabled: number;
      profit_threshold: number;
    } | undefined;
  
  if (!settings) {
    await interaction.reply({ content: 'No settings configured. Use `/settings set` to configure.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Your Settings')
    .setColor(0x3498db)
    .addFields(
      { name: 'Default Character', value: settings.default_character || 'Not set', inline: true },
      { name: 'Default Location', value: settings.default_location || 'Not set', inline: true },
      { name: 'Notifications', value: settings.notification_enabled ? 'Enabled' : 'Disabled', inline: true },
      { name: 'Profit Threshold', value: settings.profit_threshold ? `${settings.profit_threshold.toLocaleString()} ISK` : 'Not set', inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleLocations(interaction: CommandInteraction) {
  const locations = db.prepare('SELECT * FROM locations ORDER BY is_jf_hub DESC, name').all() as { 
    name: string; 
    system: string; 
    region: string; 
    is_jf_hub: number;
  }[];
  
  const jfHubs = locations.filter(l => l.is_jf_hub);
  const others = locations.filter(l => !l.is_jf_hub);
  
  const embed = new EmbedBuilder()
    .setTitle('WinterCo Locations')
    .setColor(0x3498db)
    .addFields(
      { 
        name: 'JF Hubs', 
        value: jfHubs.map(l => `${l.name} (${l.system})`).join('\n') || 'None', 
        inline: false 
      },
      { 
        name: 'Other Stations', 
        value: others.map(l => `${l.name} (${l.system})`).join('\n') || 'None', 
        inline: false 
      }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}
