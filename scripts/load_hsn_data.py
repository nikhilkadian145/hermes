"""
Loads hsn_gst_rates.csv into the hermes.db hsn_master table.
Run once at provision time: python scripts/load_hsn_data.py <db_path>
Safe to re-run — uses INSERT OR IGNORE.
"""
import sqlite3, csv, sys, os


def load(db_path: str):
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'hsn_gst_rates.csv')
    conn = sqlite3.connect(db_path)
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [
            (r['code'], r['type'], r['description'],
             float(r['gst_rate']), r.get('chapter', r['code'][:2]),
             float(r.get('cess_rate', 0)), r.get('last_updated', '2024-07-01'))
            for r in reader
        ]
    conn.executemany(
        "INSERT OR IGNORE INTO hsn_master "
        "(code, type, description, gst_rate, chapter, cess_rate, last_updated)"
        " VALUES (?,?,?,?,?,?,?)", rows
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM hsn_master").fetchone()[0]
    conn.close()
    print(f"HSN master loaded: {count} entries in database")


if __name__ == '__main__':
    load(sys.argv[1])
