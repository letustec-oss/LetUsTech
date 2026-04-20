# Invoice Generator — Manual QA Checklist
**Version 2.1.0 — Run before every public release**
Tick every box. All items must pass before shipping.

---

## 🚀 Startup & Launch

- [ ] Launches without errors via `Launch_Invoice_Generator.bat`
- [ ] Window title reads **"Invoice Generator"**
- [ ] Dashboard loads as the default page
- [ ] Sidebar shows all nav items: Dashboard, New Invoice, Invoices, Clients, Expenses, Reports, Reminders, Settings, Help & Tutorial, About
- [ ] Version number `v2.1.0` shows in bottom-left of sidebar
- [ ] App icon appears in the taskbar
- [ ] No error dialogs on a clean first launch
- [ ] On second launch (with existing data), all data loads correctly

---

## 📊 Dashboard

- [ ] 8 stat cards display (Total Revenue, Net Profit, Outstanding, Overdue, Total Expenses, Total Invoices, Paid Invoices, Clients)
- [ ] Monthly revenue bar chart renders (6 bars)
- [ ] Revenue vs Expenses comparison chart renders
- [ ] Outstanding balance per client list appears (or "no outstanding" message)
- [ ] Recent invoices table shows up to 6 rows
- [ ] Status badges show correct colours: green=Paid, amber=Unpaid, red=Overdue, grey=Draft
- [ ] Quick action buttons navigate correctly: New Invoice, Add Expense, Add Client, All Invoices
- [ ] Reports button navigates to Reports page
- [ ] Scroll wheel works if content overflows

---

## 📄 New Invoice

- [ ] Page loads with empty fields
- [ ] Invoice number auto-populates (e.g. INV-1001)
- [ ] Invoice date defaults to today
- [ ] Due date defaults to today + payment terms
- [ ] Status dropdown works: Draft, Unpaid, Paid, Overdue
- [ ] Client name, email and phone fields accept input
- [ ] Billing address text area accepts multiline input
- [ ] If clients exist, address book dropdown appears and loads client on selection
- [ ] Date fields are editable
- [ ] PO/Reference field accepts text
- [ ] Discount % field accepts numbers
- [ ] Line item description stretches with window width
- [ ] Qty and unit price accept decimal numbers
- [ ] Tax checkbox toggles per item
- [ ] Line item total updates live
- [ ] Grand total in header updates live
- [ ] **Click the total amount** → shows "✓ Copied!" and copies value to clipboard
- [ ] Add Line Item button adds a new row
- [ ] Delete ✕ on a line item removes it
- [ ] Cannot delete the last line item (shows info message)
- [ ] Notes field accepts multiline text
- [ ] **💾 Save Draft** saves without exporting and shows confirmation
- [ ] Draft appears in Invoices list with "Draft" status
- [ ] **👁 Preview** opens text preview popup with correct figures
- [ ] **⬇ Export PDF** opens save dialog
- [ ] After export, PDF opens automatically (if Auto-open PDF is ON in Settings)
- [ ] Invoice number increments after each export
- [ ] Exported invoice appears in Invoices list
- [ ] **🔄 Reset** clears all fields

---

## 📁 Invoices

- [ ] All exported invoices and drafts appear
- [ ] Status filter buttons work: All, Unpaid, Paid, Overdue, Draft
- [ ] Active filter button highlights in green
- [ ] **🔍 Search** filters live by invoice #, client, date and status
- [ ] Clearing search restores full list
- [ ] **Open** button opens the PDF (when file exists)
- [ ] **✓ Paid** marks invoice as paid and updates status badge
- [ ] Paid invoices do NOT show the ✓ Paid button
- [ ] **⧉ Dup** duplicates invoice as a new draft with new number
- [ ] **✕** delete asks for confirmation then removes invoice
- [ ] Overdue invoices auto-detected on page load
- [ ] **📊 Export CSV** saves all invoice data to a .csv file
- [ ] Scroll wheel works in the invoice list

---

## 👥 Clients

- [ ] Client Address Book loads
- [ ] **＋ Add Client** opens dialog
- [ ] Name, email, phone, website and address all save correctly
- [ ] New client appears immediately
- [ ] **Avg. Days to Pay** column shows — or a colour-coded number for clients with history
- [ ] Colour: green ≤14d, amber ≤30d, red >30d
- [ ] **🔍 Search** filters by name, email and phone live
- [ ] **＋ Invoice** creates a new invoice pre-filled with client details
- [ ] **📋 History** opens client history dialog
- [ ] History dialog shows: Total Billed, Total Paid, Outstanding, Avg Days to Pay
- [ ] Reliability badge shows correct tier (Excellent / Good / Average / Slow)
- [ ] Invoice list in history is accurate with days-to-pay shown per row
- [ ] Send Reminder button appears in history dialog if outstanding invoices exist
- [ ] **Edit** opens dialog pre-filled with existing data
- [ ] Saving edit updates the client
- [ ] **✕** delete asks for confirmation then removes client
- [ ] Scroll wheel works in client list

---

## 💸 Expenses

