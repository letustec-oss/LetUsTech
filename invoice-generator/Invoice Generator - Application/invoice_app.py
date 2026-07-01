"""
Invoice Generator
A free, professional desktop invoice management application.
Built by Deano @ LetUsTech — letustech.uk
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json, os, sys, smtplib, csv, traceback, threading
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime, timedelta
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4, LETTER
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
        Paragraph, Spacer, HRFlowable, Image as RLImage)
    from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

try:
    from PIL import Image as PILImage, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ── Paths ────────────────────────────────────────────────────────────────────
APP_DIR   = Path(__file__).parent
DATA_DIR  = Path.home() / ".invoice_generator"
SETTINGS_FILE = DATA_DIR / "settings.json"
HISTORY_FILE  = DATA_DIR / "history.json"
CLIENTS_FILE  = DATA_DIR / "clients.json"
COUNTER_FILE  = DATA_DIR / "counter.json"
EXPENSES_FILE  = DATA_DIR / "expenses.json"
RECURRING_FILE = DATA_DIR / "recurring.json"
PAYMENTS_FILE  = DATA_DIR / "payments.json"
PROFILES_FILE  = DATA_DIR / "profiles.json"
LOGO_FILE     = APP_DIR  / "logo.png"
ICON_FILE     = APP_DIR  / "app_icon.ico"
SIDEBAR_LOGO  = APP_DIR  / "logo_sidebar.png"

APP_NAME    = "Invoice Generator"
APP_VERSION = "2.2.0"

# ── Palette ──────────────────────────────────────────────────────────────────
BG_DARK   = "#0b0e14"
BG_CARD   = "#131720"
BG_HOVER  = "#1a2030"
ACCENT    = "#00e676"
ACCENT_DIM= "#00b85a"
TEXT_WHITE= "#e8eaf0"
TEXT_DIM  = "#6b7280"
TEXT_MED  = "#9ca3af"
BORDER    = "#1f2937"
RED_ERR   = "#ef4444"
GOLD      = "#f59e0b"
BLUE      = "#3b82f6"
PURPLE    = "#8b5cf6"

FONT_HEAD = ("Segoe UI", 20, "bold")
FONT_SUB  = ("Segoe UI", 11)
FONT_BODY = ("Segoe UI", 10)
FONT_SMALL= ("Segoe UI", 9)
FONT_MONO = ("Consolas", 10)
FONT_NAV  = ("Segoe UI", 10, "bold")

def apply_theme(mode="Dark"):
    """Switch palette globals between Dark and Light mode."""
    global BG_DARK, BG_CARD, BG_HOVER, TEXT_WHITE, TEXT_DIM, TEXT_MED, BORDER
    if mode == "Light":
        BG_DARK   = "#f0f2f5"
        BG_CARD   = "#ffffff"
        BG_HOVER  = "#e8edf2"
        TEXT_WHITE= "#111827"
        TEXT_DIM  = "#6b7280"
        TEXT_MED  = "#374151"
        BORDER    = "#d1d5db"
    else:
        BG_DARK   = "#0b0e14"
        BG_CARD   = "#131720"
        BG_HOVER  = "#1a2030"
        TEXT_WHITE= "#e8eaf0"
        TEXT_DIM  = "#6b7280"
        TEXT_MED  = "#9ca3af"
        BORDER    = "#1f2937"

DEFAULT_SETTINGS = {
    "company_name":    "Your Company Name",
    "company_email":   "email@example.com",
    "company_phone":   "+44 7700 000000",
    "company_address": "123 Business Street\nLiverpool, L1 1AA\nUnited Kingdom",
    "company_website": "www.example.com",
    "vat_number":      "",
    "bank_name":       "",
    "bank_sort_code":  "",
    "bank_account":    "",
    "bank_reference":  "",
    "currency":        "GBP (£)",
    "currency_symbol": "£",
    "tax_rate":        20.0,
    "tax_label":       "VAT",
    "payment_terms":   30,
    "invoice_prefix":  "INV",
    "invoice_start":   1000,
    "page_size":       "A4",
    "date_format":     "DD/MM/YYYY",
    "theme_accent":    "#00e676",
    "default_notes":   "Thank you for your business. Payment is due within {terms} days.",
    "auto_save":       True,
    "save_directory":  str(Path.home() / "Documents" / "Invoices"),
    "smtp_host":       "smtp.gmail.com",
    "smtp_port":       "587",
    "smtp_email":      "",
    "smtp_password":   "",
    "logo_path":       str(LOGO_FILE) if LOGO_FILE.exists() else "",
    "show_logo":       True,
    "logo_width_mm":   50,
    "logo_height_mm":  18,
    # Keyboard shortcuts (empty string = disabled)
    "shortcut_new_invoice":  "Ctrl+N",
    "shortcut_export_pdf":   "Ctrl+E",
    "shortcut_save_draft":   "Ctrl+S",
    "shortcut_focus_search": "Ctrl+F",
    "shortcut_dashboard":    "Ctrl+D",
    "shortcut_invoices":     "Ctrl+I",
    "shortcut_clients":      "Ctrl+L",
    "shortcut_settings":     "Ctrl+Comma",
    "shortcut_reload":       "F5",
    "shortcut_clear_form":   "Escape",

    "auto_open_pdf":         True,
    "confirm_on_close":      True,
    "reminder_7day":         True,
    "reminder_14day":        True,
    "reminder_30day":        True,
    "reminder_email_subject":"Payment Reminder — Invoice {number}",
    "reminder_email_body":   "Dear {client},\n\nThis is a friendly reminder that invoice {number} for {amount} was due on {due_date}.\n\nPlease arrange payment at your earliest convenience.\n\nKind regards,\n{company}",
    "invoice_template":      "Professional",
    # Payment link
    "paypal_link":           "",
    "stripe_link":           "",
    "custom_pay_link":       "",
    "custom_pay_label":      "",
    # Late fees
    "late_fee_enabled":      False,
    "late_fee_days":         14,
    "late_fee_type":         "Percentage",
    "late_fee_amount":       "2.0",
    "late_fee_description":  "Late payment fee",
    # Footer & T&Cs
    "invoice_footer":        "",
    "tc_enabled":            False,
    "tc_text":               "",
    # Active company profile (empty = use main settings)
    "active_profile":        "",
    # Backup
    "backup_enabled":        False,
    "backup_folder":         "",
    # Theme
    "theme_mode":            "Dark",
}





# ── Data helpers ─────────────────────────────────────────────────────────────
def ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _ensure_counter(settings):
    """Make sure counter.json exists and is valid. Create it from invoice_start if missing."""
    ensure_dir()
    start = int(settings.get("invoice_start", 1000)) if settings else 1000
    if not COUNTER_FILE.exists():
        with open(COUNTER_FILE, "w") as f:
            import json as _j
            _j.dump({"next": start}, f)
        return
    # Validate it's readable
    try:
        with open(COUNTER_FILE) as f:
            data = json.load(f)
        if not isinstance(data.get("next"), int):
            raise ValueError("bad counter")
    except Exception:
        with open(COUNTER_FILE, "w") as f:
            json.dump({"next": start}, f)

def _safe_load_json(path, default, backup=True):
    """Load a JSON file safely. Returns default on any failure.
    Backs up corrupted files so data isn't silently lost."""
    ensure_dir()
    if not path.exists():
        return default() if callable(default) else default

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        if not raw:
            return default() if callable(default) else default
        data = json.loads(raw)
        # Type check — lists must be lists, dicts must be dicts
        expected = default() if callable(default) else default
        if not isinstance(data, type(expected)):
            raise ValueError(f"Expected {type(expected).__name__}, got {type(data).__name__}")
        return data
    except Exception as e:
        # Back up the bad file before overwriting
        if backup and path.exists():
            import shutil
            bak = path.with_suffix(f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            try:
                shutil.copy2(path, bak)
            except Exception:
                pass
        # Log the issue
        try:
            log = DATA_DIR / "error.log"
            with open(log, "a", encoding="utf-8") as lf:
                lf.write(f"\n[{datetime.now()}] Failed to load {path.name}: {e}\n")
        except Exception:
            pass
        return default() if callable(default) else default

def _safe_save_json(path, data):
    """Write JSON atomically — write to temp file then rename,
    so a crash during write never corrupts the existing file."""
    ensure_dir()
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(path)
        # Auto-backup if enabled
        _auto_backup(path)
    except Exception as e:
        try:
            log = DATA_DIR / "error.log"
            with open(log, "a", encoding="utf-8") as lf:
                lf.write(f"\n[{datetime.now()}] Failed to save {path.name}: {e}\n")
        except Exception:
            pass
        try:
            if tmp.exists(): tmp.unlink()
        except Exception:
            pass

def _auto_backup(path):
    """Silently copy a data file to the backup folder if backup is enabled."""
    try:
        settings_path = DATA_DIR / "settings.json"
        if not settings_path.exists():
            return
        with open(settings_path, encoding="utf-8") as f:
            s = json.load(f)
        if not s.get("backup_enabled", False):
            return
        folder = s.get("backup_folder", "").strip()
        if not folder:
            return
        dest = Path(folder)
        dest.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(path, dest / path.name)
    except Exception:
        pass  # Never let backup failure crash the app

def _validate_history_entry(h):
    """Ensure a history entry has all required fields with correct types."""
    if not isinstance(h, dict):
        return None
    return {
        "number":       str(h.get("number", "")),
        "date":         str(h.get("date", "")),
        "due_date":     str(h.get("due_date", "")),
        "status":       str(h.get("status", "Unpaid")),
        "client_name":  str(h.get("client_name") or h.get("client", "")),
        "client_email": str(h.get("client_email", "")),
        "client_phone": str(h.get("client_phone", "")),
        "client_address": str(h.get("client_address", "")),
        "total":        float(h.get("total", 0) or 0),
        "discount":     str(h.get("discount", "0")),
        "notes":        str(h.get("notes", "")),
        "po":           str(h.get("po", "")),
        "filepath":     str(h.get("filepath", "")),
        "items":        h.get("items", []) if isinstance(h.get("items"), list) else [],
        "paid_date":        str(h.get("paid_date", "")),
        "last_reminder":    str(h.get("last_reminder", "")),
        "currency_symbol":  str(h.get("currency_symbol", "")),
        "invoice_template": str(h.get("invoice_template", "Professional")),
        "amount_paid":      str(h.get("amount_paid", "0")),
    }

def _validate_client_entry(c):
    if not isinstance(c, dict): return None
    return {
        "name":    str(c.get("name", "")),
        "email":   str(c.get("email", "")),
        "phone":   str(c.get("phone", "")),
        "website": str(c.get("website", "")),
        "address": str(c.get("address", "")),
        "notes":   str(c.get("notes", "")),
    }

def _validate_expense_entry(e):
    if not isinstance(e, dict): return None
    return {
        "description": str(e.get("description", "")),
        "amount":      float(e.get("amount", 0) or 0),
        "date":        str(e.get("date", "")),
        "category":    str(e.get("category", "General")),
        "notes":       str(e.get("notes", "")),
    }

def load_settings():
    data = _safe_load_json(SETTINGS_FILE, dict)
    if not isinstance(data, dict):
        data = {}
    # Merge with defaults — ensures every key exists even after updates
    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    # Validate critical numeric fields
    for key in ("tax_rate", "payment_terms", "invoice_start"):
        try:
            merged[key] = float(merged[key]) if key == "tax_rate" else int(merged[key])
        except (ValueError, TypeError):
            merged[key] = DEFAULT_SETTINGS[key]
    return merged

def save_settings(s):
    _safe_save_json(SETTINGS_FILE, s)

def load_history():
    raw = _safe_load_json(HISTORY_FILE, list)
    if not isinstance(raw, list):
        return []
    validated = [_validate_history_entry(h) for h in raw]
    return [h for h in validated if h is not None]

def save_history(h):
    if not isinstance(h, list):
        h = []
    _safe_save_json(HISTORY_FILE, h[:200])

def load_clients():
    raw = _safe_load_json(CLIENTS_FILE, list)
    if not isinstance(raw, list):
        return []
    validated = [_validate_client_entry(c) for c in raw]
    return [c for c in validated if c is not None and c.get("name")]

def save_clients(c):
    if not isinstance(c, list):
        c = []
    _safe_save_json(CLIENTS_FILE, c)

def load_expenses():
    raw = _safe_load_json(EXPENSES_FILE, list)
    if not isinstance(raw, list):
        return []
    validated = [_validate_expense_entry(e) for e in raw]
    return [e for e in validated if e is not None]

def save_expenses(e):
    if not isinstance(e, list):
        e = []
    _safe_save_json(EXPENSES_FILE, e)

def load_recurring():
    ensure_dir()
    raw = _safe_load_json(RECURRING_FILE, list)
    return raw if isinstance(raw, list) else []

def save_recurring(r):
    ensure_dir()
    _safe_save_json(RECURRING_FILE, r if isinstance(r, list) else [])

def load_payments():
    ensure_dir()
    raw = _safe_load_json(PAYMENTS_FILE, dict)
    return raw if isinstance(raw, dict) else {}

def save_payments(p):
    ensure_dir()
    _safe_save_json(PAYMENTS_FILE, p if isinstance(p, dict) else {})

def load_profiles():
    ensure_dir()
    raw = _safe_load_json(PROFILES_FILE, list)
    return raw if isinstance(raw, list) else []

def save_profiles(p):
    ensure_dir()
    _safe_save_json(PROFILES_FILE, p if isinstance(p, list) else [])

def startup_integrity_check():
    """Run on launch — ensures data dir exists, all files are valid JSON,
    and writes fresh defaults for anything missing or unreadable.
    Returns a list of any issues found (shown to user if non-empty)."""
    ensure_dir()
    issues = []

    checks = [
        (SETTINGS_FILE,  "settings",  dict,  load_settings,  save_settings,  lambda: dict(DEFAULT_SETTINGS)),
        (HISTORY_FILE,   "history",   list,  load_history,   save_history,   list),
        (CLIENTS_FILE,   "clients",   list,  load_clients,   save_clients,   list),
        (EXPENSES_FILE,  "expenses",  list,  load_expenses,  save_expenses,  list),
    ]

    for path, name, expected_type, loader, saver, default_fn in checks:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                if not raw:
                    # Empty file — write default
                    saver(default_fn())
                    issues.append(f"{name}.json was empty — reset to default")
                    continue
                data = json.loads(raw)
                if not isinstance(data, expected_type):
                    raise TypeError(f"Expected {expected_type.__name__}")
            except Exception as e:
                # Back it up and reset
                import shutil
                bak = path.with_suffix(
                    f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                try:
                    shutil.copy2(path, bak)
                except Exception:
                    pass
                saver(default_fn())
                issues.append(
                    f"{name}.json was corrupted and has been reset\n"
                    f"  Backup saved as: {bak.name}")
        # File missing — will be created on first save, that's fine

    return issues

def next_inv_num(settings):
    ensure_dir()
    start  = int(settings.get("invoice_start", 1000))
    prefix = settings.get("invoice_prefix", "INV")
    num = start
    if COUNTER_FILE.exists():
        try:
            with open(COUNTER_FILE) as f:
                num = json.load(f).get("next", start)
        except Exception:
            pass
    return f"{prefix}-{num:04d}", num

def bump_counter(settings):
    ensure_dir()
    start = int(settings.get("invoice_start", 1000))
    num = start
    if COUNTER_FILE.exists():
        try:
            with open(COUNTER_FILE) as f:
                num = json.load(f).get("next", start)
        except Exception:
            pass
    with open(COUNTER_FILE, "w") as f:
        json.dump({"next": num + 1}, f)

def fdate(fmt="DD/MM/YYYY", dt=None):
    d = dt or datetime.today()
    if fmt == "DD/MM/YYYY": return d.strftime("%d/%m/%Y")
    if fmt == "MM/DD/YYYY": return d.strftime("%m/%d/%Y")
    return d.strftime("%Y-%m-%d")

def duedate(terms=30, fmt="DD/MM/YYYY"):
    return fdate(fmt, datetime.today() + timedelta(days=int(terms)))

def fc(amount, sym="£"):
    return f"{sym}{amount:,.2f}"

def is_overdue(due_str, fmt="DD/MM/YYYY"):
    try:
        if fmt == "DD/MM/YYYY": d = datetime.strptime(due_str, "%d/%m/%Y")
        elif fmt == "MM/DD/YYYY": d = datetime.strptime(due_str, "%m/%d/%Y")
        else: d = datetime.strptime(due_str, "%Y-%m-%d")
        return d < datetime.today()
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════════════════════
#  WIDGETS
# ═══════════════════════════════════════════════════════════════════════════

class FlatEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kw):
        kw.setdefault("width", 20)
        super().__init__(parent, bg=BG_HOVER, fg=TEXT_WHITE,
            insertbackground=ACCENT, relief="flat", bd=0, font=FONT_BODY,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, **kw)
        self._ph = placeholder
        self._has_ph = False
        if placeholder:
            self._show_ph()
            self.bind("<FocusIn>",  self._fi)
            self.bind("<FocusOut>", self._fo)

    def _show_ph(self):
        self.insert(0, self._ph); self.config(fg=TEXT_DIM); self._has_ph = True

    def _fi(self, e):
        if self._has_ph:
            self.delete(0, "end"); self.config(fg=TEXT_WHITE); self._has_ph = False

    def _fo(self, e):
        if not self.get(): self._show_ph()

    def get_value(self):
        return "" if self._has_ph else self.get()

    def set_value(self, v):
        self._has_ph = False
        self.delete(0, "end")
        if v:
            self.insert(0, v); self.config(fg=TEXT_WHITE)
        elif self._ph:
            self._show_ph()


class FlatText(tk.Text):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_HOVER, fg=TEXT_WHITE,
            insertbackground=ACCENT, relief="flat", bd=0, font=FONT_BODY,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, **kw)


class GreenButton(tk.Button):
    def __init__(self, parent, text="", command=None, small=False,
                 danger=False, secondary=False, **kw):
        if danger:       bg, dim, fg = RED_ERR,   "#b91c1c", "#ffffff"
        elif secondary:  bg, dim, fg = BLUE,       "#2563eb", "#ffffff"
        else:            bg, dim, fg = ACCENT,     ACCENT_DIM,"#000000"
        fs = 9 if small else 10
        px = (8, 3) if small else (14, 7)
        super().__init__(parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=dim, activeforeground=fg,
            relief="flat", bd=0, font=("Segoe UI", fs, "bold"),
            cursor="hand2", padx=px[0], pady=px[1], **kw)
        self.bind("<Enter>", lambda e: self.config(bg=dim))
        self.bind("<Leave>", lambda e: self.config(bg=bg))


class GhostButton(tk.Button):
    def __init__(self, parent, text="", command=None, **kw):
        super().__init__(parent, text=text, command=command,
            bg=BG_CARD, fg=TEXT_MED, activebackground=BG_HOVER,
            activeforeground=TEXT_WHITE, relief="flat", bd=0,
            font=FONT_BODY, cursor="hand2",
            highlightthickness=1, highlightbackground=BORDER,
            padx=10, pady=5, **kw)
        self.bind("<Enter>", lambda e: self.config(bg=BG_HOVER, fg=TEXT_WHITE))
        self.bind("<Leave>", lambda e: self.config(bg=BG_CARD,  fg=TEXT_MED))


class NavButton(tk.Button):
    def __init__(self, parent, text="", icon="", command=None, **kw):
        self._active = False
        super().__init__(parent, text=f"  {icon}  {text}", command=command,
            bg=BG_DARK, fg=TEXT_MED, activebackground=BG_CARD,
            activeforeground=ACCENT, relief="flat", bd=0,
            font=FONT_NAV, cursor="hand2", anchor="w",
            padx=8, pady=9, **kw)
        self.bind("<Enter>", lambda e: None if self._active else self.config(bg=BG_HOVER, fg=TEXT_WHITE))
        self.bind("<Leave>", lambda e: None if self._active else self.config(bg=BG_DARK, fg=TEXT_MED))

    def set_active(self, v):
        self._active = v
        if v: self.config(bg=BG_CARD, fg=ACCENT, font=("Segoe UI", 10, "bold"))
        else: self.config(bg=BG_DARK, fg=TEXT_MED, font=FONT_NAV)


class Card(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_CARD,
            highlightthickness=1, highlightbackground=BORDER, **kw)


class Divider(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BORDER, height=1, **kw)


def make_scrollable(parent):
    """Returns inner frame; packs canvas+scrollbar into parent.
    Uses a clean global bind/unbind approach for reliable scroll everywhere."""
    canvas = tk.Canvas(parent, bg=BG_DARK, highlightthickness=0)
    sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=BG_DARK)

    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)

    def _update_scrollregion(e=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _resize_inner(e):
        canvas.itemconfig(win_id, width=e.width)

    inner.bind("<Configure>", _update_scrollregion)
    canvas.bind("<Configure>", _resize_inner)

    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    # Scroll handler
    def _scroll(e):
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        return "break"

    # Bind to canvas + app-level when active, unbind cleanly when destroyed
    def _on_enter(e):
        canvas.bind_all("<MouseWheel>", _scroll)

    def _on_leave(e):
        canvas.unbind_all("<MouseWheel>")

    def _on_destroy(e):
        try:
            canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass

    canvas.bind("<Enter>",   _on_enter)
    canvas.bind("<Leave>",   _on_leave)
    canvas.bind("<Destroy>", _on_destroy)

    # Scroll to top on fresh load
    canvas.after(30, lambda: canvas.yview_moveto(0))

    return inner


def lbl(parent, text, fg=TEXT_DIM, font=FONT_SMALL, **kw):
    return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=fg, font=font, **kw)


def status_badge(parent, status):
    colours = {
        "Unpaid":  (GOLD,    "#000"),
        "Paid":    (ACCENT,  "#000"),
        "Overdue": (RED_ERR, "#fff"),
        "Draft":   (TEXT_DIM,"#fff"),
    }
    bg, fg = colours.get(status, (TEXT_DIM, "#fff"))
    return tk.Label(parent, text=status, bg=bg, fg=fg,
        font=("Segoe UI", 8, "bold"), padx=6, pady=2)


# ═══════════════════════════════════════════════════════════════════════════
#  LINE ITEM ROW
# ═══════════════════════════════════════════════════════════════════════════

class LineItemRow(tk.Frame):
    def __init__(self, parent, on_change, on_delete, sym="£", **kw):
        super().__init__(parent, bg=BG_CARD, **kw)
        self.on_change = on_change
        self._sym = sym

        self.columnconfigure(0, weight=3)  # description stretches
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=0)

        self.desc  = FlatEntry(self, placeholder="Item description")
        self.desc.grid(row=0, column=0, padx=(0,4), pady=2, sticky="ew")

        self.qty   = FlatEntry(self, placeholder="Qty", width=6)
        self.qty.grid(row=0, column=1, padx=(0,4), pady=2)

        self.price = FlatEntry(self, placeholder="Unit price", width=10)
        self.price.grid(row=0, column=2, padx=(0,4), pady=2)

        self.taxable_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text="Tax", variable=self.taxable_var,
            bg=BG_CARD, fg=TEXT_MED, selectcolor=BG_HOVER,
            activebackground=BG_CARD, font=FONT_SMALL,
            command=self._ch, cursor="hand2"
        ).grid(row=0, column=3, padx=(0,4))

        self.total_lbl = tk.Label(self, text=f"{sym}0.00",
            bg=BG_CARD, fg=TEXT_WHITE, font=FONT_MONO, width=9, anchor="e")
        self.total_lbl.grid(row=0, column=4, padx=(0,4))

        tk.Button(self, text="✕", command=on_delete,
            bg=BG_CARD, fg=TEXT_DIM, activebackground=BG_CARD,
            activeforeground=RED_ERR, relief="flat", bd=0,
            font=("Segoe UI", 10, "bold"), cursor="hand2"
        ).grid(row=0, column=5)

        for w in (self.desc, self.qty, self.price):
            w.bind("<KeyRelease>", lambda e: self._ch())

    def _ch(self): self.on_change()

    def get_data(self):
        desc = self.desc.get_value()
        try:   qty   = float(self.qty.get_value() or 0)
        except: qty  = 0
        try:   price = float(self.price.get_value() or 0)
        except: price = 0
        total = qty * price
        self.total_lbl.config(text=fc(total, self._sym))
        return {"desc": desc, "qty": qty, "price": price,
                "taxable": self.taxable_var.get(), "total": total}

    def load(self, item):
        self.desc.set_value(item.get("desc", ""))
        self.qty.set_value(str(item.get("qty", "")))
        self.price.set_value(str(item.get("price", "")))
        self.taxable_var.set(item.get("taxable", True))
        self._ch()


# ═══════════════════════════════════════════════════════════════════════════
#  PDF GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

