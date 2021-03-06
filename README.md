# ZedUtils
## Overview
ZedUtils is a capable, database-free, python discord bot.

### Go to [cogs](#cogs) to view commands

## Usage
### To get files:
```bash
git clone https://github.com/foxnerdsaysmoo/zedutils
```
### To set up:
Make a discord application from the discord developer portal.
Add a bot, copy the bot token.

Then run (linux only):
```bash
export ZEDUTILS_TOKEN='your token'
```

### To run:
```bash
python main.py
```

## Cogs

### Helper
`help` - Shows cog listings with references to readme

`help [cog]` - Shows given cog's command listings

`prefix` - list prefixes

`prefix add [prefix]` - add a new prefix for in the server

`prefix remove [prefix]` - remove prefix from the server (do not delete them all)

### Chatter
**TTS commands**

`connect` - join voice channel with you

`connect [vc]` - join given voice channel

`say ...` - say your message

`rate` - view current voice rate

`rate [rate]` - set voice rate

`disconnect` - disconnect from voice channel

### Chess
**Chess games**

`chess/challenge/playchess [user] [optional: wager]` - challenge user at a chess game

Say your move when it's your turn (uci notation):

`e2e4` - Move piece from e2 to e4

`f7f8q` - Move piece from f7 to f8, and select queen as the promotion (pawn promotion)

`a1c2` - Move piece from a1 to c2

Draws and checkmate detection is automatic.
Only one game can be played per text channel.
The wager will be given or removed from your bank.

### Utils
`pfp [optional: user]` - get given user's pfp, else yours

`rr create [name]` - create reaction role embed

`rr add [emoji] [name] [role]` - add reaction role option

### Economy
`bank [optional: user]` - view your or another user's stats

`work` - work and gain money (chance for promotion)

`crime [user]` - try to steal coins from a user

`coin-give [user] [amount]` - give coins to user

`coin-remove [user] [amount]` - remove coins from user

`coin-flip [wager]` - take a chance to win or lose a wager
