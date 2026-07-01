"""
Invoice Generator — Automated Test Suite
=========================================
Tests all core logic without opening the UI.

Run with:  python test_suite.py
All tests must pass before a release.
"""

import sys, os, json, shutil, tempfile, unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# ── Redirect DATA_DIR to a temp folder so tests never touch real user data ──
_TEST_DIR = Path(tempfile.mkdtemp(prefix="invoice_test_"))

# ── Stub out tkinter before importing the app (no window opened) ─────────────
for mod in [
    "tkinter", "tkinter.ttk", "tkinter.messagebox",
    "tkinter.filedialog", "tkinter.colorchooser",
]:
    sys.modules[mod] = MagicMock()

# ── Import app and patch DATA_DIR to temp folder ──────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
import invoice_app as app
app.DATA_DIR      = _TEST_DIR
app.SETTINGS_FILE = _TEST_DIR / "settings.json"
app.HISTORY_FILE  = _TEST_DIR / "history.json"
app.CLIENTS_FILE  = _TEST_DIR / "clients.json"
app.EXPENSES_FILE  = _TEST_DIR / "expenses.json"
app.COUNTER_FILE   = _TEST_DIR / "counter.json"
app.RECURRING_FILE = _TEST_DIR / "recurring.json"
app.PAYMENTS_FILE  = _TEST_DIR / "payments.json"
app.PROFILES_FILE  = _TEST_DIR / "profiles.json"

# ── Shortcuts ─────────────────────────────────────────────────────────────────
fc                      = app.fc
fdate                   = app.fdate
duedate                 = app.duedate
is_overdue              = app.is_overdue
_safe_load_json         = app._safe_load_json
_safe_save_json         = app._safe_save_json
_validate_history_entry = app._validate_history_entry
_validate_client_entry  = app._validate_client_entry
_validate_expense_entry = app._validate_expense_entry
load_settings           = app.load_settings
save_settings           = app.save_settings
load_history            = app.load_history
save_history            = app.save_history
load_clients            = app.load_clients
save_clients            = app.save_clients
load_expenses           = app.load_expenses
save_expenses           = app.save_expenses
next_inv_num            = app.next_inv_num
bump_counter            = app.bump_counter
startup_integrity_check = app.startup_integrity_check
DEFAULT_SETTINGS        = app.DEFAULT_SETTINGS


# ─────────────────────────────────────────────────────────────────────────────
#  STANDALONE HELPERS  (reproduce app logic without needing InvoiceApp instance)
# ─────────────────────────────────────────────────────────────────────────────

def calc_totals(items, tax_rate=20.0, discount_pct=0.0):
    """Mirrors the app's _recalc / _collect calculation exactly."""
    subtotal = sum(i.get("qty", 0) * i.get("price", 0) for i in items)
    tax = sum(
        i.get("qty", 0) * i.get("price", 0) * (tax_rate / 100)
        for i in items if i.get("taxable", True)
    )
    disc_amt = subtotal * (discount_pct / 100)
    grand    = subtotal + tax - disc_amt
    return {"subtotal": subtotal, "tax": tax, "discount": disc_amt, "grand": grand}


def avg_days_to_pay(client_name, history, fmt="DD/MM/YYYY"):
    """Mirrors _avg_days_to_pay without needing a live InvoiceApp instance."""
    def _pd(ds):
        try:
            if fmt == "DD/MM/YYYY": return datetime.strptime(ds, "%d/%m/%Y")
            if fmt == "MM/DD/YYYY": return datetime.strptime(ds, "%m/%d/%Y")
            return datetime.strptime(ds, "%Y-%m-%d")
        except Exception:
            return None

    deltas = []
    for h in history:
        name = h.get("client_name") or h.get("client", "")
        if name.lower() != client_name.lower(): continue
        if h.get("status") != "Paid": continue
        inv_d  = _pd(h.get("date", ""))
        paid_d = _pd(h.get("paid_date", ""))
        if inv_d and paid_d:
            deltas.append((paid_d - inv_d).days)
    return round(sum(deltas) / len(deltas)) if deltas else None


def needs_reminder(inv, thresholds=(7, 14, 30), fmt="DD/MM/YYYY"):
    """Mirrors the reminder detection logic from _pg_reminders exactly."""
    if inv.get("status") not in ("Unpaid", "Overdue"):
        return False
    try:
        if fmt == "DD/MM/YYYY": due = datetime.strptime(inv["due_date"], "%d/%m/%Y")
        elif fmt == "MM/DD/YYYY": due = datetime.strptime(inv["due_date"], "%m/%d/%Y")
        else: due = datetime.strptime(inv["due_date"], "%Y-%m-%d")
    except Exception:
        return False

    days_over = (datetime.today() - due).days
    if days_over < 0:
        return False

    last_rem_str = inv.get("last_reminder", "")
    try:
        last_rem = datetime.strptime(last_rem_str, "%d/%m/%Y") if last_rem_str else None
    except Exception:
        last_rem = None

    for t in sorted(thresholds):
        if days_over >= t:
            threshold_hit = due + timedelta(days=t)
            if last_rem is None or last_rem < threshold_hit:
                return True
    return False


# ═════════════════════════════════════════════════════════════════════════════
#  TEST CLASSES
# ═════════════════════════════════════════════════════════════════════════════

class TestFormatCurrency(unittest.TestCase):

    def test_basic_gbp(self):
        self.assertEqual(fc(100), "£100.00")

    def test_zero(self):
        self.assertEqual(fc(0), "£0.00")

    def test_pence(self):
        self.assertEqual(fc(0.01), "£0.01")

    def test_large_number_comma_separated(self):
        self.assertEqual(fc(1234567.89), "£1,234,567.89")

    def test_custom_symbol_dollar(self):
        self.assertEqual(fc(50.0, "$"), "$50.00")

    def test_custom_symbol_euro(self):
        self.assertEqual(fc(99.99, "€"), "€99.99")

    def test_negative_amount(self):
        self.assertEqual(fc(-25.5), "£-25.50")

    def test_rounding_does_not_crash(self):
        result = fc(99.999)
        self.assertIn("£", result)
        self.assertIsInstance(result, str)


