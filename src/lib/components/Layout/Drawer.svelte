<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { LocateIcon, Loader2, MapPin } from 'lucide-svelte';
  import Header from './Header.svelte';

  export let pois;
  export let isLocating = false;
  export let showPOIs = true;

  const dispatch = createEventDispatcher();

  let value = 0.8;

  function handleOpacityChange(e: Event) {
    const value = parseFloat((e.target as HTMLInputElement).value);
    dispatch('opacityChange', value);
  }

  function togglePOIs() {
    showPOIs = !showPOIs;
    dispatch('togglePOIs', showPOIs);
  }

  function handleShowMethodology() {
    dispatch('showMethodology');
  }
</script>

<Header on:showMethodology={handleShowMethodology} />

<div
  class="fixed w-full md:w-fit bottom-0 left-0 md:left-1/2 transform md:-translate-x-1/2 z-50"
>
  <div class="w-full max-w-sm mx-auto p-4">
    <div class="bg-white rounded-lg shadow-lg p-4 space-y-4">
      <!-- POI Toggle -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <MapPin class="w-4 h-4 text-gray-700" />
          <label for="poi-toggle" class="text-sm font-semibold text-gray-700">
            Show Flood Events
          </label>
        </div>
        <button
          id="poi-toggle"
          on:click={togglePOIs}
          class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          class:bg-blue-600={showPOIs}
          class:bg-gray-300={!showPOIs}
          role="switch"
          aria-checked={showPOIs}
        >
          <span
            class="inline-block h-4 w-4 transform rounded-full bg-white transition duration-200 ease-in-out"
            class:translate-x-6={showPOIs}
            class:translate-x-1={!showPOIs}
          ></span>
        </button>
      </div>

      <!-- Opacity control -->
      <div class="flex flex-col gap-2">
        <label for="opacity" class="text-sm font-semibold text-gray-700">
          Water Layer Opacity
        </label>
        <input
          id="opacity"
          type="range"
          min="0"
          max="1"
          step="0.1"
          bind:value
          on:input={handleOpacityChange}
          class="w-full"
        />
      </div>

      <!-- Locate button -->
      <button
        class="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-4 py-2 rounded flex items-center justify-center gap-2"
        on:click={() => dispatch('locate')}
        disabled={isLocating}
      >
        {#if isLocating}
          <Loader2 class="w-4 h-4 animate-spin" />
          Locating...
        {:else}
          <LocateIcon class="w-4 h-4" />
          Locate Me
        {/if}
      </button>
    </div>
  </div>
</div>
