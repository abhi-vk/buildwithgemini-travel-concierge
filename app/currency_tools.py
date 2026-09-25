import json
import os
import urllib.request

def get_exchange_rates(base_currency: str = "USD", target_currencies: str = "EUR,GBP,JPY,CAD,AUD") -> dict:
    """Fetch live currency exchange rates for travel planning from the Frankfurter API.

    Args:
        base_currency: The 3-letter currency code to convert from (e.g. 'USD', 'EUR').
        target_currencies: Comma-separated list of target currency codes (e.g. 'EUR,JPY,GBP').

    Returns:
        A dictionary containing live exchange rates and metadata.
    """
    base = base_currency.upper().strip()
    targets = ",".join([c.strip().upper() for c in target_currencies.split(",") if c.strip()])
    
    # Read optional API key or endpoint override from environment variable
    api_key = os.environ.get("FRANKFURTER_API_KEY", "")
    api_url = os.environ.get("CURRENCY_API_URL", f"https://api.frankfurter.app/latest?from={base}&to={targets}")

    try:
        headers = {"User-Agent": "TravelConciergeAgent/1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return {
                "status": "success",
                "base_currency": data.get("base", base),
                "date": data.get("date"),
                "rates": data.get("rates", {})
            }
    except Exception as e:
        return {"error": f"Failed to fetch exchange rates: {str(e)}"}
