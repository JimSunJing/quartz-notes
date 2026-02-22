# X URL -> Quartz Markdown GUI

A local Python GUI tool that ingests an X (Twitter) post URL and creates a new Markdown file in your Quartz `content/` folder.

## Features

- Input `https://x.com/<user>/status/<id>` URL
- Fetch public post data via FxTwitter/VxTwitter APIs
- Auto-generate Markdown with frontmatter
- Save directly to Quartz `content/`
- One-click packaging to Windows `.exe`

## Run (source)

```powershell
cd D:\Quartz4\tools\x_url_ingestor
python run_gui.py
```

Optional CLI mode:

```powershell
python run_cli.py "https://x.com/user/status/1234567890"
```

## Build EXE

```powershell
cd D:\Quartz4\tools\x_url_ingestor
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

Output:

- `D:\Quartz4\tools\x_url_ingestor\dist\XUrlToQuartz.exe`

## Workflow with Quartz

1. Run `XUrlToQuartz.exe`
2. Paste an X URL
3. Confirm target folder is `D:\Quartz4\content`
4. Click `Fetch and Create Markdown`
5. Commit and push:

```powershell
cd D:\Quartz4
git add content
git commit -m "docs: import x post"
git push
```

Your Netlify/Vercel deployment will auto-rebuild.

## Notes

- If a post is private/deleted or API mirrors are unavailable, import will fail.
- The tool currently supports post URLs, not X profile URLs.

