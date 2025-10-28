import maplibregl from 'maplibre-gl';
import type { StyleSpecification } from 'maplibre-gl';
import { Protocol, PMTiles } from 'pmtiles';
import pois from '../../data/pois.json';
import { MarkerPill } from './marker';
import { writable } from 'svelte/store';
import chroma from 'chroma-js';

// Maricopa County map constants
const MAP_CONSTANTS = {
  DARKEST_FLOOD_COLOR: '#519EA2',
  PMTILES_URL: 'tiles.pmtiles',
  CONFIG: {
    center: [-112.074, 33.448] as [number, number], // Phoenix center
    maxZoom: 15,
    hash: true,
    minZoom: 9,
    pitch: 45,
    antialias: true,
    zoom: 10,
    maxBounds: [
      [-113.33, 32.55], // Southwest - Maricopa County
      [-111.05, 33.93]  // Northeast - Maricopa County
    ] as [[number, number], [number, number]]
  }
} as const;

export const generateFloodColors = () => {
  const scale = chroma
    .scale(['#abced0', MAP_CONSTANTS.DARKEST_FLOOD_COLOR])
    .mode('lab')
    .colors(4);

  return {
    colors: scale,
    stops: [3, 4, 5]
  };
};

const initializePMTiles = () => {
  const protocol = new Protocol();
  maplibregl.addProtocol('pmtiles', protocol.tile);
  const p = new PMTiles(MAP_CONSTANTS.PMTILES_URL);
  protocol.add(p);
  return p;
};

const pmTiles = initializePMTiles();

type POIFeature = (typeof pois.features)[0];
type Marker = {
  name: string;
  coordinates: [number, number];
  markerObj?: maplibregl.Marker;
  feature?: POIFeature;
};

export const selectedPOI = writable<POIFeature | null>(null);

export default class Map {
  private map?: maplibregl.Map;
  private markers: Marker[] = [];
  private markersVisible: boolean = true;

  private initializeLayers(): void {
    if (!this.map) return;

    this.map.addSource('pmtiles-source', {
      type: 'vector',
      url: `pmtiles://${MAP_CONSTANTS.PMTILES_URL}`,
      attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a>'
    });

    this.map.addLayer({
      id: 'pmtiles-layer',
      type: 'fill',
      source: 'pmtiles-source',
      'source-layer': 'water',

      paint: {
        'fill-color': [
          'interpolate',
          ['linear'],
          ['get', 'VALUE'],
          2,
          '#C4CDD020',
          3,
          '#abced0',
          4,
          '#519ea2'
        ],
        'fill-opacity': 0.8
      }
    });
  }

  private setupEventListeners(): void {
    if (!this.map) return;

    this.map.addControl(new maplibregl.NavigationControl(), 'bottom-right');
    this.map.on('click', () => selectedPOI.set(null));

    selectedPOI.subscribe(poi => {
      if (poi && this.map) {
        const marker = this.markers.find(m => m.name === poi.properties.name);
        if (marker) {
          this.map.flyTo({
            center: marker.coordinates,
            zoom: 14,
            duration: 2000
          });
        }
      }
    });
  }

  private createMarker(feature: POIFeature): void {
    if (!this.map) return;

    const coordinates = feature.geometry.coordinates as [number, number];
    const name = feature.properties.name;

    const markerPill = new MarkerPill(this.map);
    const markerEl = markerPill.onAdd();

    markerEl.addEventListener('click', e => {
      e.stopPropagation();
      selectedPOI.set(feature);
    });

    const markerObj = new maplibregl.Marker({
      element: markerEl,
      anchor: 'left',
      offset: [0, -10],
      clickTolerance: 10,
      pitchAlignment: 'viewport',
      rotationAlignment: 'viewport'
    })
      .setLngLat(coordinates)
      .addTo(this.map);

    this.markers.push({ name, coordinates, markerObj, feature });
    markerPill.render(name);
  }

  private initializeMarkers(): void {
    const uniquePOIs = pois.features.reduce((acc: POIFeature[], current) => {
      const index = acc.findIndex(
        item => item.properties.name === current.properties.name
      );
      if (index === -1) {
        acc.push(current);
      } else if (
        parseInt(current.properties.date) > parseInt(acc[index].properties.date)
      ) {
        acc[index] = current;
      }
      return acc;
    }, []);

    uniquePOIs.forEach(feature => this.createMarker(feature));
  }

  private addBlinkingCircle(coordinates: [number, number]): void {
    if (!this.map) return;

    this.map.addSource('pulse-point', {
      type: 'geojson',
      data: {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates
        },
        properties: {}
      }
    });

