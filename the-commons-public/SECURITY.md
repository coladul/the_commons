# Security / secret-handling notes

The scripts require an OpenAI API key. **Never place a real API key inside a Python file, Markdown file, screenshot, Git commit, issue, or public report.**

Set the key only in your environment, for example:

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "YOUR_KEY_HERE"
```

macOS/Linux:

```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"
```

Do not publicly upload:

- `.env`
- `.venv/` or `venv/`
- `*.db`
- `memory_*.db`
- shell history containing secrets
- screenshots showing secrets

The public package was assembled without the experimenter's local SQLite databases or private branch-session databases.