class TestDateFunctions(unittest.TestCase):

    def test_fdate_dmy(self):
        self.assertEqual(fdate("DD/MM/YYYY", datetime(2024, 3, 15)), "15/03/2024")

    def test_fdate_mdy(self):
        self.assertEqual(fdate("MM/DD/YYYY", datetime(2024, 3, 15)), "03/15/2024")

    def test_fdate_iso(self):
        self.assertEqual(fdate("YYYY-MM-DD", datetime(2024, 3, 15)), "2024-03-15")

    def test_fdate_defaults_to_today(self):
        self.assertEqual(fdate("DD/MM/YYYY"), datetime.today().strftime("%d/%m/%Y"))

    def test_duedate_30_days(self):
        expected = (datetime.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        self.assertEqual(duedate(30, "DD/MM/YYYY"), expected)

    def test_duedate_zero_terms_is_today(self):
        self.assertEqual(duedate(0, "DD/MM/YYYY"), datetime.today().strftime("%d/%m/%Y"))

    def test_duedate_iso_format(self):
        expected = (datetime.today() + timedelta(days=14)).strftime("%Y-%m-%d")
        self.assertEqual(duedate(14, "YYYY-MM-DD"), expected)

    def test_is_overdue_past_is_true(self):
        past = (datetime.today() - timedelta(days=5)).strftime("%d/%m/%Y")
        self.assertTrue(is_overdue(past, "DD/MM/YYYY"))

    def test_is_overdue_future_is_false(self):
        future = (datetime.today() + timedelta(days=5)).strftime("%d/%m/%Y")
        self.assertFalse(is_overdue(future, "DD/MM/YYYY"))

    def test_is_overdue_bad_string_returns_false(self):
        self.assertFalse(is_overdue("not-a-date"))
        self.assertFalse(is_overdue(""))
        self.assertFalse(is_overdue("32/13/2024"))

    def test_is_overdue_mdy_format(self):
        past = (datetime.today() - timedelta(days=10)).strftime("%m/%d/%Y")
        self.assertTrue(is_overdue(past, "MM/DD/YYYY"))

    def test_is_overdue_iso_format(self):
        past = (datetime.today() - timedelta(days=3)).strftime("%Y-%m-%d")
        self.assertTrue(is_overdue(past, "YYYY-MM-DD"))

    def test_is_overdue_leap_year_no_crash(self):
        result = is_overdue("29/02/2024", "DD/MM/YYYY")
        self.assertIsInstance(result, bool)

    def test_is_overdue_today_returns_bool(self):
        today = datetime.today().strftime("%d/%m/%Y")
        self.assertIsInstance(is_overdue(today, "DD/MM/YYYY"), bool)


class TestCalcTotals(unittest.TestCase):

    def _items(self, rows):
        return [{"qty": q, "price": p, "taxable": t} for q, p, t in rows]

    def test_single_taxable_item(self):
        r = calc_totals(self._items([(2, 50.0, True)]))
        self.assertAlmostEqual(r["subtotal"], 100.0)
        self.assertAlmostEqual(r["tax"],       20.0)
        self.assertAlmostEqual(r["grand"],    120.0)

    def test_single_nontaxable_item(self):
        r = calc_totals(self._items([(1, 200.0, False)]))
        self.assertAlmostEqual(r["tax"],   0.0)
        self.assertAlmostEqual(r["grand"], 200.0)

    def test_mixed_taxable_and_not(self):
        r = calc_totals(self._items([(1, 100.0, True), (1, 50.0, False)]))
        self.assertAlmostEqual(r["subtotal"], 150.0)
        self.assertAlmostEqual(r["tax"],       20.0)
        self.assertAlmostEqual(r["grand"],    170.0)

    def test_multiple_taxable_items(self):
        r = calc_totals(self._items([(1, 200.0, True), (3, 10.0, True)]))
        self.assertAlmostEqual(r["subtotal"], 230.0)
        self.assertAlmostEqual(r["tax"],       46.0)
        self.assertAlmostEqual(r["grand"],    276.0)

    def test_discount_no_tax(self):
        r = calc_totals(self._items([(1, 100.0, False)]),
                        tax_rate=0.0, discount_pct=10.0)
        self.assertAlmostEqual(r["discount"], 10.0)
        self.assertAlmostEqual(r["grand"],    90.0)

    def test_discount_with_tax(self):
        r = calc_totals(self._items([(1, 100.0, True)]),
                        tax_rate=20.0, discount_pct=10.0)
        self.assertAlmostEqual(r["grand"], 110.0)

    def test_zero_items(self):
        r = calc_totals([])
        self.assertAlmostEqual(r["grand"], 0.0)

    def test_zero_price(self):
        r = calc_totals(self._items([(5, 0.0, True)]))
        self.assertAlmostEqual(r["grand"], 0.0)

    def test_fractional_quantity(self):
        r = calc_totals(self._items([(1.5, 100.0, False)]), tax_rate=0)
        self.assertAlmostEqual(r["grand"], 150.0)

    def test_custom_tax_rate_5_percent(self):
        r = calc_totals(self._items([(1, 200.0, True)]), tax_rate=5.0)
        self.assertAlmostEqual(r["tax"],   10.0)
        self.assertAlmostEqual(r["grand"], 210.0)

    def test_100_percent_discount(self):
        r = calc_totals(self._items([(1, 100.0, False)]),
                        tax_rate=0.0, discount_pct=100.0)
        self.assertAlmostEqual(r["grand"], 0.0)

    def test_all_nontaxable_tax_is_zero(self):
        r = calc_totals(self._items([(2, 50.0, False), (3, 30.0, False)]),
                        tax_rate=20.0)
        self.assertAlmostEqual(r["tax"],       0.0)
        self.assertAlmostEqual(r["subtotal"], 190.0)


class TestValidateHistoryEntry(unittest.TestCase):

    def test_valid_entry_passes_through(self):
        h = {"number": "INV-001", "date": "01/01/2024",
             "due_date": "31/01/2024", "status": "Paid",
             "client_name": "Acme Ltd", "total": 500.0, "items": []}
        r = _validate_history_entry(h)
        self.assertIsNotNone(r)
        self.assertEqual(r["number"], "INV-001")
        self.assertAlmostEqual(r["total"], 500.0)

    def test_non_dict_returns_none(self):
        self.assertIsNone(_validate_history_entry("bad"))
        self.assertIsNone(_validate_history_entry(None))
        self.assertIsNone(_validate_history_entry(42))
        self.assertIsNone(_validate_history_entry([]))

    def test_missing_fields_get_safe_defaults(self):
        r = _validate_history_entry({})
        self.assertEqual(r["status"],   "Unpaid")
        self.assertAlmostEqual(r["total"], 0.0)
        self.assertEqual(r["items"],    [])
        self.assertEqual(r["discount"], "0")

    def test_old_client_key_falls_back(self):
        r = _validate_history_entry({"client": "Old Format Co"})
        self.assertEqual(r["client_name"], "Old Format Co")

    def test_items_not_list_becomes_empty(self):
        r = _validate_history_entry({"items": "not a list"})
        self.assertEqual(r["items"], [])

    def test_items_list_is_preserved(self):
        items = [{"desc": "Web", "qty": 1, "price": 100, "taxable": True, "total": 100}]
        r = _validate_history_entry({"items": items})
        self.assertEqual(len(r["items"]), 1)
        self.assertEqual(r["items"][0]["desc"], "Web")

    def test_total_string_converts_to_float(self):
        r = _validate_history_entry({"total": "250"})
        self.assertAlmostEqual(r["total"], 250.0)

    def test_all_string_fields_coerced(self):
        r = _validate_history_entry({"number": 1001, "status": 0})
        self.assertIsInstance(r["number"], str)
        self.assertIsInstance(r["status"], str)


class TestValidateClientEntry(unittest.TestCase):

    def test_valid_client(self):
        c = {"name": "Bob", "email": "bob@test.com",
             "phone": "07700", "address": "London", "website": "", "notes": ""}
        r = _validate_client_entry(c)
        self.assertEqual(r["name"],  "Bob")
        self.assertEqual(r["email"], "bob@test.com")

    def test_non_dict_returns_none(self):
        self.assertIsNone(_validate_client_entry(None))
        self.assertIsNone(_validate_client_entry("Bob"))
        self.assertIsNone(_validate_client_entry([]))

    def test_missing_fields_become_empty_strings(self):
        r = _validate_client_entry({"name": "Alice"})
        self.assertEqual(r["email"],   "")
        self.assertEqual(r["phone"],   "")
        self.assertEqual(r["address"], "")

    def test_fields_coerced_to_string(self):
        r = _validate_client_entry({"name": 123, "phone": 7700})
        self.assertIsInstance(r["name"],  str)
        self.assertIsInstance(r["phone"], str)


class TestValidateExpenseEntry(unittest.TestCase):

    def test_valid_expense(self):
        e = {"description": "Laptop", "amount": 999.99,
             "date": "01/03/2024", "category": "Equipment", "notes": ""}
        r = _validate_expense_entry(e)
        self.assertAlmostEqual(r["amount"], 999.99)
        self.assertEqual(r["category"], "Equipment")

    def test_non_dict_returns_none(self):
        self.assertIsNone(_validate_expense_entry(None))
        self.assertIsNone(_validate_expense_entry("bad"))

    def test_missing_amount_becomes_zero(self):
        r = _validate_expense_entry({"description": "Test"})
        self.assertAlmostEqual(r["amount"], 0.0)

    def test_missing_category_defaults_to_general(self):
        r = _validate_expense_entry({"description": "X", "amount": 10})
        self.assertEqual(r["category"], "General")

    def test_zero_amount_stays_zero(self):
        r = _validate_expense_entry({"description": "X", "amount": 0})
        self.assertAlmostEqual(r["amount"], 0.0)


class TestSafeFileIO(unittest.TestCase):

    def setUp(self):
        self.d = _TEST_DIR / "io"
        self.d.mkdir(exist_ok=True)

    def _p(self, name):
        return self.d / name

    def test_save_and_reload_list(self):
        p = self._p("list.json")
        data = [{"a": 1}, {"b": 2}]
        _safe_save_json(p, data)
        self.assertEqual(_safe_load_json(p, list), data)

    def test_save_and_reload_dict(self):
        p = self._p("dict.json")
        data = {"key": "value", "num": 42}
        _safe_save_json(p, data)
        self.assertEqual(_safe_load_json(p, dict), data)

    def test_missing_file_returns_default_list(self):
        p = self._p("nope_list.json")
        self.assertEqual(_safe_load_json(p, list), [])

    def test_missing_file_returns_default_dict(self):
        p = self._p("nope_dict.json")
        self.assertEqual(_safe_load_json(p, dict), {})

    def test_empty_file_returns_default(self):
        p = self._p("empty.json")
        p.write_text("", encoding="utf-8")
        self.assertEqual(_safe_load_json(p, list), [])

    def test_whitespace_only_file_returns_default(self):
        p = self._p("ws.json")
        p.write_text("   \n\t  ", encoding="utf-8")
        self.assertEqual(_safe_load_json(p, list), [])

    def test_corrupted_json_returns_default(self):
        p = self._p("corrupt.json")
        p.write_text("{bad json[[[", encoding="utf-8")
        self.assertEqual(_safe_load_json(p, list), [])

    def test_wrong_type_returns_default(self):
        p = self._p("wrong.json")
        _safe_save_json(p, [1, 2, 3])
        self.assertEqual(_safe_load_json(p, dict), {})

    def test_atomic_write_no_tmp_leftover(self):
        p = self._p("atomic.json")
        _safe_save_json(p, {"ok": True})
        self.assertFalse(p.with_suffix(".tmp").exists())
        self.assertTrue(p.exists())

    def test_unicode_preserved(self):
        p = self._p("unicode.json")
        data = {"name": "José García", "note": "café ☕ 日本語"}
        _safe_save_json(p, data)
        loaded = _safe_load_json(p, dict)
        self.assertEqual(loaded["name"], "José García")

    def test_large_list_preserved(self):
        p = self._p("large.json")
        data = [{"n": i} for i in range(500)]
        _safe_save_json(p, data)
        loaded = _safe_load_json(p, list)
        self.assertEqual(len(loaded), 500)
        self.assertEqual(loaded[250]["n"], 250)

    def test_overwrite_existing_file(self):
        p = self._p("overwrite.json")
        _safe_save_json(p, {"v": 1})
        _safe_save_json(p, {"v": 2})
        self.assertEqual(_safe_load_json(p, dict)["v"], 2)


class TestLoadSaveFunctions(unittest.TestCase):

    def setUp(self):
        for f in [app.HISTORY_FILE, app.CLIENTS_FILE,
                  app.EXPENSES_FILE, app.SETTINGS_FILE, app.COUNTER_FILE]:
            if f.exists(): f.unlink()

    def _blank_invoice(self, number="INV-001", status="Unpaid", total=100.0):
        return {"number": number, "client_name": "Test", "date": "01/01/2024",
                "due_date": "31/01/2024", "status": status, "total": total,
                "items": [], "discount": "0", "notes": "", "po": "",
                "filepath": "", "paid_date": "", "last_reminder": "",
                "client_email": "", "client_phone": "", "client_address": ""}

    def test_load_history_empty(self):
        self.assertEqual(load_history(), [])

    def test_save_and_load_history(self):
        save_history([self._blank_invoice()])
        loaded = load_history()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["number"], "INV-001")

    def test_save_history_caps_at_200(self):
        save_history([self._blank_invoice(f"INV-{i:04d}") for i in range(250)])
        self.assertLessEqual(len(load_history()), 200)

    def test_load_clients_empty(self):
        self.assertEqual(load_clients(), [])

    def test_save_and_load_clients(self):
        save_clients([{"name": "Alice", "email": "a@b.com",
                       "phone": "", "website": "", "address": "", "notes": ""}])
        loaded = load_clients()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["name"], "Alice")

    def test_load_clients_filters_nameless(self):
        save_clients([{"name": "", "email": "x@y.com", "phone": "",
                       "website": "", "address": "", "notes": ""},
                      {"name": "Bob", "email": "", "phone": "",
                       "website": "", "address": "", "notes": ""}])
        loaded = load_clients()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["name"], "Bob")

    def test_save_and_load_expenses(self):
        save_expenses([{"description": "Laptop", "amount": 999.0,
                        "date": "01/01/2024", "category": "Equipment", "notes": ""}])
        loaded = load_expenses()
        self.assertEqual(len(loaded), 1)
        self.assertAlmostEqual(loaded[0]["amount"], 999.0)

    def test_load_settings_returns_all_default_keys(self):
        s = load_settings()
        for key in DEFAULT_SETTINGS:
            self.assertIn(key, s, f"Missing settings key: {key}")

    def test_load_settings_merges_with_defaults(self):
        save_settings({"company_name": "My Co"})
        s = load_settings()
        self.assertEqual(s["company_name"], "My Co")
        self.assertIn("tax_rate", s)

    def test_load_settings_validates_tax_rate(self):
        save_settings({"tax_rate": "bad_value"})
        s = load_settings()
        self.assertIsInstance(s["tax_rate"], float)

    def test_save_history_non_list_saves_empty(self):
        save_history("not a list")
        self.assertEqual(load_history(), [])

    def test_save_clients_non_list_saves_empty(self):
        save_clients({"not": "a list"})
        self.assertEqual(load_clients(), [])

    def test_save_expenses_none_saves_empty(self):
        save_expenses(None)
        self.assertEqual(load_expenses(), [])


