🔐 This app requires a Plex Token, Plex URL, and (optionally) a TMDb API key. You’ll be prompted to enter these on first run — they are securely stored in config.json (which is ignored by Git).
# Plex Collection Builder 🎬

This is a custom Python application that helps users manage and organize their Plex movie libraries by building themed collections. Whether you're a fan of franchises like *Harry Potter* or studios like *A24*, this tool streamlines the process of grouping titles into collections.


🔐 **Credentials Required**  
On first run, you'll be prompted to enter your Plex Token, Plex URL, and optionally a TMDb API key. These credentials are stored securely in a local `config.json` file, which is excluded from version control for your privacy.

---

**📎 Finding Your Plex Token & URL**

- **Plex Token**:  
  1. Open [app.plex.tv](https://app.plex.tv) and sign in.  
  2. Click any movie or show → ⋮ → **Get Info**  
  3. Scroll down and click **View XML**  
  4. In the browser address bar, find the part after `X-Plex-Token=`

- **Plex URL**:  
  - Go to your Plex Web App settings and copy the base URL (e.g. `http://192.168.0.5:32400`)  
  - Make sure it matches the IP and port of your Plex Media Server on your network

📦 **Why Use This?**  
This app is designed for individuals who use Plex as a personal media server to catalog and enjoy their legally acquired digital media — including backups of physical media like DVDs and Blu-rays. It supports better curation, discoverability, and enjoyment of your existing library.

⚙️ **Features**
- Automatically group movies into collections using TMDb (optional).
- Manual entry and studio-based collection options.
- TMDb API key is optional — fallback logic supports limited use without it.
- Local config management via built-in UI (no need to edit files manually).

🛠️ **Setup**
1. Clone the repository.
2. Ensure your Python environment is ready and install dependencies from `requirements.txt`.

```bash
pip install -r requirements.txt
```

3. Run `main.py` and follow the prompts.

```bash
python main.py
```

This project was developed as part of a software development assignment and is intended for educational and personal use only.