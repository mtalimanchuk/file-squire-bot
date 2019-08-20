# file-squire-bot
A telegram bot to fetch files from a remote machine

* Open `config.py`, set your **TOKEN** (string) and **WHITELIST** (list of user IDs)
* Open `paths.py`, add aliases and paths to PATH_MAP:
```python
PATH_MAP = {
    "me": "squire.log",
    "flask": "myflaskapp/logs/errors.log",
}
```
* Start the bot. You are ready to fetch files from any device, e.g.
`/fetch me` to get _squire.log_
