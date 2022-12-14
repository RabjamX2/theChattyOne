theChattyOne - a python based Discord bot
========================

Before you start
----------

This project has a virtual environment made using the built in python module `venv` via `python -m venv venv`

You can activate the virtual environment with 

```bash
venv\Scripts\activate.bat
```

The virtual environment has the modules `discord` and `openai` installed via `pip`

**If you don't want to mess with the venv or don't mind installing globally**, You can just run `pip install discord` and `pip install openai` and have no need for the `venv` folder

Setting up
--------

The only setup needed as of now is to insert your token and channelID into the *config.py.RENAMEME* file and rename it *config.py*

Your [OpenAI Token](https://beta.openai.com/account/api-keys), discord bot token, and Discord channel ID is needed.
You can find the ID of a discord channel by enabling developer mode in the Discord `Settings>App Settings>Advanced>Developer Mode` and the right clicking a channel

**To start the bot**, When the virtual environment is activated, you can run `bot.py` to activate the bot

```python
python bot.js
```
You can use either Ctrl^C to exit or the coded *client.close()* function (type bye in the designated channel)

Running
--------


Useful links
-----------------

[Discord Intro to Bots and Apps](https://discord.com/developers/docs/intro#bots-and-apps)

[OpenAI API](https://beta.openai.com/docs/api-reference/introduction)

[Discord Python API](https://discordpy.readthedocs.io/en/stable/quickstart.html)
