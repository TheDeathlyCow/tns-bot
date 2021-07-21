# TotallyNotSuspicious (TNS) Bot
This is the source code for the TNS bot that handles QOTD points, as well as other features.

# Setup
* Create a bot account and invite it to your server according to these instructions from Discord: https://discordpy.readthedocs.io/en/stable/discord.html
* Paste the token (see step 7 of the guide above) into a file called `TOKEN.txt` in the same folder is the `main.py`. Put nothing else in this file.

# Commands
The command prefix for this bot is `.tns ` (space included).

Note: an argument surrounded by [] is an optional argument, and an argument surrounded by {} is a required argument. For example, to run a command documented as `.tns example_command {channel} [number]`, you could type `.tns example_command #example-channel 10` or `.tns example_command #example-channel`. 
## QOTD Management
In order to manage the QOTD tracking, you must have a role named `QOTD Master`. 

To set the discussion channel use the command `.tns discussion [#optional-discussion-channel]`. This will set the specified channel (or the current channel if there is no specified channel) to be the channel for discussion about the QOTD (Requires `QOTD Master` role).

To set the suggestions channel use the command `.tns suggestions [#optional-suggestions-channel]`. This will set the specified channel (or the current channel if there is no specified channel) to be the channel for suggesstions for the QOTD (Requires `QOTD Master` role).

To pick a suggestion from a user, use the command `.tns pick {username}`. This will award the mentioned user 3 points and display their most recent suggestion.

To remove points from a user, use the command `.tns remove_points {username} {point_amount}`. 

To see the QOTD leaderboard, use the command `.tns qotdleaderboard`.

To see your own personal QOTD points, use the command `.tns points`. 

## The Game
To start *The Game* in a channel, use the command `.tns thegame [#optionl-channel]`. This will start *The Game* in the specified channel (or the current channel if no channel is specified). 
