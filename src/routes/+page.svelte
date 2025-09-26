<script lang="ts">
  let prompt = "";
  let finalUrl: string | null = null;
  let status: "idle" | "running" | "done" | "error" = "idle";
  let logs: string[] = [];

  // 👇 Your deployed Modal endpoint
  const MODAL_ENDPOINT = "https://ml5jswork--sdxl-h100-ui-generate.modal.run";

  async function startJob() {
    finalUrl = null;
    status = "running";
    logs = ["Requesting image..."];

    try {
      const url = new URL(MODAL_ENDPOINT);
      url.searchParams.set("prompt", prompt);

      const res = await fetch(url.toString());
      if (!res.ok) {
        status = "error";
        logs.push(`Error: ${res.status} ${res.statusText}`);
        return;
      }

      // Convert response to blob → object URL
      const blob = await res.blob();
      finalUrl = URL.createObjectURL(blob);
      status = "done";
      logs.push("Final image ready");
    } catch (err) {
      status = "error";
      logs.push(`Request failed: ${err}`);
    }
  }
</script>

<style>
  .container {
    max-width: 900px;
    margin: 2rem auto;
    font-family: system-ui;
  }
  .panel {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
  }
  img {
    max-width: 100%;
    border-radius: 8px;
  }
  button {
    margin-top: 0.5rem;
    padding: 0.5rem 1rem;
  }
</style>

<div class="container">
  <h2>Stable Diffusion XL (H100)</h2>

  <div class="panel">
    <input
      type="text"
      bind:value={prompt}
      placeholder="Enter your prompt"
      style="width:100%; padding:0.5rem;"
    />
    <button on:click|preventDefault={startJob} disabled={status === "running"}>
      {status === "running" ? "Generating..." : "Generate"}
    </button>
  </div>

  <div class="panel">
    <h3>Result</h3>
    {#if finalUrl}
      <img src={finalUrl} alt="Generated image" />
    {:else if status === "running"}
      <p>Generating image…</p>
    {:else}
      <p>No image yet.</p>
    {/if}
  </div>

  <div class="panel">
    <h3>Logs</h3>
    <ul>
      {#each logs as line}
        <li>{line}</li>
      {/each}
    </ul>
  </div>
</div>
