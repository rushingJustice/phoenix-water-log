<script lang="ts">
  import { X, MapPin, Calendar, ExternalLink, AlertTriangle, DollarSign, Clock } from 'lucide-svelte';
  import { createEventDispatcher } from 'svelte';

  export let poi: any;
  export let visible = false;

  const dispatch = createEventDispatcher();

  function close() {
    dispatch('close');
  }

  function formatDamage(damageStr: string): string {
    const damage = parseFloat(damageStr || '0');
    if (damage === 0) return '';
    if (damage >= 1000000) return `$${(damage / 1000000).toFixed(1)}M`;
    if (damage >= 1000) return `$${(damage / 1000).toFixed(0)}K`;
    return `$${damage.toFixed(0)}`;
  }

  function formatTime(timeStr: string): string {
    if (!timeStr || timeStr === '0') return '';
    // Parse time like "630" or "1017" as HH:MM
    const padded = timeStr.padStart(4, '0');
    return `${padded.slice(0, 2)}:${padded.slice(2, 4)}`;
  }
</script>

{#if visible && poi}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[80vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-lg">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <MapPin class="w-5 h-5" />
              <span class="text-sm font-medium opacity-90">Flood Event</span>
            </div>
            <h2 class="text-2xl font-bold">{poi.name}</h2>
            {#if poi.neighbourhood}
              <p class="text-blue-100 text-sm mt-1">{poi.neighbourhood}</p>
            {/if}
          </div>
          <button
            on:click={close}
            class="p-2 hover:bg-white/20 rounded-full transition-colors"
            aria-label="Close"
          >
            <X class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6 space-y-4">
        <!-- Date & Time -->
        <div class="grid grid-cols-2 gap-3">
          <div class="flex items-start gap-2">
            <div class="p-2 bg-blue-50 rounded-lg">
              <Calendar class="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <p class="text-xs text-gray-500 font-medium">Date</p>
              <p class="text-sm text-gray-900 font-semibold">{poi.date}</p>
            </div>
          </div>
          {#if poi.begin_time && poi.begin_time !== '0'}
            <div class="flex items-start gap-2">
              <div class="p-2 bg-blue-50 rounded-lg">
                <Clock class="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <p class="text-xs text-gray-500 font-medium">Time</p>
                <p class="text-sm text-gray-900 font-semibold">{formatTime(poi.begin_time)}</p>
              </div>
            </div>
          {/if}
        </div>

        <!-- Location Coordinates -->
        <div class="flex items-start gap-3">
          <div class="p-2 bg-blue-50 rounded-lg">
            <MapPin class="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p class="text-sm text-gray-500 font-medium">Location</p>
            <p class="text-gray-900 font-mono text-sm">
              {poi.coordinates[1].toFixed(4)}°N, {Math.abs(poi.coordinates[0]).toFixed(4)}°W
            </p>
          </div>
        </div>

        <!-- Event Type & Source -->
        <div class="flex items-center justify-between bg-gray-50 rounded-lg p-3">
          <div>
            <p class="text-xs text-gray-500">Event Type</p>
            <p class="text-sm font-semibold text-gray-900">{poi.event_type || 'Flood'}</p>
          </div>
          <div class="text-right">
            <p class="text-xs text-gray-500">Source</p>
            <p class="text-xs font-medium text-gray-700">{poi.source || 'NOAA'}</p>
          </div>
        </div>

        <!-- Casualties & Damage -->
        {#if (poi.deaths_direct && poi.deaths_direct !== '0') || (poi.injuries_direct && poi.injuries_direct !== '0') || formatDamage(poi.damage_property)}
          <div class="grid grid-cols-2 gap-3">
            {#if (poi.deaths_direct && poi.deaths_direct !== '0') || (poi.injuries_direct && poi.injuries_direct !== '0')}
              <div class="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg p-3">
                <AlertTriangle class="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p class="text-xs text-red-600 font-medium">Casualties</p>
                  {#if poi.deaths_direct && poi.deaths_direct !== '0'}
                    <p class="text-sm text-gray-900">{poi.deaths_direct} death(s)</p>
                  {/if}
                  {#if poi.injuries_direct && poi.injuries_direct !== '0'}
                    <p class="text-sm text-gray-900">{poi.injuries_direct} injured</p>
                  {/if}
                </div>
              </div>
            {/if}
            {#if formatDamage(poi.damage_property)}
              <div class="flex items-start gap-2 bg-orange-50 border border-orange-200 rounded-lg p-3">
                <DollarSign class="w-4 h-4 text-orange-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p class="text-xs text-orange-600 font-medium">Property Damage</p>
                  <p class="text-sm font-semibold text-gray-900">{formatDamage(poi.damage_property)}</p>
                </div>
              </div>
            {/if}
          </div>
        {/if}

        <!-- Event Narrative -->
        {#if poi.narrative}
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p class="text-xs text-gray-600 font-semibold mb-2 uppercase">Event Details</p>
            <p class="text-sm text-gray-800 leading-relaxed">{poi.narrative}</p>
          </div>
        {/if}

        <!-- Episode Narrative -->
        {#if poi.episode_narrative && poi.episode_narrative !== poi.narrative}
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p class="text-xs text-blue-700 font-semibold mb-2 uppercase">Regional Context</p>
            <p class="text-sm text-gray-800 leading-relaxed">{poi.episode_narrative}</p>
          </div>
        {/if}

        <!-- Google Search Link -->
        {#if poi.url}
          <a
            href={poi.url}
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center justify-center gap-2 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
          >
            <span>Search on Google</span>
            <ExternalLink class="w-4 h-4" />
          </a>
        {/if}

        <!-- Info Box -->
        <div class="bg-gray-100 border border-gray-200 rounded-lg p-3">
          <p class="text-xs text-gray-600">
            <strong>Data Source:</strong> {poi.source || 'NOAA Storm Events Database'}
            {#if poi.event_id}
              <br /><strong>Event ID:</strong> {poi.event_id}
            {/if}
          </p>
        </div>
      </div>
    </div>
  </div>
{/if}
