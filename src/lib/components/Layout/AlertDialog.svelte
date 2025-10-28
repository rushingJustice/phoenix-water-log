<script lang="ts">
  export let open = false;
  export let message = '';
</script>

{#if open}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="bg-white rounded-lg p-6 max-w-md mx-4 shadow-xl">
      <p class="text-gray-800 mb-4">{message}</p>
      <button
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
        on:click={() => (open = false)}
      >
        OK
      </button>
    </div>
  </div>
{/if}
