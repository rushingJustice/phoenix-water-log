<script>
  import { CircleHelp } from 'lucide-svelte';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();
</script>

<header class="absolute top-0 left-0 right-0 w-full min-h-[60px] p-3 md:p-4">
  <div
    class="flex pointer-events-none justify-center items-center relative flex-col gap-2"
  >
    <div
      class="relative max-w-[300px] bg-white px-2 flex md:flex-col gap-1 flex-row items-center md:h-full h-[66px] p-2 md:p-3 rounded-lg shadow-md overflow-hidden w-full md:w-auto"
    >
      <h1
        class="w-[90%] md:text-4xl text-2xl md:text-center font-bold uppercase"
      >
        Phoenix Water Log
      </h1>
      <p
        class="md:text-sm md:w-full w-[90%] text-xs md:text-center font-semibold"
      >
        Mapping where water wants to go based on topography
      </p>
    </div>
    <div class="w-full max-w-[300px] flex justify-end">
      <button
        class="bg-white p-2 rounded-md shadow-md hover:bg-zinc-50 transition-colors duration-200 pointer-events-auto md:absolute md:right-0 md:top-0"
        on:click={() => dispatch('showMethodology')}
        aria-label="Show methodology"
      >
        <CircleHelp class="w-5 h-5 text-zinc-700" />
      </button>
    </div>
  </div>
</header>
