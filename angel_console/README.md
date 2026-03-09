# LittleAngel Console

Browser-based management console for LittleAngelBot.

## Start

From the project root:

```powershell
python -m pip install -r requirements.txt
python entry_console.py
```

Alternative package entry:

```powershell
python -m angel_console
```

Open `http://127.0.0.1:7788`.

## Positioning

The Web Console is the primary entrypoint for the project. Use it to:

- start chat sessions
- configure model profiles
- manage files, search, cron, and heartbeat
- configure and launch QQ and Discord channels
- treat CLI / QQ / Discord direct scripts as advanced entrypoints only

## Direct Channel Scripts

```powershell
python channels/cli.py
python channels/qq.py
python channels/discord.py
```

Legacy root wrappers are still supported for compatibility:

```powershell
python entry_cli.py
python entry_qq.py
python entry_discord.py
```

## Notes

- Default bind host is `127.0.0.1`.
- Default port is `7788`.
- Existing `qq:*`, `cli:*`, and `web:*` sessions remain visible in the console.
- Model profiles are still persisted in `local_secrets.yaml`.
