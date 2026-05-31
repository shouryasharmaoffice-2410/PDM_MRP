# CAD/MRP Database Editor

A browser-based editor for managing your parts database and bill of materials (BOM). No installation required — open it in any browser, edit your data, and download the updated CSV files to use with the Python MRP script.

---

## Files in this repo

| File | Purpose |
|------|---------|
| `index.html` | The web editor (open this in a browser) |
| `parts_database.csv` | Parts inventory data |
| `bom_database.csv` | Bill of materials relationships |
| `PDM_MRP.py` | Python MRP calculation script |

---

## How to use the web editor

1. Go to the live URL: `https://YOUR-USERNAME.github.io/mrp-editor/`
2. Click the **Parts** tab → click **Load CSV** → select your `parts_database.csv`
3. Click the **BOM** tab → click **Load CSV** → select your `bom_database.csv`
4. Make edits directly in the table (click any cell to edit)
5. When done, click **Download parts_database.csv** and **Download bom_database.csv**
6. Replace the old files in your project folder with the downloaded ones
7. Run the Python script — it will pick up all changes automatically

---

## Tabs explained

### Parts Database
Edit all part details inline:
- Part number, description, type (raw / purchased / sub-assembly / finished)
- On hand, on order, reserved quantities
- Reorder level, unit, supplier, lead time (days), CAD file path

### Bill of Materials
Edit parent-child part relationships:
- Which parts make up which assembly
- Quantity of each child part needed
- Optional notes per row

### Reports & MRP
- **Low stock panel** — shows all parts where on-hand quantity is below the reorder level
- **MRP calculator** — enter a parent part number and production quantity to get a full net requirements breakdown (gross qty needed, available stock, what needs to be ordered, estimated delivery dates)
- Export MRP results as a CSV

### Export
Download both CSVs from one place with file stats shown.

---

## Running the Python script locally

### Requirements

```bash
pip install pandas openpyxl
```

### Usage

```bash
python mrp_system.py
```

The script looks for `parts_database.csv` and `bom_database.csv` in the same folder. Make sure the CSVs you downloaded from the web editor are placed there before running.

### Menu options

| Option | What it does |
|--------|-------------|
| 1 | Calculate MRP for a product |
| 2 | View all parts |
| 3 | Show low stock items |
| 4 | Export all reports to Excel |
| 5 | Exit |

---

## CSV format reference

### parts_database.csv columns

| Column | Description | Example |
|--------|-------------|---------|
| `part_number` | Unique part ID | `PROD-00789-A` |
| `description` | Part name | `Finished Assembly A` |
| `type` | `raw`, `purchased`, `sub-assembly`, or `finished` | `finished` |
| `on_hand` | Current stock quantity | `10` |
| `on_order` | Quantity already ordered | `5` |
| `reserved` | Quantity reserved for other orders | `2` |
| `reorder_level` | Trigger reorder when on-hand falls below this | `5` |
| `unit` | Unit of measure | `pcs` |
| `supplier` | Supplier name | `SteelSupply Ltd` |
| `lead_time_days` | Days from order to delivery | `14` |
| `cad_file_path` | Path to CAD file (optional) | `cad/frame.stp` |

### bom_database.csv columns

| Column | Description | Example |
|--------|-------------|---------|
| `parent_part_number` | The assembly part number | `PROD-00789-A` |
| `child_part_number` | The component part number | `RAW-00456` |
| `quantity` | How many child parts per one parent | `4` |
| `notes` | Optional note | `Corner bolts` |

---

## Hosting on GitHub Pages (setup guide)

1. Create a free account at [github.com](https://github.com)
2. Create a new **public** repository (e.g. `mrp-editor`)
3. Upload `index.html` (and optionally your CSV files) to the repo
4. Go to **Settings → Pages**
5. Under Source, select **Deploy from a branch → main → / (root)**
6. Click **Save** — your URL will be live within ~1 minute at:
   ```
   https://YOUR-USERNAME.github.io/mrp-editor/
   ```
7. Share this URL with your team — no login or install needed

---

## Notes

- All editing happens in the browser — no data is sent to any server
- The web editor does not auto-save; always download your CSVs before closing the tab
- The Python script and the web editor use the same CSV format and are fully compatible
