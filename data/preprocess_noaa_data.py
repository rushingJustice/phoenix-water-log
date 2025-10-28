#!/usr/bin/env python3
"""
Preprocessing script to parse NOAA Storm Events CSV file for Maricopa County
Filters to flood/flash flood events with valid lat/lon coordinates
Output: clean JSON file with filtered flood events
"""

import csv
import json
from datetime import datetime

def parse_maricopa_floods(csv_path):
    """
    Parse Maricopa County floods CSV and extract events with valid coordinates
    """
    print(f"Processing {csv_path}...")

    events = []
    total_rows = 0
    filtered_out = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_rows += 1

            # Filter: Must have valid BEGIN and END coordinates
            if (row.get('BEGIN_LAT') and row.get('BEGIN_LON') and
                row.get('END_LAT') and row.get('END_LON')):

                try:
                    begin_lat = float(row['BEGIN_LAT'])
                    begin_lon = float(row['BEGIN_LON'])
                    end_lat = float(row['END_LAT'])
                    end_lon = float(row['END_LON'])

                    # Validate lat/lon are not zero or invalid
                    if (begin_lat != 0 and begin_lon != 0 and
                        end_lat != 0 and end_lon != 0 and
                        abs(begin_lat) <= 90 and abs(begin_lon) <= 180):

                        events.append({
                            'event_id': row.get('EVENT_ID', ''),
                            'event_type': row.get('EVENT_TYPE', ''),
                            'begin_date': row.get('BEGIN_DATE', ''),
                            'begin_time': row.get('BEGIN_TIME', ''),
                            'end_date': row.get('END_DATE', ''),
                            'end_time': row.get('END_TIME', ''),
                            'begin_location': row.get('BEGIN_LOCATION', ''),
                            'end_location': row.get('END_LOCATION', ''),
                            'begin_lat': begin_lat,
                            'begin_lon': begin_lon,
                            'end_lat': end_lat,
                            'end_lon': end_lon,
                            'cz_name': row.get('CZ_NAME_STR', ''),
                            'event_narrative': row.get('EVENT_NARRATIVE', ''),
                            'episode_narrative': row.get('EPISODE_NARRATIVE', ''),
                            'injuries_direct': row.get('INJURIES_DIRECT', '0'),
                            'injuries_indirect': row.get('INJURIES_INDIRECT', '0'),
                            'deaths_direct': row.get('DEATHS_DIRECT', '0'),
                            'deaths_indirect': row.get('DEATHS_INDIRECT', '0'),
                            'damage_property_num': row.get('DAMAGE_PROPERTY_NUM', '0'),
                            'damage_crops_num': row.get('DAMAGE_CROPS_NUM', '0'),
                            'magnitude': row.get('MAGNITUDE', ''),
                            'magnitude_type': row.get('MAGNITUDE_TYPE', '')
                        })
                    else:
                        filtered_out += 1
                except (ValueError, TypeError):
                    filtered_out += 1
            else:
                filtered_out += 1

    print(f"  Total rows: {total_rows}")
    print(f"  Valid events: {len(events)}")
    print(f"  Filtered out: {filtered_out}")

    return events


def main():
    print("=" * 60)
    print("NOAA Storm Events Data Preprocessor")
    print("Processing Maricopa County flood data...")
    print("=" * 60)

    # Path to the CSV file (in project data directory)
    csv_path = 'floods_maricopa_2000yr.csv'

    all_events = parse_maricopa_floods(csv_path)

    # Save to JSON
    output_file = 'noaa_maricopa_floods.json'
    with open(output_file, 'w') as f:
        json.dump(all_events, f, indent=2)

    print("\n" + "=" * 60)
    print(f"✓ Processed {len(all_events)} total flood events")
    print(f"✓ Saved to {output_file}")
    print("=" * 60)

    # Print summary stats
    if all_events:
        event_types = {}
        for event in all_events:
            etype = event['event_type']
            event_types[etype] = event_types.get(etype, 0) + 1

        print("\nEvent type breakdown:")
        for etype, count in sorted(event_types.items()):
            print(f"  {etype}: {count} events")

        # Show date range
        dates = [e['begin_date'] for e in all_events if e['begin_date']]
        if dates:
            print(f"\nDate range: {min(dates)} to {max(dates)}")


if __name__ == "__main__":
    main()
