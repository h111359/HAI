"""Best-effort snapshot of public Standard-speed Codex credit rates."""
from html.parser import HTMLParser
import re
from urllib.request import urlopen

from environment_paths import PROFILES
from .storage import SafetyError, checked_path
from .usage import pricing


URL = 'https://learn.chatgpt.com/docs/pricing?codex-pricing-speed=standard'
MAX_BYTES = 4 * 1024 * 1024
HEADER = ('credits per 1m tokens', 'input tokens', 'cached input tokens', 'output tokens')
RATE_NAMES = ('input_credits_per_million', 'cached_input_credits_per_million', 'output_credits_per_million')


class RateTables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.table = self.row = self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.table = []
        elif tag == 'tr' and self.table is not None:
            self.row = []
        elif tag in ('th', 'td') and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('th', 'td') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == 'table' and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def parse_rates(html, models):
    parser = RateTables()
    parser.feed(html)
    candidates = {}
    for rows in parser.tables:
        if not rows or tuple(cell.casefold() for cell in rows[0]) != HEADER:
            continue
        for model, *values in rows[1:]:
            name = re.sub(r'\s+', '-', model.casefold())
            if name not in models or len(values) != len(RATE_NAMES):
                continue
            amounts = [re.fullmatch(r'(\d+(?:,\d{3})*(?:\.\d+)?) credits?', cell.casefold()) for cell in values]
            if all(amounts):
                rates = tuple(amount[1].replace(',', '') for amount in amounts)
                candidates.setdefault(name, set()).add(rates)
    return {model: dict(zip(RATE_NAMES, next(iter(rows))))
            for model, rows in candidates.items() if len(rows) == 1}


def lookup(root, captured_at):
    from role_tools import CLASSES, Invalid, read_profiles
    try:
        path = checked_path(root, PROFILES)
        if not path.is_file():
            return None
        configured = read_profiles(path)['models']
        models = {configured[key] for key in CLASSES}
        with urlopen(URL, timeout=2) as response:
            if response.geturl().split('?', 1)[0] != URL.split('?', 1)[0]:
                return None
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            return None
        rates = parse_rates(raw.decode('utf-8'), models)
        return pricing({'rates': rates, 'source': URL, 'captured_at': captured_at}) if rates else None
    except (Invalid, SafetyError, OSError, ValueError, TypeError, KeyError):
        return None
