import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import re
import os
import base64
import tempfile

FAVICON_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRy"
    "UkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA"
    "9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dH"
    "B0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjA"
    "AAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj"
    "1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA"
    "9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVj"
    "AAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb"
    "/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0d"
    "Hx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4e"
    "Hh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAAWABQDASIAAhEBAxEB/8QAGQABAQAD"
    "AQAAAAAAAAAAAAAAAAQDBQYH/8QAKRAAAgICAQIEBgMAAAAAAAAAAQIDBAAFEQYxBxITQRUhNV"
    "FhgYKhsv/EABYBAQEBAAAAAAAAAAAAAAAAAAYEBf/EACERAAICAgEFAQEAAAAAAAAAAAECAwQA"
    "MREFEiGRoUFh/9oADAMBAAIRAxEAPwDx/o/ozX7LQfGNrelghfzFfTZUCqpIJYsD7g5nvdKd"
    "IipI1DfPPYA5VFsxSc/pRzltKrYu+DQrVIXmmYMVRByTxYJPA9/kDnJaHTbattIrFnWXYIY+"
    "SzyQMqjkEdyPzjgwwQrXiFcN3qpLednfreAkmsWHsStZK9jsAvjS696zTbGsad2WszeYoe/3H"
    "cYyrqb65Y/j/kYwtajWOd0XQJH3F9WRpIEdtkA/Mv6c6w2+iqGpV9CWDksqTIT5Se/HBBy6/"
    "wCIO7uVHrPBRRXHBKRtz/bHGMpj6rcjjEayEKPzJJOj0ZZDK8QLHzz/AHOTnlkmmaWVizue"
    "ScYxkBJJ5OaQAA4Gf//Z"
)

# ── Colour palette ────────────────────────────────────────────────────────────
BG       = "#0b0e14"
SURFACE  = "#141820"
SURFACE2 = "#1c2230"
BORDER   = "#2a3040"
ACCENT   = "#00e676"
ACCENT_D = "#00b85e"
TEXT     = "#e8eaf0"
MUTED    = "#6b7a96"
RED      = "#ff4c4c"
YELLOW   = "#ffc107"

FONT_BODY  = ("Consolas", 11)
FONT_SMALL = ("Consolas", 10)
FONT_BOLD  = ("Consolas", 11, "bold")
FONT_HEAD  = ("Consolas", 14, "bold")
FONT_TITLE = ("Consolas", 18, "bold")

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(e):
    return bool(EMAIL_RE.match(e.strip()))