    this.map.addLayer({
      id: 'pulse-point-outer',
      type: 'circle',
      source: 'pulse-point',
      paint: {
        'circle-radius': 15,
        'circle-color': MAP_CONSTANTS.DARKEST_FLOOD_COLOR,
        'circle-opacity': 0.2
      }
    });

    this.map.addLayer({
      id: 'pulse-point-inner',
      type: 'circle',
      source: 'pulse-point',
      paint: {
        'circle-radius': 8,
        'circle-color': MAP_CONSTANTS.DARKEST_FLOOD_COLOR,
        'circle-stroke-width': 2,
        'circle-stroke-color': '#ffffff'
      }
    });

    const duration = 3000;
    const startTime = performance.now();
    const maxRadius = 30;
    const minRadius = 15;

    const animate = (currentTime: number) => {
      if (!this.map) return;

      const elapsed = currentTime - startTime;
      const progress = elapsed / duration;

      const radiusOffset = (maxRadius - minRadius) / 2;
      const baseRadius = minRadius + radiusOffset;
      const currentRadius =
        baseRadius + radiusOffset * Math.sin(progress * Math.PI * 6);

      this.map.setPaintProperty(
        'pulse-point-outer',
        'circle-radius',
        currentRadius
      );

      if (elapsed < duration) {
        requestAnimationFrame(animate);
      } else {
        if (this.map.getLayer('pulse-point-outer')) {
          this.map.removeLayer('pulse-point-outer');
        }
        if (this.map.getLayer('pulse-point-inner')) {
          this.map.removeLayer('pulse-point-inner');
        }
        if (this.map.getSource('pulse-point')) {
          this.map.removeSource('pulse-point');
        }
      }
    };

    requestAnimationFrame(animate);
  }

  init(container: string | HTMLElement): void {
    pmTiles.getHeader().then(() => {
      this.map = new maplibregl.Map({
        container,
        style: {
          version: 8,
          sources: {
            'osm': {
              type: 'raster',
              tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
              tileSize: 256,
              attribution: '© OpenStreetMap contributors'
            }
          },
          layers: [
            {
              id: 'osm-layer',
              type: 'raster',
              source: 'osm',
              minzoom: 0,
              maxzoom: 22
            }
          ]
        } as StyleSpecification,
        ...MAP_CONSTANTS.CONFIG
      });

      this.map.on('load', () => {
        this.initializeLayers();
        this.setupEventListeners();
        this.initializeMarkers();
      });
    });
  }

  cleanup() {
    if (this.map) {
      this.map.remove();
    }
  }

  setLayerOpacity(opacity: number): void {
    if (this.map) {
      this.map.setPaintProperty('pmtiles-layer', 'fill-opacity', opacity);
    }
  }

  locate(): Promise<{ type: 'success' | 'error'; message?: string }> {
    if (!this.map) {
      return Promise.resolve({ type: 'error', message: 'Map not initialized' });
    }

    const timeoutPromise = new Promise<{ type: 'error'; message: string }>(
      resolve => {
        setTimeout(() => {
          resolve({
            type: 'error',
            message: 'Location request timed out. Please try again.'
          });
        }, 5000);
      }
    );

    const locationPromise = new Promise<{
      type: 'success' | 'error';
      message?: string;
    }>(resolve => {
      if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
          position => {
            const { longitude, latitude } = position.coords;
            const coordinates: [number, number] = [longitude, latitude];

            if (
              longitude >= MAP_CONSTANTS.CONFIG.maxBounds[0][0] &&
              longitude <= MAP_CONSTANTS.CONFIG.maxBounds[1][0] &&
              latitude >= MAP_CONSTANTS.CONFIG.maxBounds[0][1] &&
              latitude <= MAP_CONSTANTS.CONFIG.maxBounds[1][1]
            ) {
              this.map?.flyTo({
                center: coordinates,
                zoom: 15,
                pitch: 0,
                duration: 2000
              });
              this.addBlinkingCircle(coordinates);
              resolve({ type: 'success' });
            } else {
              resolve({
                type: 'error',
                message: `You appear to be outside Maricopa County.`
              });
            }
          },
          error => {
            console.error('Error getting location:', error);
            resolve({
              type: 'error',
              message:
                'Unable to get your location. Please check your browser permissions.'
            });
          },
          {
            enableHighAccuracy: true,
            timeout: 8000,
            maximumAge: 0
          }
        );
      } else {
        resolve({
          type: 'error',
          message: 'Geolocation is not supported by your browser'
        });
      }
    });

    return Promise.race([locationPromise, timeoutPromise]);
  }

  togglePOIVisibility(visible: boolean): void {
    this.markersVisible = visible;
    this.markers.forEach(marker => {
      if (marker.markerObj) {
        const element = marker.markerObj.getElement();
        if (element) {
          element.style.display = visible ? 'block' : 'none';
        }
      }
    });
  }
}