- [ ] Expenses page loads
- [ ] Summary strip shows Total Expenses, This Month, Number of Entries
- [ ] **＋ Add Expense** opens dialog
- [ ] All fields save: description, amount, date, category, notes
- [ ] Category dropdown shows all options
- [ ] New expense appears sorted by date (newest first)
- [ ] Category badge shows correct colour
- [ ] **🔍 Search** filters by description, category and date
- [ ] **✕** delete asks for confirmation then removes expense
- [ ] Scroll wheel works in expense list

---

## 📈 Reports

- [ ] Reports page loads
- [ ] Year selector defaults to current year
- [ ] Annual summary shows Revenue, VAT Collected, Expenses, Net Profit
- [ ] Quarterly breakdown shows Q1–Q4 with revenue and VAT per quarter
- [ ] Monthly breakdown table shows all 12 months
- [ ] Totals row matches sum of monthly rows
- [ ] Net column is green for profit, red for loss
- [ ] **📊 Export Report CSV** saves correctly
- [ ] Changing year and refreshing updates all figures

---

## 🔔 Reminders

- [ ] Reminders page loads
- [ ] 7, 14, 30 day checkboxes reflect saved settings
- [ ] **Save Preferences** saves checkbox state
- [ ] Email template subject and body are editable
- [ ] **Save Template** saves the template
- [ ] Placeholder hint shows `{client}`, `{number}`, `{amount}`, `{due_date}`, `{company}`
- [ ] Overdue invoices that need reminders appear in the list
- [ ] Days overdue shown in correct colour (amber <14d, red ≥14d)
- [ ] Individual **📧 Send** button opens email preview dialog
- [ ] Email dialog pre-fills To, Subject and body correctly
- [ ] **Send All** fires all pending reminders
- [ ] After sending, invoice won't re-appear until next threshold
- [ ] "No reminders needed" message shows when all reminders up to date

---

## ⚙️ Settings

- [ ] Settings page loads and scrolls correctly
- [ ] All sections visible: Business, Banking, Tax & Currency, Invoice Defaults, Email, Keyboard Shortcuts, Appearance, Behaviour, File Saving
- [ ] All text fields are editable
- [ ] Logo Image browse button lets you pick a PNG/JPG
- [ ] Accent Colour Pick button opens colour picker
- [ ] **Keyboard Shortcuts section:**
  - [ ] **⏺ Record** turns red and shows "Listening..."
  - [ ] Pressing Ctrl+key records correctly (e.g. shows `Ctrl+N`)
  - [ ] Only ONE field records at a time
  - [ ] Escape cancels without saving
  - [ ] **✕** clears a shortcut
- [ ] **Behaviour section:** Auto-open PDF and Confirm on close save correctly
- [ ] **💾 Save Settings** saves all and shows confirmation
- [ ] Shortcuts update immediately after Save (no restart)
- [ ] **Reset to Defaults** asks for confirmation then resets

---

## ❓ Help & Tutorial

- [ ] Page loads and scrolls correctly
- [ ] All sections are readable
- [ ] Text wraps correctly on window resize

---

## ℹ️ About

- [ ] Page loads
- [ ] App name "Invoice Generator" and version display
- [ ] Feature list shows 8 items
- [ ] Tech stack pills show (Python, Tkinter, ReportLab, Pillow)
- [ ] Green-bordered shoutout card shows: Made by Deano @ LetUsTech
- [ ] All 5 links visible: Website, Email, Discord, YouTube, Kick

---

## ⌨️ Keyboard Shortcuts

- [ ] `Ctrl+N` → navigates to New Invoice from any page
- [ ] `Ctrl+E` → exports PDF when on invoice page
- [ ] `Ctrl+S` → saves draft when on invoice page
- [ ] `Ctrl+F` → focuses search box on Invoices or Clients page
- [ ] `Ctrl+D` → navigates to Dashboard
- [ ] `Ctrl+I` → navigates to Invoices
- [ ] Shortcuts do NOT fire when typing in a text field

---

## 🔒 Data Safety

- [ ] **Confirm on close** dialog appears when closing with unsaved invoice (if setting ON)
- [ ] Manually corrupt `history.json` → on next launch app warns, resets file, starts normally
- [ ] Manually empty `clients.json` → app starts with empty clients list, no crash
- [ ] `.tmp` file does NOT remain after a save operation

---

## 🖥️ Responsiveness

- [ ] Resize to minimum (900×600) — no content cut off or overlapping
- [ ] Maximise window — content fills the space
- [ ] Two-column layouts on Invoice page scale properly
- [ ] Bar charts redraw correctly after resize

---

## 🐛 Error Handling

- [ ] Trigger an error → error dialog appears with full traceback
- [ ] **📋 Copy Traceback** copies to clipboard
- [ ] **📂 Open Log File** opens `error.log`
- [ ] `error.log` exists in `~/.invoice_generator/` after an error

---

## 🧪 Automated Tests

- [ ] Run `python test_suite.py` → **ALL 125 TESTS PASS** ✅

---

## 📦 Pre-Release Final Checks

- [ ] `python test_suite.py` → all 125 pass
- [ ] Delete `~/.invoice_generator/` entirely and launch fresh — no crashes
- [ ] `logo.png`, `app_icon.ico` and `LETUSTECH.png` all present in app folder
- [ ] README.md is up to date
- [ ] README version number matches `APP_VERSION` in `invoice_app.py`

---

*Checklist v2.1.0 — Maintained by Deano @ LetUsTech — letustech.uk*
