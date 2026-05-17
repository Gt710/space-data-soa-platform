# Seed script: populates all databases with realistic sample data
# Run: services\user-service\venv\Scripts\python seed_data.py
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import random

DB_URL = "postgresql://admin:admin_pass@localhost:5432/spacedata"
engine = create_engine(DB_URL)

def seed():
    with engine.connect() as c:
        # ===== SATELLITES =====
        satellites = [
            ("ISS (ZARYA)", 25544, "1998-11-20"),
            ("HUBBLE SPACE TELESCOPE", 20580, "1990-04-24"),
            ("STARLINK-1007", 44713, "2019-11-11"),
            ("STARLINK-2305", 48601, "2021-05-04"),
            ("NOAA 20 (JPSS-1)", 43013, "2017-11-18"),
            ("TERRA", 25994, "1999-12-18"),
            ("AQUA", 27424, "2002-05-04"),
            ("LANDSAT 9", 49260, "2021-09-27"),
            ("GOES-16", 41866, "2016-11-19"),
            ("SENTINEL-2A", 40697, "2015-06-23"),
            ("JASON-3", 41240, "2016-01-17"),
            ("COSMOS 2251 DEB", 33546, "1993-06-16"),
            ("GPS BIIR-2 (PRN 13)", 24876, "1997-07-23"),
            ("METEOSAT-11", 40732, "2015-07-15"),
            ("ASTRA 1N", 38778, "2012-07-06"),
        ]
        for name, norad, launch in satellites:
            existing = c.execute(text("SELECT id FROM satellites WHERE norad_id = :n"), {"n": norad}).fetchone()
            if not existing:
                c.execute(text("INSERT INTO satellites (name, norad_id, launch_date) VALUES (:name, :norad, :launch)"),
                          {"name": name, "norad": norad, "launch": launch})
        print(f"[OK] Satellites: {len(satellites)} seeded")

        # ===== ASTRO OBJECTS =====
        astro_objects = [
            ("Sirius", "star", "06h 45m 08.9s", "-16° 42' 58\"", 8.6),
            ("Betelgeuse", "star", "05h 55m 10.3s", "+07° 24' 25\"", 642.5),
            ("Vega", "star", "18h 36m 56.3s", "+38° 47' 01\"", 25.0),
            ("Polaris", "star", "02h 31m 49.1s", "+89° 15' 51\"", 433.0),
            ("Rigel", "star", "05h 14m 32.3s", "-08° 12' 06\"", 860.0),
            ("Andromeda Galaxy", "galaxy", "00h 42m 44.3s", "+41° 16' 09\"", 2537000.0),
            ("Triangulum Galaxy", "galaxy", "01h 33m 50.9s", "+30° 39' 37\"", 2730000.0),
            ("Whirlpool Galaxy", "galaxy", "13h 29m 52.7s", "+47° 11' 43\"", 23000000.0),
            ("Sombrero Galaxy", "galaxy", "12h 39m 59.4s", "-11° 37' 23\"", 29350000.0),
            ("Orion Nebula", "nebula", "05h 35m 17.3s", "-05° 23' 28\"", 1344.0),
            ("Crab Nebula", "nebula", "05h 34m 31.9s", "+22° 00' 52\"", 6523.0),
            ("Eagle Nebula", "nebula", "18h 18m 48.0s", "-13° 49' 00\"", 7000.0),
            ("Ring Nebula", "nebula", "18h 53m 35.1s", "+33° 01' 45\"", 2283.0),
            ("Ceres", "asteroid", "—", "—", 0.0000276),
            ("Halley's Comet", "comet", "—", "—", None),
            ("Jupiter", "planet", "—", "—", 0.0000822),
            ("Saturn", "planet", "—", "—", 0.000151),
        ]
        for name, otype, ra, dec, dist in astro_objects:
            existing = c.execute(text("SELECT id FROM astro_objects WHERE name = :n"), {"n": name}).fetchone()
            if not existing:
                c.execute(text("""INSERT INTO astro_objects (name, object_type, right_ascension, declination, distance_ly) 
                                  VALUES (:name, :otype, :ra, :dec, :dist)"""),
                          {"name": name, "otype": otype, "ra": ra, "dec": dec, "dist": dist})
        print(f"[OK] Astro Objects: {len(astro_objects)} seeded")

        # ===== MISSIONS =====
        missions = [
            ("Artemis I", "NASA", "2022-11-16", "completed", "Uncrewed flight test around the Moon"),
            ("Artemis II", "NASA", "2025-09-01", "planned", "First crewed Artemis mission, lunar flyby"),
            ("Artemis III", "NASA", "2026-09-01", "planned", "First crewed lunar landing since Apollo 17"),
            ("Mars Sample Return", "NASA/ESA", "2028-01-01", "planned", "Return samples collected by Perseverance"),
            ("James Webb Operations", "NASA/ESA/CSA", "2021-12-25", "active", "Deep space infrared observatory at L2"),
            ("Chandrayaan-3", "ISRO", "2023-07-14", "completed", "Lunar south pole landing mission"),
            ("JUICE", "ESA", "2023-04-14", "active", "Jupiter Icy Moons Explorer en route to Jupiter"),
            ("Psyche", "NASA", "2023-10-13", "active", "Mission to metallic asteroid 16 Psyche"),
            ("Europa Clipper", "NASA", "2024-10-14", "active", "Detailed survey of Jupiter moon Europa"),
            ("Luna 25", "Roscosmos", "2023-08-10", "completed", "Russian lunar lander mission"),
            ("OSIRIS-APEX", "NASA", "2023-09-24", "active", "Extended mission to asteroid Apophis"),
            ("Hera", "ESA", "2024-10-07", "active", "Binary asteroid deflection assessment"),
            ("Voyager 1 Extended", "NASA", "1977-09-05", "active", "Interstellar space exploration, 24B km from Earth"),
            ("Parker Solar Probe", "NASA", "2018-08-12", "active", "Closest approach to the Sun"),
        ]
        for name, agency, launch, status, desc in missions:
            existing = c.execute(text("SELECT id FROM missions WHERE name = :n"), {"n": name}).fetchone()
            if not existing:
                c.execute(text("""INSERT INTO missions (name, agency, launch_date, status, description)
                                  VALUES (:name, :agency, :launch, :status, :desc)"""),
                          {"name": name, "agency": agency, "launch": launch, "status": status, "desc": desc})
        print(f"[OK] Missions: {len(missions)} seeded")

        # ===== SPACE EVENTS (10-14 days) =====
        now = datetime.now()
        events = [
            (now - timedelta(days=13), "Solar Flare M2.1",
             "Medium-intensity solar flare detected from AR3842. Caused brief HF radio fadeout over South America.",
             "https://apod.nasa.gov/apod/image/2405/M1_HubbleVargas1024.jpg", "image"),
            (now - timedelta(days=12), "CME Event — Halo Type",
             "Full halo coronal mass ejection observed. Estimated arrival at Earth: 2-3 days. Speed: 890 km/s.",
             "https://apod.nasa.gov/apod/image/2401/Carina_Hubble_1080.jpg", "image"),
            (now - timedelta(days=11), "Geomagnetic Storm G2",
             "Moderate geomagnetic storm in progress. Kp index reached 6. Aurora visible at latitudes 55°+.",
             "https://apod.nasa.gov/apod/image/2405/AuroraNewZealand_McDonald_1080.jpg", "image"),
            (now - timedelta(days=10), "ISS Debris Avoidance Maneuver",
             "ISS performed collision avoidance burn at 14:22 UTC to dodge tracked debris from Cosmos 2251.",
             "https://apod.nasa.gov/apod/image/2404/iss071e564695_1024.jpg", "image"),
            (now - timedelta(days=9), "NEO 2024 PT5 Close Approach",
             "Near-Earth asteroid 2024 PT5 passed at 0.02 AU. Diameter estimated 10-22m. Non-hazardous.",
             "https://apod.nasa.gov/apod/image/2405/AsteroidBennu_OSIRISREx.jpg", "image"),
            (now - timedelta(days=7), "Solar Flare X1.8",
             "Major X-class flare from sunspot region AR3848. Strong HF radio blackout over Pacific.",
             "https://apod.nasa.gov/apod/image/2405/SunSpot_Hubble1024.jpg", "image"),
            (now - timedelta(days=6), "Starlink Constellation Update",
             "SpaceX deployed Group 9-3: 22 Starlink v2-mini satellites to 550km orbit. Total constellation: 6,200+.",
             "https://apod.nasa.gov/apod/image/2405/StarlinkTrails_1024.jpg", "image"),
            (now - timedelta(days=5), "Geomagnetic Storm G3 — Strong",
             "Strong geomagnetic storm. Kp=7. Power grid irregularities reported in Scandinavia. Aurora at 50° latitude.",
             "https://apod.nasa.gov/apod/image/2405/AuroraSweden_1024.jpg", "image"),
            (now - timedelta(days=4), "JWST Discovery: Earliest Galaxy",
             "James Webb Space Telescope confirmed galaxy JADES-GS-z14-0 at redshift z=14.32, ~290M years after Big Bang.",
             "https://apod.nasa.gov/apod/image/2405/JWST_DeepField_1024.jpg", "image"),
            (now - timedelta(days=3), "Solar Wind Speed Surge",
             "Solar wind speed increased to 720 km/s from coronal hole CH1109. Minor Kp=4 activity expected.",
             "https://apod.nasa.gov/apod/image/2405/SolarWind_SDO_1024.jpg", "image"),
            (now - timedelta(days=2), "Perseverance: New Mars Sample Cached",
             "Sample tube #24 deposited at Three Forks depot. Contains igneous rock with olivine crystals.",
             "https://apod.nasa.gov/apod/image/2405/MarsRock_Perseverance_1024.jpg", "image"),
            (now - timedelta(days=1), "CME Impact — Earth-directed",
             "CME from May 15 X1.8 flare impacted Earth magnetosphere at 08:41 UTC. Bz=-18nT. Kp=5 storm in progress.",
             "https://apod.nasa.gov/apod/image/2405/CME_SOHO_1024.jpg", "image"),
            (now, "Current: Elevated Solar Activity",
             "Solar activity remains elevated. Multiple C-class flares in last 24h. Active regions AR3848, AR3851 monitored.",
             "https://apod.nasa.gov/apod/image/2405/Sun_SDO_1024.jpg", "image"),
        ]
        for date, title, explanation, url, media_type in events:
            date_str = date.strftime("%Y-%m-%d")
            existing = c.execute(text("SELECT id FROM space_events WHERE title = :t"), {"t": title}).fetchone()
            if not existing:
                c.execute(text("""INSERT INTO space_events (date, title, explanation, url, media_type) 
                                  VALUES (:date, :title, :explanation, :url, :media_type)"""),
                          {"date": date_str, "title": title, "explanation": explanation,
                           "url": url, "media_type": media_type})
        print(f"[OK] Space Events: {len(events)} seeded")

        c.commit()
        print("\nAll seed data inserted successfully!")

if __name__ == "__main__":
    seed()
