#!/usr/bin/env python3
"""
Fetch historical flood data from NOAA and USGS for Phoenix, AZ
Converts data to POI GeoJSON format for map display
"""

import requests
import json
from datetime import datetime, timedelta
import csv
from io import StringIO

# API Keys (optional - not required for this script as it uses preprocessed data)
# NOAA API Token: https://www.ncdc.noaa.gov/cdo-web/token
# USGS API Key: https://apps.nationalmap.gov/apikeys/
NOAA_TOKEN = os.environ.get("NOAA_TOKEN", "")
USGS_API_KEY = os.environ.get("USGS_API_KEY", "")

# Phoenix metro area bounds (matches water accumulation data extent)
PHOENIX_BOUNDS = {
    "min_lat": 33.25,
    "max_lat": 33.75,
    "min_lon": -112.35,
    "max_lon": -111.85
}

def fetch_usgs_stream_gauges():
    """
    Fetch USGS stream gauge sites in Phoenix area
    """
    print("Fetching USGS stream gauge sites...")

    # USGS Site Web Service
    url = "https://waterservices.usgs.gov/nwis/site/"

    params = {
        "format": "json",
        "bBox": f"{PHOENIX_BOUNDS['min_lon']},{PHOENIX_BOUNDS['min_lat']},{PHOENIX_BOUNDS['max_lon']},{PHOENIX_BOUNDS['max_lat']}",
        "siteType": "ST",  # Stream
        "siteStatus": "all"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        sites = []
        if "value" in data and "timeSeries" in data["value"]:
            for ts in data["value"]["timeSeries"]:
                site_info = ts["sourceInfo"]
                sites.append({
                    "site_no": site_info["siteCode"][0]["value"],
                    "name": site_info["siteName"],
                    "lat": float(site_info["geoLocation"]["geogLocation"]["latitude"]),
                    "lon": float(site_info["geoLocation"]["geogLocation"]["longitude"])
                })

        print(f"Found {len(sites)} USGS stream gauge sites")
        return sites

    except Exception as e:
        print(f"Error fetching USGS data: {e}")
        return []


def fetch_usgs_flood_events(site_no, start_date, end_date):
    """
    Fetch flood stage exceedance data for a specific USGS site
    """
    url = "https://waterservices.usgs.gov/nwis/iv/"

    params = {
        "format": "json",
        "sites": site_no,
        "startDT": start_date,
        "endDT": end_date,
        "parameterCd": "00065",  # Gage height
        "siteStatus": "all"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Check if there's data and if gage height exceeded flood stage
        # This is simplified - in reality you'd compare to NWS flood stage values
        if "value" in data and "timeSeries" in data["value"]:
            return True

        return False

    except Exception as e:
        print(f"Error fetching flood events for {site_no}: {e}")
        return False


def fetch_noaa_storm_events():
    """
    Load preprocessed NOAA Storm Events from JSON file
    Data was preprocessed from Maricopa County floods CSV (2000-2021)
    """
    print("Loading NOAA Storm Events from preprocessed data...")

    try:
        # Load preprocessed flood events
        with open('noaa_maricopa_floods.json', 'r') as f:
            raw_events = json.load(f)

        print(f"  ✓ Loaded {len(raw_events)} events from preprocessed data")

        # Transform to our format
        events = []
        for event in raw_events:
            # Use begin coordinates as primary location
            lat = event['begin_lat']
            lon = event['begin_lon']

            # Only include events within Phoenix bounds
            if (PHOENIX_BOUNDS['min_lat'] <= lat <= PHOENIX_BOUNDS['max_lat'] and
                PHOENIX_BOUNDS['min_lon'] <= lon <= PHOENIX_BOUNDS['max_lon']):

                # Create a readable name from location
                location = event.get('begin_location', '') or event.get('end_location', '') or 'Maricopa County'
                event_type = event.get('event_type', 'Flood')

                # Format description with key details
                description = event.get('event_narrative', '')[:200]  # Limit length
                if len(event.get('event_narrative', '')) > 200:
                    description += '...'

                # Add damage info if available
                damage = event.get('damage_property_num', '0')
                if damage and damage != '0':
                    try:
                        damage_val = float(damage)
                        if damage_val > 0:
                            description += f" Property damage: ${damage_val:,.0f}."
                    except:
                        pass

                events.append({
                    'date': event['begin_date'],
                    'name': f"{event_type} - {location}",
                    'description': description,
                    'narrative': event.get('event_narrative', ''),
                    'episode_narrative': event.get('episode_narrative', ''),
                    'lat': lat,
                    'lon': lon,
                    'source': 'NOAA Storm Events Database',
                    'event_id': event.get('event_id', ''),
                    'event_type': event_type,
                    'begin_location': event.get('begin_location', ''),
                    'end_location': event.get('end_location', ''),
                    'begin_time': event.get('begin_time', ''),
                    'end_time': event.get('end_time', ''),
                    'deaths_direct': event.get('deaths_direct', '0'),
                    'deaths_indirect': event.get('deaths_indirect', '0'),
                    'injuries_direct': event.get('injuries_direct', '0'),
                    'injuries_indirect': event.get('injuries_indirect', '0'),
                    'damage_property': event.get('damage_property_num', '0'),
                    'damage_crops': event.get('damage_crops_num', '0')
                })

        print(f"  ✓ Filtered to {len(events)} events within Phoenix bounds")
        return events

    except FileNotFoundError:
        print("  ⚠ Preprocessed data not found!")
        print("  Run: python preprocess_noaa_data.py")
        return []
    except Exception as e:
        print(f"  Error loading preprocessed data: {e}")
        return []


def convert_to_poi_geojson(usgs_sites, noaa_events):
    """
    Convert flood data to POI GeoJSON format for the map
    """
    print("Converting to GeoJSON format...")

    features = []

    # Add NOAA storm events
    for event in noaa_events:
        # Create Google search URL for the event
        search_query = f"{event['event_type']} {event.get('begin_location', '')} Phoenix {event['date']}"
        google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [event["lon"], event["lat"]]
            },
            "properties": {
                "name": event["name"],
                "neighbourhood": event.get("begin_location", "Phoenix Metro"),
                "date": event["date"],
                "url": google_url,
                "source": event.get("source", "NOAA"),
                "event_type": event.get("event_type", "Flood"),
                "narrative": event.get("narrative", ""),
                "episode_narrative": event.get("episode_narrative", ""),
                "begin_location": event.get("begin_location", ""),
                "end_location": event.get("end_location", ""),
                "begin_time": event.get("begin_time", ""),
                "end_time": event.get("end_time", ""),
                "deaths_direct": event.get("deaths_direct", "0"),
                "deaths_indirect": event.get("deaths_indirect", "0"),
                "injuries_direct": event.get("injuries_direct", "0"),
                "injuries_indirect": event.get("injuries_indirect", "0"),
                "damage_property": event.get("damage_property", "0"),
                "damage_crops": event.get("damage_crops", "0"),
                "event_id": event.get("event_id", "")
            }
        }
        features.append(feature)

    # Add USGS gauge sites (for sites with known flooding)
    for site in usgs_sites[:5]:  # Limit to first 5 for demo
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [site["lon"], site["lat"]]
            },
            "properties": {
                "name": site["name"],
                "neighbourhood": "USGS Stream Gauge",
                "date": "2024",
                "url": f"https://waterdata.usgs.gov/monitoring-location/{site['site_no']}/"
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return geojson


def main():
    print("=" * 60)
    print("Phoenix Flood Data Fetcher")
    print("=" * 60)

    # Fetch data from both sources
    usgs_sites = fetch_usgs_stream_gauges()
    noaa_events = fetch_noaa_storm_events()

    # Convert to GeoJSON
    geojson = convert_to_poi_geojson(usgs_sites, noaa_events)

    # Save to file
    output_path = "../src/lib/data/pois.json"
    with open(output_path, 'w') as f:
        json.dump(geojson, f, indent=2)

    print(f"\n✓ Saved {len(geojson['features'])} flood POIs to {output_path}")
    print(f"  - USGS sites: {min(5, len(usgs_sites))}")
    print(f"  - NOAA events: {len(noaa_events)}")
    print("\nReload the map to see the flood markers!")


if __name__ == "__main__":
    main()