def generate_pdf(filepath, inv, settings):
    """
    Generates a PDF invoice with support for:
      • 3 templates: Professional, Minimal, Bold
      • Per-invoice currency symbol
      • PAID watermark when status == "Paid"
      • Partial payment / balance due line
    """
    if not REPORTLAB_OK:
        raise RuntimeError("reportlab not installed. Run: pip install reportlab")

    # ── Per-invoice currency (falls back to global setting) ───────────────
    sym      = inv.get("currency_symbol") or settings.get("currency_symbol", "£")
    tax_lbl  = settings.get("tax_label", "VAT")
    tax_rate = float(settings.get("tax_rate", 20))
    pg_size  = A4 if settings.get("page_size", "A4") == "A4" else LETTER
    ah       = settings.get("theme_accent", "#00e676")
    acc      = colors.HexColor(ah)
    template = inv.get("invoice_template") or settings.get("invoice_template", "Professional")

    # ── Template colour schemes ───────────────────────────────────────────
    if template == "Minimal":
        header_bg   = "#ffffff"
        header_text = "#333333"
        table_head  = "#f0f0f0"
        table_htxt  = "#333333"
        divider_col = colors.HexColor("#cccccc")
        accent_col  = acc
    elif template == "Bold":
        header_bg   = ah
        header_text = "#000000"
        table_head  = ah
        table_htxt  = "#000000"
        divider_col = acc
        accent_col  = acc
    else:  # Professional (default)
        header_bg   = "#1a1a2e"
        header_text = "#ffffff"
        table_head  = "#1a1a2e"
        table_htxt  = "#ffffff"
        divider_col = acc
        accent_col  = acc

    doc = SimpleDocTemplate(filepath, pagesize=pg_size,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm)
    story = []

    def P(text, size=9, bold=False, color="#222222", align=TA_LEFT, leading=14):
        return Paragraph(text, ParagraphStyle("p",
            fontName="Helvetica-Bold" if bold else "Helvetica",
            fontSize=size, textColor=colors.HexColor(color),
            alignment=align, leading=leading))

    # ── Logo / company name header ────────────────────────────────────────
    logo_path = settings.get("logo_path", "")
    show_logo = settings.get("show_logo", True)
    logo_w    = float(settings.get("logo_width_mm",  50)) * mm
    logo_h    = float(settings.get("logo_height_mm", 18)) * mm

    if show_logo and logo_path and os.path.exists(logo_path):
        try:
            logo_cell = RLImage(logo_path, width=logo_w, height=logo_h)
        except Exception:
            logo_cell = P(settings.get("company_name",""), 18, bold=True, color=ah)
    else:
        logo_cell = P(settings.get("company_name",""), 18, bold=True, color=ah)

    inv_title = P("INVOICE", 26, bold=True, color=header_text if template=="Bold" else "#111111",
                  align=TA_RIGHT)

    if template == "Bold":
        # Bold: full-width coloured header bar
        hdr_tbl = Table([[logo_cell, inv_title]], colWidths=["60%","40%"])
        hdr_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), colors.HexColor(ah)),
            ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0),(-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
            ("LEFTPADDING", (0,0),(0,0),  10),
        ]))
        story.append(hdr_tbl)
        story.append(Spacer(1, 4*mm))
    elif template == "Minimal":
        # Minimal: just text, thin grey rule
        hdr_tbl = Table([[logo_cell, inv_title]], colWidths=["60%","40%"])
        hdr_tbl.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                     ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(hdr_tbl)
        story.append(HRFlowable(width="100%", thickness=0.5,
            color=colors.HexColor("#cccccc"), spaceAfter=6))
    else:
        # Professional: dark rule
        hdr_tbl = Table([[logo_cell, inv_title]], colWidths=["60%","40%"])
        hdr_tbl.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                     ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(hdr_tbl)
        story.append(HRFlowable(width="100%", thickness=2, color=acc, spaceAfter=6))

    # ── Company info + invoice meta ───────────────────────────────────────
    addr = settings.get("company_address","").replace("\n","<br/>")
    co   = f"<b>{settings.get('company_name','')}</b><br/>{addr}<br/>{settings.get('company_email','')}"
    if settings.get("vat_number"):   co += f"<br/>VAT: {settings['vat_number']}"
    if settings.get("company_website"): co += f"<br/>{settings['company_website']}"

    status_color = {"Paid":"#00b85a","Overdue":"#ef4444"}.get(inv.get("status","Unpaid"),"#f59e0b")
    meta = (f"<b>Invoice #:</b> {inv['number']}<br/>"
            f"<b>Date:</b> {inv['date']}<br/>"
            f"<b>Due:</b> {inv['due_date']}")
    if inv.get("po"): meta += f"<br/><b>PO/Ref:</b> {inv['po']}"
    meta += f"<br/><font color='{status_color}'><b>{inv.get('status','Unpaid').upper()}</b></font>"

    it = Table([[P(co,9,leading=14), P(meta,9,align=TA_RIGHT,leading=14)]],
               colWidths=["55%","45%"])
    it.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(it)
    story.append(Spacer(1, 8*mm))

    # ── Bill To ───────────────────────────────────────────────────────────
    story.append(P("BILL TO", 8, bold=True, color=ah))
    story.append(Spacer(1, 2*mm))
    ba = inv.get("client_address","").replace("\n","<br/>")
    story.append(P(f"<b>{inv.get('client_name','')}</b><br/>{ba}<br/>{inv.get('client_email','')}",
                   10, leading=15))
    story.append(Spacer(1, 8*mm))

    # ── Line items table ──────────────────────────────────────────────────
    cs = ParagraphStyle("td", fontSize=9, leading=13)
    rs = ParagraphStyle("tr", fontSize=9, leading=13, alignment=TA_RIGHT)

    tdata = [[P("DESCRIPTION",9,bold=True,color=table_htxt),
              P("QTY",9,bold=True,color=table_htxt),
              P("RATE",9,bold=True,color=table_htxt),
              P("TAX",9,bold=True,color=table_htxt),
              P("AMOUNT",9,bold=True,color=table_htxt)]]

    subtotal = tax_total = 0
    for item in inv.get("items", []):
        if not item.get("desc"): continue
        lt = item["qty"] * item["price"]
        subtotal  += lt
        if item.get("taxable"): tax_total += lt * (tax_rate/100)
        tdata.append([
            Paragraph(item["desc"], cs),
            Paragraph(str(item["qty"]), rs),
            Paragraph(fc(item["price"], sym), rs),
            Paragraph(f"{tax_rate}%" if item.get("taxable") else "—", rs),
            Paragraph(fc(lt, sym), rs),
        ])

    row_bg_a = colors.HexColor("#f8f9fa")
    row_bg_b = colors.white
    if template == "Minimal":
        row_bg_a = colors.white
        row_bg_b = colors.white

    lt_tbl = Table(tdata, colWidths=["42%","10%","16%","12%","20%"])
    lt_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,0),  colors.HexColor(table_head)),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[row_bg_a, row_bg_b]),
        ("GRID",         (0,0),(-1,-1), 0.3, colors.HexColor("#dee2e6")),
        ("TOPPADDING",   (0,0),(-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(lt_tbl)
    story.append(Spacer(1, 4*mm))

    # ── Totals ────────────────────────────────────────────────────────────
    try: discount = float(inv.get("discount", 0))
    except: discount = 0
    disc_amt = subtotal * (discount/100)
    grand    = subtotal + tax_total - disc_amt

    # ── Partial payment / balance due ─────────────────────────────────────
    try: amount_paid = float(inv.get("amount_paid", 0) or 0)
    except: amount_paid = 0
    balance_due = grand - amount_paid

    def trow(label, val, bold=False, highlight=False, strike=False):
        c = ah if highlight else "#333333"
        fn = "Helvetica-Bold" if bold else "Helvetica"
        sz = 10 if bold else 9
        return ["","","",
            Paragraph(label, ParagraphStyle("tl",fontName=fn,fontSize=sz,
                textColor=colors.HexColor(c),alignment=TA_RIGHT)),
            Paragraph(val,   ParagraphStyle("tv",fontName=fn,fontSize=sz,
                textColor=colors.HexColor(c),alignment=TA_RIGHT))]

    tots = [trow("Subtotal", fc(subtotal, sym)),
            trow(f"{tax_lbl} ({tax_rate}%)", fc(tax_total, sym))]
    if disc_amt:
        tots.append(trow(f"Discount ({discount}%)", f"-{fc(disc_amt,sym)}"))

    if amount_paid > 0 and amount_paid < grand:
        # Partial payment — show original total, amount paid, then balance
        tots.append(trow("Gross Total",   fc(grand, sym),       bold=True))
        tots.append(trow("Amount Paid",   f"-{fc(amount_paid,sym)}",
                         highlight=False))
        tots.append(trow("BALANCE DUE",   fc(balance_due, sym), bold=True, highlight=True))
    elif amount_paid >= grand:
        # Fully paid
        tots.append(trow("TOTAL DUE", fc(grand, sym), bold=True))
        tots.append(trow("Amount Paid", fc(amount_paid, sym)))
        tots.append(trow("BALANCE DUE", fc(0, sym), bold=True, highlight=True))
    else:
        tots.append(trow("TOTAL DUE", fc(grand, sym), bold=True, highlight=True))

    tt = Table(tots, colWidths=["42%","10%","16%","16%","16%"])
    tt.setStyle(TableStyle([
        ("LINEABOVE",    (3,-1),(-1,-1), 1.5, accent_col),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ]))
    story.append(tt)
    story.append(Spacer(1, 8*mm))

    # ── Notes ─────────────────────────────────────────────────────────────
    notes = inv.get("notes","").strip()
    if notes:
        story.append(P("NOTES", 8, bold=True, color=ah))
        story.append(Spacer(1, 2*mm))
        story.append(P(notes, 9, leading=13))
        story.append(Spacer(1, 5*mm))

    # ── Bank details ──────────────────────────────────────────────────────
    bank = [settings.get("bank_name",""), settings.get("bank_sort_code",""),
            settings.get("bank_account","")]
    if any(bank):
        story.append(HRFlowable(width="100%", thickness=1, color=accent_col, spaceAfter=4))
        story.append(P("PAYMENT DETAILS", 8, bold=True, color=ah))
        story.append(Spacer(1, 2*mm))
        pt = "  ".join(filter(None, [
            f"Bank: {bank[0]}"       if bank[0] else "",
            f"Sort Code: {bank[1]}"  if bank[1] else "",
            f"Account: {bank[2]}"    if bank[2] else "",
            f"Ref: {settings.get('bank_reference','')}" if settings.get("bank_reference") else "",
        ]))
        story.append(P(pt, 9))

    # ── Online payment links ──────────────────────────────────────────────
    paypal = settings.get("paypal_link","").strip()
    stripe = settings.get("stripe_link","").strip()
    custom_url   = settings.get("custom_pay_link","").strip()
    custom_label = settings.get("custom_pay_label","Pay Online").strip() or "Pay Online"

    pay_links = []
    if paypal: pay_links.append(("PayPal", paypal, "#003087"))
    if stripe: pay_links.append(("Stripe", stripe, "#635bff"))
    if custom_url: pay_links.append((custom_label, custom_url, ah))

    if pay_links and inv.get("status") not in ("Paid",):
        story.append(HRFlowable(width="100%", thickness=1, color=accent_col, spaceAfter=4))
        story.append(P("PAY NOW", 8, bold=True, color=ah))
        story.append(Spacer(1, 3*mm))

        # Build a row of payment buttons
        btn_data = [[]]
        for label, url, colour in pay_links:
            btn_text = (
                f'<font color="{colour}"><b>▶  {label}</b></font><br/>'
                f'<font size="7" color="#888888">{url[:50]}{"…" if len(url)>50 else ""}</font>'
            )
            cell = Paragraph(btn_text, ParagraphStyle("pl",
                fontSize=10, leading=14, spaceAfter=2))
            btn_data[0].append(cell)

        # Pad to 3 columns so table is balanced
        while len(btn_data[0]) < 3:
            btn_data[0].append(Paragraph("", ParagraphStyle("empty", fontSize=9)))

        btn_tbl = Table(btn_data, colWidths=["33%","33%","34%"])
        btn_tbl.setStyle(TableStyle([
            ("BOX",         (0,0),(-1,-1), 0.5, colors.HexColor("#444444")),
            ("INNERGRID",   (0,0),(-1,-1), 0.3, colors.HexColor("#333333")),
            ("BACKGROUND",  (0,0),(-1,-1), colors.HexColor("#1a1a2e")),
            ("TOPPADDING",  (0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("LEFTPADDING", (0,0),(-1,-1), 10),
            ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(btn_tbl)
        story.append(Spacer(1, 5*mm))

    # ── Custom footer text ────────────────────────────────────────────────
    footer_text = settings.get("invoice_footer","").strip()
    if footer_text:
        story.append(Spacer(1, 4*mm))
        story.append(HRFlowable(width="100%", thickness=0.5,
            color=colors.HexColor("#444444"), spaceAfter=3))
        story.append(P(footer_text, 8, color="#888888", align=TA_CENTER))

    # ── Footer ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=0.5,
        color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 3*mm))
    story.append(P("Generated with Invoice Generator — letustech.uk",
        7, color="#bbbbbb", align=TA_CENTER))

    # ── Terms & Conditions second page ────────────────────────────────────
    tc_enabled = settings.get("tc_enabled", False)
    tc_text    = settings.get("tc_text","").strip()
    if tc_enabled and str(tc_enabled).lower() not in ("false","0","") and tc_text:
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
        story.append(P("TERMS & CONDITIONS", 14, bold=True, color=ah))
        story.append(Spacer(1, 4*mm))
        story.append(HRFlowable(width="100%", thickness=1, color=accent_col, spaceAfter=6))
        # Split on blank lines to respect paragraph breaks
        for para in tc_text.split("\n\n"):
            para = para.strip()
            if para:
                # Bold headings: lines that end with : or are all caps
                if para.isupper() or (len(para) < 60 and para.rstrip().endswith(":")):
                    story.append(P(para, 10, bold=True, color="#dddddd"))
                else:
                    story.append(P(para.replace("\n"," "), 9, color="#cccccc", leading=14))
                story.append(Spacer(1, 3*mm))
        story.append(Spacer(1, 6*mm))
        story.append(HRFlowable(width="100%", thickness=0.5,
            color=colors.HexColor("#333333")))
        story.append(Spacer(1, 3*mm))
        story.append(P(f"Terms & Conditions — {settings.get('company_name','')}",
            7, color="#666666", align=TA_CENTER))

    # ── Build PDF ─────────────────────────────────────────────────────────
    doc.build(story)

    # ── PAID watermark (drawn on top after build) ─────────────────────────
    if inv.get("status") == "Paid":
        _stamp_paid_watermark(filepath, pg_size, accent_col)


def _stamp_paid_watermark(filepath, pg_size, stamp_color):
    """Overlay a diagonal PAID stamp on every page of an existing PDF."""
    try:
        import tempfile, shutil
        from reportlab.pdfgen import canvas as rl_canvas

        # Read original
        try:
            from PyPDF2 import PdfReader, PdfWriter
            HAS_PYPDF2 = True
        except ImportError:
            try:
                from pypdf import PdfReader, PdfWriter
                HAS_PYPDF2 = True
            except ImportError:
                HAS_PYPDF2 = False

        if not HAS_PYPDF2:
            # Fallback: draw watermark directly on the canvas before build
            # (already handled inline — skip silently)
            return

        w, h = pg_size

        # Create a one-page watermark PDF in memory
        import io
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=pg_size)
        c.saveState()
        c.setFillColor(stamp_color)
        c.setStrokeColor(stamp_color)
        c.setFillAlpha(0.18)
        c.setStrokeAlpha(0.18)
        c.setFont("Helvetica-Bold", 72)
        c.translate(w/2, h/2)
        c.rotate(45)
        c.drawCentredString(0, 0, "PAID")
        c.restoreState()
        c.save()
        buf.seek(0)

        wm_reader = PdfReader(buf)
        wm_page   = wm_reader.pages[0]

        reader = PdfReader(filepath)
        writer = PdfWriter()
        for page in reader.pages:
            page.merge_page(wm_page)
            writer.add_page(page)

        tmp = filepath + ".tmp"
        with open(tmp, "wb") as f:
            writer.write(f)
        shutil.move(tmp, filepath)

    except Exception:
        # Watermark is best-effort — never fail the whole export
        pass



# ═══════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════
#  GLOBAL ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════════════

class ErrorDialog(tk.Toplevel):
    """Shows a full traceback in a copyable window whenever an unhandled
    exception occurs — so developers can debug without losing context."""

    def __init__(self, exc_type, exc_value, exc_tb):
        # Build the full traceback string
        self._tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        self._short   = f"{exc_type.__name__}: {exc_value}"

        # Need a root window — create a temporary one if none exists
        try:
            super().__init__()
        except Exception:
            root = tk.Tk()
            root.withdraw()
            super().__init__(root)

        self.title("⚠  Unhandled Error — Invoice Generator")
        self.geometry("820x560")
        self.minsize(600, 400)
        self.configure(bg=BG_DARK)
        self.grab_set()
        self._build()

    def _build(self):
        # ── Header ──────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg="#1a0a0a",
                       highlightthickness=1, highlightbackground=RED_ERR)
        hdr.pack(fill="x")
        hf = tk.Frame(hdr, bg="#1a0a0a", padx=18, pady=14)
        hf.pack(fill="x")

        tk.Label(hf, text="⚠  An error occurred", bg="#1a0a0a",
                 fg=RED_ERR, font=("Segoe UI",13,"bold")).pack(anchor="w")
        tk.Label(hf, text=self._short, bg="#1a0a0a",
                 fg=TEXT_MED, font=("Segoe UI",10),
                 wraplength=760, justify="left").pack(anchor="w", pady=(4,0))

        # ── Traceback box ────────────────────────────────────────────────
        mid = tk.Frame(self, bg=BG_DARK, padx=14, pady=10)
        mid.pack(fill="both", expand=True)

        tk.Label(mid, text="Full traceback  (select all + copy to share with developer):",
                 bg=BG_DARK, fg=TEXT_DIM, font=("Segoe UI",9)).pack(anchor="w", pady=(0,4))

        tb_frame = tk.Frame(mid, bg=BG_CARD,
                            highlightthickness=1, highlightbackground=BORDER)
        tb_frame.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(tb_frame)
        sb.pack(side="right", fill="y")

        txt = tk.Text(tb_frame, bg="#0d0d0d", fg="#ff6b6b",
                      font=("Consolas",10), relief="flat", bd=0,
                      wrap="none", yscrollcommand=sb.set,
                      selectbackground=ACCENT, selectforeground="#000000",
                      padx=12, pady=10)
        txt.pack(fill="both", expand=True)
        sb.config(command=txt.yview)

        # Horizontal scrollbar for long lines
        hsb = ttk.Scrollbar(mid, orient="horizontal", command=txt.xview)
        hsb.pack(fill="x")
        txt.config(xscrollcommand=hsb.set)

        txt.insert("1.0", self._tb_text)
        txt.config(state="disabled")

        # ── Log file note ────────────────────────────────────────────────
        log_path = DATA_DIR / "error.log"
        tk.Label(mid,
                 text=f"This error has also been saved to:  {log_path}",
                 bg=BG_DARK, fg=TEXT_DIM, font=("Segoe UI",8)).pack(
                 anchor="w", pady=(6,0))

        # ── Buttons ──────────────────────────────────────────────────────
        bf = tk.Frame(self, bg=BG_DARK, padx=14, pady=12)
        bf.pack(fill="x")

        def copy_tb():
            self.clipboard_clear()
            self.clipboard_append(self._tb_text)
            copy_btn.config(text="✓  Copied!")
            self.after(2000, lambda: copy_btn.config(text="📋  Copy Traceback"))

        copy_btn = tk.Button(bf, text="📋  Copy Traceback", command=copy_tb,
            bg=BG_CARD, fg=TEXT_MED, activebackground=BG_HOVER,
            activeforeground=TEXT_WHITE, relief="flat", bd=0,
            font=FONT_BODY, cursor="hand2",
            highlightthickness=1, highlightbackground=BORDER,
            padx=12, pady=7)
        copy_btn.pack(side="left", padx=(0,8))

        def open_log():
            lp = str(DATA_DIR / "error.log")
            if sys.platform == "win32": os.startfile(lp)
            else: os.system(f'open "{lp}"')
        tk.Button(bf, text="📂  Open Log File", command=open_log,
            bg=BG_CARD, fg=TEXT_MED, activebackground=BG_HOVER,
            activeforeground=TEXT_WHITE, relief="flat", bd=0,
            font=FONT_BODY, cursor="hand2",
            highlightthickness=1, highlightbackground=BORDER,
            padx=12, pady=7).pack(side="left")

        tk.Button(bf, text="✕  Close", command=self.destroy,
            bg=RED_ERR, fg="#ffffff", activebackground="#b91c1c",
            activeforeground="#ffffff", relief="flat", bd=0,
            font=("Segoe UI",10,"bold"), cursor="hand2",
            padx=14, pady=7).pack(side="right")


def _handle_exception(exc_type, exc_value, exc_tb):
    """Global exception handler — logs to file and shows ErrorDialog."""
    # Always print to console too
    traceback.print_exception(exc_type, exc_value, exc_tb)

    # Write to log file
    try:
        ensure_dir()
        log_path = DATA_DIR / "error.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Version:   {APP_VERSION}\n")
            f.write(f"Platform:  {sys.platform}\n")
            f.write("="*60 + "\n")
            f.write("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
    except Exception:
        pass

    # Show the dialog (must run on main thread)
    try:
        dlg = ErrorDialog(exc_type, exc_value, exc_tb)
        dlg.mainloop()
    except Exception:
        pass


def _tk_exception_handler(exc, val, tb, *args):
    """Hook into Tkinter's internal exception handler."""
    _handle_exception(exc, val, tb)


class InvoiceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.title("Invoice Generator")
        self.geometry("1280x820")
        self.minsize(900, 600)
        self.configure(bg=BG_DARK)

        # App icon
        if ICON_FILE.exists():
            try:
                self.iconbitmap(str(ICON_FILE))
            except Exception:
                pass

        self._build_layout()
        self._invoice_prefill = None
        # Apply saved theme before building layout
        apply_theme(self.settings.get("theme_mode","Dark"))
        self._show_page("dashboard")
        self._bind_shortcuts()
        self._setup_close_confirm()

    # ── Layout ────────────────────────────────────────────────────────────
    def _build_layout(self):
        self._sidebar_open = True

        # ── Collapse toggle strip (always visible, 24px wide) ─────────────
        self._toggle_strip = tk.Frame(self, bg=BG_HOVER, width=24)
        self._toggle_strip.pack(side="left", fill="y")
        self._toggle_strip.pack_propagate(False)
        self._toggle_btn = tk.Label(
            self._toggle_strip, text="◀", bg=BG_HOVER, fg=TEXT_DIM,
            font=("Segoe UI", 9), cursor="hand2")
        self._toggle_btn.pack(expand=True)
        self._toggle_btn.bind("<Button-1>", lambda e: self._toggle_sidebar())
        self._toggle_strip.bind("<Button-1>", lambda e: self._toggle_sidebar())

        # ── Sidebar — fixed width, does NOT expand ────────────────────────
        self.sidebar = tk.Frame(self, bg=BG_DARK, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar top spacer + divider
        tk.Frame(self.sidebar, bg=BG_DARK, height=14).pack()
        Divider(self.sidebar).pack(fill="x", padx=10, pady=(0,8))

        self.nav_buttons = {}
        for key, icon, label in [
            ("dashboard", "📊", "Dashboard"),
            ("invoice",   "📄", "New Invoice"),
            ("history",   "📁", "Invoices"),
            ("clients",   "👥", "Clients"),
            ("expenses",   "💸", "Expenses"),
            ("reports",    "📈", "Reports"),
            ("reminders",  "🔔", "Reminders"),
            ("recurring",  "🔁", "Recurring"),
            ("profiles",   "🏢", "Profiles"),
            ("settings",   "⚙️", "Settings"),
            ("help",      "❓", "Help & Tutorial"),
            ("about",     "ℹ️",  "About"),
        ]:
            btn = NavButton(self.sidebar, text=label, icon=icon,
                            command=lambda k=key: self._show_page(k))
            btn.pack(fill="x", padx=6, pady=1)
            self.nav_buttons[key] = btn

        tk.Label(self.sidebar, text=f"v{APP_VERSION}",
                 bg=BG_DARK, fg=TEXT_DIM, font=FONT_SMALL).pack(side="bottom", pady=10)

        # ── Active profile indicator ──────────────────────────────────────
        self._profile_lbl = tk.Label(self.sidebar, text="", bg=BG_DARK,
            fg=ACCENT, font=("Segoe UI",8,"bold"),
            cursor="hand2", wraplength=180, justify="center")
        self._profile_lbl.pack(side="bottom", pady=(0,4))
        self._profile_lbl.bind("<Button-1>",
            lambda e: self._show_page("profiles"))
        self._refresh_profile_label()

        # Content — fills ALL remaining space and resizes with window
        self.content = tk.Frame(self, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

    def _toggle_sidebar(self):
        """Collapse or expand the sidebar."""
        if self._sidebar_open:
            # Collapse — hide sidebar, flip arrow to ▶
            self.sidebar.pack_forget()
            self._toggle_btn.config(text="▶", fg=ACCENT)
            self._toggle_strip.config(bg=BG_DARK,
                highlightthickness=1, highlightbackground=BORDER)
            self._sidebar_open = False
        else:
            # Expand — show sidebar before content, flip arrow to ◀
            self.sidebar.pack(side="left", fill="y",
                              before=self.content)
            self.sidebar.pack_propagate(False)
            self._toggle_btn.config(text="◀", fg=TEXT_DIM)
            self._toggle_strip.config(bg=BG_HOVER, highlightthickness=0)
            self._sidebar_open = True

    def _show_page(self, key, prefill=None):
        for k, b in self.nav_buttons.items(): b.set_active(k == key)
        for w in self.content.winfo_children(): w.destroy()
        if prefill is not None:
            # Explicit prefill passed — use it (edit/duplicate)
            self._invoice_prefill = prefill
        else:
            # No prefill — always clear it so New Invoice starts fresh
            self._invoice_prefill = None
        {
            "dashboard": self._pg_dashboard,
            "invoice":   lambda: self._pg_invoice(self._invoice_prefill),
            "history":   self._pg_history,
            "clients":   self._pg_clients,
            "expenses":   self._pg_expenses,
            "reports":    self._pg_reports,
            "reminders":  self._pg_reminders,
            "recurring":  self._pg_recurring,
            "profiles":   self._pg_profiles,
            "settings":   self._pg_settings,
            "help":      self._pg_help,
            "about":     self._pg_about,
        }[key]()

    # ── Shared page helpers ───────────────────────────────────────────────
    def _page_pad(self):
        """Scrollable page — Invoice, Settings, Help."""
        inner = make_scrollable(self.content)
        # Get the canvas and scroll to top immediately
        canvas = self.content.winfo_children()[-1] if self.content.winfo_children() else None
        if canvas and isinstance(canvas, tk.Canvas):
            canvas.after(10, lambda: canvas.yview_moveto(0))
        pad = tk.Frame(inner, bg=BG_DARK)
        pad.pack(fill="both", expand=True, padx=22, pady=20)
        return pad

    def _plain_pad(self):
        """Non-scrollable page — Dashboard, Clients, About."""
        pad = tk.Frame(self.content, bg=BG_DARK)
        pad.pack(fill="both", expand=True, padx=22, pady=20)
        return pad

    def _bind_shortcuts(self):
        """Bind all keyboard shortcuts from settings. Called on init and after settings save."""

        def _parse(val):
            """Convert 'Ctrl+N' -> '<Control-n>' for tkinter bind."""
            if not val: return None
            val = val.strip()
            parts = [p.strip() for p in val.replace("+", " ").split()]
            mods, key = [], ""
            for p in parts:
                pl = p.lower()
                if pl in ("ctrl","control"):   mods.append("Control")
                elif pl in ("alt",):           mods.append("Alt")
                elif pl in ("shift",):         mods.append("Shift")
                elif pl == "comma":            key = "comma"
                else:                          key = p
            if not key: return None
            mod_str = "-".join(mods)
            return f"<{mod_str}-{key.lower()}>" if mod_str else f"<{key.lower()}>"

        # Unbind ALL previously registered shortcuts cleanly
        for seq in getattr(self, "_registered_shortcuts", []):
            try: self.unbind(seq)
            except Exception: pass
        self._registered_shortcuts = []

        s = self.settings

        # ── Configurable shortcuts (from Settings page) ───────────────────
        configurable = [
            ("shortcut_new_invoice",  lambda e: (self._show_page("invoice"), "break")),
            ("shortcut_export_pdf",   lambda e: (self._safe_export(), "break")),
            ("shortcut_save_draft",   lambda e: (self._safe_save_draft(), "break")),
            ("shortcut_focus_search", lambda e: (self._safe_focus_search(), "break")),
            ("shortcut_dashboard",    lambda e: (self._show_page("dashboard"), "break")),
            ("shortcut_invoices",     lambda e: (self._show_page("history"), "break")),
            ("shortcut_clients",      lambda e: (self._show_page("clients"), "break")),
            ("shortcut_settings",     lambda e: (self._show_page("settings"), "break")),
            ("shortcut_reload",       lambda e: (self._reload_current_page(), "break")),
            ("shortcut_clear_form",   lambda e: (self._safe_clear_form(e), "break")),
        ]
        for setting_key, cmd in configurable:
            seq = _parse(s.get(setting_key, ""))
            if seq:
                for variant in {seq, seq.replace(seq[-2], seq[-2].upper())}:
                    try:
                        self.bind(variant, cmd)
                        self._registered_shortcuts.append(variant)
                    except Exception:
                        pass

        # ── Hardcoded global shortcuts (always active, not configurable) ──
        hardcoded = [
            # Navigation
            ("<Alt-Left>",     lambda e: self._nav_back()),
            ("<F5>",           lambda e: (self._reload_current_page(), "break")),
            # Invoice form
            ("<Control-plus>", lambda e: (self._safe_add_line_item(), "break")),
            ("<Control-equal>",lambda e: (self._safe_add_line_item(), "break")),
            # App
            ("<Control-w>",    lambda e: (self._clear_cache_confirm(), "break")),
            ("<F1>",           lambda e: (self._show_page("help"), "break")),
            ("<Control-comma>",lambda e: (self._show_page("settings"), "break")),
            # Quick search
            ("<Control-k>",    lambda e: (self._quick_search_popup(), "break")),
            ("<Control-K>",    lambda e: (self._quick_search_popup(), "break")),
        ]
        for seq, cmd in hardcoded:
            try:
                self.bind(seq, cmd)
                self._registered_shortcuts.append(seq)
            except Exception:
                pass

    def _current_page(self):
        """Return the key of the currently active page."""
        for k, b in self.nav_buttons.items():
            if b._active:
                return k
        return None

    def _reload_current_page(self):
        """F5 — reload whatever page is currently open."""
        page = self._current_page()
        if page:
            self._show_page(page)

    def _nav_back(self):
        """Alt+Left — go back to invoices list (most common back action)."""
        page = self._current_page()
        if page and page != "history":
            self._show_page("history")

    def _safe_clear_form(self, event=None):
        """Escape — clear the invoice form if on New Invoice page."""
        page = self._current_page()
        if page == "invoice":
            # Only clear if no text field is focused (so Escape still works in fields)
            focused = self.focus_get()
            if focused and hasattr(focused, "delete"):
                return  # Let Escape work normally in the focused field
            self._show_page("invoice")

    def _safe_add_line_item(self):
        """Ctrl+= — add a line item if on invoice page."""
        if self._current_page() == "invoice":
            try:
                self._add_item()
            except Exception:
                pass

    def _clear_cache_confirm(self):
        """
        Ctrl+W — clear app cache (data files).
        Shows a confirmation dialog listing what will be cleared.
        """
        from tkinter import messagebox as _mb
        win = tk.Toplevel(self)
        win.title("Clear Cache")
        win.configure(bg=BG_DARK)
        win.grab_set()
        win.resizable(False, False)

        hf = tk.Frame(win, bg="#1a0808", padx=20, pady=14)
        hf.pack(fill="x")
        tk.Label(hf, text="🗑️  Clear Cache / Data",
                 bg="#1a0808", fg=RED_ERR,
                 font=("Segoe UI",12,"bold")).pack(anchor="w")
        tk.Label(hf,
            text="Choose what to clear. This cannot be undone.",
            bg="#1a0808", fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")

        body = tk.Frame(win, bg=BG_DARK, padx=20, pady=12)
        body.pack(fill="x")

        options = [
            ("counter",  "Invoice counter (resets numbering to start)", True),
            ("history",  "All invoices", False),
            ("clients",  "All clients", False),
            ("expenses", "All expenses", False),
            ("recurring","Recurring schedules", False),
            ("settings", "All settings (resets to defaults)", False),
        ]
        vars_ = {}
        for key, label, default in options:
            v = tk.BooleanVar(value=default)
            tk.Checkbutton(body, text=label, variable=v,
                bg=BG_DARK, fg=TEXT_WHITE, selectcolor=BG_HOVER,
                activebackground=BG_DARK, font=FONT_BODY,
                cursor="hand2").pack(anchor="w", pady=2)
            vars_[key] = v

        def do_clear():
            cleared = []
            if vars_["counter"].get():
                if COUNTER_FILE.exists(): COUNTER_FILE.unlink()
                cleared.append("Invoice counter")
            if vars_["history"].get():
                save_history([]); cleared.append("Invoices")
            if vars_["clients"].get():
                save_clients([]); cleared.append("Clients")
            if vars_["expenses"].get():
                save_expenses([]); cleared.append("Expenses")
            if vars_["recurring"].get():
                save_recurring([]); cleared.append("Recurring schedules")
            if vars_["settings"].get():
                if SETTINGS_FILE.exists(): SETTINGS_FILE.unlink()
                self.settings = load_settings()
                self._bind_shortcuts()
                cleared.append("Settings")
            win.destroy()
            if cleared:
                _mb.showinfo("✅ Cleared",
                    "Cleared:\n" + "\n".join(f"  • {c}" for c in cleared))
                self._show_page(self._current_page() or "dashboard")

        br = tk.Frame(win, bg=BG_DARK, padx=20, pady=12)
        br.pack(fill="x")
        tk.Button(br, text="🗑️  Clear Selected",
            command=do_clear,
            bg=RED_ERR, fg="#ffffff",
            font=("Segoe UI",10,"bold"),
            relief="flat", bd=0, padx=16, pady=8,
            cursor="hand2").pack(side="right", padx=(8,0))
        GhostButton(br, text="Cancel",
            command=win.destroy).pack(side="right")

        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - win.winfo_reqwidth())  // 2
        y = self.winfo_y() + (self.winfo_height() - win.winfo_reqheight()) // 2
        win.geometry(f"+{x}+{y}")

    def _setup_close_confirm(self):
        def _on_close():
            if self.settings.get("confirm_on_close", True):
                # Check if invoice page is open with content
                current = [k for k,b in self.nav_buttons.items() if b._active]
                if current and current[0] == "invoice":
                    if not messagebox.askyesno("Close",
                        "You may have unsaved invoice data.\nClose anyway?"):
                        return
            self.destroy()
        self.protocol("WM_DELETE_WINDOW", _on_close)

    def _safe_export(self):
        """Export only if on invoice page."""
        current = [k for k,b in self.nav_buttons.items() if b._active]
        if current and current[0] == "invoice":
            try: self._export()
            except Exception: pass

    def _safe_save_draft(self):
        """Save draft only if on invoice page."""
        current = [k for k,b in self.nav_buttons.items() if b._active]
        if current and current[0] == "invoice":
            try: self._save_draft()
            except Exception: pass

    def _safe_focus_search(self):
        """Focus search box on invoices or clients page."""
        current = [k for k,b in self.nav_buttons.items() if b._active]
        if not current: return
        page = current[0]
        if page == "history":
            try: self._inv_search_var  # check it exists
            except AttributeError: return
            # Find and focus the search entry
            for w in self.content.winfo_children():
                self._focus_entry_recursive(w)
        elif page == "clients":
            for w in self.content.winfo_children():
                self._focus_entry_recursive(w)

    def _focus_entry_recursive(self, widget):
        if isinstance(widget, tk.Entry):
            widget.focus_set()
            return True
        for child in widget.winfo_children():
            if self._focus_entry_recursive(child):
                return True
        return False

    def _update_logo_preview(self, path):
        """Update the logo preview label in settings with a thumbnail."""
        if not hasattr(self, "_logo_preview"): return
        if not PIL_OK: return
        try:
            img = PILImage.open(path).convert("RGBA")
            img.thumbnail((200, 60), PILImage.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._logo_preview.config(image=photo, text="")
            self._logo_preview._photo = photo  # keep reference
        except Exception:
            self._logo_preview.config(image="",
                text="⚠ Could not preview image", fg=RED_ERR)

    def _h1(self, parent, title, sub=""):
        tk.Label(parent, text=title, bg=BG_DARK, fg=TEXT_WHITE,
                 font=FONT_HEAD).pack(anchor="w", pady=(0, 2))
        if sub:
            tk.Label(parent, text=sub, bg=BG_DARK, fg=TEXT_DIM,
                     font=FONT_SUB).pack(anchor="w", pady=(0,12))

    def _section_card(self, parent, title):
        card = Card(parent)
        card.pack(fill="x", pady=(0,12))
        tk.Label(card, text=title, bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(card).pack(fill="x", padx=14)
        inner = tk.Frame(card, bg=BG_CARD, padx=14, pady=10)
        inner.pack(fill="x")
        return inner

    # ═══════════════ DASHBOARD ═══════════════════════════════════════════
    # ── Canvas bar chart helper ──────────────────────────────────────────
    def _bar_chart(self, parent, data, title, color=None, height=160):
        """Draw a simple bar chart using tkinter Canvas. data = list of (label, value)."""
        color = color or ACCENT
        card = Card(parent)
        card.pack(fill="x", pady=(0,12))
        tk.Label(card, text=title, bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(card).pack(fill="x", padx=14)

        if not data or all(v == 0 for _, v in data):
            tk.Label(card, text="No data yet", bg=BG_CARD, fg=TEXT_DIM,
                     font=FONT_BODY, pady=20).pack()
            return

        c = tk.Canvas(card, bg=BG_CARD, height=height, highlightthickness=0)
        c.pack(fill="x", padx=14, pady=(8,12))

        def _draw(event=None):
            c.delete("all")
            W = c.winfo_width() or 600
            H = height
            pad_l, pad_r, pad_t, pad_b = 10, 10, 10, 30
            n = len(data)
            max_val = max(v for _, v in data) or 1
            bar_area_w = W - pad_l - pad_r
            bar_w = max(8, int(bar_area_w / n * 0.6))
            gap   = (bar_area_w - bar_w * n) / (n + 1)
            chart_h = H - pad_t - pad_b

            # Grid lines
            for pct in (0.25, 0.5, 0.75, 1.0):
                y = pad_t + chart_h * (1 - pct)
                c.create_line(pad_l, y, W-pad_r, y, fill=BORDER, dash=(2,4))

            for i, (label, val) in enumerate(data):
                x = pad_l + gap + i * (bar_w + gap)
                bar_h = int(chart_h * (val / max_val))
                y0 = pad_t + chart_h - bar_h
                y1 = pad_t + chart_h

                # Bar with slight rounding effect (two rects)
                c.create_rectangle(x, y0+2, x+bar_w, y1, fill=color, outline="", width=0)
                c.create_rectangle(x, y0,   x+bar_w, y0+4, fill=color, outline="", width=0)

                # Value label above bar
                if bar_h > 16:
                    sym = self.settings.get("currency_symbol","£")
                    c.create_text(x + bar_w//2, y0-4,
                        text=f"{sym}{val:,.0f}" if val >= 1 else "",
                        fill=TEXT_WHITE, font=("Segoe UI",7), anchor="s")

                # X label
                c.create_text(x + bar_w//2, H - pad_b + 8,
                    text=label, fill=TEXT_DIM,
                    font=("Segoe UI",7), anchor="n")

        c.bind("<Configure>", _draw)
        c.after(50, _draw)

    def _pg_dashboard(self):
        inner = make_scrollable(self.content)
        pad = tk.Frame(inner, bg=BG_DARK)
        pad.pack(fill="both", expand=True, padx=22, pady=20)

        tr = tk.Frame(pad, bg=BG_DARK)
        tr.pack(fill="x", pady=(0,14))
        self._h1(tr, "Dashboard", "Your business at a glance")
        GhostButton(tr, text="📈  Reports",
                    command=lambda: self._show_page("reports")).pack(side="right")

        history  = load_history()
        expenses = load_expenses()
        sym = self.settings.get("currency_symbol","£")
        fmt = self.settings.get("date_format","DD/MM/YYYY")

        for h in history:
            if h.get("status") == "Unpaid" and is_overdue(h.get("due_date",""), fmt):
                h["status"] = "Overdue"
        save_history(history)

        revenue     = sum(h.get("total",0) for h in history if h.get("status") == "Paid")
        outstanding = sum(h.get("total",0) for h in history if h.get("status") == "Unpaid")
        overdue_amt = sum(h.get("total",0) for h in history if h.get("status") == "Overdue")
        total_inv   = len(history)
        total_exp   = sum(e.get("amount",0) for e in expenses)
        net_profit  = revenue - total_exp

        # ── 8 stat cards ────────────────────────────────────────────────
        sf = tk.Frame(pad, bg=BG_DARK)
        sf.pack(fill="x", pady=(0,14))
        for i in range(4): sf.columnconfigure(i, weight=1)

        stats = [
            ("Total Revenue",  fc(revenue,sym),     ACCENT,   "All paid invoices"),
            ("Net Profit",     fc(net_profit,sym),  "#22d3ee", "Revenue minus expenses"),
            ("Outstanding",    fc(outstanding,sym),  GOLD,     "Awaiting payment"),
            ("Overdue",        fc(overdue_amt,sym),  RED_ERR,  "Past due date"),
        ]
        for i, (label, val, col, sub) in enumerate(stats):
            c = Card(sf)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i==0 else 6, 0))
            cf = tk.Frame(c, bg=BG_CARD, padx=14, pady=12)
            cf.pack(fill="both", expand=True)
            tk.Label(cf, text=label, bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
            tk.Label(cf, text=val, bg=BG_CARD, fg=col,
                     font=("Segoe UI",15,"bold")).pack(anchor="w", pady=(2,0))
            tk.Label(cf, text=sub, bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")

        sf2 = tk.Frame(pad, bg=BG_DARK)
        sf2.pack(fill="x", pady=(0,14))
        for i in range(4): sf2.columnconfigure(i, weight=1)

        stats2 = [
            ("Total Expenses", fc(total_exp,sym),   RED_ERR,  "All logged expenses"),
            ("Total Invoices", str(total_inv),       BLUE,     "All time"),
            ("Paid Invoices",  str(sum(1 for h in history if h.get("status")=="Paid")), ACCENT, ""),
            ("Clients",        str(len(load_clients())), PURPLE, "In address book"),
        ]
        for i, (label, val, col, sub) in enumerate(stats2):
            c = Card(sf2)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i==0 else 6, 0))
            cf = tk.Frame(c, bg=BG_CARD, padx=14, pady=12)
            cf.pack(fill="both", expand=True)
            tk.Label(cf, text=label, bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
            tk.Label(cf, text=val, bg=BG_CARD, fg=col,
                     font=("Segoe UI",15,"bold")).pack(anchor="w", pady=(2,0))
            if sub:
                tk.Label(cf, text=sub, bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")

        # ── Monthly revenue chart ────────────────────────────────────────
        # Last 6 months
        months_data = {}
        now = datetime.today()
        for delta in range(5, -1, -1):
            d = datetime(now.year, now.month, 1) - timedelta(days=delta*28)
            key = d.strftime("%b %y")
            months_data[key] = 0

        for h in history:
            if h.get("status") != "Paid": continue
            try:
                date_str = h.get("date","")
                if fmt == "DD/MM/YYYY": d = datetime.strptime(date_str, "%d/%m/%Y")
                elif fmt == "MM/DD/YYYY": d = datetime.strptime(date_str, "%m/%d/%Y")
                else: d = datetime.strptime(date_str, "%Y-%m-%d")
                key = d.strftime("%b %y")
                if key in months_data:
                    months_data[key] += h.get("total",0)
            except Exception:
                pass

        chart_row = tk.Frame(pad, bg=BG_DARK)
        chart_row.pack(fill="x", pady=(0,12))
        chart_row.columnconfigure(0, weight=3)
        chart_row.columnconfigure(1, weight=2)

        chart_left = tk.Frame(chart_row, bg=BG_DARK)
        chart_left.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        self._bar_chart(chart_left,
            list(months_data.items()),
            "MONTHLY REVENUE  (last 6 months)",
            color=ACCENT, height=180)

        # ── Expenses vs Revenue bar ──────────────────────────────────────
        chart_right = tk.Frame(chart_row, bg=BG_DARK)
        chart_right.grid(row=0, column=1, sticky="nsew")
        self._bar_chart(chart_right,
            [("Revenue", revenue), ("Expenses", total_exp), ("Profit", max(net_profit,0))],
            "REVENUE vs EXPENSES",
            color=ACCENT, height=180)

        # ── Outstanding per client ───────────────────────────────────────
        client_owed = {}
        for h in history:
            if h.get("status") in ("Unpaid","Overdue"):
                name = h.get("client_name") or h.get("client","Unknown")
                client_owed[name] = client_owed.get(name,0) + h.get("total",0)

        oc = Card(pad)
        oc.pack(fill="x", pady=(0,12))
        tk.Label(oc, text="OUTSTANDING BALANCE PER CLIENT", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(oc).pack(fill="x", padx=14)

        if client_owed:
            sorted_clients = sorted(client_owed.items(), key=lambda x: x[1], reverse=True)
            for i, (name, amt) in enumerate(sorted_clients[:6]):
                rb = BG_CARD if i%2==0 else BG_HOVER
                row = tk.Frame(oc, bg=rb, padx=14, pady=8)
                row.pack(fill="x")
                row.columnconfigure(0, weight=1)
                tk.Label(row, text=name, bg=rb, fg=TEXT_WHITE,
                         font=FONT_BODY, anchor="w").grid(row=0, column=0, sticky="ew")
                tk.Label(row, text=fc(amt,sym), bg=rb, fg=GOLD,
                         font=("Segoe UI",10,"bold"), anchor="e").grid(row=0, column=1, sticky="e")
        else:
            tk.Label(oc, text="No outstanding balances — all invoices paid! 🎉",
                     bg=BG_CARD, fg=ACCENT, font=FONT_BODY, pady=14).pack()

        # ── Quick actions ────────────────────────────────────────────────
        qi = self._section_card(pad, "QUICK ACTIONS")
        GreenButton(qi, text="＋  New Invoice",
                    command=lambda: self._show_page("invoice")).pack(side="left", padx=(0,8))
        GhostButton(qi, text="💸  Add Expense",
                    command=lambda: self._add_expense_dialog()).pack(side="left", padx=(0,8))
        GhostButton(qi, text="👥  Add Client",
                    command=lambda: self._add_client_dialog()).pack(side="left", padx=(0,8))
        GhostButton(qi, text="📁  All Invoices",
                    command=lambda: self._show_page("history")).pack(side="left", padx=(0,8))

        # ── Late fee callout ─────────────────────────────────────────────
        if str(self.settings.get("late_fee_enabled","False")).lower() in ("true","1"):
            fee_eligible = []
            for h in history:
                fee, _ = self._calc_late_fee(h)
                if fee > 0:
                    fee_eligible.append(h)
            if fee_eligible:
                fc_card = tk.Frame(pad, bg="#1a1000",
                    highlightthickness=1, highlightbackground=GOLD)
                fc_card.pack(fill="x", pady=(0,12))
                ff = tk.Frame(fc_card, bg="#1a1000", padx=14, pady=10)
                ff.pack(fill="x")
                tk.Label(ff,
                    text=f"⏰  {len(fee_eligible)} invoice(s) eligible for late fees",
                    bg="#1a1000", fg=GOLD,
                    font=("Segoe UI",10,"bold")).pack(side="left")
                GhostButton(ff, text="View Invoices",
                    command=lambda: self._show_page("history")
                ).pack(side="right")

        # ── Recent invoices ──────────────────────────────────────────────
        rc = Card(pad)
        rc.pack(fill="x")
        tk.Label(rc, text="RECENT INVOICES", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(rc).pack(fill="x", padx=14)

        hdr = tk.Frame(rc, bg=BG_HOVER, padx=14, pady=7)
        hdr.pack(fill="x")
        hdr.columnconfigure(0, weight=2); hdr.columnconfigure(1, weight=3)
        hdr.columnconfigure(2, weight=2); hdr.columnconfigure(3, weight=2)
        hdr.columnconfigure(4, weight=1)
        for i, txt in enumerate(["Invoice #","Client","Date","Amount","Status"]):
            tk.Label(hdr, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                     font=("Segoe UI",9,"bold"), anchor="w").grid(
                     row=0, column=i, sticky="ew", padx=(0,8))

        for i, h in enumerate(history[:6]):
            rb = BG_CARD if i%2==0 else BG_HOVER
            row = tk.Frame(rc, bg=rb, padx=14, pady=7)
            row.pack(fill="x")
            row.columnconfigure(0, weight=2); row.columnconfigure(1, weight=3)
            row.columnconfigure(2, weight=2); row.columnconfigure(3, weight=2)
            row.columnconfigure(4, weight=1)
            client = h.get("client_name") or h.get("client","—")
            inv_sym = h.get("currency_symbol") or sym
            for ci, txt in enumerate([h.get("number","—"), client,
                                       h.get("date","—"),
                                       fc(h.get("total",0),inv_sym)]):
                tk.Label(row, text=str(txt), bg=rb, fg=TEXT_WHITE,
                         font=FONT_BODY, anchor="w").grid(
                         row=0, column=ci, sticky="ew", padx=(0,8))
            status_badge(row, h.get("status","Unpaid")).grid(row=0, column=4, sticky="w")

        if not history:
            tk.Label(rc, text="No invoices yet — create your first one!",
                     bg=BG_CARD, fg=TEXT_DIM, font=FONT_BODY, pady=20).pack()

        tk.Frame(pad, bg=BG_DARK, height=20).pack()

    # ═══════════════ NEW INVOICE ══════════════════════════════════════════
    def _pg_invoice(self, prefill=None):
        self.line_items = []
        pad = self._page_pad()

        # Title row
        tr = tk.Frame(pad, bg=BG_DARK)
        tr.pack(fill="x", pady=(0,14))
        tk.Label(tr, text="New Invoice", bg=BG_DARK, fg=TEXT_WHITE,
                 font=FONT_HEAD).pack(side="left")

        # Status + inv number on right
        right = tk.Frame(tr, bg=BG_DARK)
        right.pack(side="right")

        self._status_var = tk.StringVar(
            value=prefill.get("status","Unpaid") if prefill else "Unpaid")
        sf = tk.Frame(right, bg=BG_DARK)
        sf.pack(side="left", padx=(0,10))
        tk.Label(sf, text="Status:", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side="left")
        ttk.Combobox(sf, textvariable=self._status_var,
            values=["Draft","Unpaid","Paid","Overdue"],
            state="readonly", width=10, font=FONT_BODY
        ).pack(side="left", padx=6)

        inv_num, _ = next_inv_num(self.settings)
        self._inv_num = tk.StringVar(
            value=prefill.get("number", inv_num) if prefill else inv_num)
        nf = tk.Frame(right, bg=BG_CARD,
                      highlightthickness=1, highlightbackground=BORDER)
        nf.pack(side="left")
        tk.Label(nf, text="Invoice #", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL, padx=8, pady=6).pack(side="left")
        tk.Entry(nf, textvariable=self._inv_num,
            bg=BG_CARD, fg=ACCENT, insertbackground=ACCENT, relief="flat",
            bd=0, font=("Segoe UI",11,"bold"), width=12
        ).pack(side="left", padx=(0,8), pady=6)

        # ── Responsive two-column grid ────────────────────────────────────
        two_col = tk.Frame(pad, bg=BG_DARK)
        two_col.pack(fill="x", pady=(0,12))
        two_col.columnconfigure(0, weight=1)
        two_col.columnconfigure(1, weight=1)

        # Client card
        cc = Card(two_col)
        cc.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        tk.Label(cc, text="CLIENT DETAILS", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(cc).pack(fill="x", padx=14)
        cf = tk.Frame(cc, bg=BG_CARD, padx=14, pady=10)
        cf.pack(fill="both", expand=True)
        cf.columnconfigure(0, weight=1)

        clients = load_clients()
        self._client_entries = {}
        if clients:
            tk.Label(cf, text="Load from Address Book", bg=BG_CARD, fg=TEXT_DIM,
                     font=FONT_SMALL).pack(anchor="w", pady=(0,2))
            self._cpick = tk.StringVar(value="— Select client —")
            cb = ttk.Combobox(cf, textvariable=self._cpick, state="readonly",
                values=["— Select client —"]+[c["name"] for c in clients],
                font=FONT_BODY)
            cb.pack(fill="x", pady=(0,8))
            cb.bind("<<ComboboxSelected>>", lambda e: self._load_client())
            Divider(cf).pack(fill="x", pady=(0,8))

        for lbl_txt, key in [("Client / Company Name","client_name"),
                              ("Email","client_email"),("Phone","client_phone")]:
            tk.Label(cf, text=lbl_txt, bg=BG_CARD, fg=TEXT_DIM,
                     font=FONT_SMALL).pack(anchor="w", pady=(4,1))
            e = FlatEntry(cf)
            e.pack(fill="x", ipady=5)
            self._client_entries[key] = e

        tk.Label(cf, text="Billing Address", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", pady=(6,1))
        self._caddr = FlatText(cf, height=3)
        self._caddr.pack(fill="x")

        # Save client shortcut
        def _save_client_from_invoice():
            name = self._client_entries["client_name"].get_value().strip()
            if not name:
                messagebox.showwarning("Required", "Enter a client name first."); return
            existing = load_clients()
            if any(c.get("name","").lower() == name.lower() for c in existing):
                if not messagebox.askyesno("Already Exists",
                    f"'{name}' is already in your address book.\nUpdate their details?"):
                    return
                existing = [c for c in existing if c.get("name","").lower() != name.lower()]
            existing.append({
                "name":    name,
                "email":   self._client_entries["client_email"].get_value(),
                "phone":   self._client_entries["client_phone"].get_value(),
                "address": self._caddr.get("1.0","end").strip(),
                "website": "",
                "notes":   "",
            })
            save_clients(existing)
            messagebox.showinfo("✅ Saved",
                f"'{name}' saved to your Client Address Book.")

        save_client_row = tk.Frame(cf, bg=BG_CARD)
        save_client_row.pack(fill="x", pady=(8,0))
        GhostButton(save_client_row, text="👥  Save to Address Book",
                    command=_save_client_from_invoice).pack(side="left")

        # Meta card
        mc = Card(two_col)
        mc.grid(row=0, column=1, sticky="nsew", padx=(8,0))
        tk.Label(mc, text="INVOICE DETAILS", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(mc).pack(fill="x", padx=14)
        mf = tk.Frame(mc, bg=BG_CARD, padx=14, pady=10)
        mf.pack(fill="both", expand=True)
        mf.columnconfigure(0, weight=1)
        mf.columnconfigure(1, weight=1)

        dfmt = self.settings["date_format"]
        self._date_e = FlatEntry(mf)
        self._date_e.insert(0, fdate(dfmt))
        self._due_e  = FlatEntry(mf)
        self._due_e.insert(0, duedate(self.settings["payment_terms"], dfmt))

        for col_i, (lbl_txt, entry) in enumerate([
            ("Invoice Date", self._date_e),
            ("Due Date",     self._due_e),
        ]):
            tk.Label(mf, text=lbl_txt, bg=BG_CARD, fg=TEXT_DIM,
                     font=FONT_SMALL).grid(row=0, column=col_i, sticky="w", pady=(0,2), padx=(0,8))
            entry.grid(row=1, column=col_i, sticky="ew", ipady=5, padx=(0,8), pady=(0,8))

        tk.Label(mf, text="PO / Reference", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0,2))
        self._po_e = FlatEntry(mf)
        self._po_e.grid(row=3, column=0, columnspan=2, sticky="ew", ipady=5, pady=(0,8))

        disc_row = tk.Frame(mf, bg=BG_CARD)
        disc_row.grid(row=4, column=0, columnspan=2, sticky="ew")
        tk.Label(disc_row, text="Discount %", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side="left")
        self._disc_e = FlatEntry(disc_row, width=8)
        self._disc_e.insert(0, str(prefill.get("discount","0")) if prefill else "0")
        self._disc_e.pack(side="left", padx=(8,0), ipady=4)

        # Currency override per invoice
        tk.Label(disc_row, text="Currency:", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side="left", padx=(16,4))
        self._currency_var = tk.StringVar(
            value=prefill.get("currency_symbol", self.settings.get("currency_symbol","£")) if prefill
            else self.settings.get("currency_symbol","£"))
        currency_cb = ttk.Combobox(disc_row, textvariable=self._currency_var,
            values=["£","$","€","C$","A$","¥","CHF","kr"], width=5,
            font=FONT_BODY, state="readonly")
        currency_cb.pack(side="left")

        # Template picker
        tk.Label(disc_row, text="Template:", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side="left", padx=(16,4))
        self._template_var = tk.StringVar(
            value=prefill.get("invoice_template", self.settings.get("invoice_template","Professional")) if prefill
            else self.settings.get("invoice_template","Professional"))
        ttk.Combobox(disc_row, textvariable=self._template_var,
            values=["Professional","Minimal","Bold"], width=12,
            font=FONT_BODY, state="readonly").pack(side="left")

        # Partial payment tracking
        pp_row = tk.Frame(mf, bg=BG_CARD)
        pp_row.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(8,0))
        tk.Label(pp_row, text="Amount Paid:", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side="left")
        self._paid_amt_e = FlatEntry(pp_row, width=10)
        self._paid_amt_e.insert(0, str(prefill.get("amount_paid","0")) if prefill else "0")
        self._paid_amt_e.pack(side="left", padx=(8,0), ipady=4)
        tk.Label(pp_row, text="(0 = unpaid, partial shows balance on PDF)",
                 bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI",8)).pack(side="left", padx=(8,0))

        # ── Line items ────────────────────────────────────────────────────
        ic = Card(pad)
        ic.pack(fill="x", pady=(0,12))
        ih = tk.Frame(ic, bg=BG_CARD, padx=14, pady=8)
        ih.pack(fill="x")
        tk.Label(ih, text="LINE ITEMS", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold")).pack(side="left")
        total_right = tk.Frame(ih, bg=BG_CARD)
        total_right.pack(side="right")
        self._total_lbl = tk.Label(total_right, text="Total: £0.00", bg=BG_CARD,
                                   fg=TEXT_WHITE, font=("Segoe UI",11,"bold"),
                                   cursor="hand2")
        self._total_lbl.pack(side="left")
        self._copy_lbl = tk.Label(total_right, text=" 📋", bg=BG_CARD,
                                  fg=TEXT_DIM, font=FONT_SMALL, cursor="hand2")
        self._copy_lbl.pack(side="left")

        def _copy_total(e=None):
            val = self._total_lbl.cget("text").replace("Total: ","")
            self.clipboard_clear(); self.clipboard_append(val)
            self._copy_lbl.config(text=" ✓ Copied!", fg=ACCENT)
            self.after(1800, lambda: self._copy_lbl.config(text=" 📋", fg=TEXT_DIM))
        self._total_lbl.bind("<Button-1>", _copy_total)
        self._copy_lbl.bind("<Button-1>", _copy_total)
        tk.Label(total_right, text=" (click to copy)", bg=BG_CARD,
                 fg=TEXT_DIM, font=("Segoe UI",8)).pack(side="left")
        Divider(ic).pack(fill="x", padx=14)

        ch = tk.Frame(ic, bg=BG_HOVER, padx=14, pady=5)
        ch.pack(fill="x")
        ch.columnconfigure(0, weight=1)
        for ci, txt in enumerate(["Description","Qty","Unit Price","Tax","Amount",""]):
            tk.Label(ch, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                     font=FONT_SMALL, anchor="w").grid(row=0, column=ci, sticky="ew", padx=2)

        self._items_frame = tk.Frame(ic, bg=BG_CARD, padx=14, pady=6)
        self._items_frame.pack(fill="x")
        self._items_frame.columnconfigure(0, weight=1)

        if prefill and prefill.get("items"):
            for item in prefill["items"]: self._add_item(item)
        else:
            for _ in range(3): self._add_item()

        bf = tk.Frame(ic, bg=BG_CARD, padx=14, pady=8)
        bf.pack(fill="x")
        GhostButton(bf, text="＋  Add Line Item", command=self._add_item).pack(side="left")

        # ── Notes ────────────────────────────────────────────────────────
        nc = Card(pad)
        nc.pack(fill="x", pady=(0,12))
        tk.Label(nc, text="NOTES & TERMS", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(nc).pack(fill="x", padx=14)
        nf2 = tk.Frame(nc, bg=BG_CARD, padx=14, pady=10)
        nf2.pack(fill="x")
        nf2.columnconfigure(0, weight=1)
        default_note = self.settings.get("default_notes","").replace(
            "{terms}", str(self.settings.get("payment_terms",30)))
        self._notes = FlatText(nf2, height=3)
        self._notes.insert("1.0", prefill.get("notes",default_note) if prefill else default_note)
        self._notes.pack(fill="x")

        # Prefill
        if prefill:
            for key, entry in self._client_entries.items():
                entry.set_value(prefill.get(key,""))
            self._caddr.delete("1.0","end")
            self._caddr.insert("1.0", prefill.get("client_address",""))
            if prefill.get("date"):
                self._date_e.delete(0,"end"); self._date_e.insert(0,prefill["date"])
            if prefill.get("due_date"):
                self._due_e.delete(0,"end"); self._due_e.insert(0,prefill["due_date"])
            if prefill.get("po"):
                self._po_e.set_value(prefill["po"])
            if prefill.get("currency_symbol"):
                self._currency_var.set(prefill["currency_symbol"])
            if prefill.get("invoice_template"):
                self._template_var.set(prefill["invoice_template"])
            if prefill.get("amount_paid"):
                self._paid_amt_e.delete(0,"end")
                self._paid_amt_e.insert(0, prefill["amount_paid"])

        # Actions
        ar = tk.Frame(pad, bg=BG_DARK)
        ar.pack(fill="x", pady=(4,20))
        GreenButton(ar, text="⬇  Export PDF", command=self._export).pack(side="right", padx=(8,0))
        GreenButton(ar, text="📧  Email", command=self._email,
                    secondary=True).pack(side="right", padx=(8,0))
        GhostButton(ar, text="👁  Preview",    command=self._preview).pack(side="right")
        save_lbl = "💾  Save" if prefill else "💾  Save Draft"
        GhostButton(ar, text=save_lbl, command=self._save_draft).pack(side="right", padx=(0,8))
        GhostButton(ar, text="🔄  Reset", command=lambda: self._show_page("invoice")).pack(side="left")

    def _add_item(self, item=None):
        sym = self._currency_var.get() if hasattr(self,"_currency_var") else self.settings.get("currency_symbol","£")
        row = LineItemRow(self._items_frame,
            on_change=self._recalc,
            on_delete=lambda r=None: self._del_item(row),
            sym=sym)
        row.pack(fill="x", pady=1)
        self.line_items.append(row)
        if item: row.load(item)

    def _del_item(self, row):
        if len(self.line_items) <= 1:
            messagebox.showinfo("Info","At least one line item required."); return
        self.line_items.remove(row); row.destroy(); self._recalc()

    def _recalc(self):
        sym = self._currency_var.get() if hasattr(self,"_currency_var") else self.settings.get("currency_symbol","£")
        tr  = float(self.settings.get("tax_rate",20))
        sub = tax = 0
        try: disc = float(self._disc_e.get() or 0)
        except: disc = 0
        for r in self.line_items:
            d = r.get_data()
            sub += d["total"]
            if d["taxable"]: tax += d["total"]*(tr/100)
        grand = sub + tax - sub*(disc/100)
        self._total_lbl.config(text=f"Total: {fc(grand, sym)}")

    def _collect(self):
        sym  = self.settings.get("currency_symbol","£")
        tr   = float(self.settings.get("tax_rate",20))
        items= [r.get_data() for r in self.line_items]
        sub  = sum(i["total"] for i in items)
        tax  = sum(i["total"]*(tr/100) for i in items if i["taxable"])
        try: disc = float(self._disc_e.get() or 0)
        except: disc = 0
        grand = sub + tax - sub*(disc/100)
        return {
            "number":         self._inv_num.get(),
            "date":           self._date_e.get(),
            "due_date":       self._due_e.get(),
            "po":             self._po_e.get_value(),
            "status":         self._status_var.get(),
            "client_name":    self._client_entries["client_name"].get_value(),
            "client_email":   self._client_entries["client_email"].get_value(),
            "client_phone":   self._client_entries["client_phone"].get_value(),
            "client_address": self._caddr.get("1.0","end").strip(),
            "discount":         self._disc_e.get() or "0",
            "notes":            self._notes.get("1.0","end").strip(),
            "items":            items,
            "total":            grand,
            "currency_symbol":  self._currency_var.get(),
            "invoice_template": self._template_var.get(),
            "amount_paid":      self._paid_amt_e.get() or "0",
        }

    def _load_client(self):
        name = self._cpick.get()
        if name == "— Select client —": return
        for c in load_clients():
            if c["name"] == name:
                self._client_entries["client_name"].set_value(c.get("name",""))
                self._client_entries["client_email"].set_value(c.get("email",""))
                self._client_entries["client_phone"].set_value(c.get("phone",""))
                self._caddr.delete("1.0","end")
                self._caddr.insert("1.0", c.get("address",""))
                break

    def _preview(self):
        data = self._collect()
        # Use per-invoice currency if set
        sym  = data.get("currency_symbol") or self.settings.get("currency_symbol","£")
        tr   = float(self.settings.get("tax_rate",20))
        tl   = self.settings.get("tax_label","VAT")
        tmpl = data.get("invoice_template","Professional")
        items= [i for i in data["items"] if i["desc"]]
        sub  = sum(i["total"] for i in items)
        tax  = sum(i["total"]*(tr/100) for i in items if i["taxable"])
        try: disc = float(data["discount"])
        except: disc = 0
        grand = sub + tax - sub*(disc/100)
        try: paid = float(data.get("amount_paid",0) or 0)
        except: paid = 0

        win = tk.Toplevel(self)
        win.title(f"Preview — {data['number']}")
        win.geometry("580x680")
        win.configure(bg="#ffffff")
        txt = tk.Text(win, bg="#ffffff", fg="#111", font=("Courier New",10),
                      relief="flat", padx=20, pady=20)
        txt.pack(fill="both", expand=True)
        lines = [
            "="*56, f"  {self.settings['company_name']}", "="*56,
            f"  Invoice: {data['number']}   [{data['status']}]",
            f"  Template: {tmpl}   Currency: {sym}",
            f"  Date: {data['date']}   Due: {data['due_date']}",
            "-"*56,
            f"  Bill To: {data['client_name']}",
            f"           {data['client_email']}",
            "-"*56,
            f"  {'Description':<24} {'Qty':>4} {'Price':>9} {'Total':>9}",
            "  "+"-"*52,
        ]
        for i in items:
            lines.append(f"  {i['desc']:<24} {i['qty']:>4} "
                         f"{fc(i['price'],sym):>9} {fc(i['total'],sym):>9}")
        lines += ["  "+"-"*52,
                  f"  {'Subtotal':<38} {fc(sub,sym):>9}",
                  f"  {tl+' ('+str(tr)+'%)':<38} {fc(tax,sym):>9}"]
        if disc: lines.append(f"  {'Discount ('+str(disc)+'%)':<38} -{fc(sub*(disc/100),sym):>8}")
        if paid > 0 and paid < grand:
            lines += ["  "+"="*52,
                      f"  {'Gross Total':<38} {fc(grand,sym):>9}",
                      f"  {'Amount Paid':<38} -{fc(paid,sym):>8}",
                      f"  {'BALANCE DUE':<38} {fc(grand-paid,sym):>9}"]
        elif paid >= grand:
            lines += ["  "+"="*52,
                      f"  {'TOTAL':<38} {fc(grand,sym):>9}",
                      f"  {'PAID IN FULL':<38} {'':>9}"]
        else:
            lines += ["  "+"="*52, f"  {'TOTAL DUE':<38} {fc(grand,sym):>9}"]
        lines.append("="*56)
        # Show payment links in preview
        paypal = self.settings.get("paypal_link","").strip()
        stripe = self.settings.get("stripe_link","").strip()
        custom_url   = self.settings.get("custom_pay_link","").strip()
        custom_label = self.settings.get("custom_pay_label","Pay Online").strip() or "Pay Online"
        pay_links = []
        if paypal: pay_links.append(f"  PayPal:  {paypal}")
        if stripe: pay_links.append(f"  Stripe:  {stripe}")
        if custom_url: pay_links.append(f"  {custom_label}:  {custom_url}")
        if pay_links and data.get("status") != "Paid":
            lines += ["", "  PAY NOW:", "-"*56] + pay_links + ["-"*56]
        txt.insert("1.0", "\n".join(lines))
        txt.config(state="disabled")

    def _check_duplicate_number(self, number, current_status=None):
        """
        Check if an invoice number already exists in history.
        Returns True if it's safe to proceed, False if user cancels.
        If the existing entry is a Draft being edited, allow it silently.
        """
        history = load_history()
        existing = next((h for h in history if h.get("number") == number), None)
        if not existing:
            return True  # Number is free — safe to proceed

        # If we're editing the same draft, no conflict
        if (self._invoice_prefill is not None and
                self._invoice_prefill.get("number") == number):
            return True

        existing_client = existing.get("client_name") or existing.get("client", "Unknown")
        existing_status = existing.get("status", "Unknown")
        existing_date   = existing.get("date", "")
        existing_total  = existing.get("total", 0)
        sym = self.settings.get("currency_symbol", "£")

        # Build warning dialog
        win = tk.Toplevel(self)
        win.title("⚠️  Duplicate Invoice Number")
        win.configure(bg=BG_DARK)
        win.grab_set()
        win.resizable(False, False)

        result = {"proceed": False}

        hf = tk.Frame(win, bg="#1a1000", padx=18, pady=14)
        hf.pack(fill="x")
        tk.Label(hf, text=f"⚠️  Invoice {number} already exists",
                 bg="#1a1000", fg=GOLD,
                 font=("Segoe UI",12,"bold")).pack(anchor="w")
        tk.Label(hf,
            text="Saving will overwrite the existing invoice.",
            bg="#1a1000", fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")

        body = tk.Frame(win, bg=BG_CARD, padx=18, pady=14)
        body.pack(fill="x")
        tk.Label(body, text="Existing invoice details:",
                 bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w", pady=(0,6))

        for label, value, col in [
            ("Client:",  existing_client,                TEXT_WHITE),
            ("Date:",    existing_date,                   TEXT_MED),
            ("Status:",  existing_status,                 ACCENT if existing_status=="Paid" else GOLD),
            ("Amount:",  fc(existing_total, sym),         TEXT_WHITE),
        ]:
            row = tk.Frame(body, bg=BG_CARD); row.pack(fill="x", pady=1)
            tk.Label(row, text=label, bg=BG_CARD, fg=TEXT_DIM,
                     font=FONT_SMALL, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=value, bg=BG_CARD, fg=col,
                     font=("Segoe UI",10,"bold")).pack(side="left")

        note = tk.Frame(win, bg=BG_DARK, padx=18, pady=10)
        note.pack(fill="x")
        tk.Label(note,
            text="💡 Tip: Change the Invoice # field to a new number to keep both invoices.",
            bg=BG_DARK, fg=TEXT_DIM, font=("Segoe UI",8),
            wraplength=420, justify="left").pack(anchor="w")

        br = tk.Frame(win, bg=BG_DARK, padx=18, pady=12)
        br.pack(fill="x")

        def on_overwrite():
            result["proceed"] = True
            win.destroy()

        def on_cancel():
            result["proceed"] = False
            win.destroy()

        tk.Button(br, text="⚠️  Overwrite Existing",
            command=on_overwrite,
            bg="#b45309", fg="#ffffff",
            font=("Segoe UI",10,"bold"),
            relief="flat", bd=0, padx=14, pady=8,
            cursor="hand2").pack(side="right", padx=(8,0))
        GhostButton(br, text="Cancel — Keep Both",
            command=on_cancel).pack(side="right")

        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - win.winfo_reqwidth())  // 2
        y = self.winfo_y() + (self.winfo_height() - win.winfo_reqheight()) // 2
        win.geometry(f"+{x}+{y}")

        win.wait_window()
        return result["proceed"]

    def _save_draft(self):
        data = self._collect()
        is_edit = self._invoice_prefill is not None
        if not is_edit:
            data["status"] = "Draft"
        data["filepath"] = data.get("filepath", "")
        # Check for duplicate number before saving
        if not self._check_duplicate_number(data["number"]):
            return  # User cancelled — let them fix the number
        # Save to history — filter out any existing entry with same number first
        hist = [h for h in load_history() if h.get("number") != data["number"]]
        hist.insert(0, data)
        save_history(hist)
        saved_num = data["number"]
        saved_status = data["status"]
        self._invoice_prefill = None
        if not is_edit:
            # Bump counter NOW so the next New Invoice page gets a fresh number
            bump_counter(self.settings)
        # Navigate to invoices — do this last so no widgets are touched after destroy
        self._show_page("history")
        self.title(f"Invoice Generator — {saved_num} saved as {saved_status}")
        self.after(3000, lambda: self.title("Invoice Generator"))

    def _export(self):
        if not REPORTLAB_OK:
            messagebox.showerror("Missing","Run: pip install reportlab"); return
        data = self._collect()
        if not data["client_name"]:
            messagebox.showwarning("Required","Enter a client name."); return

        # ── Legal compliance check ────────────────────────────────────────
        is_valid, warnings, errors = self._check_invoice_legal_fields(data)
        if errors or warnings:
            # Show dialog — it will call _do_export() if user proceeds
            self._show_legal_check_dialog(warnings, errors,
                on_proceed=lambda: self._do_export(data))
            return
        self._do_export(data)

    def _do_export(self, data):
        """Actually write the PDF after compliance check passes."""
        # Check for duplicate number before exporting
        if not self._check_duplicate_number(data["number"]):
            return  # User cancelled
        save_dir = self.settings.get("save_directory","")
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        default = f"{data['number']}_{data['client_name'].replace(' ','_')}.pdf"
        fp = filedialog.asksaveasfilename(
            initialdir=save_dir, initialfile=default,
            defaultextension=".pdf",
            filetypes=[("PDF Files","*.pdf"),("All","*.*")])
        if not fp: return
        try:
            generate_pdf(fp, data, self.settings)
            data["filepath"] = fp
            hist = [h for h in load_history() if h.get("number") != data["number"]]
            hist.insert(0, data); save_history(hist)
            self._invoice_prefill = None
            bump_counter(self.settings)
            new_num, _ = next_inv_num(self.settings)
            self._inv_num.set(new_num)
            if self.settings.get("auto_open_pdf", True):
                if sys.platform == "win32": os.startfile(fp)
                elif sys.platform == "darwin": os.system(f'open "{fp}"')
                else: os.system(f'xdg-open "{fp}"')
            else:
                messagebox.showinfo("✅ Exported", f"Saved to:\n{fp}")
        except Exception as ex:
            messagebox.showerror("Export Failed", str(ex))

    def _email(self):
        if not self.settings.get("smtp_email") or not self.settings.get("smtp_password"):
            messagebox.showwarning("Not Configured",
                "Set SMTP email and password in Settings first."); return
        data = self._collect()
        if not data["client_email"]:
            messagebox.showwarning("Required","Client email required."); return
        tmp = DATA_DIR / f"tmp_{data['number']}.pdf"
        try:
            generate_pdf(str(tmp), data, self.settings)
        except Exception as ex:
            messagebox.showerror("PDF Error", str(ex)); return
        self._email_dialog(data, str(tmp))

    def _email_dialog(self, data, pdf_path):
        win = tk.Toplevel(self)
        win.title("Send Invoice"); win.minsize(480, 400)
        win.configure(bg=BG_DARK); win.grab_set()
        tk.Label(win, text="Send Invoice by Email", bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Segoe UI",14,"bold"), padx=20, pady=14).pack(anchor="w")
        frm = tk.Frame(win, bg=BG_DARK, padx=20); frm.pack(fill="x")
        fields = {}
        for lbl_txt, key, default in [
            ("To",      "to",      data.get("client_email","")),
            ("Subject", "subject", f"Invoice {data['number']} from {self.settings.get('company_name','')}"),
        ]:
            tk.Label(frm, text=lbl_txt, bg=BG_DARK, fg=TEXT_DIM,
                     font=FONT_SMALL).pack(anchor="w", pady=(8,1))
            e = FlatEntry(frm); e.insert(0, default); e.pack(fill="x", ipady=5)
            fields[key] = e

        tk.Label(frm, text="Message", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", pady=(8,1))
        mb = FlatText(frm, height=7)
        mb.insert("1.0",
            f"Dear {data.get('client_name','')},\n\n"
            f"Please find attached invoice {data['number']} for "
            f"{fc(data.get('total',0), self.settings.get('currency_symbol','£'))}.\n\n"
            f"Payment is due by {data.get('due_date','')}.\n\n"
            f"Kind regards,\n{self.settings.get('company_name','')}")
        mb.pack(fill="x")

        def send():
            try:
                msg = MIMEMultipart()
                msg["From"]    = self.settings["smtp_email"]
                msg["To"]      = fields["to"].get()
                msg["Subject"] = fields["subject"].get()
                msg.attach(MIMEText(mb.get("1.0","end").strip(),"plain"))
                with open(pdf_path,"rb") as f:
                    part = MIMEBase("application","octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition",
                        f"attachment; filename={os.path.basename(pdf_path)}")
                    msg.attach(part)
                with smtplib.SMTP(
                    self.settings.get("smtp_host","smtp.gmail.com"),
                    int(self.settings.get("smtp_port",587))
                ) as srv:
                    srv.starttls()
                    srv.login(self.settings["smtp_email"],self.settings["smtp_password"])
                    srv.sendmail(self.settings["smtp_email"],fields["to"].get(),msg.as_string())
                messagebox.showinfo("Sent!","Invoice emailed successfully.")
                win.destroy()
            except Exception as ex:
                messagebox.showerror("Send Failed", str(ex))

        br = tk.Frame(win, bg=BG_DARK, padx=20, pady=14); br.pack(fill="x")
        GreenButton(br, text="📧  Send", command=send).pack(side="right")
        GhostButton(br, text="Cancel", command=win.destroy).pack(side="right", padx=8)

    # ═══════════════ INVOICES ════════════════════════════════════════════

    def _calc_late_fee(self, inv):
        """
        Calculate the late fee for an overdue invoice.
        Returns (fee_amount, description) or (0, "") if not applicable.
        """
        s = self.settings
        if not s.get("late_fee_enabled", False):
            return 0, ""
        if str(s.get("late_fee_enabled","False")).lower() not in ("true","1","yes"):
            return 0, ""

        if inv.get("status") not in ("Unpaid","Overdue"):
            return 0, ""

        # Check how many days overdue
        fmt = s.get("date_format","DD/MM/YYYY")
        try:
            if fmt == "DD/MM/YYYY":
                due = datetime.strptime(inv["due_date"], "%d/%m/%Y")
            elif fmt == "MM/DD/YYYY":
                due = datetime.strptime(inv["due_date"], "%m/%d/%Y")
            else:
                due = datetime.strptime(inv["due_date"], "%Y-%m-%d")
        except Exception:
            return 0, ""

        days_over = (datetime.today() - due).days
        threshold = int(s.get("late_fee_days", 14))

        if days_over < threshold:
            return 0, ""

        # Already has a late fee item?
        desc = s.get("late_fee_description","Late payment fee")
        for item in inv.get("items",[]):
            if item.get("desc","").startswith(desc):
                return 0, ""  # Already applied

        total = float(inv.get("total", 0))
        try:
            fee_amt_setting = float(s.get("late_fee_amount","2.0"))
        except Exception:
            fee_amt_setting = 2.0

        if s.get("late_fee_type","Percentage") == "Percentage":
            fee = round(total * (fee_amt_setting / 100), 2)
            full_desc = f"{desc} ({fee_amt_setting}% — {days_over} days overdue)"
        else:
            fee = fee_amt_setting
            full_desc = f"{desc} ({days_over} days overdue)"

        return fee, full_desc

    def _apply_late_fee(self, inv_entry):
        """
        Apply a late fee to an existing invoice and re-save it.
        Shows confirmation dialog first.
        """
        fee, desc = self._calc_late_fee(inv_entry)
        if fee == 0:
            messagebox.showinfo("No Fee Applicable",
                "This invoice doesn't meet the late fee criteria.\n"
                "Check Settings → Automatic Late Fees.")
            return

        sym = inv_entry.get("currency_symbol") or self.settings.get("currency_symbol","£")
        if not messagebox.askyesno("Apply Late Fee",
            f"Add a late fee of {fc(fee, sym)} to invoice "
            f"{inv_entry.get('number','')}?\n\n"
            f"Description: {desc}\n\n"
            f"This will update the invoice total and mark it for re-export."):
            return

        # Add fee as a new line item
        new_item = {
            "desc":    desc,
            "qty":     1,
            "price":   fee,
            "taxable": False,
            "total":   fee,
        }
        hist = load_history()
        for h in hist:
            if h.get("number") == inv_entry.get("number"):
                h["items"] = h.get("items",[]) + [new_item]
                h["total"] = float(h.get("total",0)) + fee
                h["filepath"] = ""  # Invalidate old PDF — needs re-export
                break
        save_history(hist)
        messagebox.showinfo("✅ Late Fee Applied",
            f"Late fee of {fc(fee,sym)} added.\n"
            f"Re-export the invoice to generate an updated PDF.")
        self._show_page("history")

    def _pg_history(self):
        # Non-scrollable outer pad so filter bar stays visible
        outer = tk.Frame(self.content, bg=BG_DARK)
        outer.pack(fill="both", expand=True)
        top_pad = tk.Frame(outer, bg=BG_DARK, padx=22, pady=20)
        top_pad.pack(fill="x")

        tr = tk.Frame(top_pad, bg=BG_DARK)
        tr.pack(fill="x", pady=(0,12))
        tk.Label(tr, text="Invoices", bg=BG_DARK, fg=TEXT_WHITE,
                 font=FONT_HEAD).pack(side="left")
        GhostButton(tr, text="🔄 Reload",
                    command=lambda: self._show_page("history")).pack(side="left", padx=(12,0))

        history = load_history()
        sym = self.settings.get("currency_symbol","£")
        fmt = self.settings.get("date_format","DD/MM/YYYY")
        for h in history:
            if h.get("status") == "Unpaid" and is_overdue(h.get("due_date",""), fmt):
                h["status"] = "Overdue"
        save_history(history)

        # Search bar row
        sb_row = tk.Frame(top_pad, bg=BG_DARK)
        sb_row.pack(fill="x", pady=(0,8))
        tk.Label(sb_row, text="🔍", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_BODY).pack(side="left", padx=(0,6))
        self._inv_search_var = tk.StringVar()
        search_entry = tk.Entry(sb_row, textvariable=self._inv_search_var,
            bg=BG_HOVER, fg=TEXT_WHITE, insertbackground=ACCENT,
            relief="flat", bd=0, font=FONT_BODY,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT)
        search_entry.pack(side="left", fill="x", expand=True, ipady=6)
        tk.Label(sb_row, text="Search by invoice #, client, date or status",
                 bg=BG_DARK, fg=TEXT_DIM, font=FONT_SMALL).pack(side="left", padx=(8,0))

        # Filter + export row
        fb = tk.Frame(tr, bg=BG_DARK)
        fb.pack(side="right")
        self._filter_btns = {}
        self._active_status_filter = "All"
        for f in ["All","Unpaid","Paid","Overdue","Draft"]:
            btn = tk.Button(fb, text=f,
                command=lambda v=f: self._apply_filter(v, sym),
                bg=ACCENT if f=="All" else BG_CARD,
                fg="#000" if f=="All" else TEXT_MED,
                relief="flat", bd=0, font=FONT_SMALL,
                cursor="hand2", padx=10, pady=4)
            btn.pack(side="left", padx=2)
            self._filter_btns[f] = btn

        def export_csv():
            fp = filedialog.asksaveasfilename(defaultextension=".csv",
                filetypes=[("CSV","*.csv"),("All","*.*")])
            if not fp: return
            with open(fp,"w",newline="",encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Invoice #","Client","Date","Due Date","Total","Status"])
                for h in history:
                    w.writerow([h.get("number"),h.get("client_name",""),
                        h.get("date"),h.get("due_date"),h.get("total",0),h.get("status")])
            messagebox.showinfo("Exported",f"CSV saved to:\n{fp}")
        GhostButton(fb, text="📊 Export CSV", command=export_csv).pack(side="left", padx=(8,0))

        def _on_search(*_):
            self._apply_filter(self._active_status_filter, sym)
        self._inv_search_var.trace_add("write", _on_search)

        if not history:
            tk.Label(top_pad, text="No invoices yet.",
                     bg=BG_DARK, fg=TEXT_DIM, font=FONT_SUB, pady=40).pack()
            return

        # Scrollable table below
        table_frame = tk.Frame(outer, bg=BG_DARK, padx=22)
        table_frame.pack(fill="both", expand=True, pady=(8,20))

        card = Card(table_frame)
        card.pack(fill="both", expand=True)

        hdr = tk.Frame(card, bg=BG_HOVER, padx=14, pady=7)
        hdr.pack(fill="x")
        for txt in ["Invoice #","Client","Date","Due","Amount","Status","Actions"]:
            tk.Label(hdr, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                     font=("Segoe UI",9,"bold"), anchor="w",
                     width=12 if txt not in ("Client","Actions") else (20 if txt=="Client" else 0)
                     ).pack(side="left", padx=(0,6))

        scroll_area = tk.Frame(card, bg=BG_CARD)
        scroll_area.pack(fill="both", expand=True)
        canvas = tk.Canvas(scroll_area, bg=BG_CARD, highlightthickness=0)
        sb2 = ttk.Scrollbar(scroll_area, orient="vertical", command=canvas.yview)
        self._hist_rows = tk.Frame(canvas, bg=BG_CARD)
        self._hist_rows.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win_id = canvas.create_window((0,0), window=self._hist_rows, anchor="nw")
        canvas.configure(yscrollcommand=sb2.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        self._hist_data = history
        self._render_rows(history, sym)
        canvas.after(50, lambda: canvas.yview_moveto(0))

        # Keyboard navigation in invoice list
        self._hist_selected = [0]
        def _hist_key(e):
            rows = self._hist_rows.winfo_children()
            if not rows: return
            idx = self._hist_selected[0]
            if e.keysym == "Down":
                idx = min(idx+1, len(rows)-1)
            elif e.keysym == "Up":
                idx = max(idx-1, 0)
            elif e.keysym == "Return":
                # Open or edit the selected row
                if idx < len(self._hist_data):
                    h = self._hist_data[idx]
                    if h.get("status") == "Draft":
                        self._show_page("invoice", prefill=dict(h))
                    else:
                        fp = h.get("filepath","")
                        if fp and os.path.exists(fp):
                            if sys.platform=="win32": os.startfile(fp)
                return
            elif e.keysym == "Delete":
                if idx < len(self._hist_data):
                    h = self._hist_data[idx]
                    if messagebox.askyesno("Delete", f"Delete {h.get('number')}?"):
                        save_history([x for x in load_history()
                                      if x.get("number") != h.get("number")])
                        self._show_page("history")
                return
            self._hist_selected[0] = idx
            # Highlight selected row
            for i, row in enumerate(rows):
                bg = BG_HOVER if i == idx else (BG_CARD if i%2==0 else BG_HOVER)
                try:
                    row.config(bg=bg)
                    for child in row.winfo_children():
                        child.config(bg=bg)
                except Exception:
                    pass
            canvas.focus_set()

        canvas.bind("<KeyPress>", _hist_key)
        canvas.bind("<Button-1>", lambda e: canvas.focus_set())
        canvas.config(takefocus=True)

    def _apply_filter(self, status, sym=None):
        if sym is None: sym = self.settings.get("currency_symbol","£")
        self._active_status_filter = status
        for k, btn in self._filter_btns.items():
            btn.config(bg=ACCENT if k==status else BG_CARD,
                       fg="#000" if k==status else TEXT_MED)
        # Apply status filter
        filtered = self._hist_data if status=="All" else [
            h for h in self._hist_data if h.get("status")==status]
        # Apply search text on top
        search = getattr(self, "_inv_search_var", None)
        query = search.get().strip().lower() if search else ""
        if query:
            filtered = [h for h in filtered if
                query in (h.get("number","")).lower() or
                query in (h.get("client_name","")).lower() or
                query in (h.get("date","")).lower() or
                query in (h.get("due_date","")).lower() or
                query in (h.get("status","")).lower() or
                query in str(h.get("total","")).lower()]
        self._render_rows(filtered, sym)

    def _render_rows(self, history, sym):
        for w in self._hist_rows.winfo_children(): w.destroy()
        # Reset scrollregion so empty space doesn't linger
        self._hist_rows.update_idletasks()
        for i, h in enumerate(history):
            rb = BG_CARD if i%2==0 else BG_HOVER
            row = tk.Frame(self._hist_rows, bg=rb, padx=14, pady=6)
            row.pack(fill="x")
            client = (h.get("client_name") or h.get("client","—"))[:22]
            # Use per-invoice currency if set
            inv_sym = h.get("currency_symbol") or sym
            for txt, w in [(h.get("number","—"),12),(client,20),
                           (h.get("date","—"),12),(h.get("due_date","—"),12),
                           (fc(h.get("total",0),inv_sym),12)]:
                tk.Label(row, text=str(txt), bg=rb, fg=TEXT_WHITE,
                         font=FONT_BODY, width=w, anchor="w").pack(side="left")
            status_badge(row, h.get("status","Unpaid")).pack(side="left", padx=(0,8))
            # Show partial payment badge if applicable
            try: paid = float(h.get("amount_paid",0) or 0)
            except: paid = 0
            if paid > 0 and paid < h.get("total",0):
                balance = h.get("total",0) - paid
                tk.Label(row, text=f"Part-paid · {fc(balance,inv_sym)} due",
                         bg=GOLD, fg="#000", font=("Segoe UI",7,"bold"),
                         padx=5, pady=2).pack(side="left", padx=(0,4))
            # Template shown in tooltip/hover only — removed from row to reduce clutter
            bf = tk.Frame(row, bg=rb); bf.pack(side="right")
            fp = h.get("filepath","")
            if fp and os.path.exists(fp):
                def open_pdf(p=fp):
                    if sys.platform=="win32": os.startfile(p)
                    else: os.system(f'open "{p}"')
                GhostButton(bf, text="Open", command=open_pdf).pack(side="left", padx=2)
            if h.get("status") not in ("Paid","Draft"):
                def mark_paid(entry=h):
                    hist = load_history()
                    for x in hist:
                        if x.get("number") == entry.get("number"):
                            x["status"] = "Paid"
                            x["paid_date"] = fdate(self.settings["date_format"])
                    save_history(hist)
                    # Re-stamp PAID watermark on existing PDF
                    fp = entry.get("filepath","")
                    if fp and os.path.exists(fp) and REPORTLAB_OK:
                        try:
                            entry_copy = dict(entry)
                            entry_copy["status"] = "Paid"
                            ah = self.settings.get("theme_accent","#00e676")
                            from reportlab.lib import colors as _c
                            _stamp_paid_watermark(fp, A4, _c.HexColor(ah))
                        except Exception:
                            pass
                    self._show_page("history")
                GreenButton(bf, text="✓ Paid", command=mark_paid, small=True).pack(side="left", padx=2)
                # Show late fee button if overdue and late fees enabled
                fee, _ = self._calc_late_fee(h)
                if fee > 0:
                    inv_sym = h.get("currency_symbol") or sym
                    def apply_fee(entry=h):
                        self._apply_late_fee(entry)
                    GhostButton(bf, text=f"＋Fee {fc(fee,inv_sym)}",
                                command=apply_fee).pack(side="left", padx=2)
            # Edit button — only for Draft invoices
            if h.get("status") == "Draft":
                def edit_draft(entry=h):
                    self._show_page("invoice", prefill=dict(entry))
                GreenButton(bf, text="✏️ Edit", command=edit_draft,
                            small=True).pack(side="left", padx=2)

            def duplicate(entry=h):
                num, _ = next_inv_num(self.settings)
                pf = dict(entry); pf["number"] = num; pf["status"] = "Draft"
                pf["date"] = fdate(self.settings["date_format"])
                pf["due_date"] = duedate(self.settings["payment_terms"], self.settings["date_format"])
                self._show_page("invoice", prefill=pf)
            GhostButton(bf, text="⧉ Dup", command=duplicate).pack(side="left", padx=2)
            def delete(entry=h):
                if messagebox.askyesno("Delete", f"Delete {entry.get('number')}?"):
                    save_history([x for x in load_history()
                                  if x.get("number")!=entry.get("number")])
                    self._show_page("history")
            GhostButton(bf, text="✕", command=delete).pack(side="left", padx=2)

    # ═══════════════ CLIENTS ═════════════════════════════════════════════
    # ═══════════════ EXPENSES ════════════════════════════════════════════
    def _pg_expenses(self):
        outer = tk.Frame(self.content, bg=BG_DARK)
        outer.pack(fill="both", expand=True)

        top = tk.Frame(outer, bg=BG_DARK, padx=22, pady=20)
        top.pack(fill="x")
        self._h1(top, "Expenses", "Track your business spending")
        GreenButton(top, text="＋  Add Expense",
                    command=self._add_expense_dialog).pack(side="right")

        expenses = load_expenses()
        sym = self.settings.get("currency_symbol","£")

        # Search bar
        sb_row = tk.Frame(top, bg=BG_DARK)
        sb_row.pack(fill="x", pady=(8,0))
        tk.Label(sb_row, text="🔍", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_BODY).pack(side="left", padx=(0,6))
        exp_search = tk.StringVar()
        tk.Entry(sb_row, textvariable=exp_search,
            bg=BG_HOVER, fg=TEXT_WHITE, insertbackground=ACCENT,
            relief="flat", bd=0, font=FONT_BODY,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT
        ).pack(side="left", fill="x", expand=True, ipady=6)

        # Summary strip
        total_exp = sum(e.get("amount",0) for e in expenses)
        this_month = datetime.today().strftime("%Y-%m")
        month_exp  = sum(e.get("amount",0) for e in expenses
                         if e.get("date","").startswith(this_month[:7]) or
                            (len(e.get("date","")) >= 7 and
                             e.get("date","")[3:] == datetime.today().strftime("%m/%Y")))

        sf = tk.Frame(outer, bg=BG_DARK, padx=22)
        sf.pack(fill="x", pady=(0,8))
        sf.columnconfigure(0, weight=1); sf.columnconfigure(1, weight=1)
        sf.columnconfigure(2, weight=1)
        for i, (lbl, val, col) in enumerate([
            ("Total Expenses",    fc(total_exp, sym), RED_ERR),
            ("This Month",        fc(month_exp, sym), GOLD),
            ("Number of Entries", str(len(expenses)), BLUE),
        ]):
            c = Card(sf)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i==0 else 8, 0))
            cf = tk.Frame(c, bg=BG_CARD, padx=14, pady=10); cf.pack(fill="x")
            tk.Label(cf, text=lbl, bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
            tk.Label(cf, text=val, bg=BG_CARD, fg=col,
                     font=("Segoe UI",14,"bold")).pack(anchor="w")

        if not expenses:
            tk.Label(outer, text="No expenses logged yet.",
                     bg=BG_DARK, fg=TEXT_DIM, font=FONT_SUB, pady=30).pack()
            return

        card = Card(outer)
        card.pack(fill="both", expand=True, padx=22, pady=(8,20))

        hdr = tk.Frame(card, bg=BG_HOVER, padx=14, pady=7)
        hdr.pack(fill="x")
        for txt, w in [("Date",12),("Category",16),("Description",0),("Amount",12),("Actions","")]:
            tk.Label(hdr, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                     font=("Segoe UI",9,"bold"),
                     width=w if isinstance(w,int) and w>0 else 0,
                     anchor="w").pack(side="left", padx=(0,8))

        list_outer = tk.Frame(card, bg=BG_CARD)
        list_outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(list_outer, bg=BG_CARD, highlightthickness=0)
        esb = ttk.Scrollbar(list_outer, orient="vertical", command=canvas.yview)
        rows_frame = tk.Frame(canvas, bg=BG_CARD)
        rows_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win_id = canvas.create_window((0,0), window=rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=esb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        esb.pack(side="right", fill="y")

        def _escroll(e):
            canvas.yview_scroll(int(-1*(e.delta/120)),"units"); return "break"
        canvas.bind("<MouseWheel>", _escroll)
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _escroll))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        def _render_expenses(items):
            for w in rows_frame.winfo_children(): w.destroy()
            if not items:
                tk.Label(rows_frame, text="No expenses match your search.",
                         bg=BG_CARD, fg=TEXT_DIM, font=FONT_BODY, pady=16).pack()
                return
            for i, e in enumerate(sorted(items, key=lambda x: x.get("date",""), reverse=True)):
                rb = BG_CARD if i%2==0 else BG_HOVER
                row = tk.Frame(rows_frame, bg=rb, padx=14, pady=7)
                row.pack(fill="x")
                tk.Label(row, text=e.get("date","—"), bg=rb, fg=TEXT_MED,
                         font=FONT_SMALL, width=12, anchor="w").pack(side="left")
                cat_lbl = tk.Label(row, text=e.get("category","General"), bg=rb,
                    fg="#000", font=("Segoe UI",8,"bold"), padx=6, pady=2)
                cat_lbl.config(bg=self._cat_color(e.get("category","General")))
                cat_lbl.pack(side="left", padx=(0,8))
                tk.Label(row, text=e.get("description","—"), bg=rb, fg=TEXT_WHITE,
                         font=FONT_BODY, anchor="w").pack(side="left", fill="x", expand=True)
                tk.Label(row, text=fc(e.get("amount",0),sym), bg=rb, fg=RED_ERR,
                         font=("Segoe UI",10,"bold"), width=10, anchor="e").pack(side="left")
                bf = tk.Frame(row, bg=rb); bf.pack(side="right")
                def del_e(entry=e):
                    if messagebox.askyesno("Delete", f"Delete this expense?"):
                        exps = [x for x in load_expenses()
                                if not (x.get("date")==entry.get("date") and
                                        x.get("description")==entry.get("description") and
                                        x.get("amount")==entry.get("amount"))]
                        save_expenses(exps); self._show_page("expenses")
                GhostButton(bf, text="✕", command=del_e).pack(side="left")

        _render_expenses(expenses)

        def _on_exp_search(*_):
            q = exp_search.get().strip().lower()
            if not q: _render_expenses(expenses)
            else:
                _render_expenses([e for e in expenses if
                    q in e.get("description","").lower() or
                    q in e.get("category","").lower() or
                    q in e.get("date","").lower()])
        exp_search.trace_add("write", _on_exp_search)

    def _cat_color(self, cat):
        return {"Travel": BLUE, "Software": PURPLE, "Office": GOLD,
                "Marketing": "#ec4899", "Equipment": "#06b6d4",
                "Food": "#84cc16"}.get(cat, TEXT_DIM)

    def _add_expense_dialog(self):
        win = tk.Toplevel(self)
        win.title("Add Expense")
        win.configure(bg=BG_DARK); win.grab_set()
        win.resizable(True, True)
        tk.Label(win, text="Add Expense", bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Segoe UI",14,"bold"), padx=20, pady=14).pack(anchor="w")
        frm = tk.Frame(win, bg=BG_DARK, padx=20); frm.pack(fill="both", expand=True)
        fields = {}
        for lbl, key in [("Description","description"),("Amount (numbers only)","amount"),("Date (e.g. today)","date")]:
            tk.Label(frm, text=lbl, bg=BG_DARK, fg=TEXT_DIM,
                     font=FONT_SMALL).pack(anchor="w", pady=(8,1))
            e = FlatEntry(frm); e.pack(fill="x", ipady=5)
            if key == "date":
                e.insert(0, fdate(self.settings.get("date_format","DD/MM/YYYY")))
            fields[key] = e

        tk.Label(frm, text="Category", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", pady=(8,1))
        cat_var = tk.StringVar(value="General")
        ttk.Combobox(frm, textvariable=cat_var, state="readonly", font=FONT_BODY,
            values=["General","Travel","Software","Office","Marketing",
                    "Equipment","Food","Other"]
        ).pack(fill="x", ipady=4)

        tk.Label(frm, text="Notes (optional)", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", pady=(8,1))
        notes = FlatText(frm, height=2); notes.pack(fill="x")

        def save():
            desc = fields["description"].get_value()
            if not desc: messagebox.showwarning("Required","Description required."); return
            try: amt = float(fields["amount"].get_value().replace(",","").replace("£","").replace("$","").strip())
            except: messagebox.showwarning("Invalid","Enter a valid number for amount."); return
            exps = load_expenses()
            exps.append({
                "description": desc,
                "amount":      amt,
                "date":        fields["date"].get(),
                "category":    cat_var.get(),
                "notes":       notes.get("1.0","end").strip(),
            })
            save_expenses(exps); win.destroy()
            self._show_page("expenses")

        br = tk.Frame(win, bg=BG_DARK, padx=20, pady=14)
        br.pack(fill="x", side="bottom")
        GreenButton(br, text="💾  Save Expense", command=save).pack(side="right")
        GhostButton(br, text="Cancel", command=win.destroy).pack(side="right", padx=8)

        # Auto-size to content after all widgets are built
        win.update_idletasks()
        win.geometry(f"{win.winfo_reqwidth()}x{win.winfo_reqheight()}")
        # Centre on parent
        x = self.winfo_x() + (self.winfo_width()  - win.winfo_reqwidth())  // 2
        y = self.winfo_y() + (self.winfo_height() - win.winfo_reqheight()) // 2
        win.geometry(f"+{x}+{y}")

    # ═══════════════ REPORTS ═════════════════════════════════════════════

    # ═══════════════ COMPLIANCE & LEGAL TOOLS ════════════════════════════

    # ── UK VAT Invoice Required Fields (per HMRC Notice 700) ─────────────
    # A valid UK VAT invoice must contain:
    #   1. A unique sequential invoice number
    #   2. Your VAT registration number
    #   3. The invoice date
    #   4. The tax point (time of supply) if different from invoice date
    #   5. Your name and address
    #   6. Your customer's name and address
    #   7. Description of goods/services
    #   8. Quantity, unit price, and total (excl. VAT) per line
    #   9. Rate of any discount
    #  10. Rate and amount of VAT charged per line
    #  11. Total amount excluding VAT
    #  12. Total VAT
    #  13. Total amount including VAT

    def _check_invoice_legal_fields(self, data):
        """
        Check UK VAT invoice legal requirements before export.
        Returns (is_valid, warnings, errors) where:
          errors   = must-fix issues (block export if VAT registered)
          warnings = should-fix issues (allow export but alert user)
        """
        errors   = []
        warnings = []
        s = self.settings
        is_vat_registered = bool(s.get("vat_number","").strip())

        # ── Company fields ────────────────────────────────────────────────
        if not s.get("company_name","").strip():
            errors.append("Company name is missing (Settings → Your Business)")
        if not s.get("company_address","").strip():
            errors.append("Company address is missing — required by UK law")
        if is_vat_registered and not s.get("vat_number","").strip():
            errors.append("VAT number is missing — required on all VAT invoices")

        # ── Invoice fields ────────────────────────────────────────────────
        if not data.get("client_name","").strip():
            errors.append("Client name is missing")
        if not data.get("client_address","").strip():
            warnings.append("Client address is missing — required on VAT invoices")
        if not data.get("date","").strip():
            errors.append("Invoice date is missing")
        if not data.get("due_date","").strip():
            warnings.append("Due date is missing")

        # ── Line items ─────────────────────────────────────────────────────
        items = [i for i in data.get("items",[]) if i.get("desc","").strip()]
        if not items:
            errors.append("No line items — invoice has nothing to charge for")
        else:
            for i, item in enumerate(items, 1):
                if not item.get("desc","").strip():
                    warnings.append(f"Line item {i} has no description")
                if item.get("price",0) <= 0:
                    warnings.append(f"Line item {i} has zero or negative price")

        # ── VAT-specific checks ────────────────────────────────────────────
        if is_vat_registered:
            if not s.get("tax_label","").strip():
                warnings.append("Tax label is blank (should be 'VAT' for UK businesses)")
            try:
                rate = float(s.get("tax_rate", 0))
                if rate == 0:
                    warnings.append("Tax rate is 0% — correct for zero-rated but check if intentional")
            except Exception:
                errors.append("Tax rate is not a valid number")

        return (len(errors) == 0), warnings, errors

    def _show_legal_check_dialog(self, warnings, errors, on_proceed):
        """Show a compliance check dialog. Calls on_proceed() if user confirms."""
        win = tk.Toplevel(self)
        win.title("⚖️  Invoice Compliance Check")
        win.configure(bg=BG_DARK)
        win.grab_set()
        win.resizable(False, False)

        # Header
        has_errors = len(errors) > 0
        hdr_bg = "#1a0808" if has_errors else "#0d1a0d"
        hdr_col = RED_ERR if has_errors else GOLD
        hdr_icon = "⛔" if has_errors else "⚠️"
        hdr_text = "Issues found before export" if has_errors else "Warnings — review before export"

        hf = tk.Frame(win, bg=hdr_bg, padx=18, pady=14)
        hf.pack(fill="x")
        tk.Label(hf, text=f"{hdr_icon}  {hdr_text}", bg=hdr_bg, fg=hdr_col,
                 font=("Segoe UI",12,"bold")).pack(anchor="w")
        tk.Label(hf,
            text="UK VAT invoices must meet HMRC Notice 700 requirements.",
            bg=hdr_bg, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w", pady=(4,0))

        body = tk.Frame(win, bg=BG_DARK, padx=18, pady=12)
        body.pack(fill="x")

        if errors:
            tk.Label(body, text="❌  Must fix (required by UK law):",
                     bg=BG_DARK, fg=RED_ERR,
                     font=("Segoe UI",9,"bold")).pack(anchor="w", pady=(0,4))
            for e in errors:
                row = tk.Frame(body, bg=BG_DARK); row.pack(fill="x", pady=1)
                tk.Label(row, text="•", bg=BG_DARK, fg=RED_ERR,
                         font=FONT_BODY, width=2).pack(side="left")
                tk.Label(row, text=e, bg=BG_DARK, fg=TEXT_WHITE,
                         font=FONT_BODY, wraplength=460,
                         justify="left").pack(side="left", anchor="w")

        if warnings:
            if errors:
                tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=8)
            tk.Label(body, text="⚠️  Should fix (recommended):",
                     bg=BG_DARK, fg=GOLD,
                     font=("Segoe UI",9,"bold")).pack(anchor="w", pady=(0,4))
            for w in warnings:
                row = tk.Frame(body, bg=BG_DARK); row.pack(fill="x", pady=1)
                tk.Label(row, text="•", bg=BG_DARK, fg=GOLD,
                         font=FONT_BODY, width=2).pack(side="left")
                tk.Label(row, text=w, bg=BG_DARK, fg=TEXT_MED,
                         font=FONT_BODY, wraplength=460,
                         justify="left").pack(side="left", anchor="w")

        # HMRC link note
        note = tk.Frame(win, bg=BG_CARD, padx=18, pady=10)
        note.pack(fill="x")
        tk.Label(note,
            text="📋  UK law: VAT invoice requirements defined in HMRC Notice 700, Section 16.",
            bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI",8)).pack(anchor="w")

        # Buttons
        br = tk.Frame(win, bg=BG_DARK, padx=18, pady=12)
        br.pack(fill="x")

        if has_errors:
            tk.Label(br,
                text="Fix the errors above before exporting a VAT invoice.",
                bg=BG_DARK, fg=RED_ERR, font=FONT_SMALL).pack(side="left")
            GhostButton(br, text="Go to Settings",
                command=lambda: (win.destroy(), self._show_page("settings"))
                ).pack(side="right", padx=(8,0))
            GhostButton(br, text="Export Anyway",
                command=lambda: (win.destroy(), on_proceed())
                ).pack(side="right")
        else:
            tk.Label(br,
                text="Warnings found — you can still export.",
                bg=BG_DARK, fg=GOLD, font=FONT_SMALL).pack(side="left")
            GreenButton(br, text="✅  Export PDF",
                command=lambda: (win.destroy(), on_proceed())
                ).pack(side="right", padx=(8,0))
            GhostButton(br, text="Cancel",
                command=win.destroy).pack(side="right")

        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - win.winfo_reqwidth())  // 2
        y = self.winfo_y() + (self.winfo_height() - win.winfo_reqheight()) // 2
        win.geometry(f"+{x}+{y}")

    def _audit_invoice_sequence(self, history=None):
        """
        Check for gaps in invoice numbering sequence.
        Returns list of (expected_number, issue_description) tuples.
        """
        if history is None:
            history = load_history()

        prefix = self.settings.get("invoice_prefix", "INV")
        issues = []

        # Extract all numbers for this prefix
        nums = []
        for h in history:
            num_str = h.get("number","")
            if num_str.startswith(prefix + "-"):
                try:
                    n = int(num_str[len(prefix)+1:])
                    nums.append((n, h.get("date",""), h.get("status",""), num_str))
                except ValueError:
                    pass

        if len(nums) < 2:
            return []

        nums.sort(key=lambda x: x[0])

        # Check for gaps
        for i in range(len(nums) - 1):
            current = nums[i][0]
            next_n  = nums[i+1][0]
            if next_n - current > 1:
                for missing in range(current + 1, next_n):
                    issues.append({
                        "type":    "gap",
                        "missing": f"{prefix}-{missing:04d}",
                        "between": f"{nums[i][3]} and {nums[i+1][3]}",
                        "note":    "Missing from sequence — could indicate deleted invoice",
                    })

        # Check for duplicates
        seen = {}
        for n, date, status, full in nums:
            if n in seen:
                issues.append({
                    "type":      "duplicate",
                    "missing":   full,
                    "between":   f"appears more than once",
                    "note":      "Duplicate invoice numbers are not allowed",
                })
            seen[n] = full

        return issues

    def _pg_reports(self):
        pad = self._page_pad()
        self._h1(pad, "Reports", "Financial summaries for your business")

        history  = load_history()
        expenses = load_expenses()
        sym  = self.settings.get("currency_symbol","£")
        fmt  = self.settings.get("date_format","DD/MM/YYYY")
        now  = datetime.today()
        yr   = now.year

        # ── Year selector ────────────────────────────────────────────────
        years_in_data = set()
        for h in history:
            try:
                ds = h.get("date","")
                if fmt == "DD/MM/YYYY": d = datetime.strptime(ds, "%d/%m/%Y")
                elif fmt == "MM/DD/YYYY": d = datetime.strptime(ds, "%m/%d/%Y")
                else: d = datetime.strptime(ds, "%Y-%m-%d")
                years_in_data.add(d.year)
            except Exception: pass
        years_in_data.add(yr)
        years = sorted(years_in_data, reverse=True)

        yr_var = tk.StringVar(value=str(yr))
        yr_row = tk.Frame(pad, bg=BG_DARK)
        yr_row.pack(fill="x", pady=(0,14))
        tk.Label(yr_row, text="Year:", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_BODY).pack(side="left", padx=(0,8))
        ttk.Combobox(yr_row, textvariable=yr_var,
            values=[str(y) for y in years], state="readonly",
            width=8, font=FONT_BODY).pack(side="left")
        GhostButton(yr_row, text="🔄 Refresh",
                    command=lambda: self._show_page("reports")).pack(side="left", padx=8)

        try: selected_yr = int(yr_var.get())
        except: selected_yr = yr

        def parse_date(ds):
            try:
                if fmt == "DD/MM/YYYY": return datetime.strptime(ds, "%d/%m/%Y")
                if fmt == "MM/DD/YYYY": return datetime.strptime(ds, "%m/%d/%Y")
                return datetime.strptime(ds, "%Y-%m-%d")
            except Exception: return None

        paid = [h for h in history if h.get("status")=="Paid"
                and parse_date(h.get("date","")) is not None
                and parse_date(h.get("date","")).year == selected_yr]

        # ── Annual summary card ──────────────────────────────────────────
        total_rev  = sum(h.get("total",0) for h in paid)
        tax_rate   = float(self.settings.get("tax_rate",20))
        tax_label  = self.settings.get("tax_label","VAT")
        # VAT collected = sum of tax on taxable items
        vat_collected = 0
        for h in paid:
            for item in h.get("items",[]):
                if item.get("taxable",True):
                    vat_collected += item.get("total",0) * (tax_rate/100)

        yr_expenses = sum(e.get("amount",0) for e in expenses
            if parse_date(e.get("date","")) and
               parse_date(e.get("date","")).year == selected_yr)
        net = total_rev - yr_expenses

        sc = Card(pad); sc.pack(fill="x", pady=(0,12))
        tk.Label(sc, text=f"ANNUAL SUMMARY  —  {selected_yr}", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(sc).pack(fill="x", padx=14)
        sf = tk.Frame(sc, bg=BG_CARD, padx=14, pady=12); sf.pack(fill="x")
        sf.columnconfigure(0, weight=1); sf.columnconfigure(1, weight=1)
        sf.columnconfigure(2, weight=1); sf.columnconfigure(3, weight=1)
        for ci, (lbl, val, col) in enumerate([
            ("Total Revenue",    fc(total_rev,sym),   ACCENT),
            (f"{tax_label} Collected", fc(vat_collected,sym), PURPLE),
            ("Total Expenses",   fc(yr_expenses,sym), RED_ERR),
            ("Net Profit",       fc(net,sym),         "#22d3ee"),
        ]):
            c = tk.Frame(sf, bg=BG_CARD)
            c.grid(row=0, column=ci, sticky="ew", padx=(0 if ci==0 else 8,0))
            tk.Label(c, text=lbl, bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
            tk.Label(c, text=val, bg=BG_CARD, fg=col,
                     font=("Segoe UI",15,"bold")).pack(anchor="w")

        # ── VAT / Tax quarterly breakdown ────────────────────────────────
        qc = Card(pad); qc.pack(fill="x", pady=(0,12))
        tk.Label(qc, text=f"{tax_label} QUARTERLY BREAKDOWN  —  {selected_yr}",
                 bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(qc).pack(fill="x", padx=14)

        quarters = {"Q1 (Jan-Mar)":[], "Q2 (Apr-Jun)":[], "Q3 (Jul-Sep)":[], "Q4 (Oct-Dec)":[]}
        def quarter_key(month):
            if month <= 3:  return "Q1 (Jan-Mar)"
            if month <= 6:  return "Q2 (Apr-Jun)"
            if month <= 9:  return "Q3 (Jul-Sep)"
            return "Q4 (Oct-Dec)"

        for h in paid:
            d = parse_date(h.get("date",""))
            if not d: continue
            qk = quarter_key(d.month)
            qvat = sum(item.get("total",0)*(tax_rate/100)
                       for item in h.get("items",[]) if item.get("taxable",True))
            quarters[qk].append((h.get("total",0), qvat))

        qf = tk.Frame(qc, bg=BG_CARD, padx=14, pady=12); qf.pack(fill="x")
        qf.columnconfigure(0, weight=1); qf.columnconfigure(1, weight=1)
        qf.columnconfigure(2, weight=1); qf.columnconfigure(3, weight=1)
        for ci, (qname, entries) in enumerate(quarters.items()):
            qrev  = sum(r for r,v in entries)
            qvat  = sum(v for r,v in entries)
            qinvs = len(entries)
            c = Card(qf)
            c.grid(row=0, column=ci, sticky="nsew", padx=(0 if ci==0 else 6, 0))
            cf = tk.Frame(c, bg=BG_CARD, padx=12, pady=10); cf.pack(fill="x")
            tk.Label(cf, text=qname, bg=BG_CARD, fg=TEXT_WHITE,
                     font=("Segoe UI",9,"bold")).pack(anchor="w")
            tk.Label(cf, text=f"Revenue: {fc(qrev,sym)}", bg=BG_CARD,
                     fg=ACCENT, font=FONT_SMALL).pack(anchor="w", pady=(4,0))
            tk.Label(cf, text=f"{tax_label}: {fc(qvat,sym)}", bg=BG_CARD,
                     fg=PURPLE, font=FONT_SMALL).pack(anchor="w")
            tk.Label(cf, text=f"Invoices: {qinvs}", bg=BG_CARD,
                     fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")

        # ── Monthly breakdown table ──────────────────────────────────────
        mt = Card(pad); mt.pack(fill="x", pady=(0,12))
        tk.Label(mt, text=f"MONTHLY BREAKDOWN  —  {selected_yr}", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(mt).pack(fill="x", padx=14)

        month_names = ["Jan","Feb","Mar","Apr","May","Jun",
                       "Jul","Aug","Sep","Oct","Nov","Dec"]
        monthly = {m: {"rev":0,"vat":0,"exp":0,"count":0} for m in range(1,13)}

        for h in paid:
            d = parse_date(h.get("date",""))
            if not d: continue
            monthly[d.month]["rev"]   += h.get("total",0)
            monthly[d.month]["count"] += 1
            monthly[d.month]["vat"]   += sum(
                item.get("total",0)*(tax_rate/100)
                for item in h.get("items",[]) if item.get("taxable",True))

        for e in expenses:
            d = parse_date(e.get("date",""))
            if d and d.year == selected_yr:
                monthly[d.month]["exp"] += e.get("amount",0)

        hdr2 = tk.Frame(mt, bg=BG_HOVER, padx=14, pady=6); hdr2.pack(fill="x")
        for txt, w in [("Month",10),("Invoices",10),("Revenue",14),(f"{tax_label}",14),("Expenses",14),("Net",14)]:
            tk.Label(hdr2, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                     font=("Segoe UI",9,"bold"), width=w, anchor="w").pack(side="left")

        for mi in range(1, 13):
            m = monthly[mi]
            rb = BG_CARD if mi%2==0 else BG_HOVER
            row = tk.Frame(mt, bg=rb, padx=14, pady=6); row.pack(fill="x")
            net_m = m["rev"] - m["exp"]
            net_col = ACCENT if net_m >= 0 else RED_ERR
            for txt, w, col in [
                (month_names[mi-1], 10, TEXT_WHITE),
                (str(m["count"]),   10, TEXT_MED),
                (fc(m["rev"],sym),  14, ACCENT),
                (fc(m["vat"],sym),  14, PURPLE),
                (fc(m["exp"],sym),  14, RED_ERR),
                (fc(net_m,sym),     14, net_col),
            ]:
                tk.Label(row, text=txt, bg=rb, fg=col,
                         font=FONT_BODY, width=w, anchor="w").pack(side="left")

        # ── Totals row ───────────────────────────────────────────────────
        tot_frame = tk.Frame(mt, bg=BG_HOVER, padx=14, pady=7); tot_frame.pack(fill="x")
        for txt, w, col in [
            ("TOTAL", 10, TEXT_WHITE),
            (str(len(paid)), 10, TEXT_MED),
            (fc(total_rev,sym), 14, ACCENT),
            (fc(vat_collected,sym), 14, PURPLE),
            (fc(yr_expenses,sym), 14, RED_ERR),
            (fc(net,sym), 14, "#22d3ee"),
        ]:
            tk.Label(tot_frame, text=txt, bg=BG_HOVER, fg=col,
                     font=("Segoe UI",10,"bold"), width=w, anchor="w").pack(side="left")

        # ── Export report button ─────────────────────────────────────────
        def export_report():
            fp = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=f"report_{selected_yr}.csv",
                filetypes=[("CSV","*.csv"),("All","*.*")])
            if not fp: return
            with open(fp,"w",newline="",encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([f"Invoice Generator — Annual Report {selected_yr}"])
                w.writerow([])
                w.writerow(["Month","Invoices","Revenue",f"{tax_label}","Expenses","Net"])
                for mi in range(1,13):
                    m = monthly[mi]
                    w.writerow([month_names[mi-1], m["count"],
                                round(m["rev"],2), round(m["vat"],2),
                                round(m["exp"],2), round(m["rev"]-m["exp"],2)])
                w.writerow(["TOTAL", len(paid),
                            round(total_rev,2), round(vat_collected,2),
                            round(yr_expenses,2), round(net,2)])
            messagebox.showinfo("Exported", f"Report saved to:\n{fp}")

        br = tk.Frame(pad, bg=BG_DARK)
        br.pack(fill="x", pady=(4,20))
        GreenButton(br, text="📊  Export Report CSV",
                    command=export_report).pack(side="right", padx=(8,0))
        GreenButton(br, text="🇬🇧  HMRC VAT Return",
                    command=lambda: self._export_hmrc_vat(selected_yr, paid,
                        total_rev, vat_collected, yr_expenses, sym),
                    secondary=True).pack(side="right", padx=(0,0))

        # ── Sequential numbering audit ────────────────────────────────────
        audit_issues = self._audit_invoice_sequence(history)
        audit_card = Card(pad)
        audit_card.pack(fill="x", pady=(0,12))
        tk.Label(audit_card, text="🔢  INVOICE SEQUENCE AUDIT",
                 bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(audit_card).pack(fill="x", padx=14)
        af = tk.Frame(audit_card, bg=BG_CARD, padx=14, pady=10)
        af.pack(fill="x")

        prefix = self.settings.get("invoice_prefix","INV")
        if not audit_issues:
            tick = tk.Frame(af, bg=BG_CARD); tick.pack(fill="x")
            tk.Label(tick, text="✅", bg=BG_CARD, fg=ACCENT,
                     font=("Segoe UI",14)).pack(side="left", padx=(0,10))
            msg = tk.Frame(tick, bg=BG_CARD); msg.pack(side="left")
            tk.Label(msg, text="No sequence gaps detected",
                     bg=BG_CARD, fg=ACCENT,
                     font=("Segoe UI",11,"bold")).pack(anchor="w")
            tk.Label(msg,
                text=f"All {prefix}-XXXX invoice numbers are sequential and uninterrupted.",
                bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
        else:
            tk.Label(af,
                text=f"⚠️  {len(audit_issues)} issue(s) found in {prefix} sequence — "
                     f"review before a tax audit:",
                bg=BG_CARD, fg=GOLD,
                font=("Segoe UI",9,"bold")).pack(anchor="w", pady=(0,8))
            # Column headers
            hdr = tk.Frame(af, bg=BG_HOVER, padx=8, pady=5); hdr.pack(fill="x")
            for txt, w in [("Type",10),("Number",12),("Detail",0)]:
                tk.Label(hdr, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                         font=("Segoe UI",8,"bold"),
                         width=w if w else 0, anchor="w").pack(side="left", padx=(0,8))
            for i, issue in enumerate(audit_issues):
                rb = BG_CARD if i%2==0 else BG_HOVER
                row = tk.Frame(af, bg=rb, padx=8, pady=6); row.pack(fill="x")
                type_col = RED_ERR if issue["type"]=="duplicate" else GOLD
                tk.Label(row,
                    text="DUPLICATE" if issue["type"]=="duplicate" else "GAP",
                    bg=type_col, fg="#000",
                    font=("Segoe UI",7,"bold"), padx=6, pady=2
                ).pack(side="left", padx=(0,8))
                tk.Label(row, text=issue["missing"], bg=rb, fg=TEXT_WHITE,
                         font=FONT_MONO, width=12, anchor="w").pack(side="left")
                tk.Label(row,
                    text=f"{issue['between']} — {issue['note']}",
                    bg=rb, fg=TEXT_MED, font=FONT_SMALL, anchor="w"
                ).pack(side="left", fill="x", expand=True)

            # Export audit report button
            def export_audit():
                fp = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    initialfile=f"sequence_audit_{selected_yr}.csv",
                    filetypes=[("CSV","*.csv"),("All","*.*")])
                if not fp: return
                with open(fp,"w",newline="",encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["Invoice Generator — Sequence Audit Report"])
                    w.writerow([f"Generated: {datetime.today().strftime('%d/%m/%Y %H:%M')}"])
                    w.writerow([])
                    w.writerow(["Issue Type","Invoice Number","Detail","Note"])
                    for issue in audit_issues:
                        w.writerow([issue["type"].upper(), issue["missing"],
                                    issue["between"], issue["note"]])
                messagebox.showinfo("Exported", f"Audit report saved to:\n{fp}")
            GhostButton(af, text="📥  Export Audit Report CSV",
                        command=export_audit).pack(anchor="w", pady=(8,0))

        tk.Frame(pad, bg=BG_DARK, height=20).pack()

    def _export_hmrc_vat(self, year, paid_invoices, total_rev,
                          vat_collected, expenses, sym):
        """
        Export HMRC-format VAT Return data.
        Covers the 9 boxes of the UK VAT100 return form.
        Formatted for Making Tax Digital (MTD) record-keeping obligations.
        """
        s = self.settings
        tax_rate = float(s.get("tax_rate", 20))
        tax_label = s.get("tax_label", "VAT")

        # Calculate VAT figures
        # Box 1: VAT due on sales (output tax)
        box1 = vat_collected
        # Box 2: VAT due on acquisitions from EC (usually 0 for most small businesses)
        box2 = 0.0
        # Box 3: Total VAT due (Box 1 + Box 2)
        box3 = box1 + box2
        # Box 4: VAT reclaimed on purchases (input tax — from expenses if VAT registered)
        box4 = round(expenses * (tax_rate / (100 + tax_rate)), 2)
        # Box 5: Net VAT to pay/reclaim (Box 3 - Box 4)
        box5 = round(box3 - box4, 2)
        # Box 6: Total value of sales, excl. VAT
        box6 = round(total_rev - vat_collected, 2)
        # Box 7: Total value of purchases, excl. VAT
        box7 = round(expenses - box4, 2)
        # Box 8: Total value of EC supplies (0 for most UK-only businesses)
        box8 = 0.0
        # Box 9: Total value of EC acquisitions (0 for most UK-only businesses)
        box9 = 0.0

        # Show preview dialog
        win = tk.Toplevel(self)
        win.title(f"🇬🇧  HMRC VAT Return — {year}")
        win.configure(bg=BG_DARK)
        win.grab_set()
        win.minsize(520, 400)

        # Header
        hf = tk.Frame(win, bg="#0d1a0d", padx=18, pady=14)
        hf.pack(fill="x")
        tk.Label(hf, text="🇬🇧  HMRC VAT Return (VAT100)", bg="#0d1a0d",
                 fg=ACCENT, font=("Segoe UI",13,"bold")).pack(anchor="w")
        tk.Label(hf, text=f"Period: {year}  •  {s.get('company_name','')}  •  VAT: {s.get('vat_number','Not set')}",
                 bg="#0d1a0d", fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w", pady=(4,0))

        if not s.get("vat_number","").strip():
            tk.Label(hf,
                text="⚠️  VAT number not set — add it in Settings before filing",
                bg="#0d1a0d", fg=GOLD, font=FONT_SMALL).pack(anchor="w", pady=(4,0))

        body = tk.Frame(win, bg=BG_DARK, padx=18, pady=12)
        body.pack(fill="both", expand=True)

        boxes = [
            ("Box 1", "VAT due on sales and other outputs",              f"£{box1:,.2f}", ACCENT),
            ("Box 2", "VAT due on acquisitions from other EU states",    f"£{box2:,.2f}", TEXT_MED),
            ("Box 3", "Total VAT due (Box 1 + Box 2)",                   f"£{box3:,.2f}", ACCENT),
            ("Box 4", "VAT reclaimed on purchases and other inputs",     f"£{box4:,.2f}", TEXT_MED),
            ("Box 5", "Net VAT to pay HMRC or reclaim",                  f"£{box5:,.2f}",
             RED_ERR if box5 > 0 else "#22d3ee"),
            ("Box 6", "Total sales, excl. VAT",                          f"£{box6:,.2f}", TEXT_WHITE),
            ("Box 7", "Total purchases, excl. VAT",                      f"£{box7:,.2f}", TEXT_WHITE),
            ("Box 8", "Total value of supplies to other EU states",      f"£{box8:,.2f}", TEXT_MED),
            ("Box 9", "Total value of acquisitions from other EU states",f"£{box9:,.2f}", TEXT_MED),
        ]

        # Header row
        hdr = tk.Frame(body, bg=BG_HOVER, padx=8, pady=6); hdr.pack(fill="x")
        for txt, w in [("Box",6),("Description",0),("Amount",12)]:
            tk.Label(hdr, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                     font=("Segoe UI",8,"bold"),
                     width=w if w else 0, anchor="w").pack(side="left", padx=(0,8))

        for i, (box, desc, amt, col) in enumerate(boxes):
            rb = BG_CARD if i%2==0 else BG_HOVER
            row = tk.Frame(body, bg=rb, padx=8, pady=7); row.pack(fill="x")
            tk.Label(row, text=box, bg=rb, fg=ACCENT,
                     font=("Segoe UI",9,"bold"), width=6, anchor="w").pack(side="left")
            tk.Label(row, text=desc, bg=rb, fg=TEXT_MED,
                     font=FONT_BODY, anchor="w").pack(side="left", fill="x", expand=True)
            tk.Label(row, text=amt, bg=rb, fg=col,
                     font=("Segoe UI",10,"bold"), width=12, anchor="e").pack(side="right")

        # Important note
        note = tk.Frame(win, bg=BG_CARD, padx=18, pady=8)
        note.pack(fill="x")
        tk.Label(note,
            text="⚠️  This is a pre-calculation for your records. Always verify figures with your "
                 "accountant before submitting to HMRC via Making Tax Digital.",
            bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI",8),
            wraplength=480, justify="left").pack(anchor="w")

        # Export CSV button
        def export_vat():
            fp = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=f"VAT_Return_{year}_{s.get('company_name','').replace(' ','_')}.csv",
                filetypes=[("CSV","*.csv"),("All","*.*")])
            if not fp: return
            with open(fp,"w",newline="",encoding="utf-8") as csvf:
                w = csv.writer(csvf)
                w.writerow(["HMRC VAT Return — Invoice Generator"])
                w.writerow(["Company:", s.get("company_name","")])
                w.writerow(["VAT Number:", s.get("vat_number","")])
                w.writerow(["Period:", str(year)])
                w.writerow(["Generated:", datetime.today().strftime("%d/%m/%Y %H:%M")])
                w.writerow([])
                w.writerow(["Box","Description","Amount (£)"])
                for box, desc, amt, _ in boxes:
                    w.writerow([box, desc, amt.replace("£","").replace(",","")])
                w.writerow([])
                w.writerow(["DISCLAIMER: Verify with your accountant before filing to HMRC."])
            messagebox.showinfo("✅ Exported",
                f"VAT Return saved to:\n{fp}")

        br2 = tk.Frame(win, bg=BG_DARK, padx=18, pady=12)
        br2.pack(fill="x")
        GreenButton(br2, text="📥  Export VAT Return CSV",
                    command=export_vat).pack(side="right", padx=(8,0))
        GhostButton(br2, text="Close", command=win.destroy).pack(side="right")

        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - win.winfo_reqwidth())  // 2
        y = self.winfo_y() + (self.winfo_height() - win.winfo_reqheight()) // 2
        win.geometry(f"+{x}+{y}")

    def _avg_days_to_pay(self, client_name, history=None):
        """Return average days between invoice date and paid date for a client.
        Returns None if no paid data available."""
        if history is None:
            history = load_history()
        fmt = self.settings.get("date_format","DD/MM/YYYY")

        def _pd(ds):
            try:
                if fmt == "DD/MM/YYYY": return datetime.strptime(ds, "%d/%m/%Y")
                if fmt == "MM/DD/YYYY": return datetime.strptime(ds, "%m/%d/%Y")
                return datetime.strptime(ds, "%Y-%m-%d")
            except Exception:
                return None

        deltas = []
        for h in history:
            name = h.get("client_name") or h.get("client","")
            if name.lower() != client_name.lower(): continue
            if h.get("status") != "Paid": continue
            inv_d  = _pd(h.get("date",""))
            paid_d = _pd(h.get("paid_date",""))
            if inv_d and paid_d:
                delta = (paid_d - inv_d).days
                # Only count if paid_date was actually recorded separately
                # (delta > 0 means a real payment date was set, not just same-day mark)
                if delta >= 0:
                    deltas.append(delta)

        if not deltas:
            return None
        avg = round(sum(deltas) / len(deltas))
        # Return None if only same-day payments (avg=0) — not enough real data
        return avg if avg > 0 else None

    def _pg_clients(self):
        # Outer frame — no scroll, header stays pinned
        outer = tk.Frame(self.content, bg=BG_DARK)
        outer.pack(fill="both", expand=True)

        # Fixed top bar — title + Add Client button always visible
        top = tk.Frame(outer, bg=BG_DARK, padx=22, pady=20)
        top.pack(fill="x")
        self._h1(top, "Client Address Book")
        GreenButton(top, text="＋  Add Client",
                    command=self._add_client_dialog).pack(side="right")

        all_clients  = load_clients()
        history_all  = load_history()

        # Search bar
        sb_row = tk.Frame(top, bg=BG_DARK)
        sb_row.pack(fill="x", pady=(0,4))
        tk.Label(sb_row, text="🔍", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_BODY).pack(side="left", padx=(0,6))
        client_search_var = tk.StringVar()
        tk.Entry(sb_row, textvariable=client_search_var,
            bg=BG_HOVER, fg=TEXT_WHITE, insertbackground=ACCENT,
            relief="flat", bd=0, font=FONT_BODY,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT
        ).pack(side="left", fill="x", expand=True, ipady=6)
        tk.Label(sb_row, text="Search by name, email or phone",
                 bg=BG_DARK, fg=TEXT_DIM, font=FONT_SMALL).pack(side="left", padx=(8,0))

        if not all_clients:
            tk.Label(outer, text="No clients saved yet. Add your first client!",
                     bg=BG_DARK, fg=TEXT_DIM, font=FONT_SUB, pady=30).pack()
            return

        # Card with fixed column header
        card = Card(outer)
        card.pack(fill="both", expand=True, padx=22, pady=20)

        hdr = tk.Frame(card, bg=BG_HOVER, padx=14, pady=7)
        hdr.pack(fill="x")
        for txt, w in [("Name",20),("Email",22),("Phone",14),("Avg. Days to Pay",16),("Actions","")]:
            tk.Label(hdr, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                     font=("Segoe UI",9,"bold"),
                     width=w if isinstance(w,int) else 0,
                     anchor="w").pack(side="left", padx=(0,4))

        # Scrollable client list
        list_outer = tk.Frame(card, bg=BG_CARD)
        list_outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(list_outer, bg=BG_CARD, highlightthickness=0)
        csb = ttk.Scrollbar(list_outer, orient="vertical", command=canvas.yview)
        rows_frame = tk.Frame(canvas, bg=BG_CARD)
        rows_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win_id = canvas.create_window((0,0), window=rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=csb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        csb.pack(side="right", fill="y")

        def _cscroll(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
            return "break"

        def _bind_rows(w):
            w.bind("<MouseWheel>", _cscroll, add="+")
            for ch in w.winfo_children(): _bind_rows(ch)

        canvas.bind("<MouseWheel>", _cscroll)
        canvas.bind("<Enter>", lambda e: _bind_rows(rows_frame))
        canvas.bind("<Leave>", lambda e: rows_frame.unbind("<MouseWheel>"))

        def _render_clients(clients):
            for w in rows_frame.winfo_children(): w.destroy()
            if not clients:
                tk.Label(rows_frame, text="No clients match your search.",
                         bg=BG_CARD, fg=TEXT_DIM, font=FONT_BODY, pady=20).pack()
                return
            for i, c in enumerate(clients):
                rb = BG_CARD if i%2==0 else BG_HOVER
                row = tk.Frame(rows_frame, bg=rb, padx=14, pady=8)
                row.pack(fill="x")
                # Calculate avg days to pay for this client
                avg_days = self._avg_days_to_pay(c.get("name",""), history_all)
                avg_str  = f"{avg_days}d" if avg_days is not None else "—"
                avg_col  = (ACCENT  if avg_days <= 7  else
                            "#22d3ee" if avg_days <= 14 else
                            GOLD    if avg_days <= 30 else
                            RED_ERR) if avg_days is not None else TEXT_DIM
                for txt, w in [(c.get("name","—"),20),(c.get("email","—"),22),(c.get("phone","—"),14)]:
                    tk.Label(row, text=txt, bg=rb, fg=TEXT_WHITE,
                             font=FONT_BODY, width=w, anchor="w").pack(side="left")
                tk.Label(row, text=avg_str, bg=rb, fg=avg_col,
                         font=("Segoe UI",10,"bold"), width=16, anchor="w").pack(side="left")
                bf = tk.Frame(row, bg=rb); bf.pack(side="right")
                def inv_for(client=c):
                    num, _ = next_inv_num(self.settings)
                    self._show_page("invoice", prefill={
                        "number": num, "client_name": client.get("name",""),
                        "client_email": client.get("email",""),
                        "client_phone": client.get("phone",""),
                        "client_address": client.get("address",""), "status": "Draft"})
                GreenButton(bf, text="＋ Invoice", command=inv_for, small=True).pack(side="left", padx=2)
                GhostButton(bf, text="📋 History",
                            command=lambda cl=c: self._client_history_dialog(cl)).pack(side="left", padx=2)
                GhostButton(bf, text="Edit",
                            command=lambda cl=c: self._add_client_dialog(cl)).pack(side="left", padx=2)
                def del_c(client=c):
                    if messagebox.askyesno("Delete",f"Delete {client.get('name')}?"):
                        save_clients([x for x in load_clients() if x.get("name")!=client.get("name")])
                        self._show_page("clients")
                GhostButton(bf, text="✕", command=del_c).pack(side="left", padx=2)

        _render_clients(all_clients)

        def _on_client_search(*_):
            q = client_search_var.get().strip().lower()
            if not q:
                _render_clients(all_clients)
            else:
                filtered = [c for c in all_clients if
                    q in c.get("name","").lower() or
                    q in c.get("email","").lower() or
                    q in c.get("phone","").lower()]
                _render_clients(filtered)

        client_search_var.trace_add("write", _on_client_search)

    def _client_history_dialog(self, client):
        """Show full payment history and stats for a single client."""
        history = load_history()
        sym  = self.settings.get("currency_symbol","£")
        fmt  = self.settings.get("date_format","DD/MM/YYYY")
        name = client.get("name","")

        def _pd(ds):
            try:
                if fmt == "DD/MM/YYYY": return datetime.strptime(ds, "%d/%m/%Y")
                if fmt == "MM/DD/YYYY": return datetime.strptime(ds, "%m/%d/%Y")
                return datetime.strptime(ds, "%Y-%m-%d")
            except: return None

        client_invoices = [h for h in history
            if (h.get("client_name") or h.get("client","")).lower() == name.lower()]

        win = tk.Toplevel(self)
        win.title(f"Payment History — {name}")
        win.minsize(600, 480); win.configure(bg=BG_DARK); win.grab_set()

        # Header
        hf = tk.Frame(win, bg=BG_CARD, padx=20, pady=16,
                      highlightthickness=1, highlightbackground=BORDER)
        hf.pack(fill="x")
        tk.Label(hf, text=f"📋  {name}", bg=BG_CARD, fg=TEXT_WHITE,
                 font=("Segoe UI",14,"bold")).pack(anchor="w")
        tk.Label(hf, text=client.get("email",""), bg=BG_CARD,
                 fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")

        # Stats strip
        total_billed  = sum(h.get("total",0) for h in client_invoices)
        total_paid    = sum(h.get("total",0) for h in client_invoices if h.get("status")=="Paid")
        outstanding   = sum(h.get("total",0) for h in client_invoices
                            if h.get("status") in ("Unpaid","Overdue"))
        avg_days      = self._avg_days_to_pay(name, history)
        num_invoices  = len(client_invoices)
        num_paid      = sum(1 for h in client_invoices if h.get("status")=="Paid")
        num_overdue   = sum(1 for h in client_invoices if h.get("status")=="Overdue")

        sf = tk.Frame(win, bg=BG_DARK, padx=16, pady=10)
        sf.pack(fill="x")
        for i in range(4): sf.columnconfigure(i, weight=1)
        for ci, (lbl, val, col) in enumerate([
            ("Total Billed",      fc(total_billed, sym),  TEXT_WHITE),
            ("Total Paid",        fc(total_paid, sym),    ACCENT),
            ("Outstanding",       fc(outstanding, sym),   GOLD),
            ("Avg. Days to Pay",  f"{avg_days}d" if avg_days is not None else "N/A",
             ACCENT if avg_days and avg_days<=14 else GOLD if avg_days and avg_days<=30 else RED_ERR),
        ]):
            c = Card(sf)
            c.grid(row=0, column=ci, sticky="nsew", padx=(0 if ci==0 else 6,0))
            cf = tk.Frame(c, bg=BG_CARD, padx=10, pady=8); cf.pack(fill="x")
            tk.Label(cf, text=lbl, bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
            tk.Label(cf, text=val, bg=BG_CARD, fg=col,
                     font=("Segoe UI",13,"bold")).pack(anchor="w")

        # Reliability badge
        rel_frame = tk.Frame(win, bg=BG_DARK, padx=16); rel_frame.pack(fill="x", pady=(0,8))
        if avg_days is not None:
            if avg_days <= 7:   rel, rel_col = "⭐ Excellent payer — pays within a week", ACCENT
            elif avg_days <= 14: rel, rel_col = "✅ Good payer — pays within 2 weeks", "#22d3ee"
            elif avg_days <= 30: rel, rel_col = "⚠️ Average payer — takes up to a month", GOLD
            else:                rel, rel_col = "🔴 Slow payer — often takes over a month", RED_ERR
        else:
            rel, rel_col = "📊 No payment data yet", TEXT_DIM
        tk.Label(rel_frame, text=rel, bg=BG_DARK, fg=rel_col,
                 font=("Segoe UI",10,"bold")).pack(anchor="w")

        extra = f"  •  {num_invoices} invoices  •  {num_paid} paid  •  {num_overdue} overdue"
        tk.Label(rel_frame, text=extra, bg=BG_DARK, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")

        Divider(win).pack(fill="x", padx=16, pady=(4,0))

        # Invoice list
        hdr = tk.Frame(win, bg=BG_HOVER, padx=16, pady=6); hdr.pack(fill="x", padx=16)
        for txt, w in [("Invoice #",12),("Date",12),("Due",12),("Paid On",12),("Amount",12),("Status",10)]:
            tk.Label(hdr, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                     font=("Segoe UI",9,"bold"), width=w, anchor="w").pack(side="left")

        list_f = tk.Frame(win, bg=BG_CARD); list_f.pack(fill="both", expand=True, padx=16)
        cv = tk.Canvas(list_f, bg=BG_CARD, highlightthickness=0)
        sv = ttk.Scrollbar(list_f, orient="vertical", command=cv.yview)
        rf = tk.Frame(cv, bg=BG_CARD)
        rf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        wid = cv.create_window((0,0), window=rf, anchor="nw")
        cv.configure(yscrollcommand=sv.set)
        cv.bind("<Configure>", lambda e: cv.itemconfig(wid, width=e.width))
        cv.pack(side="left", fill="both", expand=True)
        sv.pack(side="right", fill="y")
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(int(-1*(e.delta/120)),"units"))

        for i, h in enumerate(sorted(client_invoices,
                               key=lambda x: x.get("date",""), reverse=True)):
            rb = BG_CARD if i%2==0 else BG_HOVER
            row = tk.Frame(rf, bg=rb, padx=16, pady=7); row.pack(fill="x")

            paid_on = h.get("paid_date","—")
            # Calculate days delta if available
            days_str = ""
            inv_d  = _pd(h.get("date",""))
            paid_d = _pd(paid_on)
            if inv_d and paid_d:
                delta = (paid_d - inv_d).days
                days_str = f" ({delta}d)"

            for txt, w in [
                (h.get("number","—"), 12),
                (h.get("date","—"),   12),
                (h.get("due_date","—"),12),
                (paid_on + days_str,  12),
                (fc(h.get("total",0),sym), 12),
            ]:
                tk.Label(row, text=txt, bg=rb, fg=TEXT_WHITE,
                         font=FONT_BODY, width=w, anchor="w").pack(side="left")
            status_badge(row, h.get("status","Unpaid")).pack(side="left")

        if not client_invoices:
            tk.Label(rf, text="No invoices for this client yet.",
                     bg=BG_CARD, fg=TEXT_DIM, font=FONT_BODY, pady=20).pack()

        # Bottom buttons
        br = tk.Frame(win, bg=BG_DARK, padx=16, pady=12); br.pack(fill="x")

        if outstanding > 0:
            def send_reminder():
                self._send_reminder_email(client, client_invoices, manual=True)
            GreenButton(br, text="📧 Send Payment Reminder",
                        command=send_reminder, secondary=True).pack(side="left")

        GhostButton(br, text="Close", command=win.destroy).pack(side="right")

    # ── Reminder email sender ─────────────────────────────────────────────
    def _send_reminder_email(self, client, invoices, manual=False):
        """Send a payment reminder email for outstanding invoices."""
        if not self.settings.get("smtp_email") or not self.settings.get("smtp_password"):
            messagebox.showwarning("Email Not Configured",
                "Set up SMTP email in Settings first."); return

        sym       = self.settings.get("currency_symbol","£")
        company   = self.settings.get("company_name","")
        overdue   = [h for h in invoices if h.get("status") in ("Unpaid","Overdue")]
        if not overdue:
            if manual: messagebox.showinfo("Nothing to Send","No outstanding invoices."); return
            return

        # Build invoice summary lines
        inv_lines = "\n".join(
            f"  • Invoice {h.get('number')} — {fc(h.get('total',0),sym)} (due {h.get('due_date','')})"
            for h in overdue)
        total_owed = sum(h.get("total",0) for h in overdue)

        subject_tmpl = self.settings.get("reminder_email_subject",
            "Payment Reminder — Invoice {number}")
        body_tmpl    = self.settings.get("reminder_email_body","")

        subject = subject_tmpl.replace("{number}", overdue[0].get("number",""))
        body = body_tmpl.replace("{client",  client.get("name",""))                         .replace("{client}", client.get("name",""))                         .replace("{number}", overdue[0].get("number",""))                         .replace("{amount}", fc(total_owed, sym))                         .replace("{due_date}", overdue[0].get("due_date",""))                         .replace("{company}", company)

        # Add invoice list if multiple
        if len(overdue) > 1:
            body += f"\n\nOutstanding invoices:\n{inv_lines}\n\nTotal owed: {fc(total_owed,sym)}"

        # Show preview dialog first
        win = tk.Toplevel(self)
        win.title("Send Payment Reminder")
        win.minsize(500, 420); win.configure(bg=BG_DARK); win.grab_set()
        tk.Label(win, text="📧  Payment Reminder Email", bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Segoe UI",13,"bold"), padx=20, pady=14).pack(anchor="w")
        frm = tk.Frame(win, bg=BG_DARK, padx=20); frm.pack(fill="x")
        fields = {}
        for lbl, key, val in [
            ("To",      "to",      client.get("email","")),
            ("Subject", "subject", subject),
        ]:
            tk.Label(frm, text=lbl, bg=BG_DARK, fg=TEXT_DIM,
                     font=FONT_SMALL).pack(anchor="w", pady=(8,1))
            e = FlatEntry(frm); e.insert(0, val); e.pack(fill="x", ipady=5)
            fields[key] = e

        tk.Label(frm, text="Message", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", pady=(8,1))
        mb = FlatText(frm, height=8)
        mb.insert("1.0", body); mb.pack(fill="x")

        def do_send():
            try:
                from email.mime.multipart import MIMEMultipart as MMP
                from email.mime.text import MIMEText as MMT
                msg = MMP()
                msg["From"]    = self.settings["smtp_email"]
                msg["To"]      = fields["to"].get()
                msg["Subject"] = fields["subject"].get()
                msg.attach(MMT(mb.get("1.0","end").strip(), "plain"))
                with smtplib.SMTP(
                    self.settings.get("smtp_host","smtp.gmail.com"),
                    int(self.settings.get("smtp_port",587))
                ) as srv:
                    srv.starttls()
                    srv.login(self.settings["smtp_email"], self.settings["smtp_password"])
                    srv.sendmail(self.settings["smtp_email"], fields["to"].get(), msg.as_string())

                # Log reminder sent date
                history = load_history()
                for h in history:
                    if h.get("number") in [i.get("number") for i in overdue]:
                        h["last_reminder"] = fdate(self.settings["date_format"])
                save_history(history)

                messagebox.showinfo("Sent!", f"Reminder sent to {fields['to'].get()}")
                win.destroy()
            except Exception as ex:
                messagebox.showerror("Failed", str(ex))

        br2 = tk.Frame(win, bg=BG_DARK, padx=20, pady=12); br2.pack(fill="x")
        GreenButton(br2, text="📧  Send Reminder", command=do_send).pack(side="right")
        GhostButton(br2, text="Cancel", command=win.destroy).pack(side="right", padx=8)

    # ═══════════════ REMINDERS PAGE ══════════════════════════════════════
    def _pg_reminders(self):
        pad = self._page_pad()
        self._h1(pad, "Overdue Reminders",
                 "Automatically chase unpaid invoices by email")

        history = load_history()
        sym = self.settings.get("currency_symbol","£")
        fmt = self.settings.get("date_format","DD/MM/YYYY")

        def _pd(ds):
            try:
                if fmt == "DD/MM/YYYY": return datetime.strptime(ds, "%d/%m/%Y")
                if fmt == "MM/DD/YYYY": return datetime.strptime(ds, "%m/%d/%Y")
                return datetime.strptime(ds, "%Y-%m-%d")
            except: return None

        today = datetime.today()

        # ── Reminder settings card ───────────────────────────────────────
        sc = Card(pad); sc.pack(fill="x", pady=(0,14))
        tk.Label(sc, text="REMINDER SCHEDULE", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(sc).pack(fill="x", padx=14)
        sf = tk.Frame(sc, bg=BG_CARD, padx=14, pady=12); sf.pack(fill="x")

        tk.Label(sf, text="Send automatic email reminders after invoice is overdue by:",
                 bg=BG_CARD, fg=TEXT_MED, font=FONT_BODY).pack(anchor="w", pady=(0,8))

        chk_frame = tk.Frame(sf, bg=BG_CARD); chk_frame.pack(anchor="w")
        r7  = tk.BooleanVar(value=self.settings.get("reminder_7day",  True))
        r14 = tk.BooleanVar(value=self.settings.get("reminder_14day", True))
        r30 = tk.BooleanVar(value=self.settings.get("reminder_30day", True))
        for var, label in [(r7,"7 days"),(r14,"14 days"),(r30,"30 days")]:
            tk.Checkbutton(chk_frame, text=label, variable=var,
                bg=BG_CARD, fg=TEXT_WHITE, selectcolor=BG_HOVER,
                activebackground=BG_CARD, font=FONT_BODY, cursor="hand2"
            ).pack(side="left", padx=(0,20))

        def save_reminder_prefs():
            self.settings["reminder_7day"]  = r7.get()
            self.settings["reminder_14day"] = r14.get()
            self.settings["reminder_30day"] = r30.get()
            save_settings(self.settings)
            messagebox.showinfo("Saved","Reminder preferences saved.")
        GhostButton(sf, text="💾 Save Preferences",
                    command=save_reminder_prefs).pack(anchor="w", pady=(8,0))

        # ── Email template card ──────────────────────────────────────────
        tc = Card(pad); tc.pack(fill="x", pady=(0,14))
        tk.Label(tc, text="EMAIL TEMPLATE", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(tc).pack(fill="x", padx=14)
        tf = tk.Frame(tc, bg=BG_CARD, padx=14, pady=10); tf.pack(fill="x")

        tk.Label(tf, text="Available placeholders:  {client}  {number}  {amount}  {due_date}  {company}",
                 bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI",8)).pack(anchor="w", pady=(0,8))

        tk.Label(tf, text="Subject", bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
        subj_var = tk.StringVar(value=self.settings.get("reminder_email_subject",""))
        tk.Entry(tf, textvariable=subj_var, bg=BG_HOVER, fg=TEXT_WHITE,
            insertbackground=ACCENT, relief="flat", bd=0, font=FONT_BODY,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT).pack(fill="x", ipady=5, pady=(2,8))

        tk.Label(tf, text="Body", bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
        body_txt = FlatText(tf, height=5)
        body_txt.insert("1.0", self.settings.get("reminder_email_body",""))
        body_txt.pack(fill="x")

        def save_template():
            self.settings["reminder_email_subject"] = subj_var.get()
            self.settings["reminder_email_body"]    = body_txt.get("1.0","end").strip()
            save_settings(self.settings)
            messagebox.showinfo("Saved","Email template saved.")
        GhostButton(tf, text="💾 Save Template",
                    command=save_template).pack(anchor="w", pady=(8,0))

        # ── Invoices needing reminders ───────────────────────────────────
        rc = Card(pad); rc.pack(fill="x", pady=(0,14))
        tk.Label(rc, text="INVOICES NEEDING REMINDERS", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(rc).pack(fill="x", padx=14)

        # Find overdue invoices and how many days overdue they are
        needs_reminder = []
        thresholds = []
        if self.settings.get("reminder_7day",  True): thresholds.append(7)
        if self.settings.get("reminder_14day", True): thresholds.append(14)
        if self.settings.get("reminder_30day", True): thresholds.append(30)

        for h in history:
            if h.get("status") not in ("Unpaid","Overdue"): continue
            due = _pd(h.get("due_date",""))
            if not due: continue
            days_over = (today - due).days
            if days_over < 0: continue  # not yet overdue

            # Check if a threshold has been hit and reminder not yet sent for it
            last_rem = _pd(h.get("last_reminder",""))
            for t in thresholds:
                if days_over >= t:
                    # Has reminder been sent since this threshold was hit?
                    threshold_hit = due + timedelta(days=t)
                    if last_rem is None or last_rem < threshold_hit:
                        needs_reminder.append((h, days_over, t))
                        break

        if needs_reminder:
            hdr = tk.Frame(rc, bg=BG_HOVER, padx=14, pady=6); hdr.pack(fill="x")
            for txt, w in [("Invoice #",12),("Client",20),("Due Date",12),
                           ("Days Over",10),("Amount",12),("Actions","")]:
                tk.Label(hdr, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                         font=("Segoe UI",9,"bold"), width=w if w else 0,
                         anchor="w").pack(side="left", padx=(0,4))

            sent_count = [0]
            def _send_all():
                for h, days_over, t in needs_reminder:
                    client_name = h.get("client_name","")
                    clients = load_clients()
                    client = next((c for c in clients
                                   if c.get("name","").lower()==client_name.lower()),
                                  {"name": client_name,
                                   "email": h.get("client_email","")})
                    if client.get("email"):
                        self._send_reminder_email(client, [h], manual=False)
                        sent_count[0] += 1
                messagebox.showinfo("Done",
                    f"Sent {sent_count[0]} reminder email(s).")
                self._pg_reminders()

            GreenButton(rc, text=f"📧  Send All {len(needs_reminder)} Reminders",
                        command=_send_all).pack(anchor="w", padx=14, pady=8)

            for h, days_over, threshold in needs_reminder:
                row = tk.Frame(rc, bg=BG_CARD, padx=14, pady=7); row.pack(fill="x")
                days_col = GOLD if days_over < 14 else RED_ERR
                client_name = h.get("client_name","")
                for txt, w in [
                    (h.get("number","—"),   12),
                    (client_name[:20],       20),
                    (h.get("due_date","—"),  12),
                    (f"{days_over}d",        10),
                    (fc(h.get("total",0),sym),12),
                ]:
                    lbl = tk.Label(row, text=txt, bg=BG_CARD,
                        fg=days_col if txt==f"{days_over}d" else TEXT_WHITE,
                        font=FONT_BODY if txt!=f"{days_over}d" else ("Segoe UI",10,"bold"),
                        width=w, anchor="w")
                    lbl.pack(side="left")

                clients_all = load_clients()
                client_obj = next(
                    (c for c in clients_all
                     if c.get("name","").lower()==client_name.lower()),
                    {"name":client_name,"email":h.get("client_email","")})

                def send_one(cl=client_obj, inv=h):
                    self._send_reminder_email(cl, [inv], manual=True)
                    self._pg_reminders()
                GhostButton(row, text="📧 Send",
                            command=send_one).pack(side="right", padx=4)
        else:
            tk.Label(rc, text="✅  No reminders needed right now — all overdue invoices are up to date.",
                     bg=BG_CARD, fg=ACCENT, font=FONT_BODY, padx=14, pady=18).pack(anchor="w")

        tk.Frame(pad, bg=BG_DARK, height=20).pack()



    def _refresh_profile_label(self):
        """Update the active profile label in the sidebar."""
        active = self.settings.get("active_profile","").strip()
        if active:
            self._profile_lbl.config(text=f"🏢 {active}")
        else:
            self._profile_lbl.config(text="🏢 Default Profile")

    def _load_profile(self, profile):
        """Apply a saved profile's settings over current settings."""
        PROFILE_KEYS = [
            "company_name","company_email","company_phone","company_address",
            "company_website","vat_number","bank_name","bank_sort_code",
            "bank_account","bank_reference","logo_path","show_logo",
            "logo_width_mm","logo_height_mm","currency","currency_symbol",
            "tax_rate","tax_label","invoice_prefix","invoice_start",
            "theme_accent","invoice_footer","tc_enabled","tc_text",
            "paypal_link","stripe_link","custom_pay_link","custom_pay_label",
            "invoice_template",
        ]
        for key in PROFILE_KEYS:
            if key in profile:
                self.settings[key] = profile[key]
        self.settings["active_profile"] = profile.get("name","")
        save_settings(self.settings)
        self._refresh_profile_label()

    # ═══════════════ COMPANY PROFILES ════════════════════════════════════
    def _pg_profiles(self):
        pad = self._page_pad()
        self._h1(pad, "Company Profiles",
                 "Switch between different businesses or trading names")

        profiles  = load_profiles()
        active_nm = self.settings.get("active_profile","").strip()

        # ── Active profile banner ─────────────────────────────────────────
        banner_bg = "#0d1a0d" if active_nm else BG_CARD
        banner = tk.Frame(pad, bg=banner_bg,
            highlightthickness=1,
            highlightbackground=ACCENT if active_nm else BORDER)
        banner.pack(fill="x", pady=(0,14))
        bf = tk.Frame(banner, bg=banner_bg, padx=14, pady=12)
        bf.pack(fill="x")
        if active_nm:
            tk.Label(bf, text=f"🏢  Active: {active_nm}",
                     bg=banner_bg, fg=ACCENT,
                     font=("Segoe UI",11,"bold")).pack(anchor="w")
            tk.Label(bf,
                text="Invoice PDFs and settings are using this profile.",
                bg=banner_bg, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
            def use_default():
                self.settings["active_profile"] = ""
                save_settings(self.settings)
                self._refresh_profile_label()
                self._show_page("profiles")
            GhostButton(bf, text="↩  Use Default Settings",
                        command=use_default).pack(anchor="w", pady=(8,0))
        else:
            tk.Label(bf, text="🏢  Using Default Settings",
                     bg=banner_bg, fg=TEXT_MED,
                     font=("Segoe UI",11,"bold")).pack(anchor="w")
            tk.Label(bf,
                text="Create a profile below to switch between company identities.",
                bg=banner_bg, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")

        # ── Create new profile ────────────────────────────────────────────
        nc = Card(pad); nc.pack(fill="x", pady=(0,14))
        tk.Label(nc, text="CREATE NEW PROFILE", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(nc).pack(fill="x", padx=14)
        nf = tk.Frame(nc, bg=BG_CARD, padx=14, pady=12); nf.pack(fill="x")
        nf.columnconfigure(0, weight=1); nf.columnconfigure(1, weight=1)

        # Profile name + company name on row 0
        tk.Label(nf, text="Profile Name (e.g. 'Freelance Design')",
                 bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=0, column=0, sticky="w", pady=(0,2))
        tk.Label(nf, text="Company / Trading Name",
                 bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=0, column=1, sticky="w", pady=(0,2), padx=(8,0))
        prof_name_e = FlatEntry(nf, placeholder="e.g. Freelance Design")
        prof_name_e.grid(row=1, column=0, sticky="ew", ipady=5, pady=(0,8))
        prof_co_e   = FlatEntry(nf, placeholder="e.g. Dean Wilson Design")
        prof_co_e.grid(row=1, column=1, sticky="ew", ipady=5, pady=(0,8), padx=(8,0))

        # Pre-fill from current settings option
        tk.Label(nf, text="This profile will start as a copy of your current settings.",
                 bg=BG_CARD, fg=TEXT_DIM,
                 font=("Segoe UI",8)).grid(row=2, column=0, columnspan=2, sticky="w")

        # VAT + invoice prefix on row 3
        tk.Label(nf, text="VAT Number",
                 bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=3, column=0, sticky="w", pady=(8,2))
        tk.Label(nf, text="Invoice Prefix",
                 bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=3, column=1, sticky="w", pady=(8,2), padx=(8,0))
        prof_vat_e = FlatEntry(nf, placeholder="e.g. GB123456789")
        prof_vat_e.grid(row=4, column=0, sticky="ew", ipady=5)
        prof_pfx_e = FlatEntry(nf, placeholder="e.g. INV or DWD")
        prof_pfx_e.grid(row=4, column=1, sticky="ew", ipady=5, padx=(8,0))

        # Accent colour
        tk.Label(nf, text="PDF Accent Colour (hex)",
                 bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=5, column=0, sticky="w", pady=(8,2))
        prof_colour_e = FlatEntry(nf, placeholder="#00e676")
        prof_colour_e.insert(0, self.settings.get("theme_accent","#00e676"))
        prof_colour_e.grid(row=5, column=1, sticky="ew", ipady=5, pady=(8,0), padx=(8,0))

        def save_new_profile():
            name = prof_name_e.get_value().strip()
            if not name:
                messagebox.showwarning("Required","Enter a profile name."); return
            # Check duplicate
            existing = load_profiles()
            if any(p["name"] == name for p in existing):
                messagebox.showwarning("Duplicate",
                    f"A profile named '{name}' already exists."); return

            # Copy current settings, then override with form values
            PROFILE_KEYS = [
                "company_name","company_email","company_phone","company_address",
                "company_website","vat_number","bank_name","bank_sort_code",
                "bank_account","bank_reference","logo_path","show_logo",
                "logo_width_mm","logo_height_mm","currency","currency_symbol",
                "tax_rate","tax_label","invoice_prefix","invoice_start",
                "theme_accent","invoice_footer","tc_enabled","tc_text",
                "paypal_link","stripe_link","custom_pay_link","custom_pay_label",
                "invoice_template",
            ]
            profile = {k: self.settings.get(k,"") for k in PROFILE_KEYS}
            profile["name"] = name
            if prof_co_e.get_value().strip():
                profile["company_name"] = prof_co_e.get_value().strip()
            if prof_vat_e.get_value().strip():
                profile["vat_number"] = prof_vat_e.get_value().strip()
            if prof_pfx_e.get_value().strip():
                profile["invoice_prefix"] = prof_pfx_e.get_value().strip()
            if prof_colour_e.get_value().strip():
                profile["theme_accent"] = prof_colour_e.get_value().strip()

            existing.append(profile)
            save_profiles(existing)
            messagebox.showinfo("✅ Profile Created",
                f"Profile '{name}' created.\nClick 'Switch To' to activate it.")
            self._show_page("profiles")

        GreenButton(nf, text="＋  Save New Profile",
                    command=save_new_profile).grid(
                    row=6, column=0, columnspan=2,
                    sticky="w", pady=(12,0))

        # ── Saved profiles list ───────────────────────────────────────────
        lc = Card(pad); lc.pack(fill="x", pady=(0,14))
        tk.Label(lc, text="SAVED PROFILES", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(lc).pack(fill="x", padx=14)

        if not profiles:
            tk.Label(lc,
                text="No profiles saved yet.\nCreate one above to get started.",
                bg=BG_CARD, fg=TEXT_DIM, font=FONT_BODY,
                padx=14, pady=16, justify="left").pack(anchor="w")
        else:
            for i, prof in enumerate(profiles):
                rb   = BG_CARD if i%2==0 else BG_HOVER
                is_active = prof.get("name","") == active_nm
                row  = tk.Frame(lc, bg=rb, padx=14, pady=10)
                row.pack(fill="x")

                # Left: profile info
                info = tk.Frame(row, bg=rb); info.pack(side="left", fill="x", expand=True)
                name_row = tk.Frame(info, bg=rb); name_row.pack(anchor="w")
                tk.Label(name_row, text=prof.get("name",""), bg=rb, fg=TEXT_WHITE,
                         font=("Segoe UI",11,"bold")).pack(side="left")
                if is_active:
                    tk.Label(name_row, text=" ✓ ACTIVE", bg=rb, fg=ACCENT,
                             font=("Segoe UI",8,"bold")).pack(side="left", padx=(6,0))

                # Detail line
                details = []
                if prof.get("company_name"): details.append(prof["company_name"])
                if prof.get("vat_number"):   details.append(f"VAT: {prof['vat_number']}")
                if prof.get("invoice_prefix"): details.append(f"Prefix: {prof['invoice_prefix']}")
                if prof.get("theme_accent"):
                    col = prof["theme_accent"]
                    details.append(f"Colour: {col}")
                tk.Label(info, text="  •  ".join(details) if details else "No details",
                         bg=rb, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w", pady=(2,0))

                # Accent colour swatch
                try:
                    swatch_col = prof.get("theme_accent","#00e676")
                    tk.Frame(row, bg=swatch_col, width=14, height=14,
                             highlightthickness=1,
                             highlightbackground="#000").pack(side="right", padx=(0,8))
                except Exception:
                    pass

                # Buttons
                bf2 = tk.Frame(row, bg=rb); bf2.pack(side="right")

                if not is_active:
                    def switch_to(p=prof):
                        if messagebox.askyesno("Switch Profile",
                            f"Switch to profile '{p['name']}'?\n\n"
                            f"This will update your company settings.\n"
                            f"You can switch back at any time."):
                            self._load_profile(p)
                            messagebox.showinfo("✅ Profile Active",
                                f"Now using: {p['name']}")
                            self._show_page("profiles")
                    GreenButton(bf2, text="Switch To",
                                command=switch_to, small=True).pack(side="left", padx=2)

                def edit_p(p=prof):
                    self._edit_profile_dialog(p)
                GhostButton(bf2, text="Edit",
                            command=edit_p).pack(side="left", padx=2)

                def del_p(p=prof):
                    if messagebox.askyesno("Delete",
                        f"Delete profile '{p['name']}'?"):
                        pl = [x for x in load_profiles()
                              if x.get("name") != p.get("name")]
                        save_profiles(pl)
                        if active_nm == p.get("name"):
                            self.settings["active_profile"] = ""
                            save_settings(self.settings)
                            self._refresh_profile_label()
                        self._show_page("profiles")
                GhostButton(bf2, text="✕", command=del_p).pack(side="left", padx=2)

        # ── Export/import profiles ────────────────────────────────────────
        ep = tk.Frame(pad, bg=BG_DARK)
        ep.pack(fill="x", pady=(0,20))
        GhostButton(ep, text="📥  Export All Profiles",
                    command=self._export_profiles).pack(side="left")
        GhostButton(ep, text="📤  Import Profiles",
                    command=self._import_profiles).pack(side="left", padx=8)

        tk.Frame(pad, bg=BG_DARK, height=20).pack()

    def _edit_profile_dialog(self, profile):
        """Edit an existing saved profile."""
        win = tk.Toplevel(self)
        win.title(f"Edit Profile — {profile.get('name','')}")
        win.configure(bg=BG_DARK); win.grab_set()
        win.minsize(480, 400)

        tk.Label(win, text=f"✏️  Edit: {profile.get('name','')}",
                 bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Segoe UI",13,"bold"), padx=20, pady=14).pack(anchor="w")

        frm = tk.Frame(win, bg=BG_DARK, padx=20); frm.pack(fill="both", expand=True)

        editable_fields = [
            ("Company Name",    "company_name"),
            ("Email",           "company_email"),
            ("Phone",           "company_phone"),
            ("Website",         "company_website"),
            ("VAT Number",      "vat_number"),
            ("Invoice Prefix",  "invoice_prefix"),
            ("PDF Accent Colour","theme_accent"),
            ("Bank Name",       "bank_name"),
            ("Sort Code",       "bank_sort_code"),
            ("Account Number",  "bank_account"),
        ]
        entries = {}
        for lbl, key in editable_fields:
            tk.Label(frm, text=lbl, bg=BG_DARK, fg=TEXT_DIM,
                     font=FONT_SMALL).pack(anchor="w", pady=(6,1))
            e = FlatEntry(frm); e.pack(fill="x", ipady=4)
            e.insert(0, str(profile.get(key,"")))
            entries[key] = e

        tk.Label(frm, text="Address", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", pady=(6,1))
        addr_t = FlatText(frm, height=3); addr_t.pack(fill="x")
        addr_t.insert("1.0", profile.get("company_address",""))

        def save_edit():
            pl = load_profiles()
            for p in pl:
                if p.get("name") == profile.get("name"):
                    for key, entry in entries.items():
                        p[key] = entry.get_value() or entry.get()
                    p["company_address"] = addr_t.get("1.0","end").strip()
            save_profiles(pl)
            # If this is the active profile, reload settings
            if self.settings.get("active_profile") == profile.get("name"):
                updated = next((p for p in pl
                                if p.get("name")==profile.get("name")), None)
                if updated:
                    self._load_profile(updated)
            messagebox.showinfo("Saved","Profile updated.")
            win.destroy()
            self._show_page("profiles")

        br = tk.Frame(win, bg=BG_DARK, padx=20, pady=12)
        br.pack(fill="x", side="bottom")
        GreenButton(br, text="💾  Save Changes", command=save_edit).pack(side="right")
        GhostButton(br, text="Cancel", command=win.destroy).pack(side="right", padx=8)

        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - win.winfo_reqwidth())  // 2
        y = self.winfo_y() + (self.winfo_height() - win.winfo_reqheight()) // 2
        win.geometry(f"+{x}+{y}")

    def _export_profiles(self):
        if not load_profiles():
            messagebox.showinfo("None","No profiles to export."); return
        fp = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile="invoice_profiles.json",
            filetypes=[("JSON","*.json"),("All","*.*")])
        if not fp: return
        import json as _j
        with open(fp,"w",encoding="utf-8") as f:
            _j.dump(load_profiles(), f, indent=2, ensure_ascii=False)
        messagebox.showinfo("✅ Exported",f"Profiles saved to:\n{fp}")

    def _import_profiles(self):
        fp = filedialog.askopenfilename(
            filetypes=[("JSON","*.json"),("All","*.*")])
        if not fp: return
        try:
            import json as _j
            with open(fp,"r",encoding="utf-8") as f:
                imported = _j.load(f)
            if not isinstance(imported, list):
                raise ValueError("File must contain a list of profiles")
            existing = load_profiles()
            added = 0
            for p in imported:
                if isinstance(p,dict) and p.get("name"):
                    if not any(x.get("name")==p["name"] for x in existing):
                        existing.append(p); added += 1
            save_profiles(existing)
            messagebox.showinfo("✅ Imported",
                f"Imported {added} new profile(s).\n"
                f"(Duplicates were skipped)")
            self._show_page("profiles")
        except Exception as ex:
            messagebox.showerror("Import Failed",str(ex))

    # ═══════════════ RECURRING INVOICES ══════════════════════════════════
    def _pg_recurring(self):
        pad = self._page_pad()
        self._h1(pad, "Recurring Invoices",
                 "Auto-generate draft invoices on a schedule")

        recurring = load_recurring()
        sym = self.settings.get("currency_symbol","£")

        # ── Add recurring schedule ────────────────────────────────────────
        add_card = Card(pad)
        add_card.pack(fill="x", pady=(0,14))
        tk.Label(add_card, text="NEW RECURRING SCHEDULE", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(add_card).pack(fill="x", padx=14)
        af = tk.Frame(add_card, bg=BG_CARD, padx=14, pady=12)
        af.pack(fill="x")
        af.columnconfigure(0, weight=1)
        af.columnconfigure(1, weight=1)
        af.columnconfigure(2, weight=1)

        # Client picker
        clients = load_clients()
        client_names = ["— Select client —"] + [c["name"] for c in clients]
        client_var = tk.StringVar(value="— Select client —")
        tk.Label(af, text="Client", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=0, column=0, sticky="w", pady=(0,2))
        ttk.Combobox(af, textvariable=client_var, values=client_names,
            state="readonly", font=FONT_BODY).grid(
            row=1, column=0, sticky="ew", padx=(0,8), ipady=4)

        # Interval
        interval_var = tk.StringVar(value="Monthly")
        tk.Label(af, text="Interval", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=0, column=1, sticky="w", pady=(0,2))
        ttk.Combobox(af, textvariable=interval_var,
            values=["Weekly","Monthly","Quarterly","Annually"],
            state="readonly", font=FONT_BODY).grid(
            row=1, column=1, sticky="ew", padx=(0,8), ipady=4)

        # Amount
        tk.Label(af, text="Invoice Amount", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=0, column=2, sticky="w", pady=(0,2))
        amount_e = FlatEntry(af, placeholder="e.g. 500")
        amount_e.grid(row=1, column=2, sticky="ew", ipady=5)

        # Description + start date
        tk.Label(af, text="Description (line item)", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=2, column=0, sticky="w", pady=(8,2))
        desc_e = FlatEntry(af, placeholder="e.g. Monthly retainer")
        desc_e.grid(row=3, column=0, sticky="ew", padx=(0,8), ipady=5)

        tk.Label(af, text="Next Due Date", bg=BG_CARD, fg=TEXT_DIM,
                 font=FONT_SMALL).grid(row=2, column=1, sticky="w", pady=(8,2))
        next_e = FlatEntry(af)
        next_e.insert(0, fdate(self.settings["date_format"]))
        next_e.grid(row=3, column=1, sticky="ew", padx=(0,8), ipady=5)

        def add_schedule():
            client = client_var.get()
            if client == "— Select client —":
                messagebox.showwarning("Required","Please select a client."); return
            desc = desc_e.get_value()
            if not desc:
                messagebox.showwarning("Required","Please enter a description."); return
            try:
                amt = float(amount_e.get_value().replace(",","").replace(sym,""))
            except Exception:
                messagebox.showwarning("Invalid","Enter a valid amount."); return

            r = load_recurring()
            r.append({
                "client":   client,
                "interval": interval_var.get(),
                "amount":   amt,
                "desc":     desc,
                "next_due": next_e.get(),
                "active":   True,
                "created":  fdate(self.settings["date_format"]),
            })
            save_recurring(r)
            messagebox.showinfo("Added",
                f"Recurring schedule added for {client} ({interval_var.get()})")
            self._show_page("recurring")

        GreenButton(af, text="＋  Add Schedule",
                    command=add_schedule).grid(row=3, column=2, sticky="ew",
                    padx=(0,0), ipady=3, pady=(0,0))

        # ── Generate due drafts ───────────────────────────────────────────
        today_str = fdate(self.settings["date_format"])
        fmt = self.settings["date_format"]

        def parse_d(ds):
            try:
                if fmt == "DD/MM/YYYY": return datetime.strptime(ds, "%d/%m/%Y")
                if fmt == "MM/DD/YYYY": return datetime.strptime(ds, "%m/%d/%Y")
                return datetime.strptime(ds, "%Y-%m-%d")
            except: return None

        def next_interval(ds, interval):
            d = parse_d(ds)
            if not d: return ds
            if interval == "Weekly":    d += timedelta(weeks=1)
            elif interval == "Monthly": 
                m = d.month + 1
                y = d.year + (m-1)//12
                m = ((m-1) % 12) + 1
                import calendar
                day = min(d.day, calendar.monthrange(y,m)[1])
                d = d.replace(year=y, month=m, day=day)
            elif interval == "Quarterly":
                m = d.month + 3
                y = d.year + (m-1)//12
                m = ((m-1) % 12) + 1
                d = d.replace(year=y, month=m)
            elif interval == "Annually":
                d = d.replace(year=d.year+1)
            return fdate(fmt, d)

        due_now = [r for r in recurring
                   if r.get("active",True)
                   and parse_d(r.get("next_due","")) is not None
                   and parse_d(r.get("next_due","")) <= datetime.today()]

        if due_now:
            dc = Card(pad); dc.pack(fill="x", pady=(0,12))
            tk.Label(dc, text=f"⚡  {len(due_now)} SCHEDULE(S) DUE — READY TO GENERATE",
                     bg=BG_CARD, fg=GOLD, font=("Segoe UI",9,"bold"),
                     padx=14, pady=8).pack(anchor="w")
            Divider(dc).pack(fill="x", padx=14)

            def generate_all_due():
                r_list = load_recurring()
                created = 0
                for r in due_now:
                    num, _ = next_inv_num(self.settings)
                    bump_counter(self.settings)
                    terms = int(self.settings.get("payment_terms",30))
                    due_dt = fdate(fmt, datetime.today() + timedelta(days=terms))
                    # Find client details
                    cl = next((c for c in load_clients()
                                if c["name"]==r["client"]), {})
                    inv = {
                        "number":       num,
                        "date":         fdate(fmt),
                        "due_date":     due_dt,
                        "status":       "Draft",
                        "client_name":  r["client"],
                        "client_email": cl.get("email",""),
                        "client_phone": cl.get("phone",""),
                        "client_address": cl.get("address",""),
                        "po": "", "discount": "0",
                        "notes": self.settings.get("default_notes","").replace(
                            "{terms}", str(terms)),
                        "items": [{"desc": r["desc"], "qty": 1,
                                   "price": r["amount"], "taxable": True,
                                   "total": r["amount"]}],
                        "total":    r["amount"] * 1.2,
                        "filepath": "",
                        "paid_date":"",
                        "last_reminder":"",
                        "currency_symbol": self.settings.get("currency_symbol","£"),
                        "invoice_template": self.settings.get("invoice_template","Professional"),
                        "amount_paid": "0",
                    }
                    hist = load_history()
                    hist.insert(0, inv)
                    save_history(hist)
                    # Advance next_due
                    for rec in r_list:
                        if (rec["client"]==r["client"] and
                                rec["desc"]==r["desc"] and
                                rec["next_due"]==r["next_due"]):
                            rec["next_due"] = next_interval(r["next_due"],r["interval"])
                    created += 1
                save_recurring(r_list)
                messagebox.showinfo("Done",
                    f"Created {created} draft invoice(s).\nFind them in 📁 Invoices.")
                self._show_page("recurring")

            GreenButton(dc, text=f"⚡  Generate {len(due_now)} Draft Invoice(s)",
                        command=generate_all_due).pack(anchor="w", padx=14, pady=10)

        # ── Active schedules list ─────────────────────────────────────────
        lc = Card(pad); lc.pack(fill="x", pady=(0,12))
        tk.Label(lc, text="ACTIVE SCHEDULES", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
        Divider(lc).pack(fill="x", padx=14)

        if not recurring:
            tk.Label(lc, text="No recurring schedules set up yet.",
                     bg=BG_CARD, fg=TEXT_DIM, font=FONT_BODY, pady=16).pack()
        else:
            hdr = tk.Frame(lc, bg=BG_HOVER, padx=14, pady=7); hdr.pack(fill="x")
            for txt, w in [("Client",18),("Interval",12),("Amount",12),
                           ("Description",0),("Next Due",12),("Actions","")]:
                tk.Label(hdr, text=txt, bg=BG_HOVER, fg=TEXT_DIM,
                         font=("Segoe UI",9,"bold"),
                         width=w if w else 0, anchor="w").pack(side="left", padx=(0,4))

            for i, r in enumerate(recurring):
                rb = BG_CARD if i%2==0 else BG_HOVER
                row = tk.Frame(lc, bg=rb, padx=14, pady=7); row.pack(fill="x")
                for txt, w in [
                    (r.get("client","")[:18],  18),
                    (r.get("interval",""),      12),
                    (fc(r.get("amount",0),sym), 12),
                    (r.get("desc","")[:24],      0),
                    (r.get("next_due",""),       12),
                ]:
                    tk.Label(row, text=txt, bg=rb, fg=TEXT_WHITE,
                             font=FONT_BODY, width=w if w else 0,
                             anchor="w").pack(side="left", padx=(0,4))

                # Active toggle
                act_var = tk.BooleanVar(value=r.get("active",True))
                def toggle_active(v=act_var, rec=r):
                    rl = load_recurring()
                    for x in rl:
                        if x["client"]==rec["client"] and x["desc"]==rec["desc"]:
                            x["active"] = v.get()
                    save_recurring(rl)
                tk.Checkbutton(row, text="On", variable=act_var,
                    bg=rb, fg=TEXT_MED, selectcolor=BG_HOVER,
                    activebackground=rb, font=FONT_SMALL,
                    cursor="hand2", command=toggle_active).pack(side="left", padx=4)

                def delete_r(rec=r):
                    if messagebox.askyesno("Delete", f"Remove recurring schedule for {rec['client']}?"):
                        rl = [x for x in load_recurring()
                              if not (x["client"]==rec["client"] and x["desc"]==rec["desc"])]
                        save_recurring(rl); self._show_page("recurring")
                GhostButton(row, text="✕", command=delete_r).pack(side="right")

        tk.Frame(pad, bg=BG_DARK, height=20).pack()

    def _add_client_dialog(self, existing=None):
        win = tk.Toplevel(self)
        win.title("Edit Client" if existing else "Add Client")
        win.minsize(440, 400); win.configure(bg=BG_DARK); win.grab_set()
        tk.Label(win, text="Edit Client" if existing else "Add New Client",
                 bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Segoe UI",14,"bold"), padx=20, pady=14).pack(anchor="w")
        frm = tk.Frame(win, bg=BG_DARK, padx=20); frm.pack(fill="x")
        fields = {}
        for lbl_txt, key in [("Name","name"),("Email","email"),("Phone","phone"),("Website","website")]:
            tk.Label(frm, text=lbl_txt, bg=BG_DARK, fg=TEXT_DIM,
                     font=FONT_SMALL).pack(anchor="w", pady=(6,1))
            e = FlatEntry(frm); e.pack(fill="x", ipady=5)
            if existing: e.set_value(existing.get(key,""))
            fields[key] = e
        tk.Label(frm, text="Billing Address", bg=BG_DARK, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", pady=(6,1))
        addr = FlatText(frm, height=3)
        if existing: addr.insert("1.0", existing.get("address",""))
        addr.pack(fill="x")
        def save():
            name = fields["name"].get_value().strip()
            if not name: messagebox.showwarning("Required","Name required."); return
            # Load fresh from disk every time to avoid overwriting concurrent changes
            current = load_clients()
            existing_name = (existing or {}).get("name","")
            # Filter out only the one being edited (empty string = new client, filters nothing)
            cl = [x for x in current if x.get("name","") != existing_name] if existing_name else list(current)
            cl.append({
                "name":    name,
                "email":   fields["email"].get_value(),
                "phone":   fields["phone"].get_value(),
                "website": fields["website"].get_value(),
                "address": addr.get("1.0","end").strip(),
                "notes":   "",
            })
            save_clients(cl); win.destroy(); self._show_page("clients")
        br = tk.Frame(win, bg=BG_DARK, padx=20, pady=14); br.pack(fill="x")
        GreenButton(br, text="💾  Save Client", command=save).pack(side="right")
        GhostButton(br, text="Cancel", command=win.destroy).pack(side="right", padx=8)

    # ═══════════════ SETTINGS ════════════════════════════════════════════

    # ═══════════════ DATA EXPORT / IMPORT ════════════════════════════════

    def _full_export(self):
        """Export all data as a single ZIP — settings, clients, invoices, expenses, profiles."""
        import zipfile, io
        fp = filedialog.asksaveasfilename(
            defaultextension=".zip",
            initialfile=f"InvoiceGenerator_backup_{datetime.today().strftime('%Y%m%d_%H%M')}.zip",
            filetypes=[("ZIP backup","*.zip"),("All","*.*")])
        if not fp: return
        try:
            with zipfile.ZipFile(fp, "w", zipfile.ZIP_DEFLATED) as zf:
                for data_file in [
                    SETTINGS_FILE, HISTORY_FILE, CLIENTS_FILE,
                    EXPENSES_FILE, RECURRING_FILE, PAYMENTS_FILE,
                    PROFILES_FILE, COUNTER_FILE,
                ]:
                    if data_file.exists():
                        zf.write(data_file, data_file.name)
            messagebox.showinfo("✅ Backup Complete",
                f"All data backed up to:\n{fp}\n\n"
                f"You can restore this on any machine by using Import.")
        except Exception as ex:
            messagebox.showerror("Export Failed", str(ex))

    def _full_import(self):
        """Import a full backup ZIP, merging or replacing data."""
        import zipfile
        fp = filedialog.askopenfilename(
            filetypes=[("ZIP backup","*.zip"),("All","*.*")])
        if not fp: return

        # Preview what's in the ZIP
        try:
            with zipfile.ZipFile(fp, "r") as zf:
                names = zf.namelist()
        except Exception as ex:
            messagebox.showerror("Invalid File", str(ex)); return

        win = tk.Toplevel(self)
        win.title("Import Backup")
        win.configure(bg=BG_DARK); win.grab_set()
        win.minsize(420, 300)

        tk.Label(win, text="📦  Import Backup",
                 bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Segoe UI",13,"bold"), padx=20, pady=14).pack(anchor="w")

        body = tk.Frame(win, bg=BG_DARK, padx=20); body.pack(fill="x")
        tk.Label(body, text="Files found in backup:",
                 bg=BG_DARK, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w", pady=(0,6))
        for name in names:
            tk.Label(body, text=f"  ✓  {name}", bg=BG_DARK,
                     fg=ACCENT, font=FONT_SMALL).pack(anchor="w")

        mode_var = tk.StringVar(value="replace")
        tk.Label(body, text="\nImport mode:", bg=BG_DARK,
                 fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w", pady=(10,4))
        for val, lbl in [
            ("replace", "Replace all — overwrites everything (clean install on new machine)"),
            ("merge",   "Merge — keeps existing data, adds new entries from backup"),
        ]:
            tk.Radiobutton(body, text=lbl, variable=mode_var, value=val,
                bg=BG_DARK, fg=TEXT_WHITE, selectcolor=BG_HOVER,
                activebackground=BG_DARK, font=FONT_SMALL,
                cursor="hand2").pack(anchor="w", pady=2)

        def do_import():
            mode = mode_var.get()
            try:
                with zipfile.ZipFile(fp, "r") as zf:
                    for name in names:
                        dest = DATA_DIR / name
                        if mode == "replace":
                            zf.extract(name, DATA_DIR)
                        else:
                            # Merge: combine lists, settings dict-merge
                            raw = zf.read(name).decode("utf-8")
                            imported = json.loads(raw)
                            if dest.exists():
                                existing_raw = dest.read_text(encoding="utf-8")
                                existing = json.loads(existing_raw)
                                if isinstance(imported, list) and isinstance(existing, list):
                                    # Merge by number/name key
                                    key = "number" if "history" in name else "name"
                                    existing_keys = {e.get(key) for e in existing if e.get(key)}
                                    new_entries = [e for e in imported if e.get(key) not in existing_keys]
                                    combined = existing + new_entries
                                    dest.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
                                elif isinstance(imported, dict) and isinstance(existing, dict):
                                    existing.update(imported)
                                    dest.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
                            else:
                                dest.write_text(raw, encoding="utf-8")

                self.settings = load_settings()
                apply_theme(self.settings.get("theme_mode","Dark"))
                win.destroy()
                messagebox.showinfo("✅ Import Complete",
                    f"Data imported successfully.\nRestart the app to see all changes.")
                self._show_page("dashboard")
            except Exception as ex:
                messagebox.showerror("Import Failed", str(ex))

        br = tk.Frame(win, bg=BG_DARK, padx=20, pady=12); br.pack(fill="x")
        GreenButton(br, text="📦  Import", command=do_import).pack(side="right", padx=(8,0))
        GhostButton(br, text="Cancel", command=win.destroy).pack(side="right")

        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - win.winfo_reqwidth())  // 2
        y = self.winfo_y() + (self.winfo_height() - win.winfo_reqheight()) // 2
        win.geometry(f"+{x}+{y}")

    def _import_invoices_csv(self):
        """Import invoices from a CSV file."""
        fp = filedialog.askopenfilename(
            filetypes=[("CSV files","*.csv"),("All","*.*")])
        if not fp: return

        try:
            imported = []
            with open(fp, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Flexible column mapping — handles common CSV export formats
                    def g(*keys):
                        for k in keys:
                            for col in row:
                                if col.strip().lower() == k.lower():
                                    return row[col].strip()
                        return ""

                    try:   total = float(g("total","amount","grand total","invoice total").replace("£","").replace("$","").replace(",","") or 0)
                    except: total = 0.0

                    entry = {
                        "number":       g("invoice #","invoice number","number","inv #") or f"IMP-{len(imported)+1:04d}",
                        "date":         g("date","invoice date"),
                        "due_date":     g("due","due date","payment due"),
                        "status":       g("status") or "Unpaid",
                        "client_name":  g("client","client name","customer","company"),
                        "client_email": g("email","client email","customer email"),
                        "client_phone": g("phone","client phone"),
                        "client_address": g("address","billing address"),
                        "total":        total,
                        "items":        [],
                        "discount":     "0",
                        "notes":        g("notes","description","memo"),
                        "filepath":     "",
                        "paid_date":    g("paid date","payment date"),
                        "last_reminder":"",
                        "po":           g("po","po number","reference","ref"),
                        "currency_symbol": g("currency","symbol") or self.settings.get("currency_symbol","£"),
                        "invoice_template": "Professional",
                        "amount_paid":  g("amount paid","paid") or "0",
                    }
                    imported.append(entry)

        except Exception as ex:
            messagebox.showerror("CSV Error", f"Could not read CSV:\n{ex}"); return

        if not imported:
            messagebox.showinfo("Nothing Imported", "No rows found in CSV."); return

        # Preview dialog
        win = tk.Toplevel(self)
        win.title("Import Invoices from CSV")
        win.configure(bg=BG_DARK); win.grab_set()
        win.minsize(500, 350)

        tk.Label(win, text=f"📊  Found {len(imported)} invoice(s) to import",
                 bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Segoe UI",13,"bold"), padx=20, pady=14).pack(anchor="w")

        body = tk.Frame(win, bg=BG_DARK, padx=20); body.pack(fill="x")

        # Show first 5
        tk.Label(body, text="Preview (first 5):", bg=BG_DARK,
                 fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w", pady=(0,6))
        hdr = tk.Frame(body, bg=BG_HOVER, padx=8, pady=5); hdr.pack(fill="x")
        for t, w in [("Invoice #",12),("Client",18),("Date",12),("Total",10),("Status",10)]:
            tk.Label(hdr, text=t, bg=BG_HOVER, fg=TEXT_DIM,
                     font=("Segoe UI",8,"bold"), width=w, anchor="w").pack(side="left")
        sym = self.settings.get("currency_symbol","£")
        for i, row in enumerate(imported[:5]):
            rb = BG_CARD if i%2==0 else BG_HOVER
            r = tk.Frame(body, bg=rb, padx=8, pady=5); r.pack(fill="x")
            for txt, w in [(row["number"],12),(row["client_name"][:18],18),
                           (row["date"],12),(fc(row["total"],sym),10),(row["status"],10)]:
                tk.Label(r, text=txt, bg=rb, fg=TEXT_WHITE,
                         font=FONT_SMALL, width=w, anchor="w").pack(side="left")
        if len(imported) > 5:
            tk.Label(body, text=f"  ... and {len(imported)-5} more",
                     bg=BG_DARK, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w", pady=4)

        skip_dupes_var = tk.BooleanVar(value=True)
        tk.Checkbutton(body, text="Skip invoices with numbers that already exist",
            variable=skip_dupes_var,
            bg=BG_DARK, fg=TEXT_WHITE, selectcolor=BG_HOVER,
            activebackground=BG_DARK, font=FONT_SMALL,
            cursor="hand2").pack(anchor="w", pady=(12,0))

        def do_import():
            hist = load_history()
            existing_nums = {h.get("number") for h in hist}
            added = 0
            for entry in imported:
                if skip_dupes_var.get() and entry["number"] in existing_nums:
                    continue
                hist.insert(0, entry)
                added += 1
            save_history(hist)
            win.destroy()
            messagebox.showinfo("✅ Imported", f"Imported {added} invoice(s).")
            self._show_page("history")

        br = tk.Frame(win, bg=BG_DARK, padx=20, pady=12); br.pack(fill="x")
        GreenButton(br, text=f"📊  Import {len(imported)} Invoice(s)",
                    command=do_import).pack(side="right", padx=(8,0))
        GhostButton(br, text="Cancel", command=win.destroy).pack(side="right")
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - win.winfo_reqwidth())  // 2
        y = self.winfo_y() + (self.winfo_height() - win.winfo_reqheight()) // 2
        win.geometry(f"+{x}+{y}")


    def _quick_search_popup(self):
        """Ctrl+K — floating search popup across all invoices and clients."""
        history = load_history()
        clients = load_clients()
        sym     = self.settings.get("currency_symbol","£")

        win = tk.Toplevel(self)
        win.title("")
        win.configure(bg=BG_CARD)
        win.overrideredirect(True)   # borderless
        win.grab_set()

        # Position centred
        w, h = 560, 420
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height()  - h) // 3
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.lift()

        # Border frame
        outer = tk.Frame(win, bg=ACCENT, padx=1, pady=1)
        outer.pack(fill="both", expand=True)
        inner = tk.Frame(outer, bg=BG_CARD)
        inner.pack(fill="both", expand=True)

        # Search bar
        bar = tk.Frame(inner, bg=BG_CARD, padx=12, pady=10)
        bar.pack(fill="x")
        tk.Label(bar, text="🔍", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",14)).pack(side="left", padx=(0,8))
        q_var = tk.StringVar()
        entry = tk.Entry(bar, textvariable=q_var, bg=BG_CARD,
                         fg=TEXT_WHITE, insertbackground=ACCENT,
                         relief="flat", bd=0, font=("Segoe UI",14))
        entry.pack(side="left", fill="x", expand=True)
        tk.Label(bar, text="Esc to close", bg=BG_CARD,
                 fg=TEXT_DIM, font=FONT_SMALL).pack(side="right")

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x")

        # Results area
        results_frame = tk.Frame(inner, bg=BG_CARD)
        results_frame.pack(fill="both", expand=True, padx=0, pady=0)

        result_items = []  # (type, data) tuples for keyboard nav
        selected_idx = [0]

        def highlight(idx):
            for i, (widget, _, _) in enumerate(result_items):
                bg = BG_HOVER if i == idx else BG_CARD
                widget.config(bg=bg)
                for child in widget.winfo_children():
                    try: child.config(bg=bg)
                    except Exception: pass

        def open_result(idx=None):
            if idx is None: idx = selected_idx[0]
            if not result_items: return
            _, rtype, rdata = result_items[idx]
            win.destroy()
            if rtype == "invoice":
                self._show_page("history")
            elif rtype == "invoice_edit":
                self._show_page("invoice", prefill=dict(rdata))
            elif rtype == "client":
                self._show_page("clients")

        def update_results(*_):
            for w in results_frame.winfo_children(): w.destroy()
            result_items.clear()
            selected_idx[0] = 0

            q = q_var.get().strip().lower()
            if not q:
                tk.Label(results_frame,
                    text="Start typing to search invoices and clients...",
                    bg=BG_CARD, fg=TEXT_DIM, font=FONT_BODY,
                    pady=30).pack()
                return

            matches = []
            # Search invoices
            for h in history:
                if (q in h.get("number","").lower() or
                    q in (h.get("client_name") or "").lower() or
                    q in h.get("date","").lower() or
                    q in h.get("status","").lower()):
                    matches.append(("invoice", h))
            # Search clients
            for c in clients:
                if (q in c.get("name","").lower() or
                    q in c.get("email","").lower()):
                    matches.append(("client", c))

            if not matches:
                tk.Label(results_frame,
                    text=f'No results for "{q_var.get()}"',
                    bg=BG_CARD, fg=TEXT_DIM, font=FONT_BODY,
                    pady=30).pack()
                return

            for i, (rtype, rdata) in enumerate(matches[:12]):
                rb = BG_HOVER if i==0 else BG_CARD
                row = tk.Frame(results_frame, bg=rb, padx=14, pady=8,
                               cursor="hand2")
                row.pack(fill="x")

                if rtype == "invoice":
                    status_col = {"Paid":ACCENT,"Overdue":RED_ERR,
                                  "Draft":TEXT_DIM}.get(rdata.get("status",""),GOLD)
                    tk.Label(row, text="📄", bg=rb, fg=ACCENT,
                             font=FONT_BODY).pack(side="left", padx=(0,8))
                    tk.Label(row, text=rdata.get("number",""),
                             bg=rb, fg=TEXT_WHITE,
                             font=("Segoe UI",10,"bold"), width=12,
                             anchor="w").pack(side="left")
                    client = (rdata.get("client_name") or "")[:20]
                    tk.Label(row, text=client, bg=rb, fg=TEXT_MED,
                             font=FONT_BODY, width=20, anchor="w").pack(side="left")
                    tk.Label(row, text=fc(rdata.get("total",0),sym),
                             bg=rb, fg=TEXT_WHITE,
                             font=FONT_BODY, width=10, anchor="e").pack(side="left")
                    tk.Label(row, text=rdata.get("status",""),
                             bg=rb, fg=status_col,
                             font=("Segoe UI",9,"bold")).pack(side="right")
                    is_draft = rdata.get("status") == "Draft"
                    result_items.append((row, "invoice_edit" if is_draft else "invoice", rdata))
                else:
                    tk.Label(row, text="👤", bg=rb, fg=BLUE,
                             font=FONT_BODY).pack(side="left", padx=(0,8))
                    tk.Label(row, text=rdata.get("name",""),
                             bg=rb, fg=TEXT_WHITE,
                             font=("Segoe UI",10,"bold")).pack(side="left")
                    tk.Label(row, text=rdata.get("email",""),
                             bg=rb, fg=TEXT_DIM,
                             font=FONT_SMALL).pack(side="left", padx=(8,0))
                    tk.Label(row, text="Client", bg=rb, fg=BLUE,
                             font=("Segoe UI",9,"bold")).pack(side="right")
                    result_items.append((row, "client", rdata))

                def on_click(e, idx=i): selected_idx[0]=idx; open_result(idx)
                row.bind("<Button-1>", on_click)
                for child in row.winfo_children():
                    child.bind("<Button-1>", on_click)

            if result_items:
                highlight(0)

        def on_key(e):
            if e.keysym == "Escape":
                win.destroy()
            elif e.keysym == "Return":
                open_result()
            elif e.keysym == "Down":
                if result_items:
                    selected_idx[0] = min(selected_idx[0]+1, len(result_items)-1)
                    highlight(selected_idx[0])
            elif e.keysym == "Up":
                if result_items:
                    selected_idx[0] = max(selected_idx[0]-1, 0)
                    highlight(selected_idx[0])

        q_var.trace_add("write", update_results)
        entry.bind("<KeyPress>", on_key)
        win.bind("<Escape>", lambda e: win.destroy())
        entry.focus_set()
        update_results()

    def _pg_settings(self):
        # ── Tab bar (fixed, not scrollable) ──────────────────────────────
        outer_wrap = tk.Frame(self.content, bg=BG_DARK)
        outer_wrap.pack(fill="both", expand=True)

        tab_bar = tk.Frame(outer_wrap, bg=BG_DARK, padx=16, pady=10)
        tab_bar.pack(fill="x", side="top")
        tk.Label(tab_bar, text="Settings", bg=BG_DARK, fg=TEXT_WHITE,
                 font=FONT_HEAD).pack(side="left")

        TABS = [
            ("🏢 Business",   "business"),
            ("💰 Invoicing",  "invoicing"),
            ("📧 Email",      "email"),
            ("⌨️ Shortcuts",  "shortcuts"),
            ("🎨 Appearance", "appearance"),
            ("☁️ Backup",     "backup"),
        ]
        active_tab = getattr(self, "_settings_tab", "business")
        tab_btns = {}

        content_area = tk.Frame(outer_wrap, bg=BG_DARK)
        content_area.pack(fill="both", expand=True)

        def show_tab(name):
            self._settings_tab = name
            for k, b in tab_btns.items():
                b.config(
                    bg=ACCENT if k==name else BG_HOVER,
                    fg="#000" if k==name else TEXT_MED)
            for w in content_area.winfo_children(): w.destroy()
            _build_tab(name, content_area)

        tab_frame = tk.Frame(tab_bar, bg=BG_DARK)
        tab_frame.pack(side="right")
        for label, name in TABS:
            b = tk.Button(tab_frame, text=label,
                command=lambda n=name: show_tab(n),
                bg=ACCENT if name==active_tab else BG_HOVER,
                fg="#000" if name==active_tab else TEXT_MED,
                relief="flat", bd=0, font=FONT_SMALL,
                cursor="hand2", padx=12, pady=6)
            b.pack(side="left", padx=2)
            tab_btns[name] = b

        self._sv = {}

        def _build_tab(tab_name, parent):
            inner = make_scrollable(parent)
            pad = tk.Frame(inner, bg=BG_DARK)
            pad.pack(fill="both", expand=True, padx=22, pady=16)

            def section(title, fields):
                card = Card(pad); card.pack(fill="x", pady=(0,12))
                tk.Label(card, text=title, bg=BG_CARD, fg=ACCENT,
                         font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
                Divider(card).pack(fill="x", padx=14)
                outer = tk.Frame(card, bg=BG_CARD, padx=14, pady=10); outer.pack(fill="x")
                outer.columnconfigure(0, weight=1); outer.columnconfigure(1, weight=1)
                for i,(lbl_txt,key,ftype,opts) in enumerate(fields):
                    col_frame = tk.Frame(outer, bg=BG_CARD)
                    col_frame.grid(row=i//2, column=i%2, sticky="ew",
                                   padx=(0 if i%2==0 else 8,0), pady=2)
                    if ftype == "check":
                        var = tk.BooleanVar(value=bool(self.settings.get(key,True)))
                        tk.Checkbutton(col_frame, text=lbl_txt, variable=var,
                            bg=BG_CARD, fg=TEXT_MED, selectcolor=BG_HOVER,
                            activebackground=BG_CARD, font=FONT_BODY,
                            cursor="hand2").pack(anchor="w", pady=(10,0))
                        self._sv[key] = var; continue

                    tk.Label(col_frame, text=lbl_txt, bg=BG_CARD, fg=TEXT_DIM,
                             font=FONT_SMALL).pack(anchor="w", pady=(4,1))

                    if ftype in ("entry","password"):
                        var = tk.StringVar(value=str(self.settings.get(key,"")))
                        e = tk.Entry(col_frame, textvariable=var,
                            show="•" if ftype=="password" else "",
                            bg=BG_HOVER, fg=TEXT_WHITE, insertbackground=ACCENT,
                            relief="flat", bd=0, font=FONT_BODY,
                            highlightthickness=1, highlightbackground=BORDER,
                            highlightcolor=ACCENT)
                        e.pack(fill="x", ipady=5); self._sv[key] = var

                    elif ftype == "text":
                        t = FlatText(col_frame, height=3)
                        t.insert("1.0", str(self.settings.get(key,""))); t.pack(fill="x")
                        self._sv[key] = t

                    elif ftype == "combo":
                        var = tk.StringVar(value=str(self.settings.get(key, opts[0] if opts else "")))
                        ttk.Combobox(col_frame, textvariable=var, values=opts,
                            state="readonly", font=FONT_BODY).pack(fill="x", ipady=4)
                        self._sv[key] = var

                    elif ftype == "color":
                        var = tk.StringVar(value=str(self.settings.get(key,"#00e676")))
                        cf2 = tk.Frame(col_frame, bg=BG_CARD); cf2.pack(fill="x")
                        sw = tk.Label(cf2, text="   ", bg=var.get(), padx=14, pady=8)
                        sw.pack(side="left", padx=(0,6))
                        tk.Entry(cf2, textvariable=var, bg=BG_HOVER, fg=TEXT_WHITE,
                            insertbackground=ACCENT, relief="flat", bd=0, font=FONT_BODY,
                            highlightthickness=1, highlightbackground=BORDER, width=10
                        ).pack(side="left", ipady=5)
                        def pick(v=var, s=sw):
                            c = colorchooser.askcolor(color=v.get())[1]
                            if c: v.set(c); s.config(bg=c)
                        GhostButton(cf2, text="Pick", command=pick).pack(side="left", padx=6)
                        self._sv[key] = var

                    elif ftype == "shortcut":
                        # ── Live hotkey recorder ─────────────────────────────
                        # Uses a single app-level active recorder tracker so
                        # only ONE field can be recording at a time.
                        var = tk.StringVar(value=str(self.settings.get(key, "")))
                        sf2 = tk.Frame(col_frame, bg=BG_CARD)
                        sf2.pack(fill="x")

                        display = tk.Label(sf2, textvariable=var,
                            bg=BG_HOVER, fg=ACCENT,
                            font=("Consolas", 10), anchor="w",
                            highlightthickness=1, highlightbackground=BORDER,
                            relief="flat", padx=8, pady=6)
                        display.pack(side="left", fill="x", expand=True)

                        rec_btn = tk.Button(sf2, text="⏺ Record",
                            bg=BG_HOVER, fg=TEXT_MED,
                            activebackground=BG_HOVER, activeforeground=TEXT_WHITE,
                            relief="flat", bd=0, font=FONT_SMALL,
                            cursor="hand2", padx=8, pady=4)
                        rec_btn.pack(side="left", padx=(4,0))

                        clear_btn = tk.Button(sf2, text="✕",
                            bg=BG_HOVER, fg=TEXT_DIM,
                            activebackground=BG_HOVER, activeforeground=RED_ERR,
                            relief="flat", bd=0, font=FONT_SMALL,
                            cursor="hand2", padx=6, pady=4)
                        clear_btn.pack(side="left", padx=(2,0))

                        hint = tk.Label(col_frame,
                            text="Click ⏺ Record then press your combo",
                            bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI", 8))
                        hint.pack(anchor="w", pady=(2,0))

                        # ── Per-field stop function stored in list so lambdas can reference it
                        _stop_fn = [None]

                        def _stop_record(v=var, btn=rec_btn, h=hint, d=display, sf=_stop_fn):
                            # Unbind app-level key listener
                            try: self.unbind("<KeyPress>")
                            except Exception: pass
                            # Reset to idle visual
                            btn.config(bg=BG_HOVER, fg=TEXT_MED, text="⏺ Record")
                            d.config(highlightbackground=BORDER, bg=BG_HOVER)
                            if v.get():
                                h.config(fg=ACCENT,
                                    text="✓ Saved — hit Save Settings to apply")
                            else:
                                h.config(fg=TEXT_DIM,
                                    text="Click ⏺ Record then press your combo")
                            # Clear global active tracker
                            if hasattr(self, "_active_recorder") and self._active_recorder is sf:
                                self._active_recorder = None

                        _stop_fn[0] = _stop_record

                        def _start_record(v=var, btn=rec_btn, h=hint, d=display, sf=_stop_fn):
                            # Cancel any other field currently recording
                            if hasattr(self, "_active_recorder") and self._active_recorder is not None:
                                try: self._active_recorder[0]()
                                except Exception: pass

                            self._active_recorder = sf

                            btn.config(bg=RED_ERR, fg="#ffffff", text="🔴 Listening...")
                            h.config(text="Press your key combo now (Esc to cancel)...",
                                     fg=GOLD)
                            d.config(highlightbackground=RED_ERR, bg="#1a0a0a")

                            def _on_key(event, v=v, sf=sf):
                                keysym = event.keysym

                                # Escape = cancel
                                if keysym == "Escape":
                                    sf[0]()
                                    return "break"

                                # Modifier-only keypresses — update hint and wait
                                MODS = ("Control_L","Control_R","Shift_L","Shift_R",
                                        "Alt_L","Alt_R","Meta_L","Meta_R",
                                        "Super_L","Super_R","caps_lock","Caps_Lock")
                                if keysym in MODS:
                                    # Show which modifiers are held so far
                                    holding = []
                                    if keysym in ("Control_L","Control_R"): holding.append("Ctrl")
                                    if keysym in ("Shift_L","Shift_R"):     holding.append("Shift")
                                    if keysym in ("Alt_L","Alt_R"):         holding.append("Alt")
                                    h.config(
                                        text=f"Holding {'+'.join(holding)}... now press a key",
                                        fg=GOLD)
                                    return "break"

                                # Real key pressed — read modifiers directly from keysym
                                # via the event.state bits but ONLY the clean ones
                                parts = []
                                # Ctrl bit = 4, never false-positive
                                if event.state & 0x4:   parts.append("Ctrl")
                                # Shift bit = 1
                                if event.state & 0x1:   parts.append("Shift")
                                # Alt bit = 0x8 but ONLY if Ctrl is NOT also set
                                # (Ctrl+Alt together = AltGr on Windows = ignore Alt)
                                if (event.state & 0x8) and not (event.state & 0x4):
                                    parts.append("Alt")

                                # Normalise key display
                                if len(keysym) == 1:
                                    key_display = keysym.upper()
                                elif keysym.startswith("F") and keysym[1:].isdigit():
                                    key_display = keysym
                                else:
                                    key_display = keysym.capitalize()

                                parts.append(key_display)

                                # Must have at least modifier + key
                                if len(parts) < 2:
                                    h.config(
                                        text="⚠ Hold Ctrl / Shift / Alt then press a key",
                                        fg=RED_ERR)
                                    return "break"

                                v.set("+".join(parts))
                                sf[0]()
                                return "break"

                            # Bind at app (root) level so it fires regardless of focus
                            self.bind("<KeyPress>", _on_key)

                        def _clear_sc(v=var, h=hint, d=display):
                            v.set("")
                            h.config(text="Click ⏺ Record then press your combo",
                                     fg=TEXT_DIM)
                            d.config(highlightbackground=BORDER, bg=BG_HOVER)

                        rec_btn.config(command=_start_record)
                        clear_btn.config(command=_clear_sc)

                        self._sv[key] = var

                    elif ftype in ("folder","file"):
                        var = tk.StringVar(value=str(self.settings.get(key,"")))
                        ff = tk.Frame(col_frame, bg=BG_CARD); ff.pack(fill="x")
                        tk.Entry(ff, textvariable=var, bg=BG_HOVER, fg=TEXT_WHITE,
                            insertbackground=ACCENT, relief="flat", bd=0, font=FONT_BODY,
                            highlightthickness=1, highlightbackground=BORDER, width=20
                        ).pack(side="left", ipady=5, fill="x", expand=True)

                        # Clear button for file fields
                        def clear_file(v=var):
                            v.set("")
                            if hasattr(self, "_logo_preview"):
                                self._logo_preview.config(image="", text="No logo set",
                                    fg=TEXT_DIM)
                        tk.Button(ff, text="✕", command=clear_file,
                            bg=BG_HOVER, fg=TEXT_DIM, activebackground=BG_HOVER,
                            activeforeground=RED_ERR, relief="flat", bd=0,
                            font=FONT_SMALL, cursor="hand2", padx=6
                        ).pack(side="left", padx=(2,0))

                        def browse(v=var, is_file=ftype=="file", k=key):
                            if is_file:
                                p = filedialog.askopenfilename(
                                    filetypes=[("Images","*.png *.jpg *.jpeg *.gif"),("All","*.*")])
                            else:
                                p = filedialog.askdirectory(initialdir=v.get())
                            if p:
                                v.set(p)
                                # Update logo preview if this is the logo field
                                if k == "logo_path" and PIL_OK:
                                    self._update_logo_preview(p)
                        GhostButton(ff, text="Browse", command=browse).pack(side="left", padx=4)

                        # Logo preview — only for logo_path field
                        if key == "logo_path":
                            preview_frame = tk.Frame(col_frame, bg=BG_HOVER,
                                highlightthickness=1, highlightbackground=BORDER)
                            preview_frame.pack(fill="x", pady=(6,0))
                            self._logo_preview = tk.Label(preview_frame, bg=BG_HOVER,
                                fg=TEXT_DIM, font=FONT_SMALL, pady=8,
                                text="No logo set" if not var.get() else "")
                            self._logo_preview.pack(padx=8, pady=6)
                            # Show existing logo if set
                            if var.get() and PIL_OK:
                                self._update_logo_preview(var.get())

                        self._sv[key] = var

            if tab_name == "business":
                section("🏢  Your Business", [
                    ("Company Name",     "company_name",    "entry",   []),
                    ("Email",            "company_email",   "entry",   []),
                    ("Phone",            "company_phone",   "entry",   []),
                    ("Website",          "company_website", "entry",   []),
                    ("VAT Number",       "vat_number",      "entry",   []),
                    ("Address",          "company_address", "text",    []),
                    ("Logo Image",       "logo_path",       "file",    []),
                    ("Show Logo on PDF", "show_logo",        "check",   []),
                    ("Logo Width (mm)",  "logo_width_mm",    "entry",   []),
                    ("Logo Height (mm)", "logo_height_mm",   "entry",   []),
                ])
                section("🏦  Banking & Payments", [
                    ("Bank Name",        "bank_name",       "entry",   []),
                    ("Sort Code",        "bank_sort_code",  "entry",   []),
                    ("Account Number",   "bank_account",    "entry",   []),
                    ("Payment Reference","bank_reference",  "entry",   []),
                    ("Payment Terms (days)", "payment_terms","entry",  []),
                ])

            elif tab_name == "invoicing":
                section("💰  Tax & Currency", [
                    ("Currency",         "currency",        "combo",
                     ["GBP (£)","USD ($)","EUR (€)","CAD (C$)","AUD (A$)"]),
                    ("Currency Symbol",  "currency_symbol", "entry",   []),
                    ("Tax Rate (%)",     "tax_rate",        "entry",   []),
                    ("Tax Label",        "tax_label",       "entry",   []),
                ])
                section("📄  Invoice Defaults", [
                    ("Invoice Prefix",   "invoice_prefix",  "entry",   []),
                    ("Starting Number",  "invoice_start",   "entry",   []),
                    ("Page Size",        "page_size",       "combo",   ["A4","Letter"]),
                    ("Date Format",      "date_format",     "combo",
                     ["DD/MM/YYYY","MM/DD/YYYY","YYYY-MM-DD"]),
                    ("PDF Template",     "invoice_template","combo",
                     ["Professional","Minimal","Bold"]),
                    ("Default Notes",    "default_notes",   "text",    []),
                ])
                section("🔗  Online Payment Links (shown on PDF)", [
                    ("PayPal.me Link",   "paypal_link",     "entry",   []),
                    ("Stripe Link",      "stripe_link",     "entry",   []),
                    ("Custom Link URL",  "custom_pay_link", "entry",   []),
                    ("Custom Link Label","custom_pay_label","entry",   []),
                ])
                section("⏰  Automatic Late Fees", [
                    ("Enable Late Fees", "late_fee_enabled","combo",   ["True","False"]),
                    ("Apply After (days)","late_fee_days",  "entry",   []),
                    ("Fee Type",         "late_fee_type",   "combo",   ["Percentage","Fixed Amount"]),
                    ("Fee Amount",       "late_fee_amount", "entry",   []),
                    ("Fee Description",  "late_fee_description","entry",[]),
                ])

            elif tab_name == "email":
                section("📧  Email (SMTP)", [
                    ("Your Email",       "smtp_email",      "entry",    []),
                    ("App Password",     "smtp_password",   "password", []),
                    ("SMTP Host",        "smtp_host",       "entry",    []),
                    ("SMTP Port",        "smtp_port",       "entry",    []),
                ])
                # Help card
                hc = Card(pad); hc.pack(fill="x", pady=(0,12))
                tk.Label(hc, text="📋  HOW TO SET UP EMAIL", bg=BG_CARD, fg=ACCENT,
                         font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
                Divider(hc).pack(fill="x", padx=14)
                hf = tk.Frame(hc, bg=BG_CARD, padx=14, pady=12); hf.pack(fill="x")
                for step in [
                    "1. Enable 2-Step Verification on your Google account",
                    "2. Go to myaccount.google.com/apppasswords",
                    "3. Create an app password named 'Invoice Generator'",
                    "4. Paste the 16-character password into App Password above",
                    "5. For Outlook: use smtp-mail.outlook.com / port 587 / your normal password",
                ]:
                    tk.Label(hf, text=step, bg=BG_CARD, fg=TEXT_MED,
                             font=FONT_SMALL, anchor="w").pack(anchor="w", pady=1)
                section("📩  Reminder Email Template", [
                    ("Subject",  "reminder_email_subject", "entry", []),
                    ("Body",     "reminder_email_body",    "text",  []),
                ])

            elif tab_name == "shortcuts":
                section("⌨️  Keyboard Shortcuts", [
                    ("New Invoice",      "shortcut_new_invoice",  "shortcut", []),
                    ("Export PDF",       "shortcut_export_pdf",   "shortcut", []),
                    ("Save Draft",       "shortcut_save_draft",   "shortcut", []),
                    ("Focus Search",     "shortcut_focus_search", "shortcut", []),
                    ("Go to Dashboard",  "shortcut_dashboard",    "shortcut", []),
                    ("Go to Invoices",   "shortcut_invoices",     "shortcut", []),
                    ("Go to Clients",    "shortcut_clients",      "shortcut", []),
                    ("Go to Settings",   "shortcut_settings",     "shortcut", []),
                    ("Reload Page",      "shortcut_reload",       "shortcut", []),
                    ("Clear/Reset Form", "shortcut_clear_form",   "shortcut", []),
                ])
                # Hardcoded shortcuts info card
                ic = Card(pad); ic.pack(fill="x", pady=(0,12))
                tk.Label(ic, text="⚡  ALWAYS-ON SHORTCUTS (not configurable)",
                         bg=BG_CARD, fg=ACCENT,
                         font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
                Divider(ic).pack(fill="x", padx=14)
                inf = tk.Frame(ic, bg=BG_CARD, padx=14, pady=12); inf.pack(fill="x")
                for sc, desc in [
                    ("Ctrl+K",   "Quick search popup — find any invoice or client instantly"),
                    ("Ctrl+W",   "Clear cache / data manager"),
                    ("Ctrl+=",   "Add line item (on invoice page)"),
                    ("F1",       "Help & Tutorial"),
                    ("F5",       "Reload current page"),
                    ("Alt+←",   "Go back to Invoices"),
                    ("Delete",   "Delete selected invoice (in invoice list)"),
                    ("↑ / ↓",   "Navigate invoice list rows"),
                    ("Enter",    "Open / edit selected invoice"),
                ]:
                    row = tk.Frame(inf, bg=BG_CARD); row.pack(fill="x", pady=2)
                    tk.Label(row, text=sc, bg=BG_CARD, fg=ACCENT,
                             font=("Consolas",9,"bold"), width=12, anchor="w").pack(side="left")
                    tk.Label(row, text=desc, bg=BG_CARD, fg=TEXT_MED,
                             font=FONT_SMALL).pack(side="left")

            elif tab_name == "appearance":
                section("🎨  Appearance & Branding", [
                    ("Theme",            "theme_mode",      "combo",   ["Dark","Light"]),
                    ("Accent Colour",    "theme_accent",    "color",   []),
                    ("Invoice Footer",   "invoice_footer",  "text",    []),
                ])
                section("📋  Terms & Conditions", [
                    ("Add T&Cs Page to PDF", "tc_enabled",  "check",   []),
                    ("Terms & Conditions Text", "tc_text",  "text",    []),
                ])
                section("🖥️  Behaviour", [
                    ("Auto-open PDF after export", "auto_open_pdf",    "check", []),
                    ("Confirm before closing",     "confirm_on_close", "check", []),
                ])
                section("💾  File Saving", [
                    ("Default Save Folder","save_directory","folder",  []),
                    ("Auto-save on export","auto_save",     "check",   []),
                ])

            elif tab_name == "backup":
                section("☁️  Auto-Backup", [
                    ("Enable Auto-Backup","backup_enabled", "check",   []),
                    ("Backup Folder",    "backup_folder",   "folder",  []),
                ])
                # Data tools card
                dt = Card(pad); dt.pack(fill="x", pady=(0,12))
                tk.Label(dt, text="📦  DATA BACKUP & IMPORT", bg=BG_CARD, fg=ACCENT,
                         font=("Segoe UI",8,"bold"), padx=14, pady=8).pack(anchor="w")
                Divider(dt).pack(fill="x", padx=14)
                df2 = tk.Frame(dt, bg=BG_CARD, padx=14, pady=12); df2.pack(fill="x")
                tk.Label(df2,
                    text="Export everything as a single ZIP to back up or move to another machine.",
                    bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI",8)).pack(anchor="w", pady=(0,8))
                row1 = tk.Frame(df2, bg=BG_CARD); row1.pack(fill="x", pady=(0,8))
                GreenButton(row1, text="📦  Export Full Backup (.zip)",
                    command=self._full_export).pack(side="left")
                GhostButton(row1, text="📥  Import Backup (.zip)",
                    command=self._full_import).pack(side="left", padx=8)
                Divider(df2).pack(fill="x", pady=(8,10))
                tk.Label(df2,
                    text="Import invoices from a spreadsheet CSV.",
                    bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI",8)).pack(anchor="w", pady=(0,6))
                GhostButton(df2, text="📊  Import Invoices from CSV",
                    command=self._import_invoices_csv).pack(anchor="w")

            # ── Save button (always shown at bottom of each tab) ─────────
            br = tk.Frame(pad, bg=BG_DARK); br.pack(fill="x", pady=(8,24))

            def save_all():
                # Collect ALL values first, before any widget is touched or destroyed
                collected = {}
                for key, widget in self._sv.items():
                    try:
                        if isinstance(widget, tk.Text):
                            collected[key] = widget.get("1.0", "end").strip()
                        else:
                            collected[key] = widget.get()
                    except Exception:
                        pass  # Widget already gone — skip it
                # Now safe to update settings and rebuild the page
                self.settings.update(collected)
                save_settings(self.settings)
                self._bind_shortcuts()
                apply_theme(self.settings.get("theme_mode", "Dark"))
                self.title("Invoice Generator — Settings saved ✅")
                self.after(2500, lambda: self.title("Invoice Generator"))
                self._show_page("settings")

            GreenButton(br, text="💾  Save Settings", command=save_all).pack(side="right")
            GhostButton(br, text="Reset to Defaults",
                command=lambda: (self.settings.update(DEFAULT_SETTINGS),
                                 save_settings(self.settings),
                                 self._show_page("settings"))
            ).pack(side="right", padx=8)

        show_tab(active_tab)

    # ═══════════════ HELP ════════════════════════════════════════════════
    def _pg_help(self):
        pad = self._page_pad()
        self._h1(pad, "Help & Tutorial",
                 "A practical guide for business owners using Invoice Generator")

        def section(title, items, colour=ACCENT):
            sc = Card(pad); sc.pack(fill="x", pady=(0,12))
            hdr = tk.Frame(sc, bg=BG_CARD, padx=14, pady=10)
            hdr.pack(fill="x")
            tk.Label(hdr, text=title, bg=BG_CARD, fg=colour,
                     font=("Segoe UI",10,"bold")).pack(anchor="w")
            Divider(sc).pack(fill="x", padx=14)
            for item_title, body in items:
                f = tk.Frame(sc, bg=BG_CARD, padx=14, pady=9)
                f.pack(fill="x")
                tk.Label(f, text=item_title, bg=BG_CARD, fg=TEXT_WHITE,
                         font=("Segoe UI",10,"bold")).pack(anchor="w")
                tk.Label(f, text=body, bg=BG_CARD, fg=TEXT_MED,
                         font=FONT_BODY, wraplength=860,
                         justify="left").pack(anchor="w", padx=(10,0), pady=(3,0))

        # ── Quick Start ───────────────────────────────────────────────────
        section("🚀  First Time Setup — Do This Before Anything Else", [
            ("1.  Enter your business details",
             "Go to ⚙️ Settings → 🏢 Business tab. Fill in your company name, address, email, phone and website. "
             "This information prints on every invoice so clients know who to pay."),
            ("2.  Add your bank details",
             "Still in Settings → 🏢 Business, scroll to Banking & Payments. Add your bank name, sort code, "
             "account number and payment reference. These appear on the PDF so clients can do a bank transfer."),
            ("3.  Set your VAT number (if VAT registered)",
             "Settings → 🏢 Business → VAT Number. UK law requires your VAT number on every invoice you send "
             "to VAT-registered customers. If you're not VAT registered, leave this blank."),
            ("4.  Set your currency and tax rate",
             "Settings → 💰 Invoicing → Tax & Currency. Set your currency symbol (£ for UK), tax rate (20% "
             "for standard UK VAT, 0% if not registered), and tax label (VAT for UK businesses)."),
            ("5.  Upload your logo",
             "Settings → 🏢 Business → Logo Image. Browse to your logo file (PNG or JPG). "
             "It prints in the top-left of every PDF invoice."),
            ("6.  Add your clients",
             "Go to 👥 Clients → ＋ Add Client. Save each client's name, email, phone and address. "
             "Once saved, you can load any client onto an invoice in one click."),
        ])

        # ── Creating Invoices ─────────────────────────────────────────────
        section("📄  Creating & Sending an Invoice", [
            ("Step 1 — Start a new invoice",
             "Click 📄 New Invoice in the sidebar (or press Ctrl+N). "
             "A unique invoice number is assigned automatically."),
            ("Step 2 — Fill in the client",
             "Use the 'Load from Address Book' dropdown to load a saved client instantly, "
             "or type the client details manually. You can save a new client to your address book "
             "using the 👥 Save to Address Book button at the bottom of the client section."),
            ("Step 3 — Set the dates",
             "Invoice Date defaults to today. Due Date defaults to 30 days from now (you can change "
             "payment terms in Settings). Both are editable — click to type a new date."),
            ("Step 4 — Add your line items",
             "Click each 'Item description' field and type what you're charging for. "
             "Enter the quantity (e.g. 3 for 3 hours) and unit price (e.g. 50 for £50/hour). "
             "Tick the Tax box if this item is VAT-able. The total updates live as you type. "
             "Click + Add Line Item for more rows."),
            ("Step 5 — Review the total",
             "The running total shows top-right of the Line Items section. "
             "Click it to copy the amount to your clipboard. "
             "Use the Discount % field to apply a percentage discount to the whole invoice."),
            ("Step 6 — Export as PDF",
             "Click ⬇ Export PDF. Choose where to save it. The PDF opens automatically. "
             "Send it to your client by email attachment, or use the 📧 Email button "
             "to send it directly from the app if you've set up SMTP in Settings."),
            ("Saving a draft",
             "Not ready to send? Click 💾 Save Draft. It saves to your Invoices list "
             "with a Draft badge. Come back any time and click ✏️ Edit to continue."),
        ])

        # ── Getting Paid ──────────────────────────────────────────────────
        section("💷  Getting Paid & Chasing Late Invoices", [
            ("Marking an invoice as paid",
             "Go to 📁 Invoices. When payment arrives, click ✓ Paid on that invoice. "
             "The status changes to Paid, the date is recorded, and a PAID watermark is stamped "
             "on the PDF (if pypdf is installed — run: pip install pypdf)."),
            ("Overdue invoices",
             "Invoices past their due date are automatically flagged as Overdue in red. "
             "You don't need to do anything — the app checks every time you open the Invoices page."),
            ("Sending a payment reminder",
             "Go to 🔔 Reminders. Any overdue invoices that have passed the 7, 14 or 30-day "
             "threshold appear here with a Send button. Click 📧 Send to fire a reminder email. "
             "The email uses your template from the Reminders page — edit it to match your tone."),
            ("Partial payments",
             "If a client pays part of an invoice, go to ✏️ Edit the invoice, "
             "enter the amount paid in the 'Amount Paid' field, and re-export. "
             "The PDF will show: Gross Total → Amount Paid → Balance Due."),
            ("Late fees",
             "Settings → 💰 Invoicing → Automatic Late Fees. Enable it, set how many days "
             "before the fee kicks in, and whether it's a percentage or fixed amount. "
             "When an invoice qualifies, a ＋Fee button appears on the invoice row — click it to add the fee."),
        ])

        # ── Clients & Records ─────────────────────────────────────────────
        section("👥  Managing Clients", [
            ("Client address book",
             "Go to 👥 Clients. Add each client once and they're available on every invoice. "
             "The list shows their average days to pay — green means reliable, red means slow."),
            ("Client payment history",
             "Click 📋 History on any client to see every invoice, how long they took to pay, "
             "their total billed and outstanding balance. Useful before agreeing new work."),
            ("Reliability badge",
             "⭐ Excellent = pays within 7 days  •  ✅ Good = within 14 days  •  "
             "⚠️ Average = within 30 days  •  🔴 Slow = over 30 days."),
        ])

        # ── Expenses & Reports ────────────────────────────────────────────
        section("💸  Expenses & Financial Reports", [
            ("Logging expenses",
             "Go to 💸 Expenses → ＋ Add Expense. Log every business cost: software subscriptions, "
             "travel, equipment, marketing etc. Give each one a category. "
             "This is what turns your revenue into actual profit on the Dashboard and Reports."),
            ("Annual report & VAT",
             "Go to 📈 Reports. Select a year. You'll see total revenue, VAT collected, expenses "
             "and net profit. The quarterly VAT breakdown shows exactly what you owe HMRC each quarter. "
             "Click 🇬🇧 HMRC VAT Return for the 9-box VAT100 format — export as CSV to give your accountant."),
            ("Invoice sequence audit",
             "Also on the Reports page — checks your invoice numbers are sequential with no gaps. "
             "HMRC can ask about gaps in invoice numbering during a tax audit."),
            ("Export for accountant",
             "On the Invoices page, click 📊 Export CSV to download all invoices as a spreadsheet. "
             "On the Reports page, click 📊 Export Report CSV for the full annual breakdown. "
             "These are the two files most accountants will ask for."),
        ])

        # ── Recurring ─────────────────────────────────────────────────────
        section("🔁  Recurring Invoices (Retainers & Regular Clients)", [
            ("Setting up a recurring schedule",
             "Go to 🔁 Recurring → ＋ Add Schedule. Choose the client, how often to invoice them "
             "(weekly, monthly, quarterly, annually), the amount, and the description. "
             "Set the first due date and click Add."),
            ("Generating recurring drafts",
             "When a schedule is due, a yellow banner appears on the Recurring page. "
             "Click ⚡ Generate Drafts and the app creates a draft invoice for each due schedule "
             "with all the details pre-filled. Open each draft, review it, then export."),
            ("Common use case",
             "Perfect for monthly retainers (e.g. £1,500/month for ongoing web work), "
             "weekly cleaning or maintenance contracts, or quarterly service agreements."),
        ])

        # ── UK Legal Requirements ─────────────────────────────────────────
        section("⚖️  UK Legal Requirements for Invoices", [
            ("What must be on every invoice",
             "UK law (HMRC Notice 700) requires: a unique sequential invoice number, your business "
             "name and address, your customer's name and address, invoice date, description of "
             "goods or services, the amount charged (excl. VAT), and the total amount due."),
            ("Additional requirements if VAT registered",
             "VAT invoices must also include: your VAT registration number, the VAT rate applied "
             "to each item, the VAT amount per item, and the total VAT charged. "
             "The app will warn you if any of these are missing before you export."),
            ("Invoice numbering",
             "Invoice numbers must be sequential with no gaps. If you delete an invoice, "
             "note down the number — HMRC may ask about gaps. Use the Invoice Sequence Audit "
             "in Reports to check your numbering is clean before year end."),
            ("Keeping records",
             "UK law requires you to keep invoices for 6 years (5 years for sole traders). "
             "Use Settings → ☁️ Backup to export a ZIP of all your data regularly, "
             "or enable Auto-Backup to keep a copy in OneDrive or Dropbox automatically."),
        ])

        # ── Gmail setup ───────────────────────────────────────────────────
        section("📧  Setting Up Email (Gmail)", [
            ("Why you need an App Password",
             "Gmail won't let apps sign in with your normal password for security reasons. "
             "You need to create a special 'App Password' that only this app uses."),
            ("Step-by-step",
             "1. Go to myaccount.google.com/security\n"
             "2. Enable 2-Step Verification if not already on\n"
             "3. Go to myaccount.google.com/apppasswords\n"
             "4. Type 'Invoice Generator' and click Create\n"
             "5. Copy the 16-character password shown\n"
             "6. In this app: Settings → 📧 Email → paste into App Password\n"
             "7. Your Email = your Gmail address, SMTP Host = smtp.gmail.com, Port = 587"),
            ("Using Outlook instead",
             "SMTP Host: smtp-mail.outlook.com  •  Port: 587  •  "
             "Password: your normal Outlook password (no App Password needed for basic accounts)."),
        ])

        # ── Keyboard shortcuts ────────────────────────────────────────────
        section("⌨️  Keyboard Shortcuts", [
            ("Navigation",
             "Ctrl+N: New Invoice  •  Ctrl+I: Invoices  •  Ctrl+L: Clients  •  Ctrl+D: Dashboard\n"
             "Ctrl+,: Settings  •  F1: Help  •  F5: Reload  •  Alt+←: Back"),
            ("Invoice page",
             "Ctrl+S: Save  •  Ctrl+E: Export PDF  •  Ctrl+=: Add line item  •  Esc: Clear form"),
            ("Search & tools",
             "Ctrl+K: Quick search (find any invoice or client instantly)\n"
             "Ctrl+F: Focus search box  •  Ctrl+W: Data manager / clear cache"),
            ("Invoice list",
             "↑ / ↓: Move between rows  •  Enter: Open or edit  •  Delete: Delete selected"),
        ])

        # ── FAQ ───────────────────────────────────────────────────────────
        section("❓  Frequently Asked Questions", [
            ("Is my data safe? Does anything go to the internet?",
             f"All your data is stored only on your machine at:\n{DATA_DIR}\n"
             "Nothing is ever uploaded anywhere. The only time the app uses the internet is "
             "when you send an email reminder via SMTP."),
            ("How do I back up my data?",
             "Go to Settings → ☁️ Backup → Export Full Backup. This saves a ZIP of all your data. "
             "You can also enable Auto-Backup to silently copy data files to OneDrive or Dropbox "
             "every time you save."),
            ("How do I move to a new computer?",
             "On the old machine: Settings → ☁️ Backup → Export Full Backup. "
             "On the new machine: install the app, then Settings → ☁️ Backup → Import Backup. "
             "Select Replace All. All your invoices, clients and settings will be restored."),
            ("My invoice number keeps repeating — how do I fix it?",
             f"Delete the file: {DATA_DIR / 'counter.json'}\n"
             "The app will recreate it starting from your Settings → Invoicing → Starting Number. "
             "Or use Ctrl+W → Clear cache and tick 'Invoice counter'."),
            ("Can I use this for multiple businesses?",
             "Yes — go to 🏢 Profiles and create a profile for each business. "
             "Each profile stores separate company details, VAT number, logo, invoice prefix "
             "and accent colour. Switch between them in one click."),
            ("How do I build a standalone .exe file?",
             "Run: python build_exe.py in the app folder. Requires: pip install pyinstaller. "
             "The .exe will be in the /dist folder — no Python needed to run it."),
        ])

        tk.Frame(pad, bg=BG_DARK, height=20).pack()

    # ═══════════════ ABOUT ═══════════════════════════════════════════════
    def _pg_about(self):
        inner = make_scrollable(self.content)
        pad = tk.Frame(inner, bg=BG_DARK)
        pad.pack(fill="both", expand=True, padx=40, pady=30)

        # ── App identity ─────────────────────────────────────────────────
        tk.Label(pad, text="🧾", bg=BG_DARK, fg=ACCENT,
                 font=("Segoe UI",42)).pack()
        tk.Label(pad, text="Invoice Generator", bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Segoe UI",26,"bold")).pack(pady=(4,0))
        tk.Label(pad, text=f"Version {APP_VERSION}  •  Free & Open Source",
                 bg=BG_DARK, fg=TEXT_DIM, font=FONT_SUB).pack(pady=(4,0))

        Divider(pad).pack(fill="x", pady=20)

        # ── What it is ───────────────────────────────────────────────────
        info_card = Card(pad); info_card.pack(fill="x", pady=(0,14))
        inf = tk.Frame(info_card, bg=BG_CARD, padx=24, pady=18); inf.pack(fill="x")
        tk.Label(inf, text="ABOUT THIS APP", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold")).pack(anchor="w", pady=(0,8))
        tk.Label(inf,
            text=("A professional, fully offline invoice management tool for freelancers,\n"
                  "small businesses and sole traders. Create and export PDF invoices,\n"
                  "track payments, manage clients, log expenses and run financial reports.\n\n"
                  "Your data is stored entirely on your own machine.\n"
                  "No accounts. No subscriptions. No internet required."),
            bg=BG_CARD, fg=TEXT_MED, font=FONT_SUB, justify="center").pack()

        # ── Feature highlights ───────────────────────────────────────────
        feat_card = Card(pad); feat_card.pack(fill="x", pady=(0,14))
        ff = tk.Frame(feat_card, bg=BG_CARD, padx=24, pady=18); ff.pack(fill="x")
        tk.Label(ff, text="FEATURES", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold")).pack(anchor="w", pady=(0,10))
        feat_grid = tk.Frame(ff, bg=BG_CARD); feat_grid.pack(fill="x")
        feat_grid.columnconfigure(0, weight=1); feat_grid.columnconfigure(1, weight=1)
        features = [
            ("📄  PDF Invoice Export",      "Professional invoices with your logo and branding"),
            ("👥  Client Address Book",      "Save clients, track payment history and reliability"),
            ("📊  Dashboard & Charts",       "Revenue charts, outstanding balances at a glance"),
            ("💸  Expense Tracking",         "Log expenses by category, see profit not just revenue"),
            ("📈  Financial Reports",        "Quarterly VAT breakdown, annual summaries, CSV export"),
            ("🔔  Overdue Reminders",        "Automatic email chasers for unpaid invoices"),
            ("📧  Email Integration",        "Send invoices and reminders directly from the app"),
            ("⌨️  Keyboard Shortcuts",       "Fully configurable with a live hotkey recorder"),
        ]
        for i, (title, desc) in enumerate(features):
            col = tk.Frame(feat_grid, bg=BG_CARD)
            col.grid(row=i//2, column=i%2, sticky="ew", padx=(0 if i%2==0 else 10, 0), pady=4)
            tk.Label(col, text=title, bg=BG_CARD, fg=TEXT_WHITE,
                     font=("Segoe UI",10,"bold")).pack(anchor="w")
            tk.Label(col, text=desc, bg=BG_CARD, fg=TEXT_DIM,
                     font=FONT_SMALL).pack(anchor="w")

        # ── Tech stack ───────────────────────────────────────────────────
        tech_card = Card(pad); tech_card.pack(fill="x", pady=(0,14))
        tf2 = tk.Frame(tech_card, bg=BG_CARD, padx=24, pady=14); tf2.pack(fill="x")
        tk.Label(tf2, text="BUILT WITH", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI",8,"bold")).pack(anchor="w", pady=(0,8))
        tech_row = tk.Frame(tf2, bg=BG_CARD); tech_row.pack(anchor="w")
        for tech, colour in [
            ("Python 3", ACCENT), ("Tkinter", BLUE),
            ("ReportLab", PURPLE), ("Pillow", GOLD),
        ]:
            pill = tk.Frame(tech_row, bg=colour)
            pill.pack(side="left", padx=(0,8))
            tk.Label(pill, text=tech, bg=colour, fg="#000000",
                     font=("Segoe UI",9,"bold"), padx=10, pady=4).pack()

        # ══════════════════════════════════════════════════════════════
        # SHOUTOUT — Made by Deano @ LetUsTech
        # ══════════════════════════════════════════════════════════════
        shout_card = tk.Frame(pad, bg="#0d1f0d",
            highlightthickness=2, highlightbackground=ACCENT)
        shout_card.pack(fill="x", pady=(0,14))
        sf2 = tk.Frame(shout_card, bg="#0d1f0d", padx=24, pady=20); sf2.pack(fill="x")

        top_row = tk.Frame(sf2, bg="#0d1f0d"); top_row.pack(fill="x")
        tk.Label(top_row, text="⚡", bg="#0d1f0d", fg=ACCENT,
                 font=("Segoe UI",28)).pack(side="left", padx=(0,12))
        text_col = tk.Frame(top_row, bg="#0d1f0d"); text_col.pack(side="left", anchor="w")
        tk.Label(text_col, text="Made by Deano @ LetUsTech",
                 bg="#0d1f0d", fg=ACCENT, font=("Segoe UI",16,"bold")).pack(anchor="w")
        tk.Label(text_col,
                 text="Free tools for everyone. Built in Liverpool. 🌍",
                 bg="#0d1f0d", fg=TEXT_MED, font=FONT_SUB).pack(anchor="w")

        Divider(sf2).pack(fill="x", pady=12)

        links_row = tk.Frame(sf2, bg="#0d1f0d"); links_row.pack(fill="x")
        for icon, label, val in [
            ("🌐", "Website",  "letustech.uk"),
            ("📧", "Email",    "letustec@gmail.com"),
            ("💬", "Discord",  "discord.gg/dkebMS5eCX"),
            ("▶️", "YouTube",  "@ItsDeano3107"),
            ("🎮", "Kick",     "@deano3107"),
        ]:
            col2 = tk.Frame(links_row, bg="#0d1f0d", padx=14)
            col2.pack(side="left")
            tk.Label(col2, text=f"{icon}  {label}", bg="#0d1f0d", fg=ACCENT,
                     font=("Segoe UI",9,"bold")).pack(anchor="w")
            tk.Label(col2, text=val, bg="#0d1f0d", fg=TEXT_MED,
                     font=FONT_SMALL).pack(anchor="w")

        Divider(sf2).pack(fill="x", pady=(12,8))

        # ── Donation section ──────────────────────────────────────────────
        don_row = tk.Frame(sf2, bg="#0d1f0d"); don_row.pack(fill="x", pady=(0,4))

        don_text = tk.Frame(don_row, bg="#0d1f0d"); don_text.pack(side="left", fill="x", expand=True)
        tk.Label(don_text,
            text="☕  Buy me a coffee",
            bg="#0d1f0d", fg=ACCENT, font=("Segoe UI",11,"bold")).pack(anchor="w")
        tk.Label(don_text,
            text="This tool is completely free. If it saved you time or money,\n"
                 "a small donation helps keep LetUsTech running. No pressure!",
            bg="#0d1f0d", fg=TEXT_MED, font=FONT_SMALL,
            justify="left").pack(anchor="w", pady=(2,0))

        def open_donate(url):
            import webbrowser
            webbrowser.open(url)

        btn_frame = tk.Frame(don_row, bg="#0d1f0d", padx=10)
        btn_frame.pack(side="right")

        # PayPal donate button
        pp_btn = tk.Button(btn_frame,
            text="💛  Donate via PayPal",
            command=lambda: open_donate(
                "https://www.paypal.com/donate/?hosted_button_id=MJNXEL8GRRPSL"),
            bg="#ffc439", fg="#000000",
            font=("Segoe UI",10,"bold"),
            relief="flat", bd=0, padx=16, pady=8,
            cursor="hand2", activebackground="#f0b800",
            activeforeground="#000000")
        pp_btn.pack(pady=(0,6))

        # Bank transfer / direct
        tk.Label(btn_frame,
            text="Sort: 04-00-04  Acc: 49376025",
            bg="#0d1f0d", fg=TEXT_DIM,
            font=("Segoe UI",8)).pack()
        tk.Label(btn_frame,
            text="Ref: LetUsTech",
            bg="#0d1f0d", fg=TEXT_DIM,
            font=("Segoe UI",8)).pack()

        Divider(sf2).pack(fill="x", pady=(10,8))
        tk.Label(sf2,
            text="Thank you for using Invoice Generator — Deano @ LetUsTech  🙏",
            bg="#0d1f0d", fg=TEXT_DIM, font=("Segoe UI",9,"italic")).pack(anchor="w")

        tk.Frame(pad, bg=BG_DARK, height=20).pack()


if __name__ == "__main__":
    # ── Install global exception handlers ────────────────────────────────
    sys.excepthook = _handle_exception

    # ── Startup integrity check ──────────────────────────────────────────
    # Runs before the UI opens — validates all data files, backs up
    # anything corrupted, and resets to safe defaults if needed.
    try:
        issues = startup_integrity_check()
    except Exception:
        issues = []

    try:
        app = InvoiceApp()
        app.report_callback_exception = _tk_exception_handler

        # Show integrity warnings after window is ready (non-blocking)
        if issues:
            def _show_startup_warnings():
                msg = "\n\n".join(issues)
                import tkinter.messagebox as mb
                mb.showwarning(
                    "Startup Notice",
                    f"The following data file issues were found and fixed automatically:\n\n"
                    f"{msg}\n\n"
                    f"Backups of any corrupted files have been saved to:\n{DATA_DIR}")
            app.after(500, _show_startup_warnings)

        app.mainloop()
    except Exception:
        _handle_exception(*sys.exc_info())
