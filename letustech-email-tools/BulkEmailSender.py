#!/usr/bin/env python3
"""
Bulk Email Sender — LetUsTech
Themes + Help section update
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import csv, smtplib, ssl, threading, time, json, re, sys, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path

try:
    from spellchecker import SpellChecker
    _SPELL_AVAILABLE = True
except ImportError:
    _SPELL_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    import hashlib, base64
    _CRYPTO_AVAILABLE = True
except ImportError:
    _CRYPTO_AVAILABLE = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ── Themes ─────────────────────────────────────────────────────────────────
THEMES = {
    "LetUsTech (Green)": {
        "accent":      "#00e676",
        "accent_dim":  "#00b359",
        "bg_main":     "#0b0e14",
        "bg_card":     "#111620",
        "bg_input":    "#0d1119",
        "bg_sidebar":  "#0e1118",
        "text_main":   "#e8eaf0",
        "text_dim":    "#6b7280",
        "border":      "#1e2533",
    },
    "Midnight Blue": {
        "accent":      "#4d9fff",
        "accent_dim":  "#2d7fdf",
        "bg_main":     "#090c14",
        "bg_card":     "#0e1525",
        "bg_input":    "#0a1020",
        "bg_sidebar":  "#0b1220",
        "text_main":   "#dce8ff",
        "text_dim":    "#5a7299",
        "border":      "#1a2840",
    },
    "Crimson": {
        "accent":      "#ff4466",
        "accent_dim":  "#cc2244",
        "bg_main":     "#120a0c",
        "bg_card":     "#1e0f13",
        "bg_input":    "#160b0e",
        "bg_sidebar":  "#180c10",
        "text_main":   "#f0dde0",
        "text_dim":    "#8a5560",
        "border":      "#2e1520",
    },
    "Purple Haze": {
        "accent":      "#b066ff",
        "accent_dim":  "#8844dd",
        "bg_main":     "#0d0b14",
        "bg_card":     "#160f22",
        "bg_input":    "#110c1c",
        "bg_sidebar":  "#130e1e",
        "text_main":   "#e8dff5",
        "text_dim":    "#6b5580",
        "border":      "#251840",
    },
    "Amber Terminal": {
        "accent":      "#ffaa00",
        "accent_dim":  "#cc8800",
        "bg_main":     "#0e0c08",
        "bg_card":     "#181408",
        "bg_input":    "#130f06",
        "bg_sidebar":  "#151108",
        "text_main":   "#f5e8c0",
        "text_dim":    "#80700a",
        "border":      "#2a2210",
    },
    "Light Mode": {
        "accent":      "#00a855",
        "accent_dim":  "#007a3d",
        "bg_main":     "#f4f6fa",
        "bg_card":     "#ffffff",
        "bg_input":    "#eef0f5",
        "bg_sidebar":  "#e8eaf0",
        "text_main":   "#1a1d26",
        "text_dim":    "#5a6070",
        "border":      "#d0d4e0",
    },
}

RED    = "#ff4444"
ORANGE = "#ff9800"

# ── Email Templates ─────────────────────────────────────────────────────────
EMAIL_TEMPLATES = {
    "── Pick a template ──": None,

    "👋  Cold Outreach": {
        "subject": "Quick question, {{first_name}}",
        "body": (
            "Hi {{first_name}},\n\n"
            "I came across {{company}} and wanted to reach out — "
            "I think there could be a really interesting opportunity for us to work together.\n\n"
            "I'll keep this short: we help businesses like yours with [what you do]. "
            "Would you be open to a quick 15-minute call this week?\n\n"
            "Let me know either way — no pressure at all.\n\n"
            "Best,\n{{sender_name}}"
        ),
    },

    "📣  Product Announcement": {
        "subject": "{{first_name}}, something new just dropped 🚀",
        "body": (
            "Hi {{first_name}},\n\n"
            "Exciting news — we've just launched [Product Name]!\n\n"
            "Here's what's new:\n"
            "  • [Feature 1]\n"
            "  • [Feature 2]\n"
            "  • [Feature 3]\n\n"
            "We built this with people like you in mind, and we'd love for you to be "
            "one of the first to try it.\n\n"
            "👉 [Link to product]\n\n"
            "As always, reply to this email if you have any questions.\n\n"
            "Thanks,\n{{sender_name}}"
        ),
    },

    "🎉  Welcome Email": {
        "subject": "Welcome to the team, {{first_name}}!",
        "body": (
            "Hi {{first_name}},\n\n"
            "Welcome aboard! We're really glad to have you with us.\n\n"
            "Here are a few things to get you started:\n"
            "  1. [Step one — e.g. set up your account]\n"
            "  2. [Step two — e.g. join our community]\n"
            "  3. [Step three — e.g. check out our docs]\n\n"
            "If you ever need help, just hit reply — we're always here.\n\n"
            "Looking forward to having you along for the ride.\n\n"
            "Cheers,\n{{sender_name}}"
        ),
    },

    "🔁  Follow Up": {
        "subject": "Following up, {{first_name}}",
        "body": (
            "Hi {{first_name}},\n\n"
            "Just following up on my last email — I wanted to make sure it didn't "
            "get buried.\n\n"
            "I know you're busy, so I'll be brief: [one line summary of your ask].\n\n"
            "Happy to work around your schedule if you'd like to chat — just let me "
            "know what works.\n\n"
            "Thanks,\n{{sender_name}}"
        ),
    },

    "🛒  Promotional Offer": {
        "subject": "{{first_name}}, here's something just for you 🎁",
        "body": (
            "Hi {{first_name}},\n\n"
            "As a valued contact, we wanted to give you early access to our latest offer:\n\n"
            "  [Offer headline — e.g. 20% off all plans this week only]\n\n"
            "Use code: [YOURCODE] at checkout.\n\n"
            "This offer expires on [date], so don't wait too long!\n\n"
            "👉 [Link to offer]\n\n"
            "Questions? Just reply to this email.\n\n"
            "Cheers,\n{{sender_name}}"
        ),
    },

    "📋  Event Invitation": {
        "subject": "You're invited, {{first_name}} 🎟️",
        "body": (
            "Hi {{first_name}},\n\n"
            "We'd love to invite you to [Event Name]!\n\n"
            "📅  Date:     [Date]\n"
            "🕐  Time:     [Time]\n"
            "📍  Location: [Location / Online link]\n\n"
            "[Short description of the event and why they should come.]\n\n"
            "Spots are limited, so grab yours here:\n"
            "👉 [RSVP link]\n\n"
            "Hope to see you there!\n\n"
            "Best,\n{{sender_name}}"
        ),
    },

    "💬  Feedback Request": {
        "subject": "Quick question for you, {{first_name}}",
        "body": (
            "Hi {{first_name}},\n\n"
            "I hope everything's going well!\n\n"
            "We're always looking to improve and your opinion genuinely matters to us. "
            "Would you be willing to spare 2 minutes to answer a quick question?\n\n"
            "[Question or link to survey]\n\n"
            "Your honest feedback helps us build something better for everyone.\n\n"
            "Thanks so much,\n{{sender_name}}"
        ),
    },

    "⚠️  Re-engagement": {
        "subject": "We miss you, {{first_name}}",
        "body": (
            "Hi {{first_name}},\n\n"
            "We noticed it's been a while since we last heard from you — and we wanted "
            "to check in.\n\n"
            "A lot has changed since you last visited:\n"
            "  • [Update 1]\n"
            "  • [Update 2]\n\n"
            "We'd love to have you back. Click below to see what's new:\n"
            "👉 [Link]\n\n"
            "And if there's anything we could do better, just hit reply — we read every "
            "message.\n\n"
            "Hope to see you soon,\n{{sender_name}}"
        ),
    },

    "🤝  Partnership Proposal": {
        "subject": "Partnership opportunity — {{company}} × [Your Company]",
        "body": (
            "Hi {{first_name}},\n\n"
            "I've been following {{company}} for a while and I think there's a genuine "
            "opportunity for us to work together.\n\n"
            "We specialise in [what you do], and based on what I've seen from {{company}}, "
            "I believe we could [specific benefit].\n\n"
            "I'd love to set up a 20-minute call to explore whether there's a fit. "
            "Would any of the following times work for you?\n\n"
            "  • [Option 1]\n"
            "  • [Option 2]\n"
            "  • [Option 3]\n\n"
            "Looking forward to hearing from you.\n\n"
            "Best,\n{{sender_name}}\n{{company_name}}"
        ),
    },

    "🎓  Course / Training Invite": {
        "subject": "{{first_name}}, you're invited to [Course Name]",
        "body": (
            "Hi {{first_name}},\n\n"
            "We're running [Course Name] and we'd love to have you join us.\n\n"
            "📚  What you'll learn:\n"
            "  • [Topic 1]\n"
            "  • [Topic 2]\n"
            "  • [Topic 3]\n\n"
            "📅  Starts: [Start Date]\n"
            "⏱️  Duration: [Duration]\n"
            "💻  Format: [Online / In-person]\n"
            "💰  Price: [Price / Free]\n\n"
            "👉 Secure your spot: [Link]\n\n"
            "Spaces are limited — don't miss out.\n\n"
            "Best,\n{{sender_name}}\n{{company_name}}"
        ),
    },

    "🛠️  Service Check-in": {
        "subject": "How's everything going, {{first_name}}?",
        "body": (
            "Hi {{first_name}},\n\n"
            "Just wanted to check in and make sure everything is running smoothly "
            "on your end.\n\n"
            "It's been [time period] since we [last worked together / you signed up], "
            "and we want to make sure you're getting the most out of [product/service].\n\n"
            "A few things that might help:\n"
            "  • [Tip or feature 1]\n"
            "  • [Tip or feature 2]\n\n"
            "If you ever have questions or need anything, just hit reply — we're always "
            "happy to help.\n\n"
            "Best,\n{{sender_name}}\n{{company_name}}"
        ),
    },

    "🎂  Birthday / Special Occasion": {
        "subject": "Happy [Occasion], {{first_name}} 🎉",
        "body": (
            "Hi {{first_name}},\n\n"
            "We just wanted to take a moment to wish you a wonderful [Birthday / Anniversary]!\n\n"
            "As a little thank you for being part of our community, we've got something "
            "special for you:\n\n"
            "  🎁  [Gift / Offer / Discount code]\n\n"
            "Valid until [Expiry Date] — just our way of saying thank you.\n\n"
            "Hope you have a brilliant day!\n\n"
            "Warm regards,\n{{sender_name}}\n{{company_name}}"
        ),
    },

    "📦  Order / Delivery Update": {
        "subject": "Your order update, {{first_name}}",
        "body": (
            "Hi {{first_name}},\n\n"
            "Great news — your order is [on its way / ready / confirmed]!\n\n"
            "📦  Order: [Order Number]\n"
            "📅  Date: [Order Date]\n"
            "🚚  Status: [Status]\n"
            "📍  Delivery: [Expected Date / Location]\n\n"
            "You can track your order here:\n"
            "👉 [Tracking Link]\n\n"
            "If you have any questions, reply to this email and we'll get back to you "
            "as soon as possible.\n\n"
            "Thanks for your order!\n\n"
            "{{sender_name}}\n{{company_name}}"
        ),
    },

    "⭐  Review Request": {
        "subject": "How did we do, {{first_name}}?",
        "body": (
            "Hi {{first_name}},\n\n"
            "Thank you for [buying / using / choosing] [Product/Service] — we really "
            "appreciate it!\n\n"
            "We'd love to know what you thought. Could you spare 60 seconds to leave "
            "us a review?\n\n"
            "👉 [Review Link]\n\n"
            "Honest feedback helps us improve and helps other customers make the right "
            "choice. It means a lot to us.\n\n"
            "Thanks so much,\n{{sender_name}}\n{{company_name}}"
        ),
    },

    "📰  Newsletter": {
        "subject": "[Month] Update from {{company_name}}",
        "body": (
            "Hi {{first_name}},\n\n"
            "Here's what's been happening at {{company_name}} this month:\n\n"
            "🔥  HIGHLIGHTS\n"
            "  • [Highlight 1]\n"
            "  • [Highlight 2]\n"
            "  • [Highlight 3]\n\n"
            "📣  ANNOUNCEMENTS\n"
            "[Announcement text here]\n\n"
            "🔗  USEFUL LINKS\n"
            "  • [Link 1 — description]\n"
            "  • [Link 2 — description]\n\n"
            "That's all for this month. As always, reply to this email if you have "
            "any questions or feedback.\n\n"
            "Best,\n{{sender_name}}\n{{company_name}}"
        ),
    },

    "💰  Payment / Invoice Reminder": {
        "subject": "Invoice reminder — {{company}}, ref [Invoice No.]",
        "body": (
            "Hi {{first_name}},\n\n"
            "I hope you're well. This is a friendly reminder that invoice [Invoice No.] "
            "for [Amount] is [due today / now overdue].\n\n"
            "📄  Invoice: [Invoice Number]\n"
            "💷  Amount: [Amount]\n"
            "📅  Due Date: [Due Date]\n"
            "🔗  Pay here: [Payment Link]\n\n"
            "If payment has already been made, please disregard this message.\n\n"
            "If you have any questions or need to discuss payment terms, just reply "
            "to this email.\n\n"
            "Many thanks,\n{{sender_name}}\n{{company_name}}"
        ),
    },

    "🚀  Product Launch": {
        "subject": "It's here, {{first_name}} — [Product Name] is live 🚀",
        "body": (
            "Hi {{first_name}},\n\n"
            "After [time period] of work, we're incredibly excited to announce that "
            "[Product Name] is officially live!\n\n"
            "✨  [One-line description of the product]\n\n"
            "Here's what makes it special:\n"
            "  🔥  [Key feature 1]\n"
            "  ⚡  [Key feature 2]\n"
            "  💎  [Key feature 3]\n\n"
            "As one of our early contacts, you get [exclusive access / a special discount / "
            "early bird pricing]:\n\n"
            "👉 [CTA Link] — [Offer details]\n\n"
            "This offer is only available until [Date], so don't wait.\n\n"
            "Thank you for your support — we built this with people like you in mind.\n\n"
            "With excitement,\n{{sender_name}}\n{{company_name}}"
        ),
    },
}
FONT_HEAD  = ("Courier New", 15, "bold")
FONT_MONO  = ("Courier New", 13)
FONT_SMALL = ("Courier New", 12)
FONT_LABEL = ("Courier New", 13, "bold")

CONFIG_FILE  = Path.home() / ".letustech_email_config.enc"
CONFIG_FILE_LEGACY = Path.home() / ".letustech_email_config.json"

# ── Encryption helpers ──────────────────────────────────────────────────────
# Key is derived from a machine-specific value so config can't just be
# copied to another machine and read. Nothing is stored in plain text.
SENSITIVE_KEYS = {"pass", "user", "host"}  # fields to always encrypt

def _get_key() -> bytes:
    """Derive a stable Fernet key from a machine identifier."""
    import uuid
    machine_id = str(uuid.getnode()).encode()
    digest = hashlib.sha256(machine_id + b"letustech-v1").digest()
    return base64.urlsafe_b64encode(digest)

def load_config() -> dict:
    # Migrate legacy plain-text config if it exists
    if CONFIG_FILE_LEGACY.exists() and not CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE_LEGACY.read_text())
            save_config(data)
            CONFIG_FILE_LEGACY.unlink()  # remove old plain-text file
        except Exception:
            pass

    if not CONFIG_FILE.exists():
        return {}
    try:
        raw = CONFIG_FILE.read_bytes()
        if _CRYPTO_AVAILABLE:
            f    = Fernet(_get_key())
            data = json.loads(f.decrypt(raw).decode())
        else:
            # Fallback: base64 only (obfuscation, not true encryption)
            data = json.loads(base64.b64decode(raw).decode())
        return data
    except Exception:
        return {}

def save_config(data: dict):
    try:
        payload = json.dumps(data, indent=2).encode()
        if _CRYPTO_AVAILABLE:
            f   = Fernet(_get_key())
            out = f.encrypt(payload)
        else:
            out = base64.b64encode(payload)
        CONFIG_FILE.write_bytes(out)
    except Exception:
        pass

HELP_CONTENT = {
    "Getting Started": """
