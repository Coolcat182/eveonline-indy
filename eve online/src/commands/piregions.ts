import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';

export const data = new SlashCommandBuilder()
  .setName('piregions')
  .setDescription('PI data for all regions')
  .addSubcommand(sub =>
    sub
      .setName('view')
      .setDescription('View PI data for a region')
      .addStringOption(opt => opt.setName('region').setDescription('Region name').setRequired(true).addChoices(
        { name: 'Pure Blind (WinterCo)', value: 'Pure Blind' },
        { name: 'Tenal', value: 'Tenal' },
        { name: 'Tribute', value: 'Tribute' },
        { name: 'Vale of the Silent', value: 'Vale of the Silent' },
        { name: 'Geminate', value: 'Geminate' },
        { name: 'Deklein', value: 'Deklein' },
        { name: 'Fade', value: 'Fade' },
        { name: 'Cloud Ring', value: 'Cloud Ring' },
        { name: 'Syndicate', value: 'Syndicate' },
        { name: 'Outer Ring', value: 'Outer Ring' },
        { name: 'The Forge (High Sec)', value: 'The Forge' },
        { name: 'Metropolis', value: 'Metropolis' },
        { name: 'Heimatar', value: 'Heimatar' },
        { name: 'Domain', value: 'Domain' },
        { name: 'Sinq Laison', value: 'Sinq Laison' }
      )))
  .addSubcommand(sub =>
    sub
      .setName('setdefault')
      .setDescription('Set your default region')
      .addStringOption(opt => opt.setName('region').setDescription('Region name').setRequired(true).addChoices(
        { name: 'Pure Blind (WinterCo)', value: 'Pure Blind' },
        { name: 'Tenal', value: 'Tenal' },
        { name: 'Tribute', value: 'Tribute' },
        { name: 'Vale of the Silent', value: 'Vale of the Silent' },
        { name: 'Geminate', value: 'Geminate' }
      )))
  .addSubcommand(sub =>
    sub
      .setName('resources')
      .setDescription('Show all PI resources available in a region')
      .addStringOption(opt => opt.setName('region').setDescription('Region name').setRequired(false)))
  .addSubcommand(sub =>
    sub
      .setName('bestplanets')
      .setDescription('Find best planets in your region for a product')
      .addStringOption(opt => opt.setName('product').setDescription('PI product').setRequired(true))
      .addStringOption(opt => opt.setName('region').setDescription('Region (uses default if not set)').setRequired(false)));

interface PlanetType {
  name: string;
  resources: string[];
  imageUrl: string;
}

interface RegionData {
  name: string;
  security: string;
  systems: { name: string; planets: { type: string; count: number }[] }[];
  imageUrl: string;
}

const PLANET_TYPES: Record<string, PlanetType> = {
  'Barren': {
    name: 'Barren',
    resources: ['Base Metals', 'Silicon', 'Precious Metals', 'Non-CS Crystals'],
    imageUrl: 'https://images.evetech.net/types/11/render?size=64'
  },
  'Gas': {
    name: 'Gas',
    resources: ['Noble Gas', 'Ionic Solutions', 'Oxidizing Compound', 'Coolant'],
    imageUrl: 'https://images.evetech.net/types/13/render?size=64'
  },
  'Ice': {
    name: 'Ice',
    resources: ['Water', 'Oxygen', 'Coolant'],
    imageUrl: 'https://images.evetech.net/types/12/render?size=64'
  },
  'Lava': {
    name: 'Lava',
    resources: ['Toxic Metals', 'Felsic Magma', 'Non-CS Crystals', 'Suspended Plasma'],
    imageUrl: 'https://images.evetech.net/types/14/render?size=64'
  },
  'Oceanic': {
    name: 'Oceanic',
    resources: ['Water', 'Bacteria', 'Biomass', 'Proteins'],
    imageUrl: 'https://images.evetech.net/types/15/render?size=64'
  },
  'Plasma': {
    name: 'Plasma',
    resources: ['Plasmoids', 'Superconductors', 'Noble Gas', 'Suspended Plasma'],
    imageUrl: 'https://images.evetech.net/types/2062/render?size=64'
  },
  'Storm': {
    name: 'Storm',
    resources: ['Noble Gas', 'Ionic Solutions', 'Suspended Plasma'],
    imageUrl: 'https://images.evetech.net/types/2016/render?size=64'
  },
  'Temperate': {
    name: 'Temperate',
    resources: ['Industrial Fibers', 'Proteins', 'Biomass', 'Bacteria'],
    imageUrl: 'https://images.evetech.net/types/11/render?size=64'
  }
};