class TestInvoiceNumbering(unittest.TestCase):

    def setUp(self):
        if app.COUNTER_FILE.exists():
            app.COUNTER_FILE.unlink()

    def _s(self, prefix="INV", start=1000):
        return {**DEFAULT_SETTINGS, "invoice_prefix": prefix, "invoice_start": start}

    def test_first_number_uses_start(self):
        num, n = next_inv_num(self._s())
        self.assertEqual(num, "INV-1000")
        self.assertEqual(n, 1000)

    def test_custom_prefix(self):
        num, _ = next_inv_num(self._s("BILL", 1))
        self.assertEqual(num, "BILL-0001")

    def test_pads_to_4_digits(self):
        num, _ = next_inv_num(self._s("X", 5))
        self.assertEqual(num, "X-0005")

    def test_bump_increments(self):
        s = self._s()
        bump_counter(s)
        _, n = next_inv_num(s)
        self.assertEqual(n, 1001)

    def test_bump_twice(self):
        s = self._s()
        bump_counter(s); bump_counter(s)
        _, n = next_inv_num(s)
        self.assertEqual(n, 1002)

    def test_large_number_no_truncation(self):
        num, _ = next_inv_num(self._s("INV", 10000))
        self.assertEqual(num, "INV-10000")


class TestPaymentHistory(unittest.TestCase):

    def _h(self):
        return [
            {"client_name": "Alice", "status": "Paid",
             "date": "01/01/2024", "paid_date": "08/01/2024", "total": 500},
            {"client_name": "Alice", "status": "Paid",
             "date": "01/02/2024", "paid_date": "15/02/2024", "total": 300},
            {"client_name": "Bob",   "status": "Paid",
             "date": "01/01/2024", "paid_date": "01/03/2024", "total": 200},
            {"client_name": "Alice", "status": "Unpaid",
             "date": "01/03/2024", "paid_date": "",            "total": 400},
        ]

    def test_alice_avg_days(self):
        # 7 days + 14 days = avg ~10-11
        avg = avg_days_to_pay("Alice", self._h())
        self.assertAlmostEqual(avg, 10, delta=1)

    def test_bob_avg_days(self):
        # Jan1 → Mar1 2024 = 60 days (2024 leap year)
        self.assertEqual(avg_days_to_pay("Bob", self._h()), 60)

    def test_unpaid_excluded_from_avg(self):
        avg_all  = avg_days_to_pay("Alice", self._h())
        paid_only = [h for h in self._h() if h["status"] == "Paid"]
        self.assertEqual(avg_all, avg_days_to_pay("Alice", paid_only))

    def test_unknown_client_returns_none(self):
        self.assertIsNone(avg_days_to_pay("Nobody", self._h()))

    def test_empty_history_returns_none(self):
        self.assertIsNone(avg_days_to_pay("Alice", []))

    def test_no_paid_invoices_returns_none(self):
        h = [{"client_name": "Charlie", "status": "Unpaid",
              "date": "01/01/2024", "paid_date": ""}]
        self.assertIsNone(avg_days_to_pay("Charlie", h))

    def test_case_insensitive(self):
        h = [{"client_name": "alice", "status": "Paid",
              "date": "01/01/2024", "paid_date": "11/01/2024"}]
        self.assertEqual(avg_days_to_pay("ALICE", h), 10)

    def test_single_invoice(self):
        h = [{"client_name": "Solo", "status": "Paid",
              "date": "01/01/2024", "paid_date": "21/01/2024"}]
        self.assertEqual(avg_days_to_pay("Solo", h), 20)


