# Phoenix Water Log

An interactive map visualizing water accumulation and drainage patterns across the Phoenix, AZ metropolitan area. Based on digital elevation models and hydrological analysis.

## Overview

This project analyzes elevation data to show where water naturally flows and accumulates during rainfall events in Phoenix. The visualization helps understand flood-prone areas and drainage patterns in the desert urban environment.

## Tech Stack

- **Frontend**: SvelteKit 2.0, MapLibre GL, TailwindCSS
- **Data Processing**: Python, WhiteboxTools, GDAL
- **Map Tiles**: PMTiles format for efficient web delivery

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- GDAL (install via Homebrew on Mac: `brew install gdal`)
- AWS CLI (for downloading DEM data: `brew install awscli`)
- Tippecanoe (for generating map tiles: `brew install tippecanoe`)

### Installation

1. Install Node dependencies:
```bash
npm install
```

2. Set up Python environment:
```bash
cd data/dem
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Data Pipeline

### Step 1: Download Elevation Data

Download Copernicus DEM data for Phoenix:

```bash
cd data/dem
./fetch.sh
```

This downloads 30m resolution elevation data and clips it to Phoenix bounds (33.25°N to 33.75°N, -112.35°W to -111.85°W).

### Step 2: Run Hydrological Analysis

Process the elevation data to calculate water flow and accumulation:

```bash
python tiles.py
```

This performs:
- Depression filling
- Flow direction calculation (D8 algorithm)
- Flow accumulation analysis
- Stream extraction (threshold: 500 cells, optimized for desert hydrology)
- Influence zone calculation with Gaussian smoothing
- Classification into 4 water accumulation levels

Output: `tiles/stream_influence_reclass.shp`

### Step 3: Generate Map Tiles

Convert the shapefile to PMTiles format:

```bash
cd ../water-tile-generation
./generate_stream_tile.sh
```

This creates `static/tiles.pmtiles` which the web app loads.

### Step 4: Run Development Server

```bash
npm run dev
```

Visit `http://localhost:5173` to see the map.

## Project Structure

```
phoenix-water-log/
├── src/
│   ├── routes/
│   │   ├── +page.svelte          # Main app
│   │   ├── +page.js              # Data loading
│   │   └── +layout.svelte        # Layout wrapper
│   ├── lib/
│   │   ├── components/
│   │   │   ├── Map/
│   │   │   │   ├── map.ts        # Map initialization
│   │   │   │   └── marker.ts     # POI markers
│   │   │   └── Layout/
│   │   │       ├── Header.svelte
│   │   │       ├── Drawer.svelte # Controls UI
│   │   │       └── SEO.svelte
│   │   └── data/
│   │       └── pois.json         # Flood incident locations
│   └── app.css                   # Global styles
├── data/
│   ├── dem/
│   │   ├── fetch.sh             # Download DEM
│   │   ├── tiles.py             # Hydrological analysis
│   │   └── requirements.txt     # Python deps
│   └── water-tile-generation/
│       └── generate_stream_tile.sh  # Create PMTiles
├── static/
│   └── tiles.pmtiles            # Generated map tiles
└── package.json

```

## Map Configuration

Phoenix-specific settings are in `src/lib/components/Map/map.ts`:

```typescript
const MAP_CONSTANTS = {
  CONFIG: {
    center: [-112.074, 33.448],    // Phoenix center
    zoom: 11.5,
    minZoom: 11,
    maxZoom: 15,
    maxBounds: [
      [-112.35, 33.25],            // Southwest corner
      [-111.85, 33.75]             // Northeast corner
    ]
  }
}
```

## Customization

### Adjusting Hydrology Parameters

Edit `data/dem/tiles.py`:

```python
# Line 159: flow accumulation threshold
# Lower = more sensitive (more streams detected)
# Higher = less sensitive (only major drainage)
delineate_basins(dem_path, output_dir, 500, 1)
                                      # ^^ change this value
```

### Changing Map Colors

Edit `src/lib/components/Map/map.ts`:

```typescript
'fill-color': [
  'interpolate',
  ['linear'],
  ['get', 'VALUE'],
  2, '#C4CDD020',   // Light accumulation
  3, '#abced0',     // Medium accumulation
  4, '#519ea2'      // High accumulation
]
```

## Adding Flood Incident Data

Edit `src/lib/data/pois.json`:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-112.074, 33.448]
      },
      "properties": {
        "name": "Downtown Phoenix",
        "neighbourhood": "Central City",
        "date": "2024",
        "url": "https://example.com/flood-report"
      }
    }
  ]
}
```

## Building for Production

```bash
npm run build
```

Output in `dist/` directory - deploy to any static host (Netlify, Vercel, GitHub Pages).

## Credits

Based on [blr-water-log](https://github.com/diagram-chasing/blr-water-log) by Diagram Chasing

- Elevation data: Copernicus DEM (30m resolution)
- Basemap: OpenStreetMap
- Hydrological analysis: WhiteboxTools

## License

MIT