const REGIONS: Record<string, RegionData> = {
  'Pure Blind': {
    name: 'Pure Blind',
    security: 'Null Sec',
    imageUrl: 'https://images.evetech.net/types/0/render?size=64',
    systems: [
      { name: 'D-PN', planets: [
        { type: 'Plasma', count: 2 },
        { type: 'Gas', count: 3 },
        { type: 'Barren', count: 2 },
        { type: 'Temperate', count: 1 }
      ]},
      { name: 'VA6-ED', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 2 },
        { type: 'Lava', count: 3 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'RD-G2R', planets: [
        { type: 'Gas', count: 3 },
        { type: 'Barren', count: 2 },
        { type: 'Temperate', count: 2 },
        { type: 'Ice', count: 1 }
      ]},
      { name: 'O-BKJY', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: '7-60QB', planets: [
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 },
        { type: 'Lava', count: 1 }
      ]},
      { name: 'X-7OMU', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 3 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'E-YCML', planets: [
        { type: 'Plasma', count: 2 },
        { type: 'Gas', count: 2 },
        { type: 'Temperate', count: 1 }
      ]},
      { name: 'H-PA29', planets: [
        { type: 'Gas', count: 2 },
        { type: 'Lava', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'F-9CZX', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'FDZ4-A', planets: [
        { type: 'Gas', count: 3 },
        { type: 'Barren', count: 2 },
        { type: 'Storm', count: 1 }
      ]},
      { name: 'B-VIP9', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Lava', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'V7-MID', planets: [
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 },
        { type: 'Oceanic', count: 1 }
      ]}
    ]
  },
  'Tenal': {
    name: 'Tenal',
    security: 'Null Sec',
    imageUrl: 'https://images.evetech.net/types/0/render?size=64',
    systems: [
      { name: 'PJ-LON', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 2 },
        { type: 'Ice', count: 3 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'Z-7O', planets: [
        { type: 'Gas', count: 3 },
        { type: 'Ice', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'H-W9TY', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 3 }
      ]},
      { name: 'LOQ-NQ', planets: [
        { type: 'Gas', count: 2 },
        { type: 'Ice', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'A-ELE2', planets: [
        { type: 'Plasma', count: 2 },
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 1 }
      ]},
      { name: 'O-2RNZ', planets: [
        { type: 'Gas', count: 3 },
        { type: 'Ice', count: 2 },
        { type: 'Lava', count: 1 }
      ]},
      { name: 'K-6K16', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'Y-W1Q1', planets: [
        { type: 'Gas', count: 2 },
        { type: 'Ice', count: 3 },
        { type: 'Barren', count: 1 }
      ]}
    ]
  },
  'Tribute': {
    name: 'Tribute',
    security: 'Null Sec',
    imageUrl: 'https://images.evetech.net/types/0/render?size=64',
    systems: [
      { name: 'N-8YET', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'M-OEE8', planets: [
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 },
        { type: 'Lava', count: 1 }
      ]},
      { name: 'Obe', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 3 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'Uemon', planets: [
        { type: 'Gas', count: 2 },
        { type: 'Temperate', count: 2 },
        { type: 'Barren', count: 1 }
      ]},
      { name: 'H-5GUI', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 }
      ]}
    ]
  },
  'Vale of the Silent': {
    name: 'Vale of the Silent',
    security: 'Null Sec',
    imageUrl: 'https://images.evetech.net/types/0/render?size=64',
    systems: [
      { name: '6NJ8-V', planets: [
        { type: 'Plasma', count: 2 },
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'EWOK-K', planets: [
        { type: 'Gas', count: 3 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'SV5-8N', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 2 },
        { type: 'Temperate', count: 1 }
      ]},
      { name: 'C-OK0R', planets: [
        { type: 'Gas', count: 2 },
        { type: 'Lava', count: 2 },
        { type: 'Barren', count: 2 }
      ]}
    ]
  },
  'Geminate': {
    name: 'Geminate',
    security: 'Null Sec',
    imageUrl: 'https://images.evetech.net/types/0/render?size=64',
    systems: [
      { name: 'O-ZXUV', planets: [
        { type: 'Plasma', count: 1 },
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'L-C3O7', planets: [
        { type: 'Gas', count: 3 },
        { type: 'Barren', count: 2 },
        { type: 'Oceanic', count: 1 }
      ]},
      { name: 'A-ELE2', planets: [
        { type: 'Plasma', count: 2 },
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 1 }
      ]}
    ]
  },
  'The Forge': {
    name: 'The Forge',
    security: 'High Sec',
    imageUrl: 'https://images.evetech.net/types/0/render?size=64',
    systems: [
      { name: 'Jita', planets: [
        { type: 'Gas', count: 3 },
        { type: 'Barren', count: 2 },
        { type: 'Temperate', count: 1 }
      ]},
      { name: 'Perimeter', planets: [
        { type: 'Gas', count: 2 },
        { type: 'Barren', count: 2 }
      ]},
      { name: 'New Caldari', planets: [
        { type: 'Barren', count: 3 },
        { type: 'Gas', count: 1 }
      ]}
    ]
  }
};

