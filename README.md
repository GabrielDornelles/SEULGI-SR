# SEULGI-SR

## Install/Run
```shell
sudo apt install ffmpeg
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 run.py
```

# What is Seulgi-sr?
Seulgi-sr is a discord bot integrated to Amazon Echo Dot (Alexa).
We plan to make Seulgi a bot that works with your voice commands instead of discord chat commands

# Q&A
Q: Why the bot is called Seulgi?

A: https://www.youtube.com/watch?v=Gd9HGUDaY1Y&feature=youtu.be&t=556

# What it can do now?

For now Seulgi is just a simple bot able to create playlists and play youtube songs by searching its name or adding a link to the queue list.
it also has a bunch of main implementations in order to avoid the bot breaking through its commands (raising errors, stoping working etc.)
Also we've implemented the right commands order, so now you can call Seulgi commands like play directly, and not needing to add her to the channel or anything, its working quite well, simple and clean(as clean as we tested it, you can report bugs so we can try to solve it). 

Also Seulgi will display to your entire server what she's playing in a call, which is not implemented in a bunch of music bots ;)
