import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';

export const data = new SlashCommandBuilder()
  .setName('profit')
  .setDescription('View your overall profit across all services')
  .addStringOption(opt => opt.setName('period').setDescription('Time period').addChoices(
    { name: 'Today', value: 'day' },
    { name: 'This Week', value: 'week' },
    { name: 'This Month', value: 'month' },
    { name: 'All Time', value: 'all' }
  ).setRequired(false));

export async function execute(interaction: CommandInteraction) {
  const period = (interaction.options.get('period')?.value as string) || 'month';
  
  let dateFilter = '';
  switch (period) {
    case 'day':
      dateFilter = "AND datetime(completed_at) >= datetime('now', '-1 day')";
      break;
    case 'week':
      dateFilter = "AND datetime(completed_at) >= datetime('now', '-7 days')";
      break;
    case 'month':
      dateFilter = "AND datetime(completed_at) >= datetime('now', '-30 days')";
      break;
    default:
      dateFilter = '';
  }
  
  const industryStats = db.prepare(`
    SELECT 
      SUM(profit) as profit,
      SUM(CASE WHEN status = 'sold' THEN 1 ELSE 0 END) as sold_jobs
    FROM industry_jobs 
    WHERE discord_user_id = ? ${dateFilter}
  `).get(interaction.user.id) as { profit: number; sold_jobs: number };
  
  const piStats = db.prepare(`
    SELECT 
      SUM(daily_profit) as daily_profit,
      COUNT(*) as colonies
    FROM pi_colonies 
    WHERE discord_user_id = ?
  `).get(interaction.user.id) as { daily_profit: number; colonies: number };
  
  const jfStats = db.prepare(`
    SELECT 
      SUM(price) as spent,
      SUM(volume_m3) as volume,
      COUNT(*) as contracts
    FROM jf_contracts 
    WHERE discord_user_id = ? AND status = 'completed' ${dateFilter}
  `).get(interaction.user.id) as { spent: number; volume: number; contracts: number };
  
  const industryProfit = industryStats.profit || 0;
  const piDailyProfit = piStats.daily_profit || 0;
  
  let piPeriodProfit = 0;
  switch (period) {
    case 'day':
      piPeriodProfit = piDailyProfit;
      break;
    case 'week':
      piPeriodProfit = piDailyProfit * 7;
      break;
    case 'month':
      piPeriodProfit = piDailyProfit * 30;
      break;
    default:
      piPeriodProfit = piDailyProfit * 365;
  }
  
  const totalProfit = industryProfit + piPeriodProfit;
  const jfSpent = jfStats.spent || 0;
  const netProfit = totalProfit - jfSpent;
  
  const periodNames: Record<string, string> = {
    day: 'Today',
    week: 'This Week',
    month: 'This Month',
    all: 'All Time'
  };
  
  const embed = new EmbedBuilder()
    .setTitle(`Profit Overview - ${periodNames[period]}`)
    .setColor(totalProfit >= 0 ? 0x00ff00 : 0xff0000)
    .addFields(
      { name: 'Industry Profit', value: `${industryProfit.toLocaleString()} ISK`, inline: true },
      { name: 'PI Profit (Est.)', value: `${piPeriodProfit.toLocaleString()} ISK`, inline: true },
      { name: 'Total Revenue', value: `${totalProfit.toLocaleString()} ISK`, inline: true },
      { name: 'JF Shipping Cost', value: `${jfSpent.toLocaleString()} ISK`, inline: true },
      { name: 'Net Profit', value: `${netProfit.toLocaleString()} ISK`, inline: true }
    )
    .addFields({ name: '\u200B', value: '\u200B' })
    .addFields(
      { name: 'Industry Jobs Sold', value: (industryStats.sold_jobs || 0).toString(), inline: true },
      { name: 'PI Colonies', value: (piStats.colonies || 0).toString(), inline: true },
      { name: 'JF Contracts', value: (jfStats.contracts || 0).toString(), inline: true }
    );
  
  if (piStats.colonies > 0) {
    embed.addFields({ name: 'PI Daily Rate', value: `${piDailyProfit.toLocaleString()} ISK/day`, inline: true });
  }
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}
