import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('help')
  .setDescription('Show help and available commands');

export async function execute(interaction: CommandInteraction) {
  const embed = new EmbedBuilder()
    .setTitle('EVE Industry Services - Complete Command List')
    .setColor(0x3498db)
    .setDescription('Max ISK profit tools for WinterCo operations')
    .addFields(
      { 
        name: '/analyze', 
        value: '`best` - Find best ISK activity now\n`pi` - Best PI tier for max profit\n`industry` - Analyze your jobs\n`trading` - Best import opportunities\n`all` - Complete profit analysis', 
        inline: false 
      },
      { 
        name: '/jf', 
        value: '`quote` - Get JF shipping quote\n`create` - Create a contract\n`list` - View your contracts\n`rates` - View current rates\n`stats` - Your shipping stats', 
        inline: false 
      },
      { 
        name: '/industry', 
        value: '`add` - Add a manufacturing job\n`list` - View your jobs\n`complete` - Mark job done\n`sell` - Record sale & profit\n`profit` - Calculate margins\n`stats` - Your industry stats', 
        inline: false 
      },
      { 
        name: '/pi', 
        value: '`add` - Add a PI colony\n`list` - View colonies\n`update` - Update colony info\n`stats` - PI statistics\n`profit` - Profit calculator\n`schematic` - Add schematics', 
        inline: false 
      },
      { 
        name: '/piproducts', 
        value: '`prices` - PI product prices by tier\n`best` - Best products by profit\n`planet` - Best products per planet type\n`setup` - Recommended PI setup', 
        inline: false 
      }
    )
    .addFields(
      { 
        name: '/trading', 
        value: '`import` - Calculate import profit Jita→WinterCo\n`stations` - Recommended trading hubs\n`bestimports` - Best items to import\n`sellorders` - Track sell orders\n`orders` - List active orders\n`flip` - Station flip calculator', 
        inline: false 
      },
      { 
        name: '/character', 
        value: '`add` - Add character with skills\n`list` - View all chars & capabilities\n`canbuild` - Check who can build an item\n`compare` - Compare two characters\n`bestfor` - Find best char for task', 
        inline: false 
      },
      { 
        name: '/materials', 
        value: '`buy` - Record material purchase\n`inventory` - View your materials\n`value` - Total inventory value\n`sell` - Sell from inventory\n`needed` - Materials for pending jobs\n`stations` - Best buying stations\n`salvage` - Buy salvage materials', 
        inline: false 
      },
      { 
        name: '/blueprint', 
        value: '`add` - Add BPO/BPC to collection\n`list` - View your blueprints\n`update` - Update ME/TE/runs\n`research` - Calculate research costs', 
        inline: false 
      },
      { 
        name: '/shopping', 
        value: '`materials` - Calculate materials needed\n`piextract` - PI extraction schedule\n`export` - Export shopping list', 
        inline: false 
      },
      { 
        name: '/market', 
        value: '`price` - Check Jita prices\n`add` - Track a market order\n`orders` - View tracked orders\n`margin` - Calculate margins\n`compare` - Compare to Jita', 
        inline: false 
      },
      { 
        name: '/config', 
        value: '`discount` - Set nullsec discount (default 10%)\n`jfrate` - Set JF rate\n`threshold` - Min profit threshold\n`view` - View all settings\n`reset` - Reset to defaults', 
        inline: false 
      },
      { 
        name: '/profit', 
        value: 'View your overall profit across all services (day/week/month/all)', 
        inline: false 
      },
      { 
        name: '/plex', 
        value: '`price` - Current Jita PLEX prices\n`convert` - ISK ↔ PLEX conversion\n`cycle` - PLEX to ISK cycle analysis\n`subs` - Subscription costs in ISK\n`omega` - Omega time costs\n`compare` - Historical price comparison', 
        inline: false 
      }
    )
    .addFields({
      name: 'Location Discounts',
      value: '• **RD-G2R**: 5% (materials)\n• **VA6-ED**: 8% (JF hub)\n• **D-PN**: 10% (primary)\n• **Regional**: 10-12%'
    })
    .setFooter({ text: 'WinterCo Industry Services - Pure Blind Region' });
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}
