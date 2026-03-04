import 'dotenv/config';
import { Client, GatewayIntentBits, Collection, Events, Interaction, AutocompleteInteraction } from 'discord.js';
import http from 'http';
import { commands } from './commands';
import './database/setup';

const PORT = parseInt(process.env.PORT || '8080');

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', uptime: process.uptime() }));
  } else if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <html>
        <head><title>EVE Industry Services</title></head>
        <body style="font-family: Arial; background: #1a1a2e; color: #eee; padding: 40px;">
          <h1>🚀 EVE Industry Services</h1>
          <p>Discord bot for WinterCo industry, PI, JF, and trading operations.</p>
          <h2>Features</h2>
          <ul>
            <li>Jump Freighter contract management</li>
            <li>Industry job tracking & profit analysis</li>
            <li>PI colony management (Pure Blind)</li>
            <li>Jita → WinterCo trading</li>
            <li>Material buying with discounts</li>
            <li>PLEX to ISK cycle analysis</li>
            <li>Character skill tracking</li>
          </ul>
          <h2>Status</h2>
          <p>✅ Bot Running</p>
          <p>Commands Loaded: ${commands.length}</p>
          <p>Uptime: ${Math.floor(process.uptime())}s</p>
        </body>
      </html>
    `);
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, () => {
  console.log(`HTTP server listening on port ${PORT}`);
  console.log(`View at: http://localhost:${PORT}`);
});

const client = new Client({
  intents: [GatewayIntentBits.Guilds],
});

client.commands = new Collection();

for (const command of commands) {
  client.commands.set(command.data.name, command);
}

client.once(Events.ClientReady, (c) => {
  console.log(`Logged in as ${c.user.tag}`);
  console.log(`Loaded ${commands.length} commands`);
});

client.on(Events.InteractionCreate, async (interaction: Interaction) => {
  if (interaction.isAutocomplete()) {
    const command = client.commands.get(interaction.commandName);
    
    if (!command || !('autocomplete' in command)) {
      return;
    }
    
    try {
      await (command as { autocomplete: (i: AutocompleteInteraction) => Promise<void> }).autocomplete(interaction);
    } catch (error) {
      console.error('Autocomplete error:', error);
    }
    return;
  }
  
  if (!interaction.isChatInputCommand()) return;
  
  const command = client.commands.get(interaction.commandName);
  
  if (!command) {
    console.error(`No command matching ${interaction.commandName} was found.`);
    return;
  }
  
  try {
    await command.execute(interaction);
  } catch (error) {
    console.error('Command execution error:', error);
    
    const errorMessage = { content: 'There was an error executing this command.', ephemeral: true };
    
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp(errorMessage);
    } else {
      await interaction.reply(errorMessage);
    }
  }
});

client.login(process.env.DISCORD_TOKEN);
