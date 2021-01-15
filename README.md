# ZedUtils
## Overview
ZedUtils is a capable, database-free, python discord bot.

## Usage
### To get files:
```bash
git clone https://github.com/foxnerdsaysmoo/zedutils
```
### To set up:
Make a discord application from the discord developer portal. Add a bot, copy the bot token. Then run (linux only):
```bash
export ZEDUTILS_TOKEN='your token'
```

### To run:
```bash
python main.py
```

## Features

### Customizable prefixes
`prefix` - list prefixes

`prefix add [prefix]` - add a new prefix for in the server

`prefix remove [prefix]` - remove prefix from the server (do not delete them all)

### TTS
`connect` - join voice channel with you

`connect [vc]` - join given voice channel

`say ...` - say your message

`rate` - view current voice rate

`rate [rate]` - set voice rate

`disconnect` - disconnect from voice channel

### Chess games

`chess/challenge/playchess [user]` - challenge use at a chess game

Say your move when it's your turn (uci notation):

`e2e4` - Move piece from e2 to e4

`f7f8q` - Move piece from f7 to f8, and select queen as the promotion (pawn promotion)

`a1c2` - Move piece from a1 to c2

Draws and checkmate detection is automatic.

