# [ChamosBot](http://chamosbotonline.herokuapp.com/)

### How to: Discord Server Admins
1. To add the bot to your Discord server, [visit the bot's authorization page.](https://discordapp.com/oauth2/authorize?client_id=625501072399532042&permissions=261184&scope=bot).
2. Once the bot has been added to your server, go to a channel that the bot has access to and say `!addkey`. From here, the bot will directly message you with the next steps.
3. To enable the bot to send Hypixel stats, you need to give it your Hypixel API key. To get this key, connect to mc.hypixel.net on Minecraft and send `/api` in the chat. The key will look something like 66e96602-6283-45a2-a9a9-240a8b249077. Copy the key, and save it someplace safe for now. **Keep the key private**.
4. Get the ID for your Discord server. If you ran the `!addkey` command from the server to which you want to add the API key, the bot will have told you the server ID in one of its direct messages. If the bot did not give you the server ID, some instructions on how to find the ID for yourself [can be found here](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-).
5. Once you have your server ID and Hypixel API key, run the following command: `!addkey <SERVER ID> <HYPIXEL API KEY>`. The bot will check the key and send you a confirmation message once it is sure your API key is legit. Other server members can add their own keys to the server in order to increase the amount of requests your server can make! **Each API key can make 120 requests per minute. Going over the limit could result in your API key getting revoked, so be sure to get more users to add their keys if you are worried about going over the limit.**
6. Now, the bot is able to send stats to your server! Try `!stats bw gamerboy80` and use a username of your own!

### Technical Details
The bot is currently being run on my Raspberry Pi 3 B+ at home. It uses [Discord.py](https://github.com/Rapptz/discord.py) to read and send messages. If the bot goes down, it is most likely that the Pi was disconnected from the network, but it should usually get back online within 15 minutes.
