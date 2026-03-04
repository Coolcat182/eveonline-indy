import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';

export const data = new SlashCommandBuilder()
  .setName('settings')
  .setDescription('Configure your preferences and market settings')
  .addSubcommand(sub =>
    sub
      .setName('discount')
      .setDescription('Set your nullsec market discount')
      .addNumberOption(opt => opt.setName('percent').setDescription('Discount percentage (e.g., 10 for 10%)').setRequired(true)))
  .addSubcommand(sub =>
    sub
      .setName('jfrate')
      .setDescription('Set your JF shipping rate')
      .addNumberOption(opt => opt.setName('isk_per_m3').setDescription('ISK per m3').setRequired(true)))
  .addSubcommand(sub =>
    sub
      .setName('threshold')
      .setDescription('Set minimum profit threshold')
      .addNumberOption(opt => opt.setName('isk').setDescription('Minimum ISK to show as profitable').setRequired(true)))
  .addSubcommand(sub =>
    sub
      .setName('view')
      .setDescription('View all your settings'))
  .addSubcommand(sub =>
    sub
      .setName('reset')
      .setDescription('Reset settings to defaults')));

db.exec(`
  CREATE TABLE IF NOT EXISTS trade_settings (
    discord_user_id TEXT PRIMARY KEY,
    nullsec_discount REAL DEFAULT 0.10,
    jf_rate_per_m3 REAL DEFAULT 1500,
    profit_threshold REAL DEFAULT 10000000,
    preferred_hub TEXT DEFAULT 'D-PN',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS user_settings (
    discord_user_id TEXT PRIMARY KEY,
    default_location TEXT,
    default_character TEXT,
    notification_enabled BOOLEAN DEFAULT 1,
    profit_threshold REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'discount': await handleDiscount(interaction); break;
    case 'jfrate': await handleJfRate(interaction); break;
    case 'threshold': await handleThreshold(interaction); break;
    case 'view': await handleView(interaction); break;
    case 'reset': await handleReset(interaction); break;
  }
}

async function handleDiscount(interaction: CommandInteraction) {
  const percent = interaction.options.get('percent')?.value as number;
  const discount = percent / 100;
  
  ensureSettings(interaction.user.id);
  
  db.prepare(`
    UPDATE trade_settings SET nullsec_discount = ? WHERE discord_user_id = ?
  `).run(discount, interaction.user.id);
  
  await interaction.reply({ 
    content: `Nullsec discount set to ${percent}%. All 0.0 material purchases will be reduced by this amount.`, 
    ephemeral: true 
  });
}

async function handleJfRate(interaction: CommandInteraction) {
  const rate = interaction.options.get('isk_per_m3')?.value as number;
  
  ensureSettings(interaction.user.id);
  
  db.prepare(`
    UPDATE trade_settings SET jf_rate_per_m3 = ? WHERE discord_user_id = ?
  `).run(rate, interaction.user.id);
  
  await interaction.reply({ 
    content: `JF rate set to ${rate.toLocaleString()} ISK/m³.`, 
    ephemeral: true 
  });
}

async function handleThreshold(interaction: CommandInteraction) {
  const threshold = interaction.options.get('isk')?.value as number;
  
  ensureSettings(interaction.user.id);
  
  db.prepare(`
    UPDATE trade_settings SET profit_threshold = ? WHERE discord_user_id = ?
  `).run(threshold, interaction.user.id);
  
  await interaction.reply({ 
    content: `Profit threshold set to ${threshold.toLocaleString()} ISK. Items below this won't be marked as profitable.`, 
    ephemeral: true 
  });
}

async function handleView(interaction: CommandInteraction) {
  const tradeSettings = db.prepare(`
    SELECT * FROM trade_settings WHERE discord_user_id = ?
  `).get(interaction.user.id) as {
    nullsec_discount: number;
    jf_rate_per_m3: number;
    profit_threshold: number;
    preferred_hub: string;
  } | undefined;
  
  const userSettings = db.prepare(`
    SELECT * FROM user_settings WHERE discord_user_id = ?
  `).get(interaction.user.id) as {
    default_location: string;
    default_character: string;
    notification_enabled: number;
  } | undefined;
  
  const embed = new EmbedBuilder()
    .setTitle('Your Settings')
    .setColor(0x3498db);
  
  if (tradeSettings) {
    embed.addFields(
      { name: 'Nullsec Discount', value: `${(tradeSettings.nullsec_discount * 100).toFixed(0)}%`, inline: true },
      { name: 'JF Rate', value: `${tradeSettings.jf_rate_per_m3.toLocaleString()} ISK/m³`, inline: true },
      { name: 'Profit Threshold', value: `${tradeSettings.profit_threshold.toLocaleString()} ISK`, inline: true },
      { name: 'Preferred Hub', value: tradeSettings.preferred_hub, inline: true }
    );
  } else {
    embed.addFields({ name: 'Trade Settings', value: 'Using defaults (10% discount, 1500 ISK/m³ JF)' });
  }
  
  if (userSettings) {
    embed.addFields(
      { name: 'Default Location', value: userSettings.default_location || 'Not set', inline: true },
      { name: 'Default Character', value: userSettings.default_character || 'Not set', inline: true },
      { name: 'Notifications', value: userSettings.notification_enabled ? 'Enabled' : 'Disabled', inline: true }
    );
  }
  
  embed.addFields({ 
    name: 'Location Discounts', 
    value: '• RD-G2R: 5%\n• VA6-ED: 8%\n• D-PN: 10%\n• Regional: 10-12%' 
  });
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleReset(interaction: CommandInteraction) {
  db.prepare(`
    INSERT OR REPLACE INTO trade_settings 
    (discord_user_id, nullsec_discount, jf_rate_per_m3, profit_threshold, preferred_hub)
    VALUES (?, 0.10, 1500, 10000000, 'D-PN')
  `).run(interaction.user.id);
  
  await interaction.reply({ 
    content: 'Settings reset to defaults:\n• 10% nullsec discount\n• 1500 ISK/m³ JF rate\n• 10M ISK profit threshold\n• D-PN preferred hub', 
    ephemeral: true 
  });
}

function ensureSettings(userId: string) {
  db.prepare(`
    INSERT OR IGNORE INTO trade_settings (discord_user_id)
    VALUES (?)
  `).run(userId);
}

export function getTradeSettings(userId: string): {
  nullsec_discount: number;
  jf_rate_per_m3: number;
  profit_threshold: number;
  preferred_hub: string;
} {
  const settings = db.prepare(`
    SELECT * FROM trade_settings WHERE discord_user_id = ?
  `).get(userId) as {
    nullsec_discount: number;
    jf_rate_per_m3: number;
    profit_threshold: number;
    preferred_hub: string;
  } | undefined;
  
  if (settings) {
    return settings;
  }
  
  db.prepare(`
    INSERT INTO trade_settings (discord_user_id)
    VALUES (?)
  `).run(userId);
  
  return {
    nullsec_discount: 0.10,
    jf_rate_per_m3: 1500,
    profit_threshold: 10000000,
    preferred_hub: 'D-PN'
  };
}