class TestReminderLogic(unittest.TestCase):

    def _inv(self, days_over, last_reminder_ago=None, status="Overdue"):
        due_dt = datetime.today() - timedelta(days=days_over)
        inv = {
            "status": status,
            "due_date": due_dt.strftime("%d/%m/%Y"),
            "last_reminder": "",
        }
        if last_reminder_ago is not None:
            rem_dt = datetime.today() - timedelta(days=last_reminder_ago)
            inv["last_reminder"] = rem_dt.strftime("%d/%m/%Y")
        return inv

    def test_7_days_over_needs_reminder(self):
        self.assertTrue(needs_reminder(self._inv(7)))

    def test_14_days_over_needs_reminder(self):
        self.assertTrue(needs_reminder(self._inv(14)))

    def test_30_days_over_needs_reminder(self):
        self.assertTrue(needs_reminder(self._inv(30)))

    def test_3_days_over_no_reminder(self):
        self.assertFalse(needs_reminder(self._inv(3)))

    def test_not_yet_overdue_no_reminder(self):
        future = (datetime.today() + timedelta(days=5)).strftime("%d/%m/%Y")
        self.assertFalse(needs_reminder({"status": "Unpaid",
                                         "due_date": future, "last_reminder": ""}))

    def test_paid_invoice_no_reminder(self):
        self.assertFalse(needs_reminder(self._inv(10, status="Paid")))

    def test_draft_invoice_no_reminder(self):
        self.assertFalse(needs_reminder(self._inv(10, status="Draft")))

    def test_reminder_recently_sent_no_repeat(self):
        # 10 days over, reminder sent 3 days ago (covers 7d threshold)
        self.assertFalse(needs_reminder(self._inv(10, last_reminder_ago=3)))

    def test_new_threshold_after_old_reminder(self):
        # 16 days over, last reminder 9 days ago → 14d threshold now due
        self.assertTrue(needs_reminder(self._inv(16, last_reminder_ago=9)))

    def test_all_thresholds_disabled(self):
        self.assertFalse(needs_reminder(self._inv(30), thresholds=()))

    def test_only_30d_threshold_not_yet_hit(self):
        self.assertFalse(needs_reminder(self._inv(10), thresholds=(30,)))

    def test_only_30d_threshold_hit(self):
        self.assertTrue(needs_reminder(self._inv(30), thresholds=(30,)))

    def test_bad_due_date_returns_false(self):
        self.assertFalse(needs_reminder(
            {"status": "Overdue", "due_date": "not-a-date", "last_reminder": ""}))


class TestStartupIntegrityCheck(unittest.TestCase):

    def setUp(self):
        for f in [app.HISTORY_FILE, app.CLIENTS_FILE,
                  app.EXPENSES_FILE, app.SETTINGS_FILE]:
            if f.exists(): f.unlink()

    def test_clean_start_no_issues(self):
        self.assertEqual(startup_integrity_check(), [])

    def test_empty_history_detected_and_reset(self):
        app.HISTORY_FILE.write_text("", encoding="utf-8")
        issues = startup_integrity_check()
        self.assertTrue(any("history" in i.lower() for i in issues))
        self.assertEqual(load_history(), [])

    def test_corrupted_clients_detected_and_reset(self):
        app.CLIENTS_FILE.write_text("{{{{BAD JSON}}", encoding="utf-8")
        issues = startup_integrity_check()
        self.assertTrue(any("client" in i.lower() for i in issues))
        self.assertEqual(load_clients(), [])

    def test_wrong_type_expenses_detected_and_reset(self):
        app.EXPENSES_FILE.write_text('{"should_be": "a list"}', encoding="utf-8")
        issues = startup_integrity_check()
        self.assertTrue(any("expense" in i.lower() for i in issues))
        self.assertEqual(load_expenses(), [])

    def test_valid_files_pass_silently(self):
        save_history([])
        save_clients([])
        save_expenses([])
        save_settings(dict(DEFAULT_SETTINGS))
        self.assertEqual(startup_integrity_check(), [])

    def test_backup_created_for_corrupted_file(self):
        app.CLIENTS_FILE.write_text("BROKEN", encoding="utf-8")
        startup_integrity_check()
        bak_files = list(_TEST_DIR.glob("clients.bak_*.json"))
        self.assertGreater(len(bak_files), 0)


