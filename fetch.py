import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
from ryanair import Ryanair
from supabase import create_client

# Konfiguration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

ROUTES = [
    ("ARN", "ALC"),
    ("GOT", "ALC"),
    ("ALC", "ARN"),
    ("ALC", "GOT"),
]

def get_dates():
    today = datetime.today().date()
    return [today + timedelta(days=i) for i in range(1, 90)]

def fetch_and_store():
    api = Ryanair("EUR")
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    snapshot_date = datetime.today().date()

    for origin, destination in ROUTES:
        print(f"Hämtar {origin} → {destination}...")
        dates = get_dates()
        for flight_date in dates:
            try:
                flights = api.get_cheapest_flights(origin, flight_date, flight_date + timedelta(days=1))
                for f in flights:
                    if f.destination != destination:
                        continue
                    row = {
                        "snapshot_date": str(snapshot_date),
                        "flight_date": str(f.departureTime.date()),
                        "dep_time": str(f.departureTime.time()),
                        "arr_time": str(f.departureTime.time()),
                        "flight_number": f.flightNumber,
                        "origin": origin,
                        "destination": destination,
                        "airline": "Ryanair",
                        "price_eur": float(f.price),
                    }
                    supabase.table("price_snapshots").insert(row).execute()
                    print(f"  {f.flightNumber} {f.departureTime} {f.price} EUR")
            except Exception as e:
                print(f"  Fel: {e}")

if __name__ == "__main__":
    fetch_and_store()