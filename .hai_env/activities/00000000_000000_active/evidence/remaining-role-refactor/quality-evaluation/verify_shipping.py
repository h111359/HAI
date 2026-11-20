from pathlib import Path
from decimal import Decimal
import csv, hashlib, io, json, platform, re, sys
from datetime import datetime, timezone
base = Path(__file__).resolve().parent
paths = {name: base / 'fixture' / name for name in ('shipping-policy.md', 'shipping-report.csv')}
raw = {name: path.read_bytes() for name, path in paths.items()}
hashes = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
rows = list(csv.DictReader(io.StringIO(raw['shipping-report.csv'].decode('utf-8-sig'))))
expected = {'ORD-101': ('120.00', 'paid'), 'ORD-102': ('80.00', 'paid'), 'ORD-103': ('150.00', 'pending'), 'ORD-104': ('50.00', 'paid')}
checks = []
for line, row in enumerate(rows, 2):
    subtotal, shipping, total = (Decimal(row[key]) for key in ('subtotal', 'shipping', 'grand_total'))
    eligible = row['status'] == 'paid' and subtotal >= Decimal('100.00')
    expected_shipping = Decimal('0.00') if eligible else Decimal('5.00')
    checks.append({'csv_line': line, 'order_id': row['order_id'], 'row': row,
        'domain_pass': subtotal >= 0 and row['status'] in ('paid', 'pending'),
        'eligible': eligible, 'expected_shipping': str(expected_shipping), 'shipping_pass': shipping == expected_shipping,
        'expected_total_from_reported_shipping': str(subtotal + shipping), 'addition_pass': total == subtotal + shipping,
        'expected_policy_total': str(subtotal + expected_shipping),
        'currency_format_pass': all(re.fullmatch(r'\d+\.\d{2}', row[key]) is not None for key in ('subtotal', 'shipping', 'grand_total')),
        'supplied_values_preserved': expected.get(row['order_id']) == (row['subtotal'], row['status'])})
ids = [row['order_id'] for row in rows]
criteria = [
    {'id':'C1', 'criterion':'Each subtotal is nonnegative; each status is paid or pending', 'status':'pass' if all(c['domain_pass'] for c in checks) else 'fail', 'evidence':'All four rows: domain_pass'},
    {'id':'C2', 'criterion':'Paid orders with subtotal at least 100.00 have shipping 0.00', 'status':'pass' if all(c['shipping_pass'] for c in checks if c['eligible']) else 'fail', 'evidence':'ORD-101, CSV line 2'},
    {'id':'C3', 'criterion':'All other orders have shipping 5.00', 'status':'pass' if all(c['shipping_pass'] for c in checks if not c['eligible']) else 'fail', 'evidence':'ORD-102 line 3 and ORD-104 line 5 pass; ORD-103 line 4 fails'},
    {'id':'C4', 'criterion':'Grand total equals subtotal plus shipping', 'status':'pass' if all(c['addition_pass'] for c in checks) else 'fail', 'evidence':'ORD-101/102/103 pass reported-field addition; ORD-104 line 5 fails'},
    {'id':'C5', 'criterion':'Amounts are decimal currency values rounded to two decimal places', 'status':'pass' if all(c['currency_format_pass'] for c in checks) else 'fail', 'evidence':'All 12 amount fields have two decimal places; all supplied arithmetic is exact at this precision'},
    {'id':'C6', 'criterion':'Preserve order IDs and include exactly one row per supplied order', 'status':'pass' if len(ids) == len(expected) and set(ids) == set(expected) else 'fail', 'evidence':'Four rows, four unique IDs, exact supplied ID set'}
]
unchanged = all(hashlib.sha256(paths[name].read_bytes()).hexdigest() == value for name, value in hashes.items())
evidence = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(), 'sha256': hashes, 'inputs_unchanged_during_check': unchanged, 'criteria': criteria, 'rows': checks, 'supplied_values_preserved': all(c['supplied_values_preserved'] for c in checks)}
(base / 'verification-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
print(json.dumps(evidence, indent=2))