db.exec(`
  CREATE TABLE IF NOT EXISTS user_regions (
    discord_user_id TEXT PRIMARY KEY,
    default_region TEXT DEFAULT 'Pure Blind',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS pi_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_name TEXT NOT NULL,
    region TEXT NOT NULL,
    planet_type TEXT NOT NULL,
    planet_count INTEGER DEFAULT 1,
    UNIQUE(system_name, planet_type)
  );
`);

for (const [regionName, regionData] of Object.entries(REGIONS)) {
  for (const system of regionData.systems) {
    for (const planet of system.planets) {
      db.prepare(`
        INSERT OR IGNORE INTO pi_systems (system_name, region, planet_type, planet_count)
        VALUES (?, ?, ?, ?)
      `).run(system.name, regionName, planet.type, planet.count);
    }
  }
}

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'view': await handleView(interaction); break;
    case 'setdefault': await handleSetDefault(interaction); break;
    case 'resources': await handleResources(interaction); break;
    case 'bestplanets': await handleBestPlanets(interaction); break;
  }
}

async function handleView(interaction: CommandInteraction) {
  const region = interaction.options.get('region')?.value as string;
  const regionData = REGIONS[region];
  
  if (!regionData) {
    await interaction.reply({ content: 'Region not found.', ephemeral: true });
    return;
  }
  
  const planetCounts: Record<string, number> = {};
  const resourceCounts: Record<string, number> = {};
  
  for (const system of regionData.systems) {
    for (const planet of system.planets) {
      planetCounts[planet.type] = (planetCounts[planet.type] || 0) + planet.count;
      const planetType = PLANET_TYPES[planet.type];
      if (planetType) {
        for (const resource of planetType.resources) {
          resourceCounts[resource] = (resourceCounts[resource] || 0) + planet.count;
        }
      }
    }
  }
  
  const embed = new EmbedBuilder()
    .setTitle(`PI Data: ${region}`)
    .setColor(0x3498db)
    .setThumbnail(regionData.imageUrl)
    .setDescription(`**${regionData.security}** - ${regionData.systems.length} systems`)
    .addFields(
      { 
        name: 'Planet Types', 
        value: Object.entries(planetCounts)
          .sort((a, b) => b[1] - a[1])
          .map(([type, count]) => `${type}: ${count}`)
          .join('\n'),
        inline: true 
      },
      { 
        name: 'Top Resources', 
        value: Object.entries(resourceCounts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 10)
          .map(([resource, count]) => `${resource}: ${count}`)
          .join('\n'),
        inline: true 
      }
    )
    .addFields({ 
      name: 'Systems', 
      value: regionData.systems.map(s => s.name).join(', ') 
    });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleSetDefault(interaction: CommandInteraction) {
  const region = interaction.options.get('region')?.value as string;
  
  db.prepare(`
    INSERT OR REPLACE INTO user_regions (discord_user_id, default_region)
    VALUES (?, ?)
  `).run(interaction.user.id, region);
  
  await interaction.reply({ content: `Default region set to **${region}**.`, ephemeral: true });
}

async function handleResources(interaction: CommandInteraction) {
  let region = interaction.options.get('region')?.value as string | undefined;
  
  if (!region) {
    const userRegion = db.prepare('SELECT default_region FROM user_regions WHERE discord_user_id = ?')
      .get(interaction.user.id) as { default_region: string } | undefined;
    region = userRegion?.default_region || 'Pure Blind';
  }
  
  const regionData = REGIONS[region];
  if (!regionData) {
    await interaction.reply({ content: 'Region not found.', ephemeral: true });
    return;
  }
  
  const resourceCounts: Record<string, { count: number; planets: string[] }> = {};
  
  for (const system of regionData.systems) {
    for (const planet of system.planets) {
      const planetType = PLANET_TYPES[planet.type];
      if (planetType) {
        for (const resource of planetType.resources) {
          if (!resourceCounts[resource]) {
            resourceCounts[resource] = { count: 0, planets: [] };
          }
          resourceCounts[resource].count += planet.count;
          if (!resourceCounts[resource].planets.includes(planet.type)) {
            resourceCounts[resource].planets.push(planet.type);
          }
        }
      }
    }
  }
  
  const sorted = Object.entries(resourceCounts)
    .sort((a, b) => b[1].count - a[1].count);
  
  const embed = new EmbedBuilder()
    .setTitle(`PI Resources: ${region}`)
    .setColor(0x00ff00)
    .setDescription(
      sorted.map(([resource, data]) => 
        `**${resource}**: ${data.count} sources (${data.planets.join(', ')})`
      ).join('\n')
    );
  
  await interaction.reply({ embeds: [embed] });
}

async function handleBestPlanets(interaction: CommandInteraction) {
  const product = interaction.options.get('product')?.value as string;
  let region = interaction.options.get('region')?.value as string | undefined;
  
  if (!region) {
    const userRegion = db.prepare('SELECT default_region FROM user_regions WHERE discord_user_id = ?')
      .get(interaction.user.id) as { default_region: string } | undefined;
    region = userRegion?.default_region || 'Pure Blind';
  }
  
  const regionData = REGIONS[region];
  if (!regionData) {
    await interaction.reply({ content: 'Region not found.', ephemeral: true });
    return;
  }
  
  const matchingPlanets: { system: string; type: string; count: number }[] = [];
  
  for (const system of regionData.systems) {
    for (const planet of system.planets) {
      const planetType = PLANET_TYPES[planet.type];
      if (planetType && planetType.resources.some(r => r.toLowerCase().includes(product.toLowerCase()))) {
        matchingPlanets.push({ system: system.name, type: planet.type, count: planet.count });
      }
    }
  }
  
  if (matchingPlanets.length === 0) {
    await interaction.reply({ content: `No planets in ${region} produce ${product}.`, ephemeral: true });
    return;
  }
  
  matchingPlanets.sort((a, b) => b.count - a.count);
  
  const embed = new EmbedBuilder()
    .setTitle(`Best Planets for ${product} in ${region}`)
    .setColor(0xf1c40f)
    .setDescription(
      matchingPlanets.slice(0, 15).map(p => 
        `**${p.system}** - ${p.type} (${p.count} planets)`
      ).join('\n')
    )
    .addFields({ 
      name: 'Total', 
      value: `${matchingPlanets.reduce((sum, p) => sum + p.count, 0)} planets across ${new Set(matchingPlanets.map(p => p.system)).size} systems` 
    });
  
  await interaction.reply({ embeds: [embed] });
}

export { PLANET_TYPES, REGIONS };
