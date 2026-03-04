import 'dotenv/config';
import { REST, Routes } from 'discord.js';
import { commands } from '../commands';

const rest = new REST().setToken(process.env.DISCORD_TOKEN!);

(async () => {
  try {
    console.log(`Started refreshing ${commands.length} application commands.`);
    
    const commandsData = commands.map(c => c.data.toJSON());
    
    if (process.env.GUILD_ID) {
      await rest.put(
        Routes.applicationGuildCommands(process.env.CLIENT_ID!, process.env.GUILD_ID),
        { body: commandsData }
      );
      console.log('Registered commands to guild.');
    } else {
      await rest.put(
        Routes.applicationCommands(process.env.CLIENT_ID!),
        { body: commandsData }
      );
      console.log('Registered commands globally.');
    }
    
    console.log('Successfully reloaded application commands.');
  } catch (error) {
    console.error(error);
  }
})();
