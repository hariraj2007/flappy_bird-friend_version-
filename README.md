# 🐦 Flappy Friend — Web Launcher

A Flask website that lets you upload your friend's photos and instantly configure & launch the Flappy Friend game.

## Project structure

```
flappy_web/
├── app.py                   # Flask backend
├── flappy_friend.py         # The game (copy here)
├── requirements.txt
├── templates/
│   ├── base.html            # Jinja2 base layout
│   ├── index.html           # Upload form page
│   └── ready.html           # Launch & command page
└── static/
    ├── css/style.css        # All styles
    ├── js/main.js           # Drag-drop & interactions
    └── uploads/             # Saved images (auto-created)
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure flappy_friend.py is in this folder
cp /path/to/flappy_friend.py .

# 3. Run the server
python app.py

# 4. Open in browser
# http://localhost:5000
```

## Usage

1. Open http://localhost:5000
2. Upload your friend's **flying photo** (normal pose)
3. Upload your friend's **jump photo** (shown while flapping)
4. Optionally set a custom jump sound file
5. Click **Continue →**
6. On the ready page: click **Launch game now** to run directly, or copy the command to run in terminal

## Notes

- Uploaded images are saved to `static/uploads/`
- "Launch game now" uses `subprocess.Popen` — only works if running the server locally
- If server is remote, copy the command and run it on the machine with pygame installed
- Requires `pygame` for the game itself: `pip install pygame`