# ── Main App ──────────────────────────────────────────────────────────────────
class CSVMaker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Email CSV Maker  //  LetUsTech")
        self.geometry("980x720")
        self.minsize(820, 600)
        self.configure(bg=BG)
        self.resizable(True, True)

        # set window icon from embedded favicon
        try:
            img_data = base64.b64decode(FAVICON_B64)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp.write(img_data)
            tmp.close()
            icon = tk.PhotoImage(file=tmp.name)
            self.iconphoto(True, icon)
            os.unlink(tmp.name)
        except Exception:
            pass

        # data store:  list of dicts  {field: value, ...}
        self.entries  = []
        self.fields   = ["email", "first_name", "last_name", "company"]   # match Email Sender tags

        self._build_ui()
        self._refresh_table()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # title bar
        hdr = tk.Frame(self, bg=BG, pady=14)
        hdr.pack(fill="x", padx=24)
        tk.Label(hdr, text="EMAIL  CSV  MAKER", font=FONT_TITLE,
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(hdr, text="LetUsTech", font=FONT_SMALL,
                 bg=BG, fg=MUTED).pack(side="right", padx=4)

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x", padx=24)

        # main layout: left panel + right table
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=16)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    def _build_left(self, parent):
        lf = tk.Frame(parent, bg=SURFACE, bd=0, width=300)
        lf.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        lf.pack_propagate(False)
        lf.columnconfigure(0, weight=1)

        # ── Manual entry section ──────────────────────────────────────────
        tk.Label(lf, text="MANUAL ENTRY", font=FONT_BOLD,
                 bg=SURFACE, fg=ACCENT, anchor="w",
                 pady=10, padx=14).pack(fill="x")
        tk.Frame(lf, bg=BORDER, height=1).pack(fill="x")

        self.field_vars   = {}   # field_name → StringVar
        self.field_frames = {}

        self.fields_container = tk.Frame(lf, bg=SURFACE)
        self.fields_container.pack(fill="x", padx=14, pady=10)

        self._render_field_inputs()

        btn_add = tk.Button(lf, text="＋  Add Entry", font=FONT_BOLD,
                            bg=ACCENT, fg=BG, relief="flat",
                            activebackground=ACCENT_D, activeforeground=BG,
                            cursor="hand2", pady=8,
                            command=self._add_entry)
        btn_add.pack(fill="x", padx=14, pady=(0, 14))

        # ── Bulk paste section ────────────────────────────────────────────
        tk.Frame(lf, bg=BORDER, height=1).pack(fill="x")
        tk.Label(lf, text="BULK PASTE", font=FONT_BOLD,
                 bg=SURFACE, fg=ACCENT, anchor="w",
                 pady=10, padx=14).pack(fill="x")

        self.bulk_hint = tk.Label(lf, text="",
                 font=FONT_SMALL, bg=SURFACE, fg=MUTED,
                 anchor="w", padx=14, wraplength=270, justify="left")
        self.bulk_hint.pack(fill="x")
        self._update_bulk_hint()

        self.bulk_text = tk.Text(lf, height=7, font=FONT_SMALL,
                                  bg=SURFACE2, fg=TEXT, insertbackground=ACCENT,
                                  relief="flat", bd=0, padx=8, pady=6,
                                  wrap="word")
        self.bulk_text.pack(fill="x", padx=14, pady=8)

        self.bulk_status = tk.Label(lf, text="", font=FONT_SMALL,
                                     bg=SURFACE, fg=MUTED, anchor="w",
                                     padx=14, wraplength=270)
        self.bulk_status.pack(fill="x")

        btn_parse = tk.Button(lf, text="⬇  Parse & Add", font=FONT_BOLD,
                               bg=SURFACE2, fg=ACCENT, relief="flat",
                               activebackground=BORDER, activeforeground=ACCENT,
                               cursor="hand2", pady=7,
                               command=self._parse_bulk)
        btn_parse.pack(fill="x", padx=14, pady=(6, 14))

        # ── Custom fields ─────────────────────────────────────────────────
        tk.Frame(lf, bg=BORDER, height=1).pack(fill="x")
        tk.Label(lf, text="CUSTOM FIELDS", font=FONT_BOLD,
                 bg=SURFACE, fg=ACCENT, anchor="w",
                 pady=10, padx=14).pack(fill="x")

        cf_row = tk.Frame(lf, bg=SURFACE)
        cf_row.pack(fill="x", padx=14, pady=(0, 8))
        cf_row.columnconfigure(0, weight=1)

        self.new_field_var = tk.StringVar()
        cf_entry = tk.Entry(cf_row, textvariable=self.new_field_var,
                             font=FONT_SMALL, bg=SURFACE2, fg=TEXT,
                             insertbackground=ACCENT, relief="flat",
                             bd=0, highlightthickness=1,
                             highlightbackground=BORDER,
                             highlightcolor=ACCENT)
        cf_entry.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 6))
        cf_entry.insert(0, "field name")
        cf_entry.bind("<FocusIn>",  lambda e: cf_entry.select_range(0, "end"))
        cf_entry.bind("<Return>",   lambda e: self._add_field())

        tk.Button(cf_row, text="Add", font=FONT_SMALL,
                  bg=SURFACE2, fg=ACCENT, relief="flat",
                  activebackground=BORDER, cursor="hand2",
                  command=self._add_field).grid(row=0, column=1)

        self.fields_list_frame = tk.Frame(lf, bg=SURFACE)
        self.fields_list_frame.pack(fill="x", padx=14)
        self._render_fields_list()

        # ── Tag reference ─────────────────────────────────────────────────
        tk.Frame(lf, bg=BORDER, height=1).pack(fill="x")
        tk.Label(lf, text="TAG REFERENCE", font=FONT_BOLD,
                 bg=SURFACE, fg=ACCENT, anchor="w",
                 pady=10, padx=14).pack(fill="x")
        tk.Label(lf,
                 text="Tags match your Email Sender — case-insensitive.\n{{first_name}}, {{FIRST_NAME}}, {{First_Name}} all work.",
                 font=FONT_SMALL, bg=SURFACE, fg=MUTED,
                 anchor="w", padx=14, wraplength=270, justify="left").pack(fill="x")
        self.tag_ref_frame = tk.Frame(lf, bg=SURFACE)
        self.tag_ref_frame.pack(fill="x", padx=14, pady=(6, 14))
        self._render_tag_reference()

    def _build_right(self, parent):
        rf = tk.Frame(parent, bg=BG)
        rf.grid(row=0, column=1, sticky="nsew")
        rf.columnconfigure(0, weight=1)
        rf.rowconfigure(1, weight=1)

        # stats bar
        stats = tk.Frame(rf, bg=BG)
        stats.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.lbl_total   = self._stat_card(stats, "0", "TOTAL")
        self.lbl_valid   = self._stat_card(stats, "0", "VALID")
        self.lbl_invalid = self._stat_card(stats, "0", "INVALID")

        # table
        table_frame = tk.Frame(rf, bg=SURFACE, bd=0)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=SURFACE, foreground=TEXT,
                         rowheight=28, font=FONT_SMALL,
                         fieldbackground=SURFACE, borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                         background=SURFACE2, foreground=ACCENT,
                         font=FONT_BOLD, relief="flat", borderwidth=0)
        style.map("Custom.Treeview",
                  background=[("selected", SURFACE2)],
                  foreground=[("selected", ACCENT)])

        self.tree = ttk.Treeview(table_frame, style="Custom.Treeview",
                                  selectmode="browse", show="headings")
        vsb = ttk.Scrollbar(table_frame, orient="vertical",
                             command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.tag_configure("invalid", foreground=RED)
        self.tree.tag_configure("valid",   foreground=TEXT)
        self.tree.bind("<Delete>",      lambda e: self._delete_selected())
        self.tree.bind("<BackSpace>",   lambda e: self._delete_selected())
        self.tree.bind("<Double-1>",    lambda e: self._edit_selected())

        # bottom action bar
        bot = tk.Frame(rf, bg=BG, pady=10)
        bot.grid(row=2, column=0, sticky="ew")

        self.skip_invalid_var = tk.BooleanVar(value=True)
        tk.Checkbutton(bot, text="Skip invalid emails on export",
                       variable=self.skip_invalid_var,
                       font=FONT_SMALL, bg=BG, fg=MUTED,
                       selectcolor=SURFACE2, activebackground=BG,
                       activeforeground=TEXT, cursor="hand2").pack(side="left")

        tk.Button(bot, text="Clear All", font=FONT_SMALL,
                  bg=SURFACE, fg=RED, relief="flat",
                  activebackground=SURFACE2, cursor="hand2",
                  command=self._clear_all).pack(side="right", padx=(8, 0))

        tk.Button(bot, text="Export CSV", font=FONT_BOLD,
                  bg=ACCENT, fg=BG, relief="flat",
                  activebackground=ACCENT_D, activeforeground=BG,
                  cursor="hand2", padx=18, pady=6,
                  command=self._export_csv).pack(side="right")

        tk.Button(bot, text="Load CSV", font=FONT_SMALL,
                  bg=SURFACE, fg=ACCENT, relief="flat",
                  activebackground=SURFACE2, activeforeground=ACCENT,
                  cursor="hand2", padx=12, pady=6,
                  command=self._load_csv).pack(side="right", padx=(0, 8))

        tk.Button(bot, text="Save Session", font=FONT_SMALL,
                  bg=SURFACE, fg=ACCENT, relief="flat",
                  activebackground=SURFACE2, activeforeground=ACCENT,
                  cursor="hand2", padx=12, pady=6,
                  command=self._save_session).pack(side="right", padx=(0, 4))

        tk.Button(bot, text="Delete Selected", font=FONT_SMALL,
                  bg=SURFACE, fg=MUTED, relief="flat",
                  activebackground=SURFACE2, cursor="hand2",
                  command=self._delete_selected).pack(side="right", padx=(0, 8))

    def _stat_card(self, parent, val, lbl):
        f = tk.Frame(parent, bg=SURFACE2, padx=18, pady=8)
        f.pack(side="left", padx=(0, 8))
        lv = tk.Label(f, text=val, font=FONT_HEAD, bg=SURFACE2, fg=TEXT)
        lv.pack()
        tk.Label(f, text=lbl, font=FONT_SMALL, bg=SURFACE2, fg=MUTED).pack()
        return lv

    # ── Field management ──────────────────────────────────────────────────────
    def _render_field_inputs(self):
        for w in self.fields_container.winfo_children():
            w.destroy()
        self.field_vars = {}
        for field in self.fields:
            row = tk.Frame(self.fields_container, bg=SURFACE)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=field.upper(), font=FONT_SMALL,
                     bg=SURFACE, fg=MUTED, width=10, anchor="w").pack(side="left")
            var = tk.StringVar()
            self.field_vars[field] = var
            e = tk.Entry(row, textvariable=var, font=FONT_SMALL,
                          bg=SURFACE2, fg=TEXT, insertbackground=ACCENT,
                          relief="flat", bd=0,
                          highlightthickness=1,
                          highlightbackground=BORDER,
                          highlightcolor=ACCENT)
            e.pack(side="left", fill="x", expand=True, ipady=5, padx=(6, 0))
            if field == "email":
                e.bind("<Return>", lambda ev: self._add_entry())

    def _copy_tag(self, tag):
        self.clipboard_clear()
        self.clipboard_append(tag)

    def _render_tag_reference(self):
        for w in self.tag_ref_frame.winfo_children():
            w.destroy()
        for field in self.fields:
            row = tk.Frame(self.tag_ref_frame, bg=SURFACE2,
                           highlightthickness=1,
                           highlightbackground=BORDER)
            row.pack(fill="x", pady=2)
            tag_str = "{{" + field + "}}"
            lbl = tk.Label(row, text=f"  {tag_str}",
                     font=("Consolas", 9), bg=SURFACE2, fg=ACCENT,
                     anchor="w", padx=4, pady=4, cursor="hand2")
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda e, t=tag_str: self._copy_tag(t))
            tk.Label(row, text="click to copy",
                     font=("Consolas", 8), bg=SURFACE2, fg=MUTED,
                     anchor="e", padx=6).pack(side="right")

    def _render_fields_list(self):
        for w in self.fields_list_frame.winfo_children():
            w.destroy()
        non_core = [f for f in self.fields if f not in ("email", "first_name", "last_name", "company")]
        for field in non_core:
            row = tk.Frame(self.fields_list_frame, bg=SURFACE)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"  {field}", font=FONT_SMALL,
                     bg=SURFACE, fg=TEXT).pack(side="left")
            tk.Button(row, text="✕", font=FONT_SMALL,
                      bg=SURFACE, fg=RED, relief="flat",
                      activebackground=SURFACE2, cursor="hand2",
                      command=lambda f=field: self._remove_field(f)).pack(side="right")

    def _add_field(self):
        raw  = self.new_field_var.get().strip()
        name = re.sub(r'[^a-z0-9_]', '', raw.lower().replace(" ", "_"))
        if not name or name in self.fields:
            return
        self.fields.append(name)
        for entry in self.entries:
            entry.setdefault(name, "")
        self.new_field_var.set("")
        self._render_field_inputs()
        self._render_fields_list()
        self._render_tag_reference()
        self._update_bulk_hint()
        self._refresh_table()

    def _remove_field(self, field):
        if field in ("email", "first_name", "last_name", "company"):
            return
        self.fields.remove(field)
        self._render_field_inputs()
        self._render_fields_list()
        self._render_tag_reference()
        self._update_bulk_hint()
        self._refresh_table()

    # ── Entry management ──────────────────────────────────────────────────────
    def _add_entry(self):
        values = {f: self.field_vars[f].get().strip() for f in self.fields}
        email = values.get("email", "")
        if not email:
            messagebox.showwarning("Missing email", "Email field is required.")
            return
        if any(e["email"].lower() == email.lower() for e in self.entries):
            messagebox.showwarning("Duplicate", f"{email} is already in the list.")
            return
        self.entries.append(values)
        for var in self.field_vars.values():
            var.set("")
        self._refresh_table()

    def _update_bulk_hint(self):
        custom = [f for f in self.fields if f not in ("email", "first_name", "last_name", "company")]
        col_order = ["email", "first_name", "last_name", "company"] + custom
        hint = "Each entry = 1 line (long lines wrap visually but stay 1 entry)\n"
        hint += "Separate fields with commas or tabs:  " + " | ".join(col_order)
        self.bulk_hint.config(text=hint)

    def _parse_bulk(self):
        raw   = self.bulk_text.get("1.0", "end")
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        added = dupes = skipped = 0
        core   = ("email", "first_name", "last_name", "company")
        custom_fields = [f for f in self.fields if f not in core]

        for line in lines:
            em_match = re.search(r"[^\s@,;<>\"']+@[^\s@,;<>\"']+\.[^\s@,;<>\"']+", line)
            if not em_match:
                skipped += 1
                continue
            email = em_match.group(0).strip()

            if any(e["email"].lower() == email.lower() for e in self.entries):
                dupes += 1
                continue

            tokens = [t.strip().strip("\"'") for t in re.split(r"[,;\t]+", line)]
            other_tokens = [t for t in tokens if t.lower() != email.lower()]

            row = {f: "" for f in self.fields}
            row["email"] = email

            if other_tokens:
                # if first token looks like "First Last" (single token, space inside), split it
                name_token = other_tokens[0]
                name_parts = name_token.split()
                if len(name_parts) >= 2 and "first_name" in self.fields and "last_name" in self.fields:
                    row["first_name"] = name_parts[0]
                    row["last_name"]  = " ".join(name_parts[1:])
                elif "first_name" in self.fields:
                    row["first_name"] = name_token
                remaining = other_tokens[1:]
            else:
                remaining = []

            # map remaining tokens to: company first, then custom fields
            extra_fields = (["company"] if "company" in self.fields else []) + custom_fields
            for i, cf in enumerate(extra_fields):
                row[cf] = remaining[i] if i < len(remaining) else ""

            self.entries.append(row)
            added += 1

        msg = f"Added {added}"
        if dupes:   msg += f" • Skipped {dupes} duplicate(s)"
        if skipped: msg += f" • {skipped} line(s) had no email"
        self.bulk_status.config(text=msg, fg=ACCENT if added else YELLOW)
        self._refresh_table()

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        idx = self.tree.index(iid)
        del self.entries[idx]
        self._refresh_table()

    def _edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx     = self.tree.index(sel[0])
        entry   = self.entries[idx]

        dlg = tk.Toplevel(self)
        dlg.title("Edit Entry")
        dlg.configure(bg=SURFACE)
        dlg.resizable(False, False)
        dlg.grab_set()

        # centre over main window
        self.update_idletasks()
        x = self.winfo_x() + self.winfo_width()  // 2 - 200
        y = self.winfo_y() + self.winfo_height() // 2 - 160
        dlg.geometry(f"400x{60 + len(self.fields)*46}+{x}+{y}")

        tk.Label(dlg, text="EDIT ENTRY", font=FONT_BOLD,
                 bg=SURFACE, fg=ACCENT, pady=10, padx=16, anchor="w").pack(fill="x")
        tk.Frame(dlg, bg=BORDER, height=1).pack(fill="x")

        form = tk.Frame(dlg, bg=SURFACE, padx=16, pady=12)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        edit_vars = {}
        for i, field in enumerate(self.fields):
            tk.Label(form, text=field.upper(), font=FONT_SMALL,
                     bg=SURFACE, fg=MUTED, anchor="w",
                     width=10).grid(row=i, column=0, sticky="w", pady=5)
            var = tk.StringVar(value=entry.get(field, ""))
            edit_vars[field] = var
            e = tk.Entry(form, textvariable=var, font=FONT_SMALL,
                          bg=SURFACE2, fg=TEXT, insertbackground=ACCENT,
                          relief="flat", bd=0, highlightthickness=1,
                          highlightbackground=BORDER, highlightcolor=ACCENT)
            e.grid(row=i, column=1, sticky="ew", ipady=5, padx=(8, 0), pady=5)

        err_lbl = tk.Label(dlg, text="", font=FONT_SMALL,
                            bg=SURFACE, fg=RED, padx=16, anchor="w")
        err_lbl.pack(fill="x")

        def save():
            new_email = edit_vars["email"].get().strip()
            if not new_email:
                err_lbl.config(text="Email cannot be empty.")
                return
            # dupe check — allow keeping same email
            for j, e in enumerate(self.entries):
                if j != idx and e["email"].lower() == new_email.lower():
                    err_lbl.config(text=f"{new_email} already exists.")
                    return
            for field in self.fields:
                self.entries[idx][field] = edit_vars[field].get().strip()
            self._refresh_table()
            dlg.destroy()

        tk.Frame(dlg, bg=BORDER, height=1).pack(fill="x")
        btn_row = tk.Frame(dlg, bg=SURFACE, padx=16, pady=10)
        btn_row.pack(fill="x")
        tk.Button(btn_row, text="Cancel", font=FONT_SMALL,
                  bg=SURFACE2, fg=MUTED, relief="flat",
                  activebackground=BORDER, cursor="hand2",
                  command=dlg.destroy).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="Save", font=FONT_BOLD,
                  bg=ACCENT, fg=BG, relief="flat",
                  activebackground=ACCENT_D, cursor="hand2",
                  padx=16, pady=4,
                  command=save).pack(side="right")

    def _clear_all(self):
        if not self.entries:
            return
        if messagebox.askyesno("Clear all", "Remove all entries?"):
            self.entries.clear()
            self._refresh_table()

    # ── Table refresh ─────────────────────────────────────────────────────────
    def _refresh_table(self):
        # rebuild columns
        self.tree["columns"] = self.fields
        for f in self.fields:
            self.tree.heading(f, text=f.upper())
            self.tree.column(f, width=160, minwidth=80, stretch=True)

        # clear rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # insert entries
        for entry in self.entries:
            vals = [entry.get(f, "") for f in self.fields]
            tag  = "valid" if is_valid_email(entry.get("email", "")) else "invalid"
            self.tree.insert("", "end", values=vals, tags=(tag,))

        # stats
        total   = len(self.entries)
        valid   = sum(1 for e in self.entries if is_valid_email(e.get("email", "")))
        invalid = total - valid
        self.lbl_total.config(text=str(total))
        self.lbl_valid.config(text=str(valid), fg=ACCENT if valid else TEXT)
        self.lbl_invalid.config(text=str(invalid), fg=RED if invalid else TEXT)


    # ── Save session ──────────────────────────────────────────────────────────
    def _save_session(self):
        """Save full session as CSV (all fields, including custom). Reloadable."""
        if not self.entries:
            messagebox.showwarning("Nothing to save", "No entries to save.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="session.csv",
            title="Save session"
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self.entries)
        messagebox.showinfo("Saved",
                             f"Session saved ({len(self.entries)} entries):\n{os.path.basename(path)}")

    # ── Load CSV ──────────────────────────────────────────────────────────────
    def _load_csv(self):
        """Load a CSV. Any columns beyond email/name become custom fields."""
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Load CSV"
        )
        if not path:
            return

        try:
            with open(path, newline="", encoding="utf-8-sig") as fh:
                reader = csv.DictReader(fh)
                if not reader.fieldnames:
                    messagebox.showerror("Load failed", "CSV has no headers.")
                    return

                # normalise header names
                csv_fields = [f.strip().lower().replace(" ", "_")
                               for f in reader.fieldnames]

                if "email" not in csv_fields:
                    messagebox.showerror("Load failed",
                                          "CSV must have an 'email' column.")
                    return

                rows = list(reader)
        except Exception as ex:
            messagebox.showerror("Load failed", str(ex))
            return

        if not rows:
            messagebox.showwarning("Empty file", "The CSV has no data rows.")
            return

        # ask: replace or append?
        mode = "replace"
        if self.entries:
            ans = messagebox.askyesnocancel(
                "Load CSV",
                f"You have {len(self.entries)} existing entries.\n\n"
                "Yes  = Replace all\n"
                "No   = Append / merge\n"
                "Cancel = Abort"
            )
            if ans is None:
                return
            mode = "replace" if ans else "append"

        # discover any new custom fields in the CSV
        new_fields = [f for f in csv_fields if f not in self.fields]
        for nf in new_fields:
            self.fields.append(nf)
            for existing in self.entries:
                existing.setdefault(nf, "")

        if mode == "replace":
            self.entries.clear()

        added = dupes = 0
        for raw_row in rows:
            # remap headers to normalised names
            row = {f.strip().lower().replace(" ", "_"): v.strip()
                   for f, v in raw_row.items()}
            email = row.get("email", "").strip()
            if not email:
                continue
            if any(e["email"].lower() == email.lower() for e in self.entries):
                dupes += 1
                continue
            entry = {f: row.get(f, "") for f in self.fields}
            self.entries.append(entry)
            added += 1

        # rebuild UI to reflect any new fields
        self._render_field_inputs()
        self._render_fields_list()
        self._render_tag_reference()
        self._update_bulk_hint()
        self._refresh_table()

        msg = f"Loaded {added} entries"
        if new_fields:
            msg += f"\nNew fields added: {', '.join(new_fields)}"
        if dupes:
            msg += f"\nSkipped {dupes} duplicate(s)"
        messagebox.showinfo("Loaded", msg)

    # ── Export ────────────────────────────────────────────────────────────────
    def _export_csv(self):
        if not self.entries:
            messagebox.showwarning("Nothing to export", "Add some entries first.")
            return
        rows = self.entries
        if self.skip_invalid_var.get():
            rows = [e for e in rows if is_valid_email(e.get("email", ""))]
        if not rows:
            messagebox.showwarning("Nothing to export",
                                    "No valid emails to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="emails.csv",
            title="Save CSV as"
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.fields,
                                     extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        messagebox.showinfo("Exported",
                             f"Saved {len(rows)} entries to:\n{os.path.basename(path)}")


if __name__ == "__main__":
    app = CSVMaker()
    app.mainloop()
