<script lang="ts">
  import { onMount } from 'svelte';
  import Map, { selectedPOI } from '../lib/components/Map/map';
  import Drawer from '../lib/components/Layout/Drawer.svelte';
  import SEO from '../lib/components/Layout/SEO.svelte';
  import AlertDialog from '../lib/components/Layout/AlertDialog.svelte';
  import POIScreen from '../lib/components/Layout/POIScreen.svelte';

  export let data;
  let mapContainer: HTMLElement;
  let map: Map;
  let alertOpen = false;
  let alertMessage = '';
  let alertTitle = '';
  let isLocating = false;
  let showPOIs = true;
  let selectedPOIData: any = null;
  let showPOIScreen = false;

  onMount(() => {
    map = new Map();
    map.init(mapContainer);

    // Subscribe to POI selection
    const unsubscribe = selectedPOI.subscribe(poi => {
      if (poi) {
        selectedPOIData = {
          name: poi.properties.name,
          neighbourhood: poi.properties.neighbourhood,
          date: poi.properties.date,
          url: poi.properties.url,
          coordinates: poi.geometry.coordinates,
          source: poi.properties.source,
          event_type: poi.properties.event_type,
          narrative: poi.properties.narrative,
          episode_narrative: poi.properties.episode_narrative,
          begin_location: poi.properties.begin_location,
          end_location: poi.properties.end_location,
          begin_time: poi.properties.begin_time,
          end_time: poi.properties.end_time,
          deaths_direct: poi.properties.deaths_direct,
          deaths_indirect: poi.properties.deaths_indirect,
          injuries_direct: poi.properties.injuries_direct,
          injuries_indirect: poi.properties.injuries_indirect,
          damage_property: poi.properties.damage_property,
          damage_crops: poi.properties.damage_crops,
          event_id: poi.properties.event_id
        };
        showPOIScreen = true;
      } else {
        showPOIScreen = false;
      }
    });

    return () => {
      map.cleanup();
      unsubscribe();
    };
  });

  let metadata = {
    title: 'Phoenix Water Log',
    description: "Where does Phoenix's water flow and accumulate?",
    date: '2025-10-27',
    categories: ['gis', 'map', 'phoenix', 'flood', 'water'],
    author: 'Phoenix Water Project',
    ogImage: `/sharecard.jpg`
  };

  function updateOpacity(value: number) {
    if (map) {
      map.setLayerOpacity(value);
    }
  }

  async function handleLocate() {
    if (isLocating) return;

    try {
      isLocating = true;
      const result = await map.locate();
      if (result.type === 'error' && result.message) {
        alertMessage = result.message;
        alertOpen = true;
      }
    } catch (error) {
      console.error('Location error:', error);
      alertMessage = 'Something went wrong while trying to locate you';
      alertOpen = true;
    } finally {
      isLocating = false;
    }
  }

  function handleTogglePOIs(event: CustomEvent<boolean>) {
    showPOIs = event.detail;
    if (map) {
      map.togglePOIVisibility(showPOIs);
    }
  }

  function handleClosePOI() {
    showPOIScreen = false;
    selectedPOI.set(null);
  }

  function handleShowMethodology() {
    alertTitle = 'About This Project';
    alertMessage = `
      <ul class="list-disc pl-5 space-y-2 text-left">
        <li>Uses digital elevation models to simulate natural water flow patterns</li>
        <li>Shows where water accumulates based on topography</li>
        <li>Displays 22 historical flood events from NOAA (2010-2021)</li>
        <li>Helps identify flood-prone areas in Phoenix metro</li>
        <li>Based on hydrological flow analysis of terrain data</li>
      </ul>
    `;
    alertOpen = true;
  }
</script>

<main>
  <SEO {...metadata} />
  <div bind:this={mapContainer} class="map-container"></div>
  <Drawer
    pois={data.pois}
    on:opacityChange={e => updateOpacity(e.detail)}
    on:locate={handleLocate}
    on:togglePOIs={handleTogglePOIs}
    on:showMethodology={handleShowMethodology}
    {isLocating}
    {showPOIs}
  />
  <POIScreen
    poi={selectedPOIData}
    visible={showPOIScreen}
    on:close={handleClosePOI}
  />
  <AlertDialog bind:open={alertOpen} message={alertMessage} title={alertTitle} />
</main>

<style lang="postcss">
  .map-container {
    width: 100%;
    height: 100dvh;
  }

  @media (max-width: 768px) {
    :global(.maplibregl-ctrl.maplibregl-ctrl-attrib) {
      display: none;
    }
  }
</style>