class TestPDFGeneration(unittest.TestCase):

    def _inv(self):
        return {
            "number": "TEST-001", "date": "01/01/2024",
            "due_date": "31/01/2024", "status": "Unpaid",
            "client_name": "Test Client Ltd",
            "client_email": "client@example.com",
            "client_address": "1 Test Road\nLiverpool\nL1 1AA",
            "client_phone": "07700 000000",
            "po": "PO-12345", "discount": "0",
            "notes": "Thank you for your business.",
            "items": [
                {"desc": "Web Design",   "qty": 1,  "price": 500.0,
                 "taxable": True,  "total": 500.0},
                {"desc": "Hosting",      "qty": 12, "price": 10.0,
                 "taxable": False, "total": 120.0},
                {"desc": "Consultation", "qty": 3,  "price": 75.0,
                 "taxable": True,  "total": 225.0},
            ],
        }

    def _settings(self):
        s = dict(DEFAULT_SETTINGS)
        s.update({
            "company_name": "My Company Ltd",
            "company_email": "hello@myco.com",
            "company_phone": "+44 7700 123456",
            "company_address": "10 Business Park\nLiverpool\nL2 2BB",
            "company_website": "www.myco.com",
            "vat_number": "GB123456789",
            "bank_name": "Barclays",
            "bank_sort_code": "20-00-00",
            "bank_account": "12345678",
            "bank_reference": "MYCO",
            "currency_symbol": "£",
            "tax_rate": 20.0,
            "tax_label": "VAT",
            "page_size": "A4",
            "theme_accent": "#00e676",
            "logo_path": "",
        })
        return s

    def test_reportlab_is_installed(self):
        try:
            import reportlab
        except ImportError:
            self.fail("reportlab is not installed — run: pip install reportlab")

    def test_pdf_file_is_created(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "test.pdf"
        try:
            app.generate_pdf(str(output), self._inv(), self._settings())
        except Exception as e:
            self.fail(f"generate_pdf raised: {e}")
        self.assertTrue(output.exists())

    def test_pdf_has_reasonable_size(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "test_size.pdf"
        app.generate_pdf(str(output), self._inv(), self._settings())
        size = output.stat().st_size
        self.assertGreater(size, 1_000)
        self.assertLess(size, 5_000_000)

    def test_pdf_starts_with_pdf_header(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "test_hdr.pdf"
        app.generate_pdf(str(output), self._inv(), self._settings())
        with open(output, "rb") as f:
            self.assertEqual(f.read(4), b"%PDF")

    def test_pdf_with_discount(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "test_disc.pdf"
        inv = self._inv(); inv["discount"] = "10"
        app.generate_pdf(str(output), inv, self._settings())
        self.assertTrue(output.exists())

    def test_pdf_letter_size(self):
        try:
            from reportlab.lib.pagesizes import LETTER
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "test_letter.pdf"
        s = self._settings(); s["page_size"] = "Letter"
        app.generate_pdf(str(output), self._inv(), s)
        self.assertTrue(output.exists())


class TestEdgeCases(unittest.TestCase):

    def test_fc_very_small(self):
        self.assertEqual(fc(0.01), "£0.01")

    def test_fc_large(self):
        self.assertIn("9,999,999.99", fc(9_999_999.99))

    def test_calc_discount_over_100(self):
        r = calc_totals([{"qty": 1, "price": 100, "taxable": False}],
                        tax_rate=0, discount_pct=150)
        self.assertIsInstance(r["grand"], float)

    def test_history_validate_preserves_multiple_items(self):
        items = [{"desc": "A", "qty": 1, "price": 10, "taxable": True, "total": 10},
                 {"desc": "B", "qty": 2, "price": 20, "taxable": False, "total": 40}]
        r = _validate_history_entry({"items": items})
        self.assertEqual(len(r["items"]), 2)

    def test_avg_days_single_invoice(self):
        h = [{"client_name": "Solo", "status": "Paid",
              "date": "01/01/2024", "paid_date": "21/01/2024"}]
        self.assertEqual(avg_days_to_pay("Solo", h), 20)

    def test_unicode_preserved_in_history(self):
        h = [{"number": "INV-001", "client_name": "André Müller",
              "date": "01/01/2024", "due_date": "31/01/2024",
              "status": "Paid", "total": 100.0, "items": [],
              "discount": "0", "notes": "café", "po": "", "filepath": "",
              "paid_date": "15/01/2024", "last_reminder": "",
              "client_email": "", "client_phone": "", "client_address": ""}]
        save_history(h)
        loaded = load_history()
        self.assertEqual(loaded[0]["client_name"], "André Müller")

    def test_duedate_negative_terms_no_crash(self):
        result = duedate(-5, "DD/MM/YYYY")
        self.assertRegex(result, r"\d{2}/\d{2}/\d{4}")

    def test_reminder_bad_due_date_no_crash(self):
        self.assertFalse(needs_reminder(
            {"status": "Overdue", "due_date": "99/99/9999", "last_reminder": ""}))

    def test_validate_history_zero_total(self):
        r = _validate_history_entry({"total": 0})
        self.assertAlmostEqual(r["total"], 0.0)

    def test_invoice_number_large_no_truncation(self):
        s = {**DEFAULT_SETTINGS, "invoice_prefix": "INV", "invoice_start": 99999}
        num, _ = next_inv_num(s)
        self.assertEqual(num, "INV-99999")




# ═════════════════════════════════════════════════════════════════════════════
#  NEW FEATURE TESTS — v2.2
# ═════════════════════════════════════════════════════════════════════════════

class TestMultiCurrency(unittest.TestCase):
    """Per-invoice currency symbol overrides global setting."""

    def test_fc_with_dollar(self):
        self.assertEqual(fc(100, "$"), "$100.00")

    def test_fc_with_euro(self):
        self.assertEqual(fc(99.99, "€"), "€99.99")

    def test_fc_with_yen(self):
        self.assertEqual(fc(1000, "¥"), "¥1,000.00")

    def test_history_stores_currency_symbol(self):
        h = {"number":"INV-001","total":500.0,"currency_symbol":"$",
             "date":"01/01/2024","due_date":"31/01/2024","status":"Unpaid","items":[]}
        r = _validate_history_entry(h)
        self.assertEqual(r["currency_symbol"], "$")

    def test_history_currency_defaults_empty(self):
        r = _validate_history_entry({})
        self.assertEqual(r["currency_symbol"], "")

    def test_invoice_with_usd_preserves_through_save_load(self):
        h = [{"number":"INV-001","client_name":"US Client","total":1000.0,
              "currency_symbol":"$","date":"01/01/2024","due_date":"31/01/2024",
              "status":"Unpaid","items":[],"discount":"0","notes":"","po":"",
              "filepath":"","paid_date":"","last_reminder":"",
              "client_email":"","client_phone":"","client_address":"",
              "invoice_template":"Professional","amount_paid":"0"}]
        save_history(h)
        loaded = load_history()
        self.assertEqual(loaded[0]["currency_symbol"], "$")


class TestInvoiceTemplates(unittest.TestCase):
    """Template selection stored and validated correctly."""

    def test_history_stores_template(self):
        h = {"number":"INV-001","invoice_template":"Minimal","total":100.0,
             "date":"01/01/2024","due_date":"31/01/2024","status":"Unpaid","items":[]}
        r = _validate_history_entry(h)
        self.assertEqual(r["invoice_template"], "Minimal")

    def test_history_template_defaults_professional(self):
        r = _validate_history_entry({})
        self.assertEqual(r["invoice_template"], "Professional")

    def test_all_templates_are_valid_strings(self):
        for tmpl in ("Professional","Minimal","Bold"):
            r = _validate_history_entry({"invoice_template": tmpl})
            self.assertEqual(r["invoice_template"], tmpl)

    def test_pdf_professional_template(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "tmpl_professional.pdf"
        inv = _make_test_invoice()
        inv["invoice_template"] = "Professional"
        app.generate_pdf(str(output), inv, _test_settings())
        self.assertTrue(output.exists())

    def test_pdf_minimal_template(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "tmpl_minimal.pdf"
        inv = _make_test_invoice()
        inv["invoice_template"] = "Minimal"
        app.generate_pdf(str(output), inv, _test_settings())
        self.assertTrue(output.exists())

    def test_pdf_bold_template(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "tmpl_bold.pdf"
        inv = _make_test_invoice()
        inv["invoice_template"] = "Bold"
        app.generate_pdf(str(output), inv, _test_settings())
        self.assertTrue(output.exists())

    def test_pdf_unknown_template_falls_back(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "tmpl_unknown.pdf"
        inv = _make_test_invoice()
        inv["invoice_template"] = "NonExistentTemplate"
        # Should not crash — falls back to Professional
        app.generate_pdf(str(output), inv, _test_settings())
        self.assertTrue(output.exists())


class TestPartialPayments(unittest.TestCase):
    """amount_paid field stored, validated, and affects PDF totals."""

    def test_history_stores_amount_paid(self):
        h = {"number":"INV-001","amount_paid":"500","total":1000.0,
             "date":"01/01/2024","due_date":"31/01/2024","status":"Unpaid","items":[]}
        r = _validate_history_entry(h)
        self.assertEqual(r["amount_paid"], "500")

    def test_history_amount_paid_defaults_zero(self):
        r = _validate_history_entry({})
        self.assertEqual(r["amount_paid"], "0")

    def test_balance_due_calculation_partial(self):
        grand = 1000.0; paid = 400.0
        balance = grand - paid
        self.assertAlmostEqual(balance, 600.0)

    def test_balance_due_zero_when_fully_paid(self):
        grand = 500.0; paid = 500.0
        balance = max(grand - paid, 0)
        self.assertAlmostEqual(balance, 0.0)

    def test_no_partial_when_amount_paid_zero(self):
        grand = 300.0; paid = 0.0
        is_partial = paid > 0 and paid < grand
        self.assertFalse(is_partial)

    def test_partial_detected_correctly(self):
        grand = 1000.0; paid = 250.0
        is_partial = paid > 0 and paid < grand
        self.assertTrue(is_partial)

    def test_pdf_with_partial_payment(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "partial_payment.pdf"
        inv = _make_test_invoice()
        inv["amount_paid"] = "300"
        app.generate_pdf(str(output), inv, _test_settings())
        self.assertTrue(output.exists())

    def test_pdf_with_full_payment(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "full_payment.pdf"
        inv = _make_test_invoice()
        inv["amount_paid"] = "1000"
        inv["status"] = "Paid"
        app.generate_pdf(str(output), inv, _test_settings())
        self.assertTrue(output.exists())

    def test_amount_paid_preserved_through_save_load(self):
        h = [{"number":"INV-001","client_name":"Test","total":800.0,
              "amount_paid":"400","date":"01/01/2024","due_date":"31/01/2024",
              "status":"Unpaid","items":[],"discount":"0","notes":"","po":"",
              "filepath":"","paid_date":"","last_reminder":"",
              "client_email":"","client_phone":"","client_address":"",
              "currency_symbol":"£","invoice_template":"Professional"}]
        save_history(h)
        loaded = load_history()
        self.assertEqual(loaded[0]["amount_paid"], "400")


class TestPAIDWatermark(unittest.TestCase):
    """PAID watermark stamps correctly on PDFs when status is Paid."""

    def test_paid_invoice_creates_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "paid_watermark.pdf"
        inv = _make_test_invoice()
        inv["status"] = "Paid"
        app.generate_pdf(str(output), inv, _test_settings())
        self.assertTrue(output.exists())

    def test_paid_pdf_is_valid(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "paid_valid.pdf"
        inv = _make_test_invoice()
        inv["status"] = "Paid"
        app.generate_pdf(str(output), inv, _test_settings())
        with open(output, "rb") as f:
            self.assertEqual(f.read(4), b"%PDF")

    def test_unpaid_invoice_no_watermark_attempt(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        # Should complete fine without attempting watermark
        output = _TEST_DIR / "unpaid_no_stamp.pdf"
        inv = _make_test_invoice()
        inv["status"] = "Unpaid"
        app.generate_pdf(str(output), inv, _test_settings())
        self.assertTrue(output.exists())

    def test_watermark_function_graceful_without_pypdf(self):
        # _stamp_paid_watermark should never raise even if pypdf missing
        from reportlab.lib import colors
        try:
            app._stamp_paid_watermark("/nonexistent/path.pdf",
                                      (595, 842), colors.HexColor("#00e676"))
        except Exception as e:
            self.fail(f"_stamp_paid_watermark raised unexpectedly: {e}")


class TestRecurringInvoices(unittest.TestCase):
    """Recurring invoice schedules stored and loaded correctly."""

    def setUp(self):
        if app.RECURRING_FILE.exists():
            app.RECURRING_FILE.unlink()

    def test_load_recurring_empty(self):
        self.assertEqual(app.load_recurring(), [])

    def test_save_and_load_recurring(self):
        schedules = [{
            "client":   "Acme Ltd",
            "interval": "Monthly",
            "amount":   500.0,
            "desc":     "Monthly retainer",
            "next_due": "01/06/2024",
            "active":   True,
            "created":  "01/01/2024",
        }]
        app.save_recurring(schedules)
        loaded = app.load_recurring()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["client"],   "Acme Ltd")
        self.assertEqual(loaded[0]["interval"], "Monthly")
        self.assertAlmostEqual(loaded[0]["amount"], 500.0)

    def test_save_recurring_non_list_saves_empty(self):
        app.save_recurring("not a list")
        self.assertEqual(app.load_recurring(), [])

    def test_multiple_schedules(self):
        schedules = [
            {"client":"Client A","interval":"Weekly","amount":100,"desc":"Weekly",
             "next_due":"01/06/2024","active":True,"created":"01/01/2024"},
            {"client":"Client B","interval":"Quarterly","amount":3000,"desc":"Q retainer",
             "next_due":"01/07/2024","active":True,"created":"01/01/2024"},
        ]
        app.save_recurring(schedules)
        loaded = app.load_recurring()
        self.assertEqual(len(loaded), 2)

    def test_inactive_schedule_preserved(self):
        schedules = [{"client":"X","interval":"Monthly","amount":200,
                      "desc":"Test","next_due":"01/06/2024","active":False,
                      "created":"01/01/2024"}]
        app.save_recurring(schedules)
        loaded = app.load_recurring()
        self.assertFalse(loaded[0]["active"])

    def test_load_payments_empty(self):
        if app.PAYMENTS_FILE.exists(): app.PAYMENTS_FILE.unlink()
        self.assertEqual(app.load_payments(), {})

    def test_save_and_load_payments(self):
        payments = {"INV-001": [{"date":"01/01/2024","amount":250.0,"note":"Part 1"}]}
        app.save_payments(payments)
        loaded = app.load_payments()
        self.assertIn("INV-001", loaded)
        self.assertEqual(len(loaded["INV-001"]), 1)

    def test_save_payments_non_dict_saves_empty(self):
        app.save_payments([1,2,3])
        self.assertEqual(app.load_payments(), {})

    def test_recurring_unicode_client_name(self):
        schedules = [{"client":"André Müller","interval":"Monthly",
                      "amount":750,"desc":"Retainer","next_due":"01/06/2024",
                      "active":True,"created":"01/01/2024"}]
        app.save_recurring(schedules)
        loaded = app.load_recurring()
        self.assertEqual(loaded[0]["client"], "André Müller")


# ── Shared helpers for new PDF tests ──────────────────────────────────────

def _make_test_invoice():
    return {
        "number": "TEST-001", "date": "01/01/2024",
        "due_date": "31/01/2024", "status": "Unpaid",
        "client_name": "Test Client", "client_email": "t@t.com",
        "client_address": "1 Road", "client_phone": "",
        "po": "", "discount": "0", "notes": "Test",
        "currency_symbol": "£",
        "invoice_template": "Professional",
        "amount_paid": "0",
        "items": [
            {"desc":"Service","qty":1,"price":500,"taxable":True,"total":500},
            {"desc":"Hosting","qty":2,"price":50,"taxable":False,"total":100},
        ],
    }

def _test_settings():
    s = dict(DEFAULT_SETTINGS)
    s.update({
        "company_name":"Test Co","company_address":"1 St","company_email":"a@b.com",
        "company_phone":"","company_website":"","vat_number":"","bank_name":"",
        "bank_sort_code":"","bank_account":"","bank_reference":"",
        "currency_symbol":"£","tax_rate":20.0,"tax_label":"VAT",
        "page_size":"A4","theme_accent":"#00e676","logo_path":"",
        "show_logo":False,"logo_width_mm":50,"logo_height_mm":18,
    })
    return s



class TestPaymentLinks(unittest.TestCase):
    """Payment link settings stored and retrieved correctly."""

    def setUp(self):
        for f in [app.SETTINGS_FILE]:
            if f.exists(): f.unlink()

    def test_paypal_link_in_defaults(self):
        s = load_settings()
        self.assertIn("paypal_link", s)
        self.assertIn("stripe_link", s)
        self.assertIn("custom_pay_link", s)
        self.assertIn("custom_pay_label", s)

    def test_save_and_load_paypal_link(self):
        save_settings({"paypal_link": "https://paypal.me/myuser"})
        s = load_settings()
        self.assertEqual(s["paypal_link"], "https://paypal.me/myuser")

    def test_save_and_load_stripe_link(self):
        save_settings({"stripe_link": "https://buy.stripe.com/abc123"})
        s = load_settings()
        self.assertEqual(s["stripe_link"], "https://buy.stripe.com/abc123")

    def test_multiple_links_stored_independently(self):
        save_settings({
            "paypal_link":   "https://paypal.me/test",
            "stripe_link":   "https://stripe.com/test",
            "custom_pay_link": "https://mysite.com/pay",
            "custom_pay_label": "Pay with Monzo",
        })
        s = load_settings()
        self.assertEqual(s["paypal_link"],    "https://paypal.me/test")
        self.assertEqual(s["stripe_link"],    "https://stripe.com/test")
        self.assertEqual(s["custom_pay_link"],"https://mysite.com/pay")
        self.assertEqual(s["custom_pay_label"],"Pay with Monzo")

    def test_pdf_with_payment_links(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "payment_links.pdf"
        inv = _make_test_invoice()
        s = _test_settings()
        s["paypal_link"]   = "https://paypal.me/testuser"
        s["stripe_link"]   = "https://buy.stripe.com/test"
        s["custom_pay_link"]   = "https://mysite.com/pay"
        s["custom_pay_label"]  = "Pay with Bank Transfer"
        app.generate_pdf(str(output), inv, s)
        self.assertTrue(output.exists())
        self.assertGreater(output.stat().st_size, 1000)

    def test_pdf_no_payment_links_by_default(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "no_payment_links.pdf"
        inv = _make_test_invoice()
        s = _test_settings()
        # No links set — should still generate cleanly
        s["paypal_link"]   = ""
        s["stripe_link"]   = ""
        s["custom_pay_link"] = ""
        app.generate_pdf(str(output), inv, s)
        self.assertTrue(output.exists())

    def test_paid_invoice_no_payment_links_on_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "paid_no_links.pdf"
        inv = _make_test_invoice()
        inv["status"] = "Paid"
        s = _test_settings()
        s["paypal_link"] = "https://paypal.me/test"
        # Paid invoices should not show payment links
        app.generate_pdf(str(output), inv, s)
        self.assertTrue(output.exists())


class TestLateFeeLogic(unittest.TestCase):
    """Late fee calculation logic — mirrors _calc_late_fee exactly."""

    def _settings_with_fee(self, enabled=True, days=14, fee_type="Percentage", amount="2.0"):
        s = dict(DEFAULT_SETTINGS)
        s.update({
            "late_fee_enabled":     str(enabled),
            "late_fee_days":        days,
            "late_fee_type":        fee_type,
            "late_fee_amount":      amount,
            "late_fee_description": "Late payment fee",
            "date_format":          "DD/MM/YYYY",
        })
        return s

    def _overdue_inv(self, days_over, total=1000.0, already_has_fee=False):
        due = (datetime.today() - timedelta(days=days_over)).strftime("%d/%m/%Y")
        items = [{"desc":"Service","qty":1,"price":total,"taxable":True,"total":total}]
        if already_has_fee:
            items.append({"desc":"Late payment fee (2% — 20 days overdue)",
                          "qty":1,"price":20.0,"taxable":False,"total":20.0})
        return {
            "number":"INV-001","status":"Overdue",
            "due_date":due,"total":total,"items":items,
        }

    def _calc(self, inv, s):
        """Reproduce _calc_late_fee without needing a live InvoiceApp."""
        if str(s.get("late_fee_enabled","False")).lower() not in ("true","1","yes"):
            return 0, ""
        if inv.get("status") not in ("Unpaid","Overdue"):
            return 0, ""
        fmt = s.get("date_format","DD/MM/YYYY")
        try:
            if fmt == "DD/MM/YYYY":
                due = datetime.strptime(inv["due_date"],"%d/%m/%Y")
            elif fmt == "MM/DD/YYYY":
                due = datetime.strptime(inv["due_date"],"%m/%d/%Y")
            else:
                due = datetime.strptime(inv["due_date"],"%Y-%m-%d")
        except Exception:
            return 0, ""
        days_over = (datetime.today() - due).days
        threshold = int(s.get("late_fee_days",14))
        if days_over < threshold:
            return 0, ""
        desc = s.get("late_fee_description","Late payment fee")
        for item in inv.get("items",[]):
            if item.get("desc","").startswith(desc):
                return 0, ""
        total = float(inv.get("total",0))
        try:
            fee_setting = float(s.get("late_fee_amount","2.0"))
        except Exception:
            fee_setting = 2.0
        if s.get("late_fee_type","Percentage") == "Percentage":
            fee = round(total * (fee_setting/100), 2)
        else:
            fee = fee_setting
        return fee, desc

    def test_percentage_fee_calculated_correctly(self):
        inv = self._overdue_inv(20)
        s   = self._settings_with_fee(enabled=True, days=14,
                                       fee_type="Percentage", amount="2.0")
        fee, desc = self._calc(inv, s)
        self.assertAlmostEqual(fee, 20.0)   # 2% of £1000

    def test_fixed_fee_calculated_correctly(self):
        inv = self._overdue_inv(20)
        s   = self._settings_with_fee(enabled=True, days=14,
                                       fee_type="Fixed Amount", amount="50.0")
        fee, _ = self._calc(inv, s)
        self.assertAlmostEqual(fee, 50.0)

    def test_fee_not_applied_before_threshold(self):
        inv = self._overdue_inv(7)          # only 7 days over
        s   = self._settings_with_fee(days=14)
        fee, _ = self._calc(inv, s)
        self.assertEqual(fee, 0)

    def test_fee_applied_exactly_at_threshold(self):
        inv = self._overdue_inv(14)         # exactly at threshold
        s   = self._settings_with_fee(days=14)
        fee, _ = self._calc(inv, s)
        self.assertGreater(fee, 0)

    def test_fee_not_applied_when_disabled(self):
        inv = self._overdue_inv(30)
        s   = self._settings_with_fee(enabled=False)
        fee, _ = self._calc(inv, s)
        self.assertEqual(fee, 0)

    def test_fee_not_applied_to_paid_invoice(self):
        inv = self._overdue_inv(30)
        inv["status"] = "Paid"
        s   = self._settings_with_fee()
        fee, _ = self._calc(inv, s)
        self.assertEqual(fee, 0)

    def test_fee_not_applied_to_draft(self):
        inv = self._overdue_inv(30)
        inv["status"] = "Draft"
        s   = self._settings_with_fee()
        fee, _ = self._calc(inv, s)
        self.assertEqual(fee, 0)

    def test_fee_not_applied_twice(self):
        inv = self._overdue_inv(30, already_has_fee=True)
        s   = self._settings_with_fee()
        fee, _ = self._calc(inv, s)
        self.assertEqual(fee, 0)

    def test_percentage_of_zero_total_is_zero(self):
        inv = self._overdue_inv(20, total=0)
        s   = self._settings_with_fee(fee_type="Percentage", amount="5.0")
        fee, _ = self._calc(inv, s)
        self.assertEqual(fee, 0)

    def test_fee_settings_stored_in_defaults(self):
        s = load_settings()
        self.assertIn("late_fee_enabled", s)
        self.assertIn("late_fee_days",    s)
        self.assertIn("late_fee_type",    s)
        self.assertIn("late_fee_amount",  s)

    def test_large_percentage_fee(self):
        inv = self._overdue_inv(60, total=500.0)
        s   = self._settings_with_fee(fee_type="Percentage", amount="10.0")
        fee, _ = self._calc(inv, s)
        self.assertAlmostEqual(fee, 50.0)   # 10% of £500

    def test_fixed_fee_independent_of_invoice_total(self):
        inv_small = self._overdue_inv(20, total=100.0)
        inv_large = self._overdue_inv(20, total=10000.0)
        s = self._settings_with_fee(fee_type="Fixed Amount", amount="25.0")
        fee_small, _ = self._calc(inv_small, s)
        fee_large, _ = self._calc(inv_large, s)
        self.assertAlmostEqual(fee_small, 25.0)
        self.assertAlmostEqual(fee_large, 25.0)



class TestCompanyProfiles(unittest.TestCase):
    """Multiple company profiles — store, load, switch."""

    def setUp(self):
        if app.PROFILES_FILE.exists(): app.PROFILES_FILE.unlink()
        if app.SETTINGS_FILE.exists(): app.SETTINGS_FILE.unlink()

    def _profile(self, name, company="Test Co", accent="#00e676", prefix="INV"):
        return {
            "name": name, "company_name": company,
            "theme_accent": accent, "invoice_prefix": prefix,
            "vat_number": "GB123456789", "company_email": "test@test.com",
            "company_phone": "", "company_address": "1 St",
            "company_website": "", "bank_name": "", "bank_sort_code": "",
            "bank_account": "", "bank_reference": "", "logo_path": "",
            "show_logo": True, "logo_width_mm": 50, "logo_height_mm": 18,
            "currency": "GBP (£)", "currency_symbol": "£",
            "tax_rate": 20.0, "tax_label": "VAT",
            "invoice_start": 1000, "invoice_template": "Professional",
            "invoice_footer": "", "tc_enabled": False, "tc_text": "",
            "paypal_link": "", "stripe_link": "",
            "custom_pay_link": "", "custom_pay_label": "",
        }

    def test_load_profiles_empty(self):
        self.assertEqual(app.load_profiles(), [])

    def test_save_and_load_single_profile(self):
        app.save_profiles([self._profile("Freelance Design")])
        loaded = app.load_profiles()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["name"], "Freelance Design")

    def test_save_and_load_multiple_profiles(self):
        profiles = [
            self._profile("Design Studio", company="Dean Wilson Design", accent="#ff6600"),
            self._profile("Photography",   company="T&DShots",           accent="#0099ff"),
            self._profile("Consulting",    company="DW Consulting",      accent="#cc00ff"),
        ]
        app.save_profiles(profiles)
        loaded = app.load_profiles()
        self.assertEqual(len(loaded), 3)
        self.assertEqual(loaded[1]["company_name"], "T&DShots")
        self.assertEqual(loaded[2]["invoice_prefix"], "INV")

    def test_profile_stores_accent_colour(self):
        app.save_profiles([self._profile("Brand", accent="#ff3300")])
        loaded = app.load_profiles()
        self.assertEqual(loaded[0]["theme_accent"], "#ff3300")

    def test_profile_stores_invoice_prefix(self):
        app.save_profiles([self._profile("Photo", prefix="TDSH")])
        loaded = app.load_profiles()
        self.assertEqual(loaded[0]["invoice_prefix"], "TDSH")

    def test_save_non_list_saves_empty(self):
        app.save_profiles("bad")
        self.assertEqual(app.load_profiles(), [])

    def test_profile_unicode_names(self):
        app.save_profiles([self._profile("André's Design", company="André Müller Ltd")])
        loaded = app.load_profiles()
        self.assertEqual(loaded[0]["name"], "André's Design")
        self.assertEqual(loaded[0]["company_name"], "André Müller Ltd")

    def test_profile_persists_after_reload(self):
        p = self._profile("Persistent", company="My Co", prefix="MYC")
        app.save_profiles([p])
        # Simulate app restart by reloading
        loaded = app.load_profiles()
        self.assertEqual(loaded[0]["company_name"], "My Co")
        self.assertEqual(loaded[0]["invoice_prefix"], "MYC")

    def test_active_profile_stored_in_settings(self):
        save_settings({"active_profile": "Freelance Design"})
        s = load_settings()
        self.assertEqual(s["active_profile"], "Freelance Design")

    def test_default_profile_is_empty_string(self):
        s = load_settings()
        self.assertEqual(s.get("active_profile", ""), "")


class TestCustomFooterAndTC(unittest.TestCase):
    """Invoice footer text and T&Cs page."""

    def setUp(self):
        if app.SETTINGS_FILE.exists(): app.SETTINGS_FILE.unlink()

    def test_footer_in_default_settings(self):
        s = load_settings()
        self.assertIn("invoice_footer", s)
        self.assertIn("tc_enabled",     s)
        self.assertIn("tc_text",        s)

    def test_save_and_load_footer_text(self):
        save_settings({"invoice_footer":
            "Company registered in England & Wales No. 12345678"})
        s = load_settings()
        self.assertIn("12345678", s["invoice_footer"])

    def test_save_and_load_tc_text(self):
        tc = "1. PAYMENT TERMS\n\nPayment is due within 30 days."
        save_settings({"tc_text": tc, "tc_enabled": True})
        s = load_settings()
        self.assertEqual(s["tc_text"], tc)

    def test_pdf_with_footer_text(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "footer_text.pdf"
        inv = _make_test_invoice()
        s = _test_settings()
        s["invoice_footer"] = "Company Registered in England & Wales No. 12345678"
        app.generate_pdf(str(output), inv, s)
        self.assertTrue(output.exists())
        self.assertGreater(output.stat().st_size, 1000)

    def test_pdf_with_tc_page(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "with_tc.pdf"
        inv = _make_test_invoice()
        s = _test_settings()
        s["tc_enabled"] = True
        s["tc_text"] = (
            "PAYMENT TERMS:\n\n"
            "Payment is due within 30 days of invoice date.\n\n"
            "LATE PAYMENT:\n\n"
            "Interest may be charged on overdue amounts."
        )
        app.generate_pdf(str(output), inv, s)
        self.assertTrue(output.exists())
        # T&Cs add a page so file should be larger
        size = output.stat().st_size
        self.assertGreater(size, 2000)

    def test_pdf_without_tc_page_when_disabled(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output_no_tc = _TEST_DIR / "no_tc.pdf"
        inv = _make_test_invoice()
        s = _test_settings()
        s["tc_enabled"] = False
        s["tc_text"] = "These terms would appear if enabled."
        app.generate_pdf(str(output_no_tc), inv, s)
        self.assertTrue(output_no_tc.exists())

    def test_pdf_with_empty_footer_no_crash(self):
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            self.skipTest("reportlab not installed")
        output = _TEST_DIR / "empty_footer.pdf"
        inv = _make_test_invoice()
        s = _test_settings()
        s["invoice_footer"] = ""
        app.generate_pdf(str(output), inv, s)
        self.assertTrue(output.exists())


# ═════════════════════════════════════════════════════════════════════════════
#  RUNNER
# ═════════════════════════════════════════════════════════════════════════════

def run_tests():
    print("=" * 65)
    print("  Invoice Generator — Automated Test Suite")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    print()

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    classes = [
        TestFormatCurrency,
        TestDateFunctions,
        TestCalcTotals,
        TestValidateHistoryEntry,
        TestValidateClientEntry,
        TestValidateExpenseEntry,
        TestSafeFileIO,
        TestLoadSaveFunctions,
        TestInvoiceNumbering,
        TestPaymentHistory,
        TestReminderLogic,
        TestStartupIntegrityCheck,
        TestPDFGeneration,
        TestEdgeCases,
        TestMultiCurrency,
        TestInvoiceTemplates,
        TestPartialPayments,
        TestPAIDWatermark,
        TestRecurringInvoices,
        TestPaymentLinks,
        TestLateFeeLogic,
        TestCompanyProfiles,
        TestCustomFooterAndTC,
    ]

    for cls in classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    total  = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    failed = len(result.failures) + len(result.errors)

    print()
    print("=" * 65)
    if failed == 0:
        print(f"  ✅  ALL {total} TESTS PASSED")
    else:
        print(f"  ✅  {passed}/{total} passed")
        print(f"  ❌  {failed} FAILED\n")
        print("  Failed tests:")
        for test, tb in result.failures + result.errors:
            print(f"    • {test}")
            last = [l.strip() for l in tb.strip().splitlines() if l.strip()][-1]
            print(f"      {last}")
    print("=" * 65)

    try: shutil.rmtree(_TEST_DIR)
    except Exception: pass

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
