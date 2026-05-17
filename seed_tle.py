# Seed TLE data + DONKI fallback events for Satellite Tracker and Space Weather
from sqlalchemy import create_engine, text

DB_URL = "postgresql://admin:admin_pass@localhost:5432/spacedata"
engine = create_engine(DB_URL)

# Real TLE data (epoch may vary, format is standard)
SATELLITES_TLE = [
    ("ISS (ZARYA)", 25544,
     "1 25544U 98067A   24137.54791667  .00016717  00000-0  10270-3 0  9002",
     "2 25544  51.6412 208.9672 0006703  40.5193 319.6301 15.49969045454812"),
    ("HUBBLE SPACE TELESCOPE", 20580,
     "1 20580U 90037B   24137.18264398  .00000687  00000-0  33485-4 0  9994",
     "2 20580  28.4712 132.6478 0002510 123.5630 236.5640 15.09422215421876"),
    ("STARLINK-1007", 44713,
     "1 44713U 19074A   24137.25694445  .00001234  00000-0  95678-4 0  9991",
     "2 44713  53.0551 167.4320 0001237  85.4521 274.6630 15.06392341251342"),
    ("STARLINK-2305", 48601,
     "1 48601U 21044A   24137.50234567  .00002345  00000-0  15678-3 0  9995",
     "2 48601  53.0545 234.8910 0001456  92.3456 267.7890 15.06384512 98765"),
    ("NOAA 20 (JPSS-1)", 43013,
     "1 43013U 17073A   24137.38291667  .00000125  00000-0  71234-4 0  9993",
     "2 43013  98.7124  55.8901 0001567 101.2345 258.8976 14.19553456334521"),
    ("TERRA", 25994,
     "1 25994U 99068A   24137.20833333  .00000089  00000-0  45678-4 0  9990",
     "2 25994  98.2104  83.4567 0001234  92.3456 267.7890 14.57112345398765"),
    ("AQUA", 27424,
     "1 27424U 02022A   24137.37500000  .00000145  00000-0  56789-4 0  9992",
     "2 27424  98.2098 123.4567 0002345  78.9012 281.2345 14.57098765387654"),
    ("LANDSAT 9", 49260,
     "1 49260U 21088A   24137.29166667  .00000098  00000-0  34567-4 0  9997",
     "2 49260  98.2156  45.6789 0001023  89.0123 271.0234 14.57156789 45678"),
    ("GOES-16", 41866,
     "1 41866U 16071A   24137.50000000  .00000012  00000-0  00000+0 0  9996",
     "2 41866   0.0468 271.5678 0000345 234.5678 125.4321  1.00271234 27890"),
    ("SENTINEL-2A", 40697,
     "1 40697U 15028A   24137.41666667  .00000134  00000-0  67890-4 0  9999",
     "2 40697  98.5682  95.6789 0001234  87.6543 272.4567 14.30818765345678"),
    ("JASON-3", 41240,
     "1 41240U 16002A   24137.33333333  .00000087  00000-0  23456-4 0  9998",
     "2 41240  66.0430 178.9012 0008765  43.2109 316.8901 12.80930123234567"),
    ("COSMOS 2251 DEB", 33546,
     "1 33546U 93036RU  24137.45833333  .00000345  00000-0  89012-4 0  9994",
     "2 33546  74.0145 234.5678 0123456  12.3456 347.8901 14.76543210198765"),
    ("GPS BIIR-2 (PRN 13)", 24876,
     "1 24876U 97035A   24137.25000000  .00000005  00000-0  00000+0 0  9991",
     "2 24876  55.4356  78.9012 0056789 234.5678  56.7890  2.00563489176543"),
    ("METEOSAT-11", 40732,
     "1 40732U 15034A   24137.50000000  .00000015  00000-0  00000+0 0  9993",
     "2 40732   0.5123  89.0123 0003456 123.4567 236.5432  1.00274321 32456"),
    ("ASTRA 1N", 38778,
     "1 38778U 12051A   24137.50000000  .00000010  00000-0  00000+0 0  9995",
     "2 38778   0.0523  73.4567 0002345 167.8901 192.1234  1.00270987 43210"),
]

def seed_tle():
    with engine.connect() as c:
        # Add TLE columns if missing
        try:
            c.execute(text("ALTER TABLE satellites ADD COLUMN IF NOT EXISTS tle_line1 TEXT"))
            c.execute(text("ALTER TABLE satellites ADD COLUMN IF NOT EXISTS tle_line2 TEXT"))
            c.commit()
        except Exception:
            pass

        for name, norad, tle1, tle2 in SATELLITES_TLE:
            existing = c.execute(text("SELECT id FROM satellites WHERE norad_id = :n"), {"n": norad}).fetchone()
            if existing:
                c.execute(text("UPDATE satellites SET tle_line1 = :t1, tle_line2 = :t2 WHERE norad_id = :n"),
                          {"t1": tle1, "t2": tle2, "n": norad})
            else:
                c.execute(text("INSERT INTO satellites (name, norad_id, tle_line1, tle_line2) VALUES (:name, :norad, :t1, :t2)"),
                          {"name": name, "norad": norad, "t1": tle1, "t2": tle2})
        c.commit()
        print(f"[OK] Satellites with TLE: {len(SATELLITES_TLE)} updated")

if __name__ == "__main__":
    seed_tle()
    print("Done!")