WELCOME TO BULK EMAIL SENDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This tool lets you send personalised emails to a list of contacts
imported from a CSV file.

QUICK START:
  1. Fill in your SMTP settings on the left panel
  2. Click "Test Connection" to verify your credentials
  3. Import a CSV file containing your contacts
  4. Write your subject and body in the composer
  5. Click "> SEND CAMPAIGN"

PERSONALISATION:
  Use {{column_name}} in your subject or body to insert
  data from your CSV automatically per contact.

  Example:  Hi {{first_name}}, thanks for joining {{company}}!

  The "Insert Tag" button shows all available columns
  from your loaded CSV.
""",
    "SMTP Setup": """
SMTP CONFIGURATION GUIDE
━━━━━━━━━━━━━━━━━━━━━━━━

SMTP is how the app connects to your email provider to send mail.

COMMON PROVIDERS:
  Gmail           smtp.gmail.com          Port 587  STARTTLS
  Outlook/Hotmail smtp.office365.com      Port 587  STARTTLS
  Yahoo Mail      smtp.mail.yahoo.com     Port 587  STARTTLS
  iCloud Mail     smtp.mail.me.com        Port 587  STARTTLS
  Zoho Mail       smtp.zoho.com           Port 587  STARTTLS

GMAIL APP PASSWORD (required):
  Gmail won't let apps use your real password.
  You need a special "App Password":

  1. Go to myaccount.google.com
  2. Security > 2-Step Verification (must be ON)
  3. Scroll down > App Passwords
  4. Select "Mail" > Generate
  5. Copy the 16-character password into this app

  Never share your app password with anyone.

CLICK "Save SMTP Settings" to remember your config
between sessions.
""",
    "CSV Format": """
CSV FILE FORMAT
━━━━━━━━━━━━━━━

Your CSV must have at least one column with "email" in the name.
All other columns are optional but can be used for personalisation.

MINIMUM REQUIRED:
  email
  alice@example.com
  bob@example.com

RECOMMENDED FORMAT:
  email, first_name, last_name, company
  alice@example.com, Alice, Smith, Acme Ltd
  bob@example.com, Bob, Jones, Beta Corp

TIPS:
  - Column names become your {{tags}} in the email template
  - Invalid email addresses are skipped automatically
  - UTF-8 encoding is recommended for special characters
  - Download a sample CSV using the button in the left panel

PERSONALISATION EXAMPLE:
  Subject: Hi {{first_name}}, your update from {{company}}
  Body:    Hello {{first_name}} {{last_name}},
           We have an update for you at {{company}}...
""",
    "Sending Tips": """
SENDING BEST PRACTICES
━━━━━━━━━━━━━━━━━━━━━━

AVOID SPAM FILTERS:
  - Use a delay of 1-3 seconds between emails
  - Keep sending volume under 500/day for Gmail free
  - Always include an unsubscribe note in your body
  - Avoid ALL CAPS in subject lines
  - Don't use too many links or images

DAILY SENDING LIMITS:
  Gmail (free):    500/day
  Gmail Workspace: 2,000/day
  Outlook:         300/day
  Zoho (free):     50/day

HTML EMAILS:
  Toggle "Send as HTML" in Options to send rich HTML.
  Your body text will be treated as raw HTML — use
  proper <p>, <b>, <a href="..."> tags etc.

ATTACHMENTS:
  Click the + button to attach a file.
  All contacts will receive the same attachment.

LOGGING:
  Enable "Log sent to file" to save a CSV record of
  sent/failed emails to your home folder.

STOP BUTTON:
  Use "STOP" to safely halt mid-campaign. The current
  email will finish before stopping.
""",
    "Themes": """
THEMES
━━━━━━

Use the theme selector in the top bar to change the
colour scheme of the application.

AVAILABLE THEMES:
  - LetUsTech (Green)  default dark green terminal look
  - Midnight Blue      deep navy with blue accents
  - Crimson            dark red / rose aesthetic
  - Purple Haze        dark purple with violet accents
  - Amber Terminal     classic amber-on-black terminal
  - Light Mode         clean light theme

Your selected theme is saved automatically and will be
remembered next time you open the app.

NOTE: A restart is required to fully apply a new theme.
""",
    "Troubleshooting": """
TROUBLESHOOTING
━━━━━━━━━━━━━━━

CONNECTION FAILED:
  - Check host, port, and security settings
  - For Gmail: use an App Password, not your real password
  - Check your internet connection
  - Some networks block SMTP ports

EMAILS NOT ARRIVING:
  - Check spam / junk folder
  - Verify recipient addresses in your CSV
  - Try sending to yourself first as a test
  - Your IP may be on a blocklist if sending high volumes

CSV IMPORT ERRORS:
  - Save the file as UTF-8 CSV
  - Ensure there's a column with "email" in the name
  - Check for extra blank rows

APP WON'T START:
  - Make sure Python 3.10+ is installed
  - Run: pip install customtkinter
  - On Mac/Linux: pip3 install customtkinter

STILL STUCK?
  Visit letustech.uk or email letustec@gmail.com
