# 🛡️ Telegram Auto-Rejection Userbot

Telegram Userbot that **automatically detects and rejects** any channel/group ownership transfers to your account — protecting you from malicious transfer attacks in real-time.

---

## ⚡ How It Works

1. The bot runs on your personal Telegram account using **Pyrogram** (Userbot mode)
2. It monitors incoming private messages for ownership transfer notifications
3. When a transfer is detected, it **instantly clicks the rejection button** (within milliseconds)
4. All rejections are logged to `rejections.json` for your records

---

## 📋 Prerequisites

- **Python 3.8+**
- A Telegram account
- API credentials from [my.telegram.org/apps](https://my.telegram.org/apps):
  - `API_ID`
  - `API_HASH`

---

## 🚀 Installation & Setup

### On Laptop/PC

```bash
# 1. Clone or download this project
git clone <your-repo-url>
cd telegram-auto-rejection-userbot

# 2. Create virtual environment
python -m venv env

# 3. Activate it
# Windows:
env\Scripts\activate
# Mac/Linux:
source env/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the bot
python main.py
```

### On Pydroid3 (Android)

1. Open Pydroid3
2. Install packages: `pip install pyrogram tgcrypto`
3. Copy `main.py` and `requirements.txt` to your project folder
4. Run `main.py`
5. Follow the setup prompts

---

## ⚙️ First Run

On first launch, the bot will ask for your credentials:

```
Bot initialized. Configuration not found.
Enter API_ID: <your api id>
Enter API_HASH: <your api hash>
Enter your phone number (with country code): +966xxxxxxxxx
```

Telegram will send you an OTP code. Enter it when prompted.
Your credentials are saved to `config.json` — subsequent runs will auto-login.

---

## 📊 Monitoring

While running, the bot displays:

```
[2025-05-05 10:15:30] ✅ Authenticated as: @yourusername
[2025-05-05 10:15:35] 🛡️ Monitoring active — watching for ownership transfers...
[2025-05-05 10:30:45] ⚠️ OWNERSHIP TRANSFER DETECTED!
[2025-05-05 10:30:45] [REJECTION] ✅ Channel: "Some Channel", Reaction: 120ms, Status: SUCCESS
[2025-05-05 10:30:46] Rejection logged to rejections.json
```

Every 5 minutes, a status heartbeat is printed showing uptime and rejection count.

---

## 📁 Project Structure

```
woner/
├── main.py              # Main bot code
├── config.json          # Credentials (auto-generated, DO NOT share)
├── rejections.json      # Rejection history (auto-generated)
├── requirements.txt     # Python dependencies
├── bot.log              # Detailed log file
├── README.md            # This file
└── .gitignore           # Protects sensitive files
```

---

## 🔐 Security Notes

- `config.json` contains your API credentials — **never share it**
- `.session` files contain your login tokens — **never share them**
- The `.gitignore` is configured to exclude all sensitive files from git

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `API ID not valid` | Verify credentials at [my.telegram.org/apps](https://my.telegram.org/apps) |
| Bot stops after hours | On Pydroid3: enable "Run in Background", disable battery saver |
| Rejection button not detected | Update Pyrogram: `pip install --upgrade pyrogram` |
| `rejections.json` not updating | Check file permissions and console for I/O errors |

---

## 📝 License

Personal use only. Not intended for distribution.
