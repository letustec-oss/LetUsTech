<div align="center">

```
██████╗ ██╗   ██╗██╗     ██╗  ██╗    ███████╗███╗   ███╗ █████╗ ██╗██╗     
██╔══██╗██║   ██║██║     ██║ ██╔╝    ██╔════╝████╗ ████║██╔══██╗██║██║     
██████╔╝██║   ██║██║     █████╔╝     █████╗  ██╔████╔██║███████║██║██║     
██╔══██╗██║   ██║██║     ██╔═██╗     ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║     
██████╔╝╚██████╔╝███████╗██║  ██╗    ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗
╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
```

**Email Tools Suite** — Free, open source, offline-first

[![Release](https://img.shields.io/github/v/release/letustec-oss/LetUsTech?label=latest&color=00e676)](https://github.com/letustec-oss/LetUsTech/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/letustec-oss/LetUsTech/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![LetUsTech](https://img.shields.io/badge/made%20by-LetUsTech-00e676)](https://letustech.uk)

</div>

---

## 📦 What's Included

| Tool | Description |
|------|-------------|
| `BulkEmailSender.exe` | Send personalised bulk emails via your own email account |
| `EmailCSVMaker.exe` | Build and manage your contact lists with custom fields |

Both tools work together — build your list in the CSV Maker and launch straight into the Email Sender with one click.

---

## ⬇️ Download

**[→ Download Latest Release](https://github.com/letustec-oss/LetUsTech/releases/latest)**

1. Download `LetUsTech_Email_Tools_Windows.zip`
2. Extract the zip
3. Run either `.exe` — no installation, no Python needed

> **Windows 10 / 11 only.** Both files must stay in the same folder.

---

## ✨ Features

### Bulk Email Sender
- 📧 Send to unlimited contacts via your own Gmail, Outlook, or any SMTP provider
- 🏷️ **Merge tags** — personalise every email with `{{first_name}}`, `{{company}}` etc.
- 📋 **18 pre-built templates** — cold outreach, follow-up, newsletter, invoice reminder and more
- 🔍 **Tag Inspector** — preview exactly how each contact's email will look before sending
- ✏️ **Rich text editor** — bold, italic, font size, colours, bullet lists, alignment
- 🔴 **Spell checker** — live red underlines, click to see suggestions
- 🎨 **6 themes** — LetUsTech Green, Midnight Blue, Crimson, Purple Haze, Amber Terminal, Light Mode
- 🔒 **Encrypted credentials** — your app password is never stored in plain text
- 📊 **Live send log** — real-time progress with sent/failed counts
- 🔁 **Auto-reconnect** — recovers from dropped connections mid-campaign

### Email CSV Maker
- ➕ Add contacts manually or paste in bulk
- 🏷️ Tag reference panel — see exactly which `{{tags}}` match your columns
- 🔧 Custom fields — add phone, company, or any field you need
- ✅ Email validation — invalid addresses highlighted in red
- 📥 Import / export CSV — works with any existing spreadsheet
- ▶️ **One-click launch** — opens Email Sender with contacts pre-loaded

---

## 🚀 Quick Start

### 1. Set up Gmail (first time only)

Gmail requires an **App Password** — not your normal password:

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. **Security** → **2-Step Verification** (must be ON)
3. Search **"App Passwords"** → Generate one for Mail
4. Copy the 16-character password

Then in the Email Sender:
- Click **⚙ Settings** → **📧 SMTP tab**
- Click **Use** next to Gmail (auto-fills host/port)
- Enter your Gmail address and App Password
- Click **Test Connection** → **Save All Settings**

### 2. Build your contact list

Open `EmailCSVMaker.exe`:
- Add contacts manually or paste a list
- Add custom fields (phone, company, location etc.)
- Click **▶ Open in Email Sender**

Or import an existing `.csv` directly in the Email Sender.

### 3. Write and send

- Pick a **Template** or write from scratch
- Use merge tags to personalise — the tag panel shows all available tags
- Use **🔍 Tag Inspector** to preview each contact's email
- Hit **▶ SEND CAMPAIGN**

---

## 🏷️ Merge Tags Reference

| Tag | What it inserts |
|-----|----------------|
| `{{first_name}}` | Contact's first name (from CSV) |
| `{{email}}` | Contact's email address |
| `{{company}}` | Contact's company (from CSV) |
| `{{company_name}}` | Your company name (from Settings) |
| `{{sender_name}}` | Your name (from Settings) |
| `{{sender_role}}` | Your job title (from Settings) |
| `{{signature}}` | Your email signature (from Settings) |
| `{{company_website}}` | Your website (from Settings) |
| `{{any_csv_column}}` | Any column name from your CSV |

Tags are **case-insensitive** — `{{First_Name}}` and `{{first_name}}` both work.

---

## ⚙️ SMTP Provider Settings

| Provider | Host | Port | Security |
|----------|------|------|----------|
| Gmail | `smtp.gmail.com` | 587 | STARTTLS |
| Outlook / Hotmail | `smtp.office365.com` | 587 | STARTTLS |
| Yahoo | `smtp.mail.yahoo.com` | 587 | STARTTLS |
| iCloud | `smtp.mail.me.com` | 587 | STARTTLS |
| Zoho | `smtp.zoho.com` | 587 | STARTTLS |

These are also listed inside the app under Settings → SMTP with one-click **Use** buttons.

---

## 🔒 Privacy & Security

- App passwords are **encrypted** using a machine-specific key — never stored in plain text
- Config file (`.letustech_email_config.enc`) cannot be read on another machine
- No data is sent to LetUsTech — everything runs locally on your machine
- Use **Settings → 🔒 Privacy** to clear saved credentials or wipe all data

---

## 🛠️ Build From Source

Requires Python 3.10+

```bash
# Install dependencies
pip install customtkinter pyspellchecker pillow cryptography pyinstaller

# Build both tools
build.bat        # Windows
./build.sh       # Mac / Linux
```

Output files appear in `LetUsTech_Email_Tools\`

---

## 📁 File Structure

```
letustech-email-tools/
  ├── BulkEmailSender.py        # Main email sending app
  ├── email_csv_maker.py        # Contact list builder
  ├── build.bat                 # Windows build script
  ├── build.sh                  # Mac/Linux build script
  ├── README.md
  ├── .gitignore
  └── .github/
      └── workflows/
          └── build_email_tools.yml   # Auto-build on GitHub Actions
```

---

## 📝 Changelog

### email-v1.0.0
- Initial release
- Bulk Email Sender with full SMTP support
- Email CSV Maker with tag reference panel
- 18 email templates
- Spell checker with click-to-fix suggestions
- Tag Inspector for previewing personalised emails
- Encrypted credential storage
- 6 UI themes
- Settings window with Company, SMTP, Defaults, Branding and Privacy tabs
- GitHub Actions auto-build

---

<div align="center">

Made with ❤️ by **[LetUsTech](https://letustech.uk)** — Free tools for everyone

</div>