""",
}

# ── Helpers ─────────────────────────────────────────────────────────────────
def validate_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email.strip()))

def personalise(template, row, config=None):
    # Build a case-insensitive lookup of the row
    row_lower = {k.lower().strip(): v for k, v in row.items()}

    # Inject app settings as built-in tags
    if config:
        builtins = {
            "company_name":    config.get("company_name", ""),
            "sender_name":     config.get("sender_name", ""),
            "sender_role":     config.get("sender_role", ""),
            "signature":       config.get("sender_sig", ""),
            "company_website": config.get("company_website", ""),
            "company_phone":   config.get("company_phone", ""),
            "company_address": config.get("company_address", ""),
        }
        row_lower.update(builtins)
        # Auto-append footer if configured
        footer = config.get("email_footer", "").strip()
        if footer and footer not in template:
            template = template.rstrip() + f"\n\n--\n{footer}"

    def replace_tag(match):
        tag = match.group(1).strip()
        if tag in row:
            return row[tag]
        if tag.lower() in row_lower:
            return row_lower[tag.lower()]
        return match.group(0)

    return re.sub(r"\{\{([^}]+)\}\}", replace_tag, template)

# ══════════════════════════════════════════════════════════════════════════
class BulkEmailApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Bulk Email Sender — LetUsTech")
        self.geometry("1220x820")
        self.minsize(1000, 680)

        self._config      = load_config()
        self._contacts    = []
        self._csv_headers = []
        self._attachment  = None
        self._sending     = False
        self._stop_flag   = threading.Event()

        saved_theme = self._config.get("theme", "LetUsTech (Green)")
        self._theme_name = saved_theme if saved_theme in THEMES else "LetUsTech (Green)"
        self._t = THEMES[self._theme_name]

        self.configure(fg_color=self._t["bg_main"])
        self._build_ui()
        self._restore_smtp()

        # Auto-load CSV if launched from CSV Maker with --load-csv path
        args = sys.argv[1:]
        if "--load-csv" in args:
            idx = args.index("--load-csv")
            if idx + 1 < len(args):
                csv_path = args[idx + 1]
                if os.path.exists(csv_path):
                    self.after(300, lambda: self._load_csv_path(csv_path))

    # ── Theme ──────────────────────────────────────────────────────────────

    def _apply_theme(self, name):
        self._theme_name = name
        self._t = THEMES[name]
        cfg = self._config
        cfg["theme"] = name
        save_config(cfg)
        messagebox.showinfo("Theme Changed",
            f'Theme set to "{name}".\n\nRestart the app to apply fully.')

    # ── UI ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        t = self._t

        # Top bar
        topbar = ctk.CTkFrame(self, fg_color=t["bg_sidebar"],
                               corner_radius=0, height=56)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        ctk.CTkLabel(topbar, text="⬡", font=("Courier New", 22, "bold"),
                     text_color=t["accent"]).pack(side="left", padx=(18, 4))
        company = self._config.get("company_name", "LETUSTECH")
        self._company_lbl = ctk.CTkLabel(topbar, text=company.upper(),
                     font=("Courier New", 15, "bold"),
                     text_color=t["accent"])
        self._company_lbl.pack(side="left")
        ctk.CTkLabel(topbar, text="/ BULK EMAIL SENDER",
                     font=FONT_MONO,
                     text_color=t["text_dim"]).pack(side="left", padx=(4, 0))

        self._theme_var = ctk.StringVar(value=self._theme_name)
        ctk.CTkOptionMenu(topbar,
                          variable=self._theme_var,
                          values=list(THEMES.keys()),
                          fg_color=t["bg_input"],
                          button_color=t["accent_dim"],
                          dropdown_fg_color=t["bg_card"],
                          text_color=t["text_main"],
                          font=FONT_SMALL, width=185,
                          command=self._apply_theme,
                          ).pack(side="right", padx=(4, 14), pady=10)
        ctk.CTkLabel(topbar, text="Theme:", font=FONT_SMALL,
                     text_color=t["text_dim"]).pack(side="right")

        ctk.CTkButton(topbar, text="⚙ Settings", font=FONT_SMALL,
                      fg_color="transparent", border_color=t["border"],
                      border_width=1, text_color=t["text_dim"],
                      hover_color=t["bg_card"], width=90,
                      command=self._open_settings
                      ).pack(side="right", padx=(0, 6), pady=10)

        ctk.CTkButton(topbar, text="? Help", font=FONT_SMALL,
                      fg_color="transparent", border_color=t["border"],
                      border_width=1, text_color=t["text_dim"],
                      hover_color=t["bg_card"], width=70,
                      command=self._open_help
                      ).pack(side="right", padx=(0, 6), pady=10)

        self._status_dot = ctk.CTkLabel(topbar, text="●  IDLE",
                                         font=FONT_SMALL,
                                         text_color=t["text_dim"])
        self._status_dot.pack(side="right", padx=10)

        # Body columns
        body = ctk.CTkFrame(self, fg_color=t["bg_main"])
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left  = ctk.CTkFrame(body, fg_color=t["bg_sidebar"], corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        right = ctk.CTkFrame(body, fg_color=t["bg_main"], corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        self._build_left(left)
        self._build_right(right)

    # ── Left panel ─────────────────────────────────────────────────────────

    def _build_left(self, parent):
        t = self._t

        self._left_scroll = ctk.CTkScrollableFrame(
            parent, fg_color=t["bg_sidebar"],
            scrollbar_button_color=t["border"],
            scrollbar_button_hover_color=t["accent_dim"])
        self._left_scroll.pack(fill="both", expand=True)
        scroll = self._left_scroll

        # ── Helper: build one accordion section ───────────────────────────
        def accordion(title, pill_text=""):
            """Returns (header_frame, body_frame, toggle_btn, pill_label, state_dict)."""
            state = {"open": False}

            outer = ctk.CTkFrame(scroll, fg_color=t["bg_card"], corner_radius=8)
            outer.pack(fill="x", padx=12, pady=(10, 0))

            btn = ctk.CTkButton(
                outer, text=f"▶  {title}",
                font=FONT_LABEL, fg_color="transparent",
                text_color=t["accent"], hover_color=t["bg_input"],
                anchor="w")
            btn.pack(fill="x", padx=4, pady=(6, 2))

            pill = ctk.CTkLabel(outer, text=pill_text,
                                font=FONT_SMALL, text_color=t["text_dim"])
            pill.pack(anchor="w", padx=14, pady=(0, 8))

            # body lives OUTSIDE outer so it can be shown/hidden cleanly
            body = ctk.CTkFrame(scroll, fg_color=t["bg_card"],
                                corner_radius=0,
                                border_width=0)

            def toggle(s=state, b=btn, p=pill, bd=body, ttl=title):
                s["open"] = not s["open"]
                if s["open"]:
                    # Insert body immediately after outer in the scroll frame
                    outer.pack_configure()
                    bd.pack(fill="x", padx=12)
                    b.configure(text=f"▼  {ttl}")
                    p.pack_forget()
                else:
                    bd.pack_forget()
                    b.configure(text=f"▶  {ttl}")
                    p.pack(anchor="w", padx=14, pady=(0, 8))

            btn.configure(command=toggle)
            state["toggle"] = toggle
            return outer, body, btn, pill, state

        # ── SMTP status card (opens Settings > SMTP tab) ──────────────────
        smtp_card = ctk.CTkFrame(scroll, fg_color=t["bg_card"], corner_radius=8)
        smtp_card.pack(fill="x", padx=12, pady=(14, 0))

        smtp_top = ctk.CTkFrame(smtp_card, fg_color="transparent")
        smtp_top.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(smtp_top, text="SMTP", font=FONT_LABEL,
                     text_color=t["accent"]).pack(side="left")
        ctk.CTkButton(smtp_top, text="Configure ▶", font=FONT_SMALL,
                      fg_color=t["accent_dim"], text_color="#000",
                      hover_color=t["accent"], width=110,
                      command=lambda: self._open_settings(tab="smtp")
                      ).pack(side="right")

        self._smtp_status_label = ctk.CTkLabel(
            smtp_card, text="Not configured — click Configure",
            font=FONT_SMALL, text_color=t["text_dim"])
        self._smtp_status_label.pack(anchor="w", padx=12, pady=(0, 10))

        # dummy hidden widgets so _restore_smtp and _get_smtp still work
        _hidden = ctk.CTkFrame(self, fg_color="transparent", width=0, height=0)
        self._smtp_outer      = smtp_card
        self._smtp_open_state = {"open": False}
        self._smtp_body       = _hidden   # not used visually any more

        # Build the actual entry widgets (hidden off-screen — values read by _get_smtp)
        self._smtp_host = ctk.CTkEntry(_hidden, font=FONT_SMALL)
        self._smtp_port = ctk.CTkEntry(_hidden, font=FONT_SMALL)
        self._smtp_user = ctk.CTkEntry(_hidden, font=FONT_SMALL)
        self._smtp_pass = ctk.CTkEntry(_hidden, font=FONT_SMALL, show="*")
        self._tls_var   = ctk.StringVar(value="STARTTLS")

        # ── 2. CONTACTS ───────────────────────────────────────────────────
        contacts_outer = ctk.CTkFrame(scroll, fg_color=t["bg_card"], corner_radius=8)
        contacts_outer.pack(fill="x", padx=12, pady=(10, 0))

        self._contacts_toggle_btn = ctk.CTkButton(
            contacts_outer, text="▶  CONTACTS",
            font=FONT_LABEL, fg_color="transparent",
            text_color=t["accent"], hover_color=t["bg_input"],
            anchor="w", command=self._toggle_contacts)
        self._contacts_toggle_btn.pack(fill="x", padx=4, pady=(6, 2))

        self._contacts_status_label = ctk.CTkLabel(
            contacts_outer, text="No file loaded",
            font=FONT_SMALL, text_color=t["text_dim"])
        self._contacts_status_label.pack(anchor="w", padx=14, pady=(0, 8))

        self._contacts_outer = contacts_outer
        self._contacts_open = False
        self._contacts_body = ctk.CTkFrame(scroll, fg_color=t["bg_card"], corner_radius=0)

        self._contact_info = ctk.CTkLabel(
            self._contacts_body, text="No file loaded",
            font=FONT_SMALL, text_color=t["text_dim"])
        self._contact_info.pack(padx=20, anchor="w", pady=(12, 0))

        ctk.CTkButton(self._contacts_body, text="Import CSV", font=FONT_LABEL,
                      fg_color=t["accent"], text_color="#000",
                      hover_color=t["accent_dim"],
                      command=self._import_csv
                      ).pack(fill="x", padx=20, pady=(10, 0))
        ctk.CTkButton(self._contacts_body, text="Download Sample CSV", font=FONT_SMALL,
                      fg_color="transparent", border_color=t["border"],
                      border_width=1, text_color=t["text_dim"],
                      hover_color=t["bg_card"],
                      command=self._export_sample
                      ).pack(fill="x", padx=20, pady=(8, 0))

        # Attachment lives inside Contacts body — makes sense contextually
        ctk.CTkFrame(self._contacts_body, fg_color=t["border"], height=1
                     ).pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(self._contacts_body, text="ATTACHMENT",
                     font=FONT_LABEL, text_color=t["text_dim"]
                     ).pack(anchor="w", padx=20, pady=(0, 6))

        self._att_card = ctk.CTkFrame(self._contacts_body,
                                       fg_color=t["bg_input"], corner_radius=8)
        self._att_card.pack(fill="x", padx=20, pady=(0, 14))

        self._att_icon = ctk.CTkLabel(self._att_card, text="📎",
                                       font=("Courier New", 20),
                                       text_color=t["text_dim"])
        self._att_icon.pack(side="left", padx=(10, 6), pady=8)

        att_info = ctk.CTkFrame(self._att_card, fg_color="transparent")
        att_info.pack(side="left", fill="x", expand=True, pady=8)

        self._att_name = ctk.CTkLabel(att_info, text="No file attached",
                                       font=FONT_SMALL, text_color=t["text_dim"],
                                       anchor="w")
        self._att_name.pack(anchor="w")
        self._att_size = ctk.CTkLabel(att_info, text="Click + to attach",
                                       font=("Courier New", 10),
                                       text_color=t["border"], anchor="w")
        self._att_size.pack(anchor="w")

        att_btns = ctk.CTkFrame(self._att_card, fg_color="transparent")
        att_btns.pack(side="right", padx=6, pady=8)
        ctk.CTkButton(att_btns, text="+ Add", width=58, font=FONT_SMALL,
                      fg_color=t["accent_dim"], text_color="#000",
                      hover_color=t["accent"],
                      command=self._pick_attachment).pack(pady=(0, 4))
        self._att_remove_btn = ctk.CTkButton(
            att_btns, text="✕ Remove", width=58, font=FONT_SMALL,
            fg_color="transparent", border_color=RED, border_width=1,
            text_color=RED, hover_color="#2a0a0a",
            state="disabled", command=self._remove_attachment)
        self._att_remove_btn.pack()

        # ── 3. OPTIONS & LOG ──────────────────────────────────────────────
        options_outer = ctk.CTkFrame(scroll, fg_color=t["bg_card"], corner_radius=8)
        options_outer.pack(fill="x", padx=12, pady=(10, 0))

        self._options_toggle_btn = ctk.CTkButton(
            options_outer, text="▶  OPTIONS & LOG",
            font=FONT_LABEL, fg_color="transparent",
            text_color=t["accent"], hover_color=t["bg_input"],
            anchor="w", command=self._toggle_options)
        self._options_toggle_btn.pack(fill="x", padx=4, pady=(6, 2))

        self._options_status_label = ctk.CTkLabel(
            options_outer, text="Delay 1s · Plain text",
            font=FONT_SMALL, text_color=t["text_dim"])
        self._options_status_label.pack(anchor="w", padx=14, pady=(0, 8))

        self._options_outer = options_outer
        self._options_open = False
        self._options_body = ctk.CTkFrame(scroll, fg_color=t["bg_card"], corner_radius=0)

        delay_row = ctk.CTkFrame(self._options_body, fg_color="transparent")
        delay_row.pack(fill="x", padx=20, pady=(12, 8))
        ctk.CTkLabel(delay_row, text="Delay (secs)", font=FONT_LABEL,
                     text_color=t["text_dim"]).pack(side="left")
        self._delay_var = ctk.StringVar(value="1")
        ctk.CTkEntry(delay_row, textvariable=self._delay_var,
                     font=FONT_MONO, fg_color=t["bg_input"],
                     border_color=t["border"], width=60).pack(side="right")

        self._html_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self._options_body, text="Send as HTML",
                        variable=self._html_var, font=FONT_SMALL,
                        text_color=t["text_dim"],
                        checkmark_color=t["accent"], fg_color=t["accent_dim"],
                        border_color=t["border"]
                        ).pack(padx=20, anchor="w", pady=4)

        self._track_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self._options_body, text="Log sent to file",
                        variable=self._track_var, font=FONT_SMALL,
                        text_color=t["text_dim"],
                        checkmark_color=t["accent"], fg_color=t["accent_dim"],
                        border_color=t["border"]
                        ).pack(padx=20, anchor="w", pady=(4, 0))

        # Log widget
        log_head_row = ctk.CTkFrame(self._options_body, fg_color="transparent")
        log_head_row.pack(fill="x", padx=20, pady=(14, 4))
        ctk.CTkLabel(log_head_row, text="LOG", font=FONT_HEAD,
                     text_color=t["accent"]).pack(side="left")
        ctk.CTkButton(log_head_row, text="Clear", font=FONT_SMALL,
                      fg_color="transparent", text_color=t["text_dim"],
                      hover_color=t["bg_input"], width=50,
                      command=self._clear_log).pack(side="right")

        self._log = tk.Text(self._options_body, font=("Courier New", 12),
                             bg=t["bg_input"], fg=t["text_dim"],
                             height=10, relief="flat", bd=0,
                             state="disabled",
                             selectbackground=t["accent_dim"],
                             highlightthickness=1,
                             highlightbackground=t["border"],
                             padx=10, pady=8)
        self._log.pack(fill="x", padx=20, pady=(0, 14))
        self._log.tag_config("ok",   foreground=t["accent"])
        self._log.tag_config("err",  foreground=RED)
        self._log.tag_config("warn", foreground=ORANGE)
        self._log.tag_config("info", foreground=t["text_dim"])

        # Bottom spacer
        ctk.CTkFrame(scroll, fg_color="transparent", height=16).pack()

    # ── Right panel ────────────────────────────────────────────────────────

    def _build_right(self, parent):
        t = self._t

        comp_head = ctk.CTkFrame(parent, fg_color=t["bg_card"],
                                  corner_radius=0, height=44)
        comp_head.pack(fill="x")
        comp_head.pack_propagate(False)
        ctk.CTkLabel(comp_head, text="COMPOSE", font=FONT_HEAD,
                     text_color=t["accent"]).pack(side="left", padx=18)
        self._tag_btn = ctk.CTkButton(
            comp_head, text="Insert Tag v", font=FONT_SMALL,
            fg_color="transparent", border_color=t["border"],
            border_width=1, text_color=t["text_dim"],
            hover_color=t["bg_input"], width=110,
            command=self._show_tag_menu)
        self._tag_btn.pack(side="right", padx=(4, 10), pady=6)

        self._tpl_btn = ctk.CTkButton(
            comp_head, text="Templates", font=FONT_SMALL,
            fg_color=t["accent_dim"], text_color="#000",
            hover_color=t["accent"], width=110,
            command=self._open_templates)
        self._tpl_btn.pack(side="right", padx=(0, 4), pady=6)

        self._fill_btn = ctk.CTkButton(
            comp_head, text="Fill [Placeholders]", font=FONT_SMALL,
            fg_color="transparent", border_color=ORANGE,
            border_width=1, text_color=ORANGE,
            hover_color="#1a1000", width=150,
            command=self._fill_placeholders)
        self._fill_btn.pack(side="right", padx=(0, 4), pady=6)

        compose = ctk.CTkFrame(parent, fg_color=t["bg_main"])
        compose.pack(fill="both", expand=True, padx=18, pady=12)

        fn_row = ctk.CTkFrame(compose, fg_color="transparent")
        fn_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(fn_row, text="FROM NAME", font=FONT_LABEL,
                     text_color=t["text_dim"], width=120).pack(side="left")
        self._from_name = ctk.CTkEntry(fn_row, font=("Courier New", 14),
                                        fg_color=t["bg_input"],
                                        border_color=t["border"],
                                        placeholder_text="e.g. LetUsTech",
                                        text_color=t["text_main"],
                                        height=38)
        self._from_name.pack(side="left", fill="x", expand=True)

        sub_row = ctk.CTkFrame(compose, fg_color="transparent")
        sub_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(sub_row, text="SUBJECT", font=FONT_LABEL,
                     text_color=t["text_dim"], width=120).pack(side="left")
        self._subject = ctk.CTkEntry(sub_row, font=("Courier New", 14),
                                      fg_color=t["bg_input"],
                                      border_color=t["border"],
                                      placeholder_text="Hello {{first_name}}...",
                                      text_color=t["text_main"],
                                      height=38)
        self._subject.pack(side="left", fill="x", expand=True)

        # ── Formatting toolbar ─────────────────────────────────────────────
        toolbar = ctk.CTkFrame(compose, fg_color=t["bg_card"],
                                corner_radius=6, height=46)
        toolbar.pack(fill="x", pady=(0, 6))
        toolbar.pack_propagate(False)

        def tb_btn(parent, text, tip, cmd, width=34):
            b = ctk.CTkButton(parent, text=text, width=width, height=28,
                               font=("Courier New", 13, "bold"),
                               fg_color="transparent",
                               border_color=t["border"], border_width=1,
                               text_color=t["text_main"],
                               hover_color=t["bg_input"],
                               command=cmd)
            b.pack(side="left", padx=2, pady=4)
            return b

        def tb_sep(parent):
            ctk.CTkFrame(parent, fg_color=t["border"],
                          width=1, height=22).pack(side="left", padx=4, pady=7)

        # Bold / Italic / Underline / Strikethrough
        tb_btn(toolbar, "B",  "Bold",          self._fmt_bold)
        tb_btn(toolbar, "I",  "Italic",         self._fmt_italic)
        tb_btn(toolbar, "U",  "Underline",      self._fmt_underline)
        tb_btn(toolbar, "S",  "Strikethrough",  self._fmt_strike)
        tb_sep(toolbar)

        # Font size
        ctk.CTkLabel(toolbar, text="Size:", font=FONT_SMALL,
                     text_color=t["text_dim"]).pack(side="left", padx=(2, 0))
        self._font_size_var = ctk.StringVar(value="13")
        size_menu = ctk.CTkOptionMenu(toolbar,
                                       variable=self._font_size_var,
                                       values=["8","9","10","11","12","14","16","18","20","24","28","32","36"],
                                       fg_color=t["bg_input"],
                                       button_color=t["border"],
                                       dropdown_fg_color=t["bg_card"],
                                       text_color=t["text_main"],
                                       font=FONT_SMALL, width=62, height=26,
                                       command=lambda v: self._fmt_size(v))
        size_menu.pack(side="left", padx=2, pady=4)
        tb_sep(toolbar)

        # Alignment
        tb_btn(toolbar, "≡L", "Align Left",    lambda: self._fmt_align("left"),   width=36)
        tb_btn(toolbar, "≡C", "Align Centre",  lambda: self._fmt_align("center"), width=36)
        tb_btn(toolbar, "≡R", "Align Right",   lambda: self._fmt_align("right"),  width=36)
        tb_sep(toolbar)

        # Text colour
        ctk.CTkLabel(toolbar, text="Colour:", font=FONT_SMALL,
                     text_color=t["text_dim"]).pack(side="left", padx=(2, 0))
        self._txt_colour_var = ctk.StringVar(value="Default")
        COLOUR_MAP = {
            "Default": t["text_main"],
            "Green":   "#00e676",
            "Orange":  "#ff9800",
            "Red":     "#ff4444",
            "Blue":    "#4d9fff",
            "White":   "#ffffff",
            "Black":   "#000000",
            "Grey":    "#888888",
        }
        self._colour_map = COLOUR_MAP
        colour_menu = ctk.CTkOptionMenu(toolbar,
                                         variable=self._txt_colour_var,
                                         values=list(COLOUR_MAP.keys()),
                                         fg_color=t["bg_input"],
                                         button_color=t["border"],
                                         dropdown_fg_color=t["bg_card"],
                                         text_color=t["text_main"],
                                         font=FONT_SMALL, width=90, height=26,
                                         command=lambda v: self._fmt_colour(v))
        colour_menu.pack(side="left", padx=2, pady=4)
        tb_sep(toolbar)

        # Lists
        tb_btn(toolbar, "• List", "Bullet list",   self._fmt_bullet, width=56)
        tb_btn(toolbar, "1. List","Numbered list", self._fmt_numbered, width=60)
        tb_sep(toolbar)

        # Clear formatting
        tb_btn(toolbar, "✕ Clear", "Clear formatting", self._fmt_clear, width=68)
        tb_sep(toolbar)

        # Spell check toggle
        self._spell_on = _SPELL_AVAILABLE
        self._spell_btn = ctk.CTkButton(
            toolbar, text="✓ Spell" if _SPELL_AVAILABLE else "Spell N/A",
            width=74, height=28,
            font=("Courier New", 13, "bold"),
            fg_color=t["accent_dim"] if _SPELL_AVAILABLE else t["border"],
            text_color="#000" if _SPELL_AVAILABLE else t["text_dim"],
            hover_color=t["accent"] if _SPELL_AVAILABLE else t["border"],
            command=self._toggle_spell)
        self._spell_btn.pack(side="left", padx=2, pady=4)

        # ── Tag quick-insert panel ─────────────────────────────────────────
        self._tag_panel_open = True
        tag_panel_wrap = ctk.CTkFrame(compose, fg_color=t["bg_card"], corner_radius=6)
        tag_panel_wrap.pack(fill="x", pady=(0, 4))

        tag_panel_head = ctk.CTkFrame(tag_panel_wrap, fg_color="transparent", height=28)
        tag_panel_head.pack(fill="x")
        tag_panel_head.pack_propagate(False)

        ctk.CTkLabel(tag_panel_head, text="  TAGS", font=FONT_LABEL,
                     text_color=t["accent"]).pack(side="left", padx=4)
        ctk.CTkLabel(tag_panel_head,
                     text="click to insert into email",
                     font=FONT_SMALL, text_color=t["text_dim"]).pack(side="left", padx=4)

        self._tag_panel_toggle = ctk.CTkButton(
            tag_panel_head, text="▲ Hide", font=FONT_SMALL, width=60,
            fg_color="transparent", text_color=t["text_dim"],
            hover_color=t["bg_input"],
            command=self._toggle_tag_panel)
        self._tag_panel_toggle.pack(side="right", padx=6)

        # Scrollable row of tag buttons
        self._tag_panel_body = ctk.CTkFrame(tag_panel_wrap, fg_color="transparent")
        self._tag_panel_body.pack(fill="x", padx=6, pady=(0, 6))

        # Built-in tags always shown
        BUILTIN_TAGS = [
            ("{{first_name}}", "First name from CSV"),
            ("{{email}}",      "Email address"),
            ("{{company}}",    "Their company"),
            ("{{company_name}}","Your company (Settings)"),
            ("{{sender_name}}", "Your name (Settings)"),
            ("{{signature}}",   "Your signature (Settings)"),
        ]
        self._tag_buttons_frame = ctk.CTkFrame(
            self._tag_panel_body, fg_color="transparent")
        self._tag_buttons_frame.pack(fill="x")
        self._builtin_tags = BUILTIN_TAGS
        self._render_tag_panel()

        # ── Body text ──────────────────────────────────────────────────────
        self._body = tk.Text(compose, font=("Courier New", 13),
                              bg=t["bg_input"], fg=t["text_main"],
                              insertbackground=t["accent"],
                              relief="flat", bd=0, wrap="word",
                              selectbackground=t["accent_dim"],
                              highlightthickness=1,
                              highlightbackground=t["border"],
                              highlightcolor=t["accent"],
                              padx=12, pady=12,
                              undo=True)
        self._body.pack(fill="both", expand=True)

        # Built-in formatting tags
        self._body.tag_config("bold",      font=("Courier New", 13, "bold"))
        self._body.tag_config("italic",    font=("Courier New", 13, "italic"))
        self._body.tag_config("underline", underline=True)
        self._body.tag_config("strike",    overstrike=True)
        self._body.tag_config("align_left",   justify="left")
        self._body.tag_config("align_center", justify="center")
        self._body.tag_config("align_right",  justify="right")
        # Spell check underline tag
        self._body.tag_config("misspelled", underline=True,
                               underlinefg="#ff4444" if hasattr(self._body, "tag_config") else None,
                               foreground="#ff6666")
        # Highlight tags
        self._body.tag_config("csv_tag",     foreground=t["accent"],
                               font=("Courier New", 13, "bold"))
        self._body.tag_config("placeholder", foreground=ORANGE,
                               font=("Courier New", 13, "bold"))
        # Pre-register colour tags
        for name, hex_val in {
            "Default": t["text_main"], "Green": "#00e676",
            "Orange": "#ff9800", "Red": "#ff4444",
            "Blue": "#4d9fff", "White": "#ffffff",
            "Black": "#000000", "Grey": "#888888"}.items():
            self._body.tag_config(f"colour_{name}", foreground=hex_val)
        # Keyboard shortcuts
        self._body.bind("<Control-b>", lambda e: self._fmt_bold())
        self._body.bind("<Control-i>", lambda e: self._fmt_italic())
        self._body.bind("<Control-u>", lambda e: self._fmt_underline())
        self._body.bind("<Control-z>", lambda e: self._body.edit_undo())
        self._body.bind("<Control-y>", lambda e: self._body.edit_redo())
        self._body.bind("<KeyRelease>", self._on_key_release)
        self._body.bind("<Button-3>",   self._show_spell_menu)   # right-click
        self._body.bind("<Button-1>",   self._on_left_click)     # left-click on red words

        # Spell checker instance
        if _SPELL_AVAILABLE:
            self._spell = SpellChecker()
        else:
            self._spell = None
        self._spell_after_id = None

        self._body.insert("1.0",
            "Hi {{first_name}},\n\n"
            "Write your message here.\n\n"
            "Use {{column_name}} to personalise with CSV data.\n\n"
            "Best regards,\nThe LetUsTech Team")
        self._highlight_body()

        bar = ctk.CTkFrame(parent, fg_color=t["bg_card"],
                            corner_radius=0, height=50)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._send_btn = ctk.CTkButton(bar, text=">  SEND CAMPAIGN",
                                        font=FONT_HEAD,
                                        fg_color=t["accent"], text_color="#000",
                                        hover_color=t["accent_dim"], width=220,
                                        command=self._start_send)
        self._send_btn.pack(side="right", padx=14, pady=8)

        self._stop_btn = ctk.CTkButton(bar, text="STOP", font=FONT_HEAD,
                                        fg_color=t["border"],
                                        text_color=t["text_dim"],
                                        hover_color=t["border"], width=110,
                                        command=self._stop_send,
                                        state="disabled")
        self._stop_btn.pack(side="right", padx=(0, 6), pady=8)

        ctk.CTkButton(bar, text="Preview", font=FONT_SMALL,
                      fg_color="transparent", border_color=t["border"],
                      border_width=1, text_color=t["text_dim"],
                      hover_color=t["bg_input"], width=90,
                      command=self._preview).pack(side="left", padx=(14,4), pady=8)

        ctk.CTkButton(bar, text="🔍 Tag Inspector", font=FONT_SMALL,
                      fg_color="transparent", border_color=t["accent"],
                      border_width=1, text_color=t["accent"],
                      hover_color=t["bg_input"], width=120,
                      command=self._open_tag_inspector).pack(side="left", padx=(0,4), pady=8)

        prog = ctk.CTkFrame(parent, fg_color=t["bg_main"])
        prog.pack(fill="x", padx=18, pady=(0, 8))
        self._progress_var = ctk.DoubleVar(value=0)
        ctk.CTkProgressBar(prog, variable=self._progress_var,
                            progress_color=t["accent"],
                            fg_color=t["bg_card"]
                            ).pack(fill="x", pady=(0, 4))
        self._prog_label = ctk.CTkLabel(prog, text="", font=FONT_SMALL,
                                         text_color=t["text_dim"])
        self._prog_label.pack(anchor="w")

    # ── Help window ────────────────────────────────────────────────────────

    def _open_settings(self, tab="company"):
        t = self._t
        win = ctk.CTkToplevel(self)
        win.title("Settings")
        win.geometry("660x580")
        win.configure(fg_color=t["bg_main"])
        win.grab_set()
        win.resizable(False, False)

        # ── Header ────────────────────────────────────────────────────────
        head = ctk.CTkFrame(win, fg_color=t["bg_sidebar"],
                             corner_radius=0, height=50)
        head.pack(fill="x")
        head.pack_propagate(False)
        ctk.CTkLabel(head, text="⚙  SETTINGS",
                     font=FONT_HEAD, text_color=t["accent"]).pack(side="left", padx=18)

        # ── Tab bar ───────────────────────────────────────────────────────
        TABS = [
            ("🏢  Company",  "company"),
            ("📧  SMTP",     "smtp"),
            ("✉️  Defaults", "defaults"),
            ("🎨  Branding", "branding"),
        ]
        tab_bar = ctk.CTkFrame(win, fg_color=t["bg_card"],
                                corner_radius=0, height=44)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)

        content_area = ctk.CTkFrame(win, fg_color=t["bg_main"])
        content_area.pack(fill="both", expand=True)

        # Bottom save bar
        btn_bar = ctk.CTkFrame(win, fg_color=t["bg_sidebar"],
                                corner_radius=0, height=54)
        btn_bar.pack(fill="x", side="bottom")
        btn_bar.pack_propagate(False)

        active_tab  = {"name": tab}
        tab_buttons = {}
        tab_frames  = {}

        def switch_tab(name):
            active_tab["name"] = name
            for n, f in tab_frames.items():
                if n == name:
                    f.pack(fill="both", expand=True)
                else:
                    f.pack_forget()
            for n, b in tab_buttons.items():
                b.configure(
                    fg_color=t["bg_input"] if n == name else "transparent",
                    text_color=t["accent"] if n == name else t["text_dim"])

        # ── Helper builders ───────────────────────────────────────────────
        def make_scroll(parent):
            return ctk.CTkScrollableFrame(parent, fg_color=t["bg_main"],
                                           scrollbar_button_color=t["border"])

        def sec(scroll, title):
            ctk.CTkLabel(scroll, text=title, font=FONT_HEAD,
                         text_color=t["accent"]).pack(anchor="w", padx=20, pady=(16, 4))
            ctk.CTkFrame(scroll, fg_color=t["border"], height=1).pack(fill="x", padx=20)

        def fld(scroll, label, key, placeholder="", secret=False):
            ctk.CTkLabel(scroll, text=label, font=FONT_LABEL,
                         text_color=t["text_dim"]).pack(anchor="w", padx=20, pady=(10, 2))
            var = ctk.StringVar(value=self._config.get(key, ""))
            ctk.CTkEntry(scroll, textvariable=var, font=FONT_MONO,
                          fg_color=t["bg_input"], border_color=t["border"],
                          text_color=t["text_main"], placeholder_text=placeholder,
                          show="*" if secret else ""
                          ).pack(fill="x", padx=20)
            return var

        def hint(scroll, text):
            ctk.CTkLabel(scroll, text=text, font=FONT_SMALL,
                         text_color=t["text_dim"], wraplength=560,
                         justify="left", anchor="w"
                         ).pack(anchor="w", padx=22, pady=(2, 0))

        # ── Tab: Company ──────────────────────────────────────────────────
        f_company = make_scroll(content_area)
        tab_frames["company"] = f_company
        sec(f_company, "🏢  YOUR COMPANY")
        v_company  = fld(f_company, "Company Name",   "company_name",    "e.g. LetUsTech")
        hint(f_company, "Shown in the top bar and used as {{company_name}} in templates.")
        v_website  = fld(f_company, "Website",        "company_website", "e.g. letustech.uk")
        v_phone    = fld(f_company, "Phone Number",   "company_phone",   "e.g. 07700 123456")
        v_address  = fld(f_company, "Address",        "company_address", "e.g. Liverpool, UK")
        sec(f_company, "👤  SENDER DETAILS")
        v_sender   = fld(f_company, "Your Name",      "sender_name",     "e.g. Deano")
        hint(f_company, "Used as {{sender_name}} in all templates.")
        v_role     = fld(f_company, "Job Title / Role", "sender_role",   "e.g. Founder")
        v_sig      = fld(f_company, "Email Signature", "sender_sig",
                         "e.g. Best regards, Deano — letustech.uk")
        hint(f_company, "Used as {{signature}} in templates.")

        # ── Tab: SMTP ─────────────────────────────────────────────────────
        f_smtp = make_scroll(content_area)
        tab_frames["smtp"] = f_smtp
        sec(f_smtp, "📧  SMTP CONFIGURATION")

        v_host = fld(f_smtp, "Host",             "host",  "smtp.gmail.com")
        v_port = fld(f_smtp, "Port",             "port",  "587")
        v_user = fld(f_smtp, "Email Address",    "user",  "you@gmail.com")
        v_pass = fld(f_smtp, "App Password",     "pass",  "", secret=True)

        ctk.CTkLabel(f_smtp, text="Security", font=FONT_LABEL,
                     text_color=t["text_dim"]).pack(anchor="w", padx=20, pady=(10, 2))
        tls_row = ctk.CTkFrame(f_smtp, fg_color="transparent")
        tls_row.pack(fill="x", padx=20)
        v_tls = ctk.StringVar(value=self._config.get("tls", "STARTTLS"))
        ctk.CTkOptionMenu(tls_row, variable=v_tls,
                          values=["STARTTLS", "SSL/TLS", "None"],
                          fg_color=t["bg_input"], button_color=t["accent_dim"],
                          dropdown_fg_color=t["bg_card"],
                          font=FONT_MONO, width=160).pack(side="left")

        hint(f_smtp, "For Gmail: use an App Password (myaccount.google.com → Security → App Passwords).")

        # Common providers reference
        ctk.CTkLabel(f_smtp, text="COMMON PROVIDERS", font=FONT_LABEL,
                     text_color=t["text_dim"]).pack(anchor="w", padx=20, pady=(16, 6))
        providers = [
            ("Gmail",           "smtp.gmail.com",       "587", "STARTTLS"),
            ("Outlook/Hotmail", "smtp.office365.com",   "587", "STARTTLS"),
            ("Yahoo",           "smtp.mail.yahoo.com",  "587", "STARTTLS"),
            ("iCloud",          "smtp.mail.me.com",     "587", "STARTTLS"),
            ("Zoho",            "smtp.zoho.com",        "587", "STARTTLS"),
        ]
        for name, host, port, sec_type in providers:
            row = ctk.CTkFrame(f_smtp, fg_color=t["bg_card"], corner_radius=6)
            row.pack(fill="x", padx=20, pady=2)
            ctk.CTkLabel(row, text=f"  {name}", font=FONT_SMALL,
                         text_color=t["text_main"], width=130, anchor="w"
                         ).pack(side="left", padx=4, pady=6)
            ctk.CTkLabel(row, text=host, font=("Courier New", 11),
                         text_color=t["accent"], anchor="w"
                         ).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f":{port}  {sec_type}",
                         font=FONT_SMALL, text_color=t["text_dim"]
                         ).pack(side="left", padx=4)
            ctk.CTkButton(row, text="Use", font=FONT_SMALL, width=46,
                          fg_color=t["accent_dim"], text_color="#000",
                          hover_color=t["accent"],
                          command=lambda h=host, p=port, s=sec_type: [
                              v_host.set(h), v_port.set(p), v_tls.set(s)]
                          ).pack(side="right", padx=8, pady=4)

        # Test connection inside SMTP tab
        test_result = ctk.CTkLabel(f_smtp, text="", font=FONT_SMALL,
                                    text_color=t["text_dim"])
        test_result.pack(anchor="w", padx=20, pady=(12, 0))

        def test_smtp_tab():
            host = v_host.get().strip()
            port_str = v_port.get().strip()
            user = v_user.get().strip()
            pwd  = v_pass.get()
            tls  = v_tls.get()
            if not all([host, user, pwd]):
                test_result.configure(text="⚠  Fill in host, email and password first.",
                                       text_color=ORANGE)
                return
            test_result.configure(text="⏳  Testing...", text_color=ORANGE)
            win.update()
            import threading as _th
            def _run():
                import smtplib as _smtp, ssl as _ssl
                try:
                    port = int(port_str or 587)
                    if tls == "SSL/TLS":
                        s = _smtp.SMTP_SSL(host, port,
                                context=_ssl.create_default_context(), timeout=10)
                    else:
                        s = _smtp.SMTP(host, port, timeout=10)
                        s.ehlo()
                        if tls == "STARTTLS":
                            s.starttls(context=_ssl.create_default_context())
                            s.ehlo()
                    s.login(user, pwd)
                    s.quit()
                    win.after(0, lambda: test_result.configure(
                        text=f"✓  Connected to {host} as {user}",
                        text_color=t["accent"]))
                except Exception as e:
                    win.after(0, lambda err=e: test_result.configure(
                        text=f"✗  {type(err).__name__}: {err}",
                        text_color=RED))
            _th.Thread(target=_run, daemon=True).start()

        ctk.CTkButton(f_smtp, text="Test Connection", font=FONT_LABEL,
                      fg_color="transparent", border_color=t["accent"],
                      border_width=1, text_color=t["accent"],
                      hover_color=t["bg_card"],
                      command=test_smtp_tab
                      ).pack(fill="x", padx=20, pady=(8, 14))

        # ── Tab: Defaults ─────────────────────────────────────────────────
        f_defaults = make_scroll(content_area)
        tab_frames["defaults"] = f_defaults
        sec(f_defaults, "✉️  EMAIL DEFAULTS")
        v_from_name = fld(f_defaults, "Default From Name", "default_from_name",
                           "e.g. LetUsTech")
        hint(f_defaults, "Pre-fills the From Name field every time the app opens.")
        v_footer    = fld(f_defaults, "Email Footer", "email_footer",
                           "e.g. Unsubscribe: [link] | letustech.uk")
        hint(f_defaults, "Auto-appended to every email. Leave blank to disable.")
        v_delay     = fld(f_defaults, "Default Send Delay (seconds)", "default_delay", "1")
        hint(f_defaults, "Seconds to wait between each email. Helps avoid spam filters.")

        # ── Tab: Branding ─────────────────────────────────────────────────
        f_branding = make_scroll(content_area)
        tab_frames["branding"] = f_branding
        sec(f_branding, "🎨  BRANDING")
        v_colour = fld(f_branding, "Accent Colour", "brand_colour",
                        "e.g. #00e676  (leave blank for theme default)")
        hint(f_branding, "Custom hex colour used as accent. Requires restart to apply.")

        # Colour preview swatches
        ctk.CTkLabel(f_branding, text="QUICK COLOURS", font=FONT_LABEL,
                     text_color=t["text_dim"]).pack(anchor="w", padx=20, pady=(14, 6))
        swatch_row = ctk.CTkFrame(f_branding, fg_color="transparent")
        swatch_row.pack(anchor="w", padx=20)
        swatches = [
            ("#00e676","Green"), ("#4d9fff","Blue"), ("#ff4466","Crimson"),
            ("#b066ff","Purple"), ("#ffaa00","Amber"), ("#ff9800","Orange"),
        ]
        for hex_c, name in swatches:
            ctk.CTkButton(swatch_row, text=name, width=72, height=30,
                          font=FONT_SMALL, fg_color=hex_c, text_color="#000",
                          hover_color=hex_c,
                          command=lambda c=hex_c: v_colour.set(c)
                          ).pack(side="left", padx=3)

        # ── Build tab buttons ─────────────────────────────────────────────
        for label, name in TABS:
            b = ctk.CTkButton(tab_bar, text=label, font=FONT_SMALL,
                               fg_color="transparent",
                               text_color=t["text_dim"],
                               hover_color=t["bg_input"],
                               corner_radius=0, height=44,
                               command=lambda n=name: switch_tab(n))
            b.pack(side="left", padx=2)
            tab_buttons[name] = b

        # ── Save ──────────────────────────────────────────────────────────
        def save_all():
            updates = {
                "company_name":      v_company.get().strip(),
                "company_website":   v_website.get().strip(),
                "company_phone":     v_phone.get().strip(),
                "company_address":   v_address.get().strip(),
                "sender_name":       v_sender.get().strip(),
                "sender_role":       v_role.get().strip(),
                "sender_sig":        v_sig.get().strip(),
                "host":              v_host.get().strip(),
                "port":              v_port.get().strip(),
                "user":              v_user.get().strip(),
                "pass":              v_pass.get(),
                "tls":               v_tls.get(),
                "default_from_name": v_from_name.get().strip(),
                "email_footer":      v_footer.get().strip(),
                "default_delay":     v_delay.get().strip(),
                "brand_colour":      v_colour.get().strip(),
            }
            self._config.update(updates)
            save_config(self._config)

            # Sync hidden SMTP widgets so _get_smtp works
            self._smtp_host.delete(0, "end"); self._smtp_host.insert(0, updates["host"])
            self._smtp_port.delete(0, "end"); self._smtp_port.insert(0, updates["port"])
            self._smtp_user.delete(0, "end"); self._smtp_user.insert(0, updates["user"])
            self._smtp_pass.delete(0, "end"); self._smtp_pass.insert(0, updates["pass"])
            self._tls_var.set(updates["tls"])

            # Update top bar
            name = updates["company_name"] or "LETUSTECH"
            self._company_lbl.configure(text=name.upper())

            # Update SMTP status pill
            self._update_smtp_pill()

            # Pre-fill From Name
            if updates["default_from_name"] and not self._from_name.get().strip():
                self._from_name.insert(0, updates["default_from_name"])

            self._log_line("Settings saved.", "ok")
            win.destroy()

        ctk.CTkButton(btn_bar, text="Save All Settings",
                      font=FONT_LABEL, fg_color=t["accent"], text_color="#000",
                      hover_color=t["accent_dim"], width=180,
                      command=save_all).pack(side="right", padx=14, pady=10)
        ctk.CTkButton(btn_bar, text="Cancel", font=FONT_SMALL,
                      fg_color="transparent", border_color=t["border"],
                      border_width=1, text_color=t["text_dim"],
                      hover_color=t["bg_card"], width=80,
                      command=win.destroy).pack(side="right", padx=(0, 6), pady=10)

        # ── Privacy tab ───────────────────────────────────────────────────
        f_privacy = make_scroll(content_area)
        tab_frames["privacy"] = f_privacy
        sec(f_privacy, "🔒  PRIVACY & DATA")

        # Encryption status
        enc_status = "✓  Enabled (cryptography library found)" if _CRYPTO_AVAILABLE \
                     else "⚠  Basic obfuscation only — install cryptography for full encryption"
        enc_colour = t["accent"] if _CRYPTO_AVAILABLE else ORANGE

        status_card = ctk.CTkFrame(f_privacy, fg_color=t["bg_card"], corner_radius=8)
        status_card.pack(fill="x", padx=20, pady=(12, 0))
        ctk.CTkLabel(status_card, text="Password Encryption",
                     font=FONT_LABEL, text_color=t["text_dim"]
                     ).pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(status_card, text=enc_status,
                     font=FONT_MONO, text_color=enc_colour
                     ).pack(anchor="w", padx=16, pady=(0, 10))

        if not _CRYPTO_AVAILABLE:
            ctk.CTkLabel(f_privacy,
                         text="  Run:  pip install cryptography  to enable full encryption",
                         font=FONT_SMALL, text_color=t["text_dim"]
                         ).pack(anchor="w", padx=20, pady=(4, 0))

        hint(f_privacy,
             "Your app password and settings are stored encrypted on your machine. "
             "The config file cannot be read without your machine's unique ID.")

        sec(f_privacy, "🗑️  CLEAR SAVED DATA")
        hint(f_privacy, "Use these buttons to remove saved data from your machine.")

        ctk.CTkFrame(f_privacy, fg_color="transparent", height=8).pack()

        def clear_passwords():
            if messagebox.askyesno("Clear passwords",
                "Remove saved email and password from config?\n\nYou'll need to re-enter them next launch."):
                for key in ("pass", "user", "host", "port", "tls"):
                    self._config.pop(key, None)
                save_config(self._config)
                self._smtp_host.delete(0, "end")
                self._smtp_port.delete(0, "end")
                self._smtp_user.delete(0, "end")
                self._smtp_pass.delete(0, "end")
                self._update_smtp_pill()
                self._log_line("SMTP credentials cleared.", "warn")
                messagebox.showinfo("Done", "Credentials removed.")

        def clear_all_data():
            if messagebox.askyesno("Clear ALL data",
                "This will remove ALL saved settings including company info, "
                "credentials and preferences.\n\nAre you sure?"):
                self._config.clear()
                save_config({})
                try:
                    CONFIG_FILE.unlink()
                except Exception:
                    pass
                self._log_line("All saved data cleared.", "warn")
                messagebox.showinfo("Done",
                    "All data cleared.\n\nRestart the app to start fresh.")

        ctk.CTkButton(f_privacy, text="Clear Saved Password & Email",
                      font=FONT_LABEL,
                      fg_color="transparent", border_color=ORANGE,
                      border_width=1, text_color=ORANGE,
                      hover_color="#1a0f00", width=260,
                      command=clear_passwords
                      ).pack(anchor="w", padx=20, pady=(0, 8))

        ctk.CTkButton(f_privacy, text="Clear ALL Saved Data",
                      font=FONT_LABEL,
                      fg_color="transparent", border_color=RED,
                      border_width=1, text_color=RED,
                      hover_color="#1a0000", width=200,
                      command=clear_all_data
                      ).pack(anchor="w", padx=20)

        hint(f_privacy, "Clearing all data is permanent and cannot be undone.")

        # Add Privacy tab button
        TABS.append(("🔒  Privacy", "privacy"))
        b = ctk.CTkButton(tab_bar, text="🔒  Privacy", font=FONT_SMALL,
                           fg_color="transparent",
                           text_color=t["text_dim"],
                           hover_color=t["bg_input"],
                           corner_radius=0, height=44,
                           command=lambda: switch_tab("privacy"))
        b.pack(side="left", padx=2)
        tab_buttons["privacy"] = b

        # Start on requested tab
        switch_tab(tab)

    def _open_help(self):
        t = self._t
        win = ctk.CTkToplevel(self)
        win.title("Help — Bulk Email Sender")
        win.geometry("860x600")
        win.configure(fg_color=t["bg_main"])
        win.grab_set()

        head = ctk.CTkFrame(win, fg_color=t["bg_sidebar"],
                             corner_radius=0, height=48)
        head.pack(fill="x")
        head.pack_propagate(False)
        ctk.CTkLabel(head, text="⬡", font=("Courier New", 18, "bold"),
                     text_color=t["accent"]).pack(side="left", padx=(16, 4))
        ctk.CTkLabel(head, text="HELP & DOCUMENTATION",
                     font=FONT_HEAD, text_color=t["accent"]).pack(side="left")

        body = ctk.CTkFrame(win, fg_color=t["bg_main"])
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        nav = ctk.CTkFrame(body, fg_color=t["bg_sidebar"],
                            corner_radius=0, width=200)
        nav.grid(row=0, column=0, sticky="nsew")
        nav.grid_propagate(False)

        ctk.CTkLabel(nav, text="TOPICS", font=FONT_LABEL,
                     text_color=t["text_dim"]
                     ).pack(anchor="w", padx=16, pady=(16, 8))

        content_frame = ctk.CTkFrame(body, fg_color=t["bg_main"],
                                      corner_radius=0)
        content_frame.grid(row=0, column=1, sticky="nsew")

        content_text = tk.Text(content_frame,
                                font=("Courier New", 11),
                                bg=t["bg_main"], fg=t["text_main"],
                                relief="flat", bd=0, wrap="word",
                                highlightthickness=0,
                                padx=24, pady=20,
                                state="disabled",
                                selectbackground=t["accent_dim"])
        content_text.pack(fill="both", expand=True)
        content_text.tag_config("heading",
                                 foreground=t["accent"],
                                 font=("Courier New", 13, "bold"))
        content_text.tag_config("body",
                                 foreground=t["text_main"],
                                 font=("Courier New", 11))

        nav_buttons = []

        def show_topic(name):
            content_text.configure(state="normal")
            content_text.delete("1.0", "end")
            for line in HELP_CONTENT[name].split("\n"):
                stripped = line.strip()
                is_heading = (stripped and
                              stripped == stripped.upper() and
                              len(stripped) > 4 and
                              not stripped.startswith("-") and
                              not stripped.startswith("•"))
                tag = "heading" if is_heading else "body"
                content_text.insert("end", line + "\n", tag)
            content_text.configure(state="disabled")
            for btn in nav_buttons:
                active = btn.cget("text") == name
                btn.configure(
                    fg_color=t["bg_card"] if active else t["bg_sidebar"],
                    text_color=t["accent"] if active else t["text_dim"])

        for topic in HELP_CONTENT:
            btn = ctk.CTkButton(nav, text=topic, font=FONT_SMALL,
                                 fg_color=t["bg_sidebar"],
                                 text_color=t["text_dim"],
                                 hover_color=t["bg_card"],
                                 anchor="w",
                                 command=lambda n=topic: show_topic(n))
            btn.pack(fill="x", padx=8, pady=2)
            nav_buttons.append(btn)

        show_topic("Getting Started")

    # ── Widget helpers ─────────────────────────────────────────────────────

    def _section(self, parent, title):
        ctk.CTkLabel(parent, text=title, font=FONT_HEAD,
                     text_color=self._t["accent"]
                     ).pack(anchor="w", padx=20, pady=(18, 6))

    def _divider(self, parent):
        ctk.CTkFrame(parent, fg_color=self._t["border"], height=1
                     ).pack(fill="x", padx=20, pady=12)

    def _field(self, parent, label, placeholder, secret=False):
        t = self._t
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 8))
        ctk.CTkLabel(row, text=label, font=FONT_LABEL,
                     text_color=t["text_dim"]).pack(anchor="w")
        entry = ctk.CTkEntry(row, font=FONT_MONO,
                              fg_color=t["bg_input"],
                              border_color=t["border"],
                              placeholder_text=placeholder,
                              text_color=t["text_main"],
                              show="*" if secret else "")
        entry.pack(fill="x")
        return entry

    def _log_line(self, msg, tag="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        self._log.configure(state="normal")
        self._log.insert("end", f"[{ts}] {msg}\n", tag)
        self._log.see("end")
        self._log.configure(state="disabled")

    def _clear_log(self):
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

    def _set_status(self, text, color=None):
        self._status_dot.configure(
            text=f"●  {text}",
            text_color=color or self._t["text_dim"])

    def _restore_smtp(self):
        c = self._config
        if c.get("host"):  self._smtp_host.insert(0, c["host"])
        if c.get("port"):  self._smtp_port.insert(0, c["port"])
        if c.get("user"):  self._smtp_user.insert(0, c["user"])
        if c.get("pass"):  self._smtp_pass.insert(0, c["pass"])
        if c.get("tls"):   self._tls_var.set(c["tls"])
        from_name = c.get("default_from_name") or c.get("fname", "")
        if from_name: self._from_name.insert(0, from_name)
        self._update_smtp_pill()
        self._toggle_contacts()

    def _toggle_contacts(self):
        self._contacts_open = not self._contacts_open
        if self._contacts_open:
            self._contacts_body.pack(fill="x", padx=12,
                                      after=self._contacts_outer)
            self._contacts_toggle_btn.configure(text="▼  CONTACTS")
            self._contacts_status_label.pack_forget()
        else:
            self._contacts_body.pack_forget()
            self._contacts_toggle_btn.configure(text="▶  CONTACTS")
            self._contacts_status_label.pack(anchor="w", padx=14, pady=(0, 8))

    def _toggle_options(self):
        self._options_open = not self._options_open
        if self._options_open:
            self._options_body.pack(fill="x", padx=12,
                                     after=self._options_outer)
            self._options_toggle_btn.configure(text="▼  OPTIONS & LOG")
            self._options_status_label.pack_forget()
        else:
            self._options_body.pack_forget()
            self._options_toggle_btn.configure(text="▶  OPTIONS & LOG")
            self._options_status_label.pack(anchor="w", padx=14, pady=(0, 8))
            self._update_options_pill()

    def _update_options_pill(self):
        delay = self._delay_var.get() if hasattr(self, "_delay_var") else "1"
        mode  = "HTML" if (hasattr(self, "_html_var") and self._html_var.get()) else "Plain text"
        self._options_status_label.configure(text=f"Delay {delay}s · {mode}")

    def _toggle_smtp(self):
        # SMTP is now in Settings — this is a no-op kept for compatibility
        pass

    def _update_smtp_pill(self):
        user = self._config.get("user", "").strip()
        if user:
            self._smtp_status_label.configure(
                text=f"✓  {user}",
                text_color=self._t["accent"])
        else:
            self._smtp_status_label.configure(
                text="Not configured — click Configure",
                text_color=self._t["text_dim"])

    def _save_smtp(self):
        """Legacy method — now handled by Settings save."""
        cfg = self._config
        cfg.update({
            "host": self._smtp_host.get(),
            "port": self._smtp_port.get(),
            "user": self._smtp_user.get(),
            "pass": self._smtp_pass.get(),
            "tls":  self._tls_var.get(),
        })
        save_config(cfg)
        self._update_smtp_pill()
        self._log_line("SMTP settings saved.", "ok")

    def _get_smtp(self):
        return (self._smtp_host.get().strip(),
                int(self._smtp_port.get().strip() or 587),
                self._smtp_user.get().strip(),
                self._smtp_pass.get(),
                self._tls_var.get())

    def _test_connection(self):
        def _run():
            self._set_status("TESTING...", ORANGE)
            host, port, user, pwd, tls = self._get_smtp()

            # Basic validation first
            if not host:
                self._log_line("ERROR: No host entered.", "err")
                self._set_status("ERROR", RED)
                return
            if not user:
                self._log_line("ERROR: No email address entered.", "err")
                self._set_status("ERROR", RED)
                return
            if not pwd:
                self._log_line("ERROR: No password entered.", "err")
                self._set_status("ERROR", RED)
                return

            self._log_line(f"Connecting to {host}:{port} ({tls})...", "info")
            s = None
            try:
                if tls == "SSL/TLS":
                    s = smtplib.SMTP_SSL(host, port,
                            context=ssl.create_default_context(), timeout=10)
                else:
                    s = smtplib.SMTP(host, port, timeout=10)
                    s.ehlo()
                    if tls == "STARTTLS":
                        s.starttls(context=ssl.create_default_context())
                        s.ehlo()

                self._log_line("Socket connected — logging in...", "info")
                s.login(user, pwd)
                self._log_line(f"✓ Login successful as {user}", "ok")
                self._set_status("CONNECTED", self._t["accent"])
            except smtplib.SMTPAuthenticationError as e:
                self._log_line(f"AUTH FAILED: Wrong email or password. ({e.smtp_code})", "err")
                self._log_line("For Gmail: use an App Password, not your real password.", "warn")
                self._set_status("AUTH ERROR", RED)
            except smtplib.SMTPConnectError as e:
                self._log_line(f"CONNECT FAILED: Could not reach {host}:{port} — {e}", "err")
                self._set_status("ERROR", RED)
            except TimeoutError:
                self._log_line(f"TIMEOUT: Could not connect to {host}:{port}", "err")
                self._set_status("ERROR", RED)
            except Exception as e:
                self._log_line(f"ERROR: {type(e).__name__}: {e}", "err")
                self._set_status("ERROR", RED)
            finally:
                if s:
                    try:
                        s.quit()
                    except Exception:
                        pass  # connection may already be closed, that's fine

        threading.Thread(target=_run, daemon=True).start()

    def _load_csv_path(self, path):
        """Load a CSV directly from a file path — used by --load-csv arg."""
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows    = list(reader)
                headers = reader.fieldnames or []
            if not rows:
                return
            email_col = next(
                (h for h in headers if "email" in h.lower()), None)
            if not email_col:
                return
            self._contacts    = rows
            self._csv_headers = headers
            valid = sum(1 for r in rows if validate_email(r.get(email_col, "")))
            self._contact_info.configure(
                text=f"{valid} valid / {len(rows)} total",
                text_color=self._t["accent"])
            self._contacts_status_label.configure(
                text=f"{valid} contacts loaded",
                text_color=self._t["accent"])
            # Open contacts accordion so user sees it
            if not self._contacts_open:
                self._toggle_contacts()
            tags_str = ", ".join("{{" + h + "}}" for h in headers)
            self._log_line(
                f"Auto-loaded {len(rows)} contacts from CSV Maker — "
                f"tags: {tags_str}", "ok")
            self._render_tag_panel()
            # Clean up temp file
            try:
                os.unlink(path)
            except Exception:
                pass
        except Exception as e:
            self._log_line(f"Auto-load failed: {e}", "err")

    def _import_csv(self):
        path = filedialog.askopenfilename(
            title="Select CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows    = list(reader)
                headers = reader.fieldnames or []
            if not rows:
                messagebox.showwarning("Empty CSV", "No data rows found.")
                return
            email_col = next(
                (h for h in headers if "email" in h.lower()), None)
            if not email_col:
                messagebox.showerror("No email column",
                    "CSV must have a column with 'email' in the name.")
                return
            self._contacts    = rows
            self._csv_headers = headers
            valid = sum(1 for r in rows
                        if validate_email(r.get(email_col, "")))
            self._contact_info.configure(
                text=f"{valid} valid / {len(rows)} total",
                text_color=self._t["accent"])
            self._contacts_status_label.configure(
                text=f"✓  {valid} contacts loaded",
                text_color=self._t["accent"])
            self._log_line(
                f"Loaded {len(rows)} contacts — "
                f"columns: {', '.join(headers)}", "ok")
            # Refresh tag panel so CSV columns appear as buttons
            self._render_tag_panel()
        except Exception as e:
            messagebox.showerror("CSV Error", str(e))

    def _export_sample(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="sample_contacts.csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["email", "first_name", "last_name", "company"])
            w.writerow(["alice@example.com", "Alice", "Smith", "Acme Ltd"])
            w.writerow(["bob@example.com",   "Bob",   "Jones", "Beta Corp"])
        self._log_line("Sample CSV saved.", "ok")

    def _pick_attachment(self):
        path = filedialog.askopenfilename(title="Select attachment")
        if path:
            self._attachment = path
            p = Path(path)
            # File size
            try:
                size = p.stat().st_size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/1024/1024:.1f} MB"
            except Exception:
                size_str = ""
            # Icon by extension
            ext = p.suffix.lower()
            icon = {"pdf": "📄", "doc": "📝", "docx": "📝",
                    "xls": "📊", "xlsx": "📊", "csv": "📊",
                    "jpg": "🖼", "jpeg": "🖼", "png": "🖼",
                    "zip": "🗜", "rar": "🗜",
                    "mp4": "🎬", "mp3": "🎵"}.get(ext.lstrip("."), "📎")
            self._att_icon.configure(text=icon)
            self._att_name.configure(text=p.name[:34],
                                      text_color=self._t["accent"])
            self._att_size.configure(text=f"{ext.upper().lstrip('.')} · {size_str}")
            self._att_remove_btn.configure(state="normal")
            self._log_line(f"Attachment: {p.name} ({size_str})", "ok")

    def _remove_attachment(self):
        self._attachment = None
        self._att_icon.configure(text="📎", text_color=self._t["text_dim"])
        self._att_name.configure(text="No file attached",
                                  text_color=self._t["text_dim"])
        self._att_size.configure(text="Click + to attach a file")
        self._att_remove_btn.configure(state="disabled")
        self._log_line("Attachment removed.", "warn")

    # ── Formatting helpers ─────────────────────────────────────────────────

    def _get_sel(self):
        """Return (start, end) of current selection, or (None, None)."""
        try:
            return self._body.index("sel.first"), self._body.index("sel.last")
        except tk.TclError:
            return None, None

    def _toggle_tag(self, tag):
        start, end = self._get_sel()
        if not start:
            return
        existing = self._body.tag_names(start)
        if tag in existing:
            self._body.tag_remove(tag, start, end)
        else:
            self._body.tag_add(tag, start, end)

    def _fmt_bold(self):
        self._toggle_tag("bold")

    def _fmt_italic(self):
        self._toggle_tag("italic")

    def _fmt_underline(self):
        self._toggle_tag("underline")

    def _fmt_strike(self):
        self._toggle_tag("strike")

    def _fmt_size(self, size):
        start, end = self._get_sel()
        if not start:
            return
        tag = f"size_{size}"
        # Remove any existing size tags in selection
        for t_name in self._body.tag_names():
            if t_name.startswith("size_"):
                self._body.tag_remove(t_name, start, end)
        self._body.tag_config(tag, font=("Courier New", int(size)))
        self._body.tag_add(tag, start, end)

    def _fmt_align(self, direction):
        start, end = self._get_sel()
        if not start:
            # Apply to current line if no selection
            start = self._body.index("insert linestart")
            end   = self._body.index("insert lineend")
        for tag in ("align_left", "align_center", "align_right"):
            self._body.tag_remove(tag, start, end)
        self._body.tag_add(f"align_{direction}", start, end)

    def _fmt_colour(self, name):
        start, end = self._get_sel()
        if not start:
            return
        # Remove other colour tags
        for tag in self._body.tag_names():
            if tag.startswith("colour_"):
                self._body.tag_remove(tag, start, end)
        self._body.tag_add(f"colour_{name}", start, end)

    def _fmt_bullet(self):
        """Prefix each selected line with a bullet point."""
        start, end = self._get_sel()
        if not start:
            start = self._body.index("insert linestart")
            end   = self._body.index("insert lineend+1c")
        start_line = int(start.split(".")[0])
        end_line   = int(end.split(".")[0])
        for ln in range(start_line, end_line + 1):
            line_start = f"{ln}.0"
            current    = self._body.get(line_start, f"{ln}.end")
            if current.startswith("• "):
                self._body.delete(line_start, f"{ln}.2")
            else:
                self._body.insert(line_start, "• ")

    def _fmt_numbered(self):
        """Prefix each selected line with a sequential number."""
        start, end = self._get_sel()
        if not start:
            start = self._body.index("insert linestart")
            end   = self._body.index("insert lineend+1c")
        start_line = int(start.split(".")[0])
        end_line   = int(end.split(".")[0])
        for i, ln in enumerate(range(start_line, end_line + 1), 1):
            line_start = f"{ln}.0"
            current    = self._body.get(line_start, f"{ln}.end")
            # Remove existing numbering if present
            import re as _re
            cleaned = _re.sub(r"^\d+\.\s", "", current)
            self._body.delete(line_start, f"{ln}.end")
            self._body.insert(line_start, f"{i}. {cleaned}")

    def _fmt_clear(self):
        """Remove all formatting tags from selection."""
        start, end = self._get_sel()
        if not start:
            return
        fmt_tags = ["bold", "italic", "underline", "strike",
                    "align_left", "align_center", "align_right"]
        for tag in self._body.tag_names():
            if tag in fmt_tags or tag.startswith("size_") or tag.startswith("colour_"):
                self._body.tag_remove(tag, start, end)

    # ── Spell check ────────────────────────────────────────────────────────

    # ── Tag panel ──────────────────────────────────────────────────────────

    def _render_tag_panel(self):
        """Rebuild the tag quick-insert buttons from CSV headers + builtins."""
        t = self._t
        for w in self._tag_buttons_frame.winfo_children():
            w.destroy()

        # Decide which tags to show — CSV headers take priority, builtins fill the rest
        csv_tags = [(f"{{{{{h}}}}}", f"Column: {h}") for h in self._csv_headers] \
                   if self._csv_headers else []
        # Always show builtins at the end
        all_tags = csv_tags if csv_tags else self._builtin_tags
        # Merge: CSV tags + any builtin not already covered
        csv_names = {t[0] for t in csv_tags}
        extra = [b for b in self._builtin_tags if b[0] not in csv_names]
        all_tags = csv_tags + extra

        row_frame = ctk.CTkFrame(self._tag_buttons_frame, fg_color="transparent")
        row_frame.pack(fill="x")
        col = 0
        MAX_COLS = 6

        for tag_str, tooltip in all_tags:
            # Shorten display text for button
            display = tag_str.replace("{{", "").replace("}}", "")
            if len(display) > 14:
                display = display[:13] + "…"
            display = f"{{{{{display}}}}}" if "…" in display else tag_str

            # Colour: CSV tags = accent, builtins = dimmer
            is_csv = any(tag_str == f"{{{{{h}}}}}" for h in self._csv_headers)
            fg = t["accent"] if is_csv else t["text_dim"]
            bg = t["bg_input"]

            btn = ctk.CTkButton(
                row_frame, text=display,
                font=("Courier New", 11, "bold"),
                fg_color=bg, text_color=fg,
                border_color=t["border"], border_width=1,
                hover_color=t["bg_card"],
                width=0, height=26,
                command=lambda tag=tag_str: self._insert_tag_at_cursor(tag))
            btn.pack(side="left", padx=2, pady=2)

            col += 1
            if col >= MAX_COLS:
                row_frame = ctk.CTkFrame(
                    self._tag_buttons_frame, fg_color="transparent")
                row_frame.pack(fill="x")
                col = 0

    def _insert_tag_at_cursor(self, tag):
        try:
            self._body.insert(tk.INSERT, tag)
            self._body.focus_set()
            self._highlight_body()
        except Exception:
            pass

    def _toggle_tag_panel(self):
        self._tag_panel_open = not self._tag_panel_open
        if self._tag_panel_open:
            self._tag_panel_body.pack(fill="x", padx=6, pady=(0, 6))
            self._tag_panel_toggle.configure(text="▲ Hide")
        else:
            self._tag_panel_body.pack_forget()
            self._tag_panel_toggle.configure(text="▼ Tags")

    # ── Left-click spell suggestion popup ─────────────────────────────────

    def _on_left_click(self, event):
        """Show spell suggestions as a small popup when clicking a red word."""
        if not self._spell_on or not _SPELL_AVAILABLE:
            return

        # Check if the clicked position has the misspelled tag
        idx = self._body.index(f"@{event.x},{event.y}")
        tags_at = self._body.tag_names(idx)

        if "misspelled" not in tags_at:
            return  # not a red word — do nothing special

        # Get the word boundaries
        word_start = self._body.index(f"{idx} wordstart")
        word_end   = self._body.index(f"{idx} wordend")
        word       = re.sub(r"[^a-zA-Z']", "", self._body.get(word_start, word_end))

        if not word or len(word) < 2:
            return

        candidates = self._spell.candidates(word.lower()) or set()
        suggestions = sorted(candidates,
                              key=lambda w: self._spell.word_probability(w),
                              reverse=True)[:6]
        if not suggestions:
            return

        t = self._t

        # Build a small popup menu anchored at click position
        popup = tk.Menu(self, tearoff=0,
                        bg=t["bg_card"], fg=t["text_main"],
                        activebackground=t["accent_dim"],
                        activeforeground="#000",
                        font=("Courier New", 13), bd=0,
                        relief="flat")

        popup.add_command(
            label=f'  "{word}" — did you mean:',
            state="disabled",
            font=("Courier New", 11))
        popup.add_separator()

        for suggestion in suggestions:
            if word[0].isupper():
                suggestion = suggestion.capitalize()
            popup.add_command(
                label=f"  ✓  {suggestion}",
                font=("Courier New", 13, "bold"),
                foreground=t["accent"],
                activeforeground="#000",
                command=lambda s=suggestion, ws=word_start, we=word_end:
                    self._replace_word(ws, we, s))

        popup.add_separator()
        popup.add_command(
            label="  + Add to dictionary",
            command=lambda w=word: self._add_to_dict(w))
        popup.add_command(
            label="  Ignore",
            command=lambda ws=word_start, we=word_end:
                self._body.tag_remove("misspelled", ws, we))

        try:
            popup.tk_popup(event.x_root, event.y_root)
        finally:
            popup.grab_release()

    def _toggle_spell(self):
        if not _SPELL_AVAILABLE:
            messagebox.showinfo("Spell Check",
                "Install pyspellchecker to enable:\n\npip install pyspellchecker")
            return
        self._spell_on = not self._spell_on
        t = self._t
        if self._spell_on:
            self._spell_btn.configure(
                text="✓ Spell",
                fg_color=t["accent_dim"], text_color="#000")
            self._run_spellcheck()
        else:
            self._spell_btn.configure(
                text="○ Spell",
                fg_color="transparent", text_color=t["text_dim"])
            self._body.tag_remove("misspelled", "1.0", "end")

    def _on_key_release(self, event=None):
        self._highlight_body()
        if self._spell_on and _SPELL_AVAILABLE:
            # Debounce — run spellcheck 600ms after last keypress
            if self._spell_after_id:
                self.after_cancel(self._spell_after_id)
            self._spell_after_id = self.after(600, self._run_spellcheck)

    def _run_spellcheck(self):
        """Find all misspelled words and tag them red."""
        if not self._spell_on or not _SPELL_AVAILABLE:
            return
        body = self._body
        body.tag_remove("misspelled", "1.0", "end")
        full_text = body.get("1.0", "end")

        # Extract plain words only — skip {{tags}} and [placeholders]
        # We tokenise line by line to get accurate positions
        for line_num, line in enumerate(full_text.split("\n"), start=1):
            # Skip words inside {{ }} or [ ]
            clean = re.sub(r"\{\{[^}]*\}\}", lambda m: " " * len(m.group()), line)
            clean = re.sub(r"\[[^\]]*\]",    lambda m: " " * len(m.group()), clean)

            for match in re.finditer(r"\b[a-zA-Z']+\b", clean):
                word = match.group()
                # Skip very short words, proper-noun-like (capitalised mid-sentence), numbers
                if len(word) <= 2:
                    continue
                # Check spelling
                if self._spell.unknown([word.lower()]):
                    start = f"{line_num}.{match.start()}"
                    end   = f"{line_num}.{match.end()}"
                    body.tag_add("misspelled", start, end)

    def _show_spell_menu(self, event):
        """Right-click: if on a misspelled word show suggestions, always show standard options."""
        t = self._t
        # Find word under cursor
        idx = self._body.index(f"@{event.x},{event.y}")
        word_start = self._body.index(f"{idx} wordstart")
        word_end   = self._body.index(f"{idx} wordend")
        word       = self._body.get(word_start, word_end).strip()
        word_clean = re.sub(r"[^a-zA-Z']", "", word)

        menu = tk.Menu(self, tearoff=0,
                       bg=t["bg_card"], fg=t["text_main"],
                       activebackground=t["accent_dim"],
                       activeforeground="#000",
                       font=("Courier New", 12), bd=0,
                       relief="flat")

        is_misspelled = (
            _SPELL_AVAILABLE and self._spell_on and
            len(word_clean) > 2 and
            bool(self._spell.unknown([word_clean.lower()]))
        )

        if is_misspelled and word_clean:
            # Header
            menu.add_command(label=f'  "{word_clean}" — suggestions:',
                             state="disabled",
                             font=("Courier New", 11, "bold"))
            menu.add_separator()

            candidates = self._spell.candidates(word_clean.lower()) or set()
            # Sort by edit distance — best first
            suggestions = sorted(candidates,
                key=lambda w: self._spell.word_probability(w),
                reverse=True)[:8]

            if suggestions:
                for suggestion in suggestions:
                    # Preserve original capitalisation
                    if word_clean[0].isupper():
                        suggestion = suggestion.capitalize()
                    menu.add_command(
                        label=f"  ✓  {suggestion}",
                        font=("Courier New", 13, "bold"),
                        foreground=t["accent"],
                        activeforeground="#000",
                        command=lambda s=suggestion, ws=word_start, we=word_end:
                            self._replace_word(ws, we, s))
            else:
                menu.add_command(label="  No suggestions found",
                                 state="disabled")

            menu.add_separator()
            menu.add_command(
                label="  + Add to dictionary",
                command=lambda w=word_clean: self._add_to_dict(w))
            menu.add_separator()

        # Standard edit options always shown
        menu.add_command(label="  Cut",   command=lambda: self._body.event_generate("<<Cut>>"))
        menu.add_command(label="  Copy",  command=lambda: self._body.event_generate("<<Copy>>"))
        menu.add_command(label="  Paste", command=lambda: self._body.event_generate("<<Paste>>"))
        if is_misspelled:
            menu.add_separator()
            menu.add_command(label="  Ignore this word",
                             command=lambda ws=word_start, we=word_end:
                                 self._body.tag_remove("misspelled", ws, we))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _replace_word(self, start, end, replacement):
        self._body.delete(start, end)
        self._body.insert(start, replacement)
        self._run_spellcheck()
        self._highlight_body()

    def _add_to_dict(self, word):
        if self._spell:
            self._spell.word_frequency.add(word.lower())
            self._run_spellcheck()
            self._log_line(f'Added "{word}" to dictionary.', "ok")

    def _highlight_body(self):
        """Highlight {{csv_tags}} in accent colour and [placeholders] in orange."""
        body = self._body
        for tag in ("csv_tag", "placeholder"):
            body.tag_remove(tag, "1.0", "end")
        # {{tags}}
        start = "1.0"
        while True:
            pos = body.search(r"\{\{[^}]+\}\}", start, "end", regexp=True)
            if not pos:
                break
            match_end = body.index(f"{pos} wordend")
            # find the closing }}
            line_text = body.get(pos, f"{pos} lineend")
            m = re.search(r"\{\{[^}]+\}\}", line_text)
            if m:
                end_pos = f"{pos}+{m.end()}c"
                body.tag_add("csv_tag", pos, end_pos)
                start = end_pos
            else:
                start = match_end
        # [placeholders]
        start = "1.0"
        while True:
            pos = body.search(r"\[[^\]]+\]", start, "end", regexp=True)
            if not pos:
                break
            line_text = body.get(pos, f"{pos} lineend")
            m = re.search(r"\[[^\]]+\]", line_text)
            if m:
                end_pos = f"{pos}+{m.end()}c"
                body.tag_add("placeholder", pos, end_pos)
                start = end_pos
            else:
                start = f"{pos}+1c"

    def _fill_placeholders(self):
        """Scan body + subject for [placeholders] and walk user through filling them."""
        t = self._t
        body_text    = self._body.get("1.0", "end")
        subject_text = self._subject.get()
        combined     = subject_text + "\n" + body_text

        # Find all unique [placeholder] values
        found = list(dict.fromkeys(re.findall(r"\[([^\]]+)\]", combined)))
        if not found:
            messagebox.showinfo("No Placeholders",
                "No [placeholders] found in your subject or body.\n\n"
                "Placeholders look like: [Event Name], [Date], [Your Link]")
            return

        win = ctk.CTkToplevel(self)
        win.title("Fill Placeholders")
        win.geometry("520x" + str(min(120 + len(found) * 80, 600)))
        win.configure(fg_color=t["bg_main"])
        win.grab_set()
        win.resizable(False, False)

        # Header
        head = ctk.CTkFrame(win, fg_color=t["bg_sidebar"],
                             corner_radius=0, height=48)
        head.pack(fill="x")
        head.pack_propagate(False)
        ctk.CTkLabel(head, text="FILL PLACEHOLDERS",
                     font=FONT_HEAD, text_color=ORANGE).pack(side="left", padx=18)
        ctk.CTkLabel(head, text=f"{len(found)} found",
                     font=FONT_SMALL, text_color=t["text_dim"]).pack(side="left")

        scroll = ctk.CTkScrollableFrame(win, fg_color=t["bg_main"],
                                         scrollbar_button_color=t["border"])
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        entries = {}
        for name in found:
            row = ctk.CTkFrame(scroll, fg_color=t["bg_card"], corner_radius=8)
            row.pack(fill="x", padx=16, pady=(10, 0))

            # Label with orange bracket styling
            lbl_frame = ctk.CTkFrame(row, fg_color="transparent")
            lbl_frame.pack(fill="x", padx=12, pady=(10, 4))
            ctk.CTkLabel(lbl_frame, text="[", font=FONT_LABEL,
                         text_color=ORANGE).pack(side="left")
            ctk.CTkLabel(lbl_frame, text=name, font=FONT_LABEL,
                         text_color=t["text_main"]).pack(side="left")
            ctk.CTkLabel(lbl_frame, text="]", font=FONT_LABEL,
                         text_color=ORANGE).pack(side="left")
            ctk.CTkLabel(lbl_frame, text=" → replace with:",
                         font=FONT_SMALL, text_color=t["text_dim"]).pack(side="left", padx=(4, 0))

            entry = ctk.CTkEntry(row, font=FONT_MONO,
                                  fg_color=t["bg_input"],
                                  border_color=ORANGE,
                                  text_color=t["text_main"],
                                  placeholder_text=f"Enter value for [{name}]")
            entry.pack(fill="x", padx=12, pady=(0, 10))
            entries[name] = entry

        # Bottom bar
        btn_bar = ctk.CTkFrame(win, fg_color=t["bg_sidebar"],
                                corner_radius=0, height=54)
        btn_bar.pack(fill="x", side="bottom")
        btn_bar.pack_propagate(False)

        def apply_all():
            new_subj = self._subject.get()
            new_body = self._body.get("1.0", "end")
            replaced = 0
            skipped  = []
            for name, entry in entries.items():
                val = entry.get().strip()
                if val:
                    new_subj = new_subj.replace(f"[{name}]", val)
                    new_body = new_body.replace(f"[{name}]", val)
                    replaced += 1
                else:
                    skipped.append(name)

            self._subject.delete(0, "end")
            self._subject.insert(0, new_subj)
            self._body.delete("1.0", "end")
            self._body.insert("1.0", new_body.rstrip("\n"))
            self._highlight_body()
            win.destroy()

            msg = f"{replaced} placeholder(s) replaced."
            if skipped:
                msg += f"\n\nSkipped (left blank):\n" + "\n".join(f"  [{s}]" for s in skipped)
            self._log_line(f"Placeholders filled: {replaced} replaced, {len(skipped)} skipped.", "ok")
            messagebox.showinfo("Done", msg)

        ctk.CTkButton(btn_bar, text="Apply All & Close",
                      font=FONT_LABEL,
                      fg_color=ORANGE, text_color="#000",
                      hover_color="#cc8800", width=180,
                      command=apply_all).pack(side="right", padx=14, pady=10)

        ctk.CTkButton(btn_bar, text="Cancel", font=FONT_SMALL,
                      fg_color="transparent", border_color=t["border"],
                      border_width=1, text_color=t["text_dim"],
                      hover_color=t["bg_card"], width=80,
                      command=win.destroy).pack(side="right", padx=(0, 6), pady=10)

        ctk.CTkLabel(btn_bar,
                     text="Blank fields will keep the original [placeholder] text",
                     font=FONT_SMALL, text_color=t["text_dim"]
                     ).pack(side="left", padx=14)

    def _open_templates(self):
        t = self._t
        win = ctk.CTkToplevel(self)
        win.title("Email Templates")
        win.geometry("780x620")
        win.configure(fg_color=t["bg_main"])
        win.grab_set()

        # Header
        head = ctk.CTkFrame(win, fg_color=t["bg_sidebar"],
                             corner_radius=0, height=48)
        head.pack(fill="x")
        head.pack_propagate(False)
        ctk.CTkLabel(head, text="EMAIL TEMPLATES",
                     font=FONT_HEAD, text_color=t["accent"]).pack(side="left", padx=18)
        ctk.CTkLabel(head, text="Pick one to load into the composer",
                     font=FONT_SMALL, text_color=t["text_dim"]).pack(side="left", padx=(0, 0))

        body = ctk.CTkFrame(win, fg_color=t["bg_main"])
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # Template list sidebar
        nav = ctk.CTkFrame(body, fg_color=t["bg_sidebar"],
                            corner_radius=0, width=220)
        nav.grid(row=0, column=0, sticky="nsew")
        nav.grid_propagate(False)
        ctk.CTkLabel(nav, text="TEMPLATES", font=FONT_LABEL,
                     text_color=t["text_dim"]).pack(anchor="w", padx=16, pady=(16, 8))

        # Preview area
        preview_frame = ctk.CTkFrame(body, fg_color=t["bg_main"], corner_radius=0)
        preview_frame.grid(row=0, column=1, sticky="nsew")
        preview_frame.rowconfigure(1, weight=1)
        preview_frame.columnconfigure(0, weight=1)

        # Subject preview
        subj_frame = ctk.CTkFrame(preview_frame, fg_color=t["bg_card"],
                                   corner_radius=0, height=44)
        subj_frame.grid(row=0, column=0, sticky="ew")
        subj_frame.grid_propagate(False)
        ctk.CTkLabel(subj_frame, text="SUBJECT", font=FONT_LABEL,
                     text_color=t["text_dim"]).pack(side="left", padx=14)
        self._tpl_subj_label = ctk.CTkLabel(
            subj_frame, text="Select a template to preview",
            font=FONT_MONO, text_color=t["text_main"])
        self._tpl_subj_label.pack(side="left", padx=(0, 14))

        # Body preview
        prev_text = tk.Text(preview_frame, font=FONT_MONO,
                             bg=t["bg_input"], fg=t["text_main"],
                             relief="flat", bd=0, wrap="word",
                             highlightthickness=0,
                             padx=16, pady=16, state="disabled",
                             selectbackground=t["accent_dim"])
        prev_text.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        prev_text.tag_config("csv_tag",     foreground=t["accent"],
                              font=("Courier New", 13, "bold"))
        prev_text.tag_config("placeholder", foreground=ORANGE,
                              font=("Courier New", 13, "bold"))

        def highlight_preview(widget):
            for tag in ("csv_tag", "placeholder"):
                widget.tag_remove(tag, "1.0", "end")
            for pattern, tag in [(r"\{\{[^}]+\}\}", "csv_tag"),
                                  (r"\[[^\]]+\]",    "placeholder")]:
                start = "1.0"
                while True:
                    pos = widget.search(pattern, start, "end", regexp=True)
                    if not pos:
                        break
                    line_text = widget.get(pos, f"{pos} lineend")
                    m = re.search(pattern, line_text)
                    if m:
                        end_pos = f"{pos}+{m.end()}c"
                        widget.tag_add(tag, pos, end_pos)
                        start = end_pos
                    else:
                        start = f"{pos}+1c"

        # Use button
        use_btn = ctk.CTkButton(preview_frame, text="Use This Template",
                                 font=FONT_HEAD,
                                 fg_color=t["accent"], text_color="#000",
                                 hover_color=t["accent_dim"],
                                 state="disabled",
                                 command=lambda: None)
        use_btn.grid(row=2, column=0, sticky="ew", padx=16, pady=12)

        selected_tpl = {"data": None}

        def preview_template(name):
            tpl = EMAIL_TEMPLATES.get(name)
            if not tpl:
                return
            selected_tpl["data"] = tpl
            self._tpl_subj_label.configure(text=tpl["subject"])
            prev_text.configure(state="normal")
            prev_text.delete("1.0", "end")
            prev_text.insert("1.0", tpl["body"])
            highlight_preview(prev_text)
            prev_text.configure(state="disabled")
            use_btn.configure(state="normal",
                command=lambda: load_template(name))
            # Highlight active
            for b in nav_btns:
                active = b.cget("text") == name
                b.configure(
                    fg_color=t["bg_card"] if active else t["bg_sidebar"],
                    text_color=t["accent"] if active else t["text_dim"])

        def load_template(name):
            tpl = EMAIL_TEMPLATES.get(name)
            if not tpl:
                return
            # Load into composer
            self._subject.delete(0, "end")
            self._subject.insert(0, tpl["subject"])
            self._body.delete("1.0", "end")
            self._body.insert("1.0", tpl["body"])
            win.destroy()
            self._highlight_body()
            self._log_line(f"Template loaded: {name}", "ok")

        nav_btns = []
        for name, tpl in EMAIL_TEMPLATES.items():
            if tpl is None:
                ctk.CTkLabel(nav, text="────────────────",
                             font=FONT_SMALL,
                             text_color=t["border"]).pack(padx=12, pady=(0, 4))
                continue
            btn = ctk.CTkButton(nav, text=name, font=FONT_SMALL,
                                 fg_color=t["bg_sidebar"],
                                 text_color=t["text_dim"],
                                 hover_color=t["bg_card"],
                                 anchor="w",
                                 command=lambda n=name: preview_template(n))
            btn.pack(fill="x", padx=8, pady=2)
            nav_btns.append(btn)

        # Auto-select first real template
        first = next((n for n, v in EMAIL_TEMPLATES.items() if v), None)
        if first:
            preview_template(first)

    def _show_tag_menu(self):
        if not self._csv_headers:
            messagebox.showinfo("No CSV", "Import a CSV first to see available tags.")
            return
        t = self._t
        menu = tk.Menu(self, tearoff=0,
                       bg=t["bg_card"], fg=t["text_main"],
                       activebackground=t["accent_dim"],
                       activeforeground="#000",
                       font=FONT_MONO, bd=0)

        menu.add_command(label="  ── Your CSV columns ──",
                         state="disabled",
                         font=("Courier New", 11))

        for h in self._csv_headers:
            # Show sample value from first contact if available
            sample = ""
            if self._contacts:
                val = self._contacts[0].get(h, "")
                if val:
                    sample = f"  →  {val[:20]}"
            menu.add_command(
                label=f"  {{{{{h}}}}} {sample}",
                font=("Courier New", 12, "bold"),
                foreground=t["accent"],
                command=lambda tag=f"{{{{{h}}}}}":
                    self._body.insert(tk.INSERT, tag))

        menu.add_separator()
        menu.add_command(label="  📋  View tag reference",
                         font=("Courier New", 11),
                         command=self._open_tag_reference)

        try:
            x = self._tag_btn.winfo_rootx()
            y = self._tag_btn.winfo_rooty() + self._tag_btn.winfo_height()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _open_tag_reference(self):
        """Show a full tag reference window with all columns and sample values."""
        t = self._t
        win = ctk.CTkToplevel(self)
        win.title("Tag Reference")
        win.geometry("620x500")
        win.configure(fg_color=t["bg_main"])
        win.grab_set()

        # Header
        head = ctk.CTkFrame(win, fg_color=t["bg_sidebar"],
                             corner_radius=0, height=48)
        head.pack(fill="x")
        head.pack_propagate(False)
        ctk.CTkLabel(head, text="TAG REFERENCE",
                     font=FONT_HEAD, text_color=t["accent"]).pack(side="left", padx=18)
        if self._contacts:
            ctk.CTkLabel(head, text=f"Sample from row 1 of {len(self._contacts)} contacts",
                         font=FONT_SMALL, text_color=t["text_dim"]).pack(side="left")

        if not self._csv_headers:
            ctk.CTkLabel(win, text="No CSV loaded — import a CSV first.",
                         font=FONT_MONO, text_color=t["text_dim"]).pack(pady=40)
            return

        # Info bar
        info = ctk.CTkFrame(win, fg_color=t["bg_card"], corner_radius=0, height=36)
        info.pack(fill="x")
        info.pack_propagate(False)
        ctk.CTkLabel(info,
                     text="  Click any tag to insert it into your email body. Tags are case-insensitive.",
                     font=FONT_SMALL, text_color=t["text_dim"]).pack(side="left", padx=8)

        # Tag table
        scroll = ctk.CTkScrollableFrame(win, fg_color=t["bg_main"],
                                         scrollbar_button_color=t["border"])
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Column headers
        hdr = ctk.CTkFrame(scroll, fg_color=t["bg_card"], corner_radius=0)
        hdr.pack(fill="x", padx=16, pady=(12, 4))
        hdr.columnconfigure(0, weight=1)
        hdr.columnconfigure(1, weight=1)
        hdr.columnconfigure(2, weight=2)
        ctk.CTkLabel(hdr, text="  CSV COLUMN", font=FONT_LABEL,
                     text_color=t["text_dim"]).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ctk.CTkLabel(hdr, text="TAG TO USE", font=FONT_LABEL,
                     text_color=t["text_dim"]).grid(row=0, column=1, sticky="w", padx=8, pady=6)
        ctk.CTkLabel(hdr, text="SAMPLE VALUE", font=FONT_LABEL,
                     text_color=t["text_dim"]).grid(row=0, column=2, sticky="w", padx=8, pady=6)

        for i, col in enumerate(self._csv_headers):
            row_bg = t["bg_card"] if i % 2 == 0 else t["bg_input"]
            row_frame = ctk.CTkFrame(scroll, fg_color=row_bg, corner_radius=0)
            row_frame.pack(fill="x", padx=16, pady=0)
            row_frame.columnconfigure(0, weight=1)
            row_frame.columnconfigure(1, weight=1)
            row_frame.columnconfigure(2, weight=2)

            sample_val = ""
            if self._contacts:
                sample_val = self._contacts[0].get(col, "—")

            ctk.CTkLabel(row_frame, text=f"  {col}",
                         font=FONT_MONO, text_color=t["text_main"],
                         anchor="w").grid(row=0, column=0, sticky="w", padx=8, pady=8)

            tag_str = f"{{{{{col}}}}}"
            tag_btn = ctk.CTkButton(row_frame, text=tag_str,
                                     font=("Courier New", 13, "bold"),
                                     fg_color="transparent",
                                     text_color=t["accent"],
                                     hover_color=t["bg_card"],
                                     anchor="w",
                                     command=lambda tg=tag_str: [
                                         self._body.insert(tk.INSERT, tg),
                                         win.destroy()])
            tag_btn.grid(row=0, column=1, sticky="w", padx=4, pady=4)

            ctk.CTkLabel(row_frame, text=str(sample_val)[:40],
                         font=FONT_MONO, text_color=t["text_dim"],
                         anchor="w").grid(row=0, column=2, sticky="w", padx=8, pady=8)

        # Footer tip
        tip = ctk.CTkFrame(win, fg_color=t["bg_sidebar"], corner_radius=0, height=44)
        tip.pack(fill="x", side="bottom")
        tip.pack_propagate(False)
        ctk.CTkLabel(tip,
                     text="  💡  {{first_name}}, {{First_Name}}, and {{FIRST_NAME}} all work the same way",
                     font=FONT_SMALL, text_color=t["text_dim"]).pack(side="left", padx=12, pady=12)

    def _open_tag_inspector(self):
        """Browse contacts one by one and see exactly what each tag resolves to."""
        t = self._t
        if not self._contacts:
            messagebox.showinfo("No contacts",
                "Import a CSV first to use the Tag Inspector.")
            return

        win = ctk.CTkToplevel(self)
        win.title("Tag Inspector")
        win.geometry("900x620")
        win.configure(fg_color=t["bg_main"])
        win.grab_set()

        # ── Header ────────────────────────────────────────────────────────
        head = ctk.CTkFrame(win, fg_color=t["bg_sidebar"],
                             corner_radius=0, height=50)
        head.pack(fill="x")
        head.pack_propagate(False)
        ctk.CTkLabel(head, text="🔍  TAG INSPECTOR",
                     font=FONT_HEAD, text_color=t["accent"]).pack(side="left", padx=18)
        ctk.CTkLabel(head,
                     text="See exactly what each {{tag}} will say for every contact",
                     font=FONT_SMALL, text_color=t["text_dim"]).pack(side="left")

        # ── Contact navigator ─────────────────────────────────────────────
        nav_bar = ctk.CTkFrame(win, fg_color=t["bg_card"],
                                corner_radius=0, height=44)
        nav_bar.pack(fill="x")
        nav_bar.pack_propagate(False)

        idx_var = {"i": 0}
        total   = len(self._contacts)

        counter_lbl = ctk.CTkLabel(nav_bar,
                                    text=f"Contact 1 of {total}",
                                    font=FONT_LABEL, text_color=t["text_main"])
        counter_lbl.pack(side="left", padx=18)

        email_lbl = ctk.CTkLabel(nav_bar, text="",
                                  font=FONT_SMALL, text_color=t["text_dim"])
        email_lbl.pack(side="left", padx=(0, 18))

        ctk.CTkButton(nav_bar, text="▶ Next", font=FONT_SMALL,
                      fg_color=t["accent_dim"], text_color="#000",
                      hover_color=t["accent"], width=80,
                      command=lambda: navigate(1)).pack(side="right", padx=(4, 14), pady=8)
        ctk.CTkButton(nav_bar, text="◀ Prev", font=FONT_SMALL,
                      fg_color="transparent", border_color=t["border"],
                      border_width=1, text_color=t["text_dim"],
                      hover_color=t["bg_input"], width=80,
                      command=lambda: navigate(-1)).pack(side="right", padx=4, pady=8)

        # Jump to specific contact
        ctk.CTkLabel(nav_bar, text="Jump to:", font=FONT_SMALL,
                     text_color=t["text_dim"]).pack(side="right", padx=(0, 4))
        jump_var = ctk.StringVar(value="1")
        jump_entry = ctk.CTkEntry(nav_bar, textvariable=jump_var,
                                   font=FONT_SMALL, width=50,
                                   fg_color=t["bg_input"],
                                   border_color=t["border"],
                                   text_color=t["text_main"])
        jump_entry.pack(side="right", padx=(0, 4), pady=8)
        jump_entry.bind("<Return>", lambda e: jump())

        def jump():
            try:
                n = int(jump_var.get()) - 1
                if 0 <= n < total:
                    idx_var["i"] = n
                    refresh()
            except ValueError:
                pass

        # ── Body: tag table + email preview ──────────────────────────────
        body = ctk.CTkFrame(win, fg_color=t["bg_main"])
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # Left: tag table
        tag_frame = ctk.CTkFrame(body, fg_color=t["bg_sidebar"], corner_radius=0)
        tag_frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(tag_frame, text="TAG VALUES FOR THIS CONTACT",
                     font=FONT_LABEL, text_color=t["text_dim"]
                     ).pack(anchor="w", padx=16, pady=(12, 6))

        tag_scroll = ctk.CTkScrollableFrame(tag_frame, fg_color=t["bg_sidebar"],
                                             scrollbar_button_color=t["border"])
        tag_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        tag_rows = {}  # field → (tag_lbl, val_lbl)

        for field in self._csv_headers:
            row_f = ctk.CTkFrame(tag_scroll, fg_color=t["bg_card"], corner_radius=6)
            row_f.pack(fill="x", pady=3)
            row_f.columnconfigure(1, weight=1)

            ctk.CTkLabel(row_f, text=f" {{{{{field}}}}} ",
                         font=("Courier New", 12, "bold"),
                         text_color=t["accent"],
                         width=140, anchor="w"
                         ).grid(row=0, column=0, padx=(8, 4), pady=8, sticky="w")

            val_lbl = ctk.CTkLabel(row_f, text="",
                                    font=("Courier New", 12),
                                    text_color=t["text_main"],
                                    anchor="w")
            val_lbl.grid(row=0, column=1, padx=(0, 8), pady=8, sticky="ew")

            tag_rows[field] = val_lbl

        # Right: live email preview
        prev_frame = ctk.CTkFrame(body, fg_color=t["bg_main"], corner_radius=0)
        prev_frame.grid(row=0, column=1, sticky="nsew")
        prev_frame.rowconfigure(1, weight=1)
        prev_frame.columnconfigure(0, weight=1)

        subj_bar = ctk.CTkFrame(prev_frame, fg_color=t["bg_card"],
                                 corner_radius=0, height=40)
        subj_bar.grid(row=0, column=0, sticky="ew")
        subj_bar.grid_propagate(False)
        ctk.CTkLabel(subj_bar, text="SUBJECT:", font=FONT_LABEL,
                     text_color=t["text_dim"]).pack(side="left", padx=12)
        subj_preview = ctk.CTkLabel(subj_bar, text="",
                                     font=FONT_MONO, text_color=t["text_main"])
        subj_preview.pack(side="left")

        ctk.CTkLabel(prev_frame, text="EMAIL PREVIEW FOR THIS CONTACT",
                     font=FONT_LABEL, text_color=t["text_dim"]
                     ).grid(row=0, column=0, sticky="w", padx=16, pady=(0, 0))

        body_preview = tk.Text(prev_frame, font=("Courier New", 12),
                                bg=t["bg_input"], fg=t["text_main"],
                                relief="flat", bd=0, wrap="word",
                                highlightthickness=0,
                                padx=14, pady=12, state="disabled",
                                selectbackground=t["accent_dim"])
        body_preview.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)

        # ── Refresh function ──────────────────────────────────────────────
        def refresh():
            i   = idx_var["i"]
            row = self._contacts[i]

            # Update navigator
            email_col = next(
                (h for h in self._csv_headers if "email" in h.lower()), "email")
            counter_lbl.configure(text=f"Contact {i+1} of {total}")
            email_lbl.configure(text=row.get(email_col, ""))
            jump_var.set(str(i + 1))

            # Update tag table
            for field, lbl in tag_rows.items():
                val = row.get(field, "")
                lbl.configure(
                    text=val if val else "— (empty)",
                    text_color=t["text_main"] if val else t["text_dim"])

            # Update subject preview
            subj_text = personalise(self._subject.get(), row, self._config)
            subj_preview.configure(text=subj_text or "(no subject)")

            # Update body preview
            body_text = personalise(self._body.get("1.0", "end"), row, self._config)
            body_preview.configure(state="normal")
            body_preview.delete("1.0", "end")
            body_preview.insert("1.0", body_text.strip())
            body_preview.configure(state="disabled")

        def navigate(direction):
            idx_var["i"] = (idx_var["i"] + direction) % total
            refresh()

        # ── Bottom tip ────────────────────────────────────────────────────
        tip = ctk.CTkFrame(win, fg_color=t["bg_sidebar"],
                            corner_radius=0, height=36)
        tip.pack(fill="x", side="bottom")
        tip.pack_propagate(False)
        ctk.CTkLabel(tip,
                     text="  💡  Left panel shows raw tag values · Right panel shows the final email · Use ◀ ▶ to browse all contacts",
                     font=FONT_SMALL, text_color=t["text_dim"]
                     ).pack(side="left", padx=12, pady=8)

        refresh()

    def _preview(self):
        if not self._contacts:
            messagebox.showinfo("No contacts", "Import a CSV to preview.")
            return
        t    = self._t
        row  = self._contacts[0]
        subj = personalise(self._subject.get(), row, self._config)
        body = personalise(self._body.get("1.0", "end"), row, self._config)
        win  = ctk.CTkToplevel(self)
        win.title("Preview — First Contact")
        win.geometry("640x500")
        win.configure(fg_color=t["bg_main"])
        ctk.CTkLabel(win, text="PREVIEW", font=FONT_HEAD,
                     text_color=t["accent"]
                     ).pack(anchor="w", padx=20, pady=(16, 4))
        ctk.CTkLabel(win, text=f"To:      {row.get('email', '?')}",
                     font=FONT_MONO, text_color=t["text_dim"]
                     ).pack(anchor="w", padx=20)
        ctk.CTkLabel(win, text=f"Subject: {subj}",
                     font=FONT_MONO, text_color=t["text_dim"]
                     ).pack(anchor="w", padx=20)
        ctk.CTkFrame(win, fg_color=t["border"], height=1
                     ).pack(fill="x", padx=20, pady=10)
        txt = tk.Text(win, font=FONT_MONO,
                      bg=t["bg_card"], fg=t["text_main"],
                      relief="flat", bd=0, padx=14, pady=10,
                      highlightthickness=0, wrap="word")
        txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        txt.insert("1.0", body)
        txt.configure(state="disabled")

    # ── Sending ────────────────────────────────────────────────────────────

    def _start_send(self):
        if self._sending:
            return
        if not self._contacts:
            messagebox.showwarning("No contacts", "Import a CSV first.")
            return
        subj = self._subject.get().strip()
        body = self._body.get("1.0", "end").strip()
        if not subj or not body:
            messagebox.showwarning("Missing", "Subject and body are required.")
            return
        host, port, user, pwd, tls = self._get_smtp()
        if not all([host, user, pwd]):
            messagebox.showwarning("SMTP", "Fill in host, email, and password.")
            return
        if not messagebox.askyesno("Confirm Send",
                f"Send to {len(self._contacts)} contacts?\n\nThis cannot be undone."):
            return
        self._sending = True
        self._stop_flag.clear()
        self._send_btn.configure(state="disabled")
        self._stop_btn.configure(
            state="normal",
            fg_color=RED, text_color="#fff",
            hover_color="#cc0000")
        self._set_status("SENDING", ORANGE)
        threading.Thread(target=self._send_thread,
                         args=(host, port, user, pwd, tls, subj, body),
                         daemon=True).start()

    def _stop_send(self):
        self._stop_flag.set()
        self._log_line("Stop requested…", "warn")

    def _send_thread(self, host, port, user, pwd, tls, subj_tpl, body_tpl):
        email_col = next(
            (h for h in self._csv_headers if "email" in h.lower()), None)
        total, sent, failed = len(self._contacts), 0, 0
        lf = lw = log_path = None

        if self._track_var.get():
            log_path = Path.home() / \
                f"letustech_sent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            lf = open(log_path, "w", newline="", encoding="utf-8")
            lw = csv.writer(lf)
            lw.writerow(["email", "status", "timestamp"])

        def connect_smtp():
            """Create and return a fresh authenticated SMTP connection."""
            if tls == "SSL/TLS":
                s = smtplib.SMTP_SSL(
                    host, port,
                    context=ssl.create_default_context(), timeout=15)
            else:
                s = smtplib.SMTP(host, port, timeout=15)
                if tls == "STARTTLS":
                    s.starttls(context=ssl.create_default_context())
            s.login(user, pwd)
            return s

        server = None
        try:
            server = connect_smtp()
            self._log_line(f"Connected to {host}:{port}", "ok")

            delay = float(self._delay_var.get() or 1)

            for i, row in enumerate(self._contacts):
                if self._stop_flag.is_set():
                    self._log_line("Stopped.", "warn")
                    break

                to_email = row.get(email_col, "").strip()
                if not validate_email(to_email):
                    self._log_line(f"Skip invalid: {to_email}", "warn")
                    failed += 1
                    continue

                msg = MIMEMultipart("alternative")
                msg["Subject"] = personalise(subj_tpl, row, self._config)
                msg["From"]    = (f"{self._from_name.get().strip() or user}"
                                  f" <{user}>")
                msg["To"]      = to_email
                body_text = personalise(body_tpl, row, self._config)
                msg.attach(MIMEText(
                    body_text,
                    "html" if self._html_var.get() else "plain"))

                if self._attachment:
                    try:
                        with open(self._attachment, "rb") as af:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(af.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition",
                            f"attachment; "
                            f"filename={Path(self._attachment).name}")
                        msg.attach(part)
                    except Exception as ae:
                        self._log_line(f"Attachment error: {ae}", "warn")

                # Try sending — reconnect once if connection dropped
                for attempt in range(2):
                    try:
                        server.sendmail(user, to_email, msg.as_string())
                        sent += 1
                        self._log_line(f"OK  {to_email}", "ok")
                        if lw:
                            lw.writerow([to_email, "sent",
                                         datetime.now().isoformat()])
                        break  # success
                    except smtplib.SMTPServerDisconnected:
                        if attempt == 0:
                            self._log_line("Connection dropped — reconnecting…", "warn")
                            try:
                                server = connect_smtp()
                                self._log_line("Reconnected.", "ok")
                            except Exception as re_err:
                                self._log_line(f"Reconnect failed: {re_err}", "err")
                                failed += 1
                                if lw:
                                    lw.writerow([to_email, f"reconnect failed",
                                                 datetime.now().isoformat()])
                                break
                        else:
                            failed += 1
                            self._log_line(f"FAIL  {to_email} — could not reconnect", "err")
                            if lw:
                                lw.writerow([to_email, "failed: disconnected",
                                             datetime.now().isoformat()])
                    except Exception as se:
                        failed += 1
                        self._log_line(f"FAIL  {to_email} — {se}", "err")
                        if lw:
                            lw.writerow([to_email, f"failed: {se}",
                                         datetime.now().isoformat()])
                        break

                self._progress_var.set((i + 1) / total)
                self._prog_label.configure(
                    text=(f"{i+1} / {total}  |  "
                          f"{sent} sent  |  {failed} failed"))

                if i < total - 1 and not self._stop_flag.is_set():
                    time.sleep(delay)

            try:
                server.quit()
            except Exception:
                pass

        except Exception as e:
            self._log_line(f"SMTP error: {e}", "err")
            self._log_line("Check your host, port, email and password in SMTP settings.", "warn")
        finally:
            self._sending = False
            if lf:
                lf.close()
                self._log_line(f"Log saved: {log_path}", "ok")
            self.after(0, self._send_done, sent, failed)

    def _send_done(self, sent, failed):
        self._send_btn.configure(state="normal")
        self._stop_btn.configure(
            state="disabled",
            fg_color=self._t["border"],
            text_color=self._t["text_dim"],
            hover_color=self._t["border"])
        self._set_status(
            f"DONE — {sent} sent, {failed} failed",
            self._t["accent"] if failed == 0 else ORANGE)
        self._log_line(
            f"Campaign complete — {sent} sent, {failed} failed.", "ok")
        messagebox.showinfo("Done",
            f"Campaign complete!\n\n"
            f"Sent:   {sent}\n"
            f"Failed: {failed}")


# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = BulkEmailApp()
    app.mainloop()
