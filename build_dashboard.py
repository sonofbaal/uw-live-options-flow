#!/usr/bin/env python3
"""
Build the Unusual Whales live options-flow dashboard.

Pulls the current trading day's filtered flow from GET /api/option-trades and
bakes it into a self-contained HTML file you can open in any browser.

Usage:
    export UW_TOKEN="your_api_key"          # macOS / Linux
    set UW_TOKEN=your_api_key               # Windows (cmd)
    python3 build_dashboard.py

No third-party packages required -- standard library only.
Edit the FILTERS block below to change the screen (same params as the website flow feed).
"""

import os, sys, json, urllib.request, urllib.parse, urllib.error
import datetime as dt

# --- your screen (same filters as the website flow page) ----------------------
FILTERS = {
    "is_otm": "true",
    "volume_greater_oi": "true",
    "is_multi_leg": "false",
    "max_open_interest": 5000,
    "max_dte": 180,
    "excluded_tags[]": "bid_side",
    "min_premium": 10000,
    "min_volume": 500,
    "max_price": 25,
    "issue_types[]": ["Common Stock", "ADR"],
    "min_ask_perc": 0.5,
    "limit": 250,
}
TEMPLATE = "uw_flow_dashboard_template.html"
OUTPUT   = "uw_flow_dashboard.html"
BASE_URL = "https://api.unusualwhales.com/api/option-trades"
# ------------------------------------------------------------------------------


def f(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0


def fetch():
    token = os.environ.get("UW_TOKEN")
    if not token:
        sys.exit("ERROR: set your API key first, e.g.  export UW_TOKEN=your_api_key")
    # build the query string (arrays repeat the key)
    pairs = []
    for k, v in FILTERS.items():
        if isinstance(v, list):
            for item in v: pairs.append((k, item))
        else:
            pairs.append((k, v))
    url = BASE_URL + "?" + urllib.parse.urlencode(pairs)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        # some CDNs block the default python-urllib signature; send a normal UA
        "User-Agent": "Mozilla/5.0 (UW-Flow-Dashboard/1.0)",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR {e.code}: {e.read().decode()[:300]}")


def shape(raw):
    trades = raw.get("data", [])
    if not trades:
        sys.exit("No trades returned. Market may be closed, or the filters are too tight.")
    today = dt.datetime.now(dt.timezone.utc).date()
    out = []
    for r in trades:
        try: dte = (dt.date.fromisoformat(r["expiry"]) - today).days
        except Exception: dte = None
        tags = r.get("tags") or []
        out.append({
            "t": r["executed_at"], "sym": r["underlying_symbol"],
            "name": r.get("full_name", ""), "type": r["option_type"],
            "strike": f(r["strike"]), "expiry": r["expiry"], "dte": dte,
            "price": f(r["price"]), "prem": f(r["premium"]),
            "vol": int(r.get("volume") or 0), "oi": int(r.get("open_interest") or 0),
            "askv": int(r.get("ask_vol") or 0), "bidv": int(r.get("bid_vol") or 0),
            "iv": f(r.get("implied_volatility")), "delta": f(r.get("delta")),
            "sector": r.get("sector") or "Unknown", "uprice": f(r.get("underlying_price")),
            "tags": tags, "issue": r.get("issue_type"),
            "erwk": ("earnings_this_week" in tags) or ("earnings_next_week" in tags),
        })
    meta = {
        "pulled_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n": len(out), "first": out[0]["t"], "last": out[-1]["t"],
        "filters": {
            "is_otm": True, "volume_greater_oi": True, "is_multi_leg": False,
            "max_open_interest": FILTERS["max_open_interest"], "max_dte": FILTERS["max_dte"],
            "excluded_tags": ["bid_side"], "min_premium": FILTERS["min_premium"],
            "min_volume": FILTERS["min_volume"], "max_price": FILTERS["max_price"],
            "issue_types": FILTERS["issue_types[]"], "min_ask_perc": FILTERS["min_ask_perc"],
        },
    }
    return {"meta": meta, "trades": out}


def main():
    data = shape(fetch())
    tpl = open(TEMPLATE, encoding="utf-8").read()
    html = tpl.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"OK: {data['meta']['n']} trades  ->  {OUTPUT}")
    print("Open it in your browser (macOS: open, Linux: xdg-open, Windows: double-click).")


if __name__ == "__main__":
    main()
