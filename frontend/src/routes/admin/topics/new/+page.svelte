<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { adminTopicsAPI } from "$lib/api.js";

  let form = {
    title: "",
    description: "",
    level: "",
    prerequisite_topic_id: null,
  };

  let allTopics = [];
  let loading = false;
  let saving = false;
  let error = "";

  onMount(async () => {
    try {
      allTopics = await adminTopicsAPI.list();
    } catch (err) {
      error = err.message || "Failed to load topics";
    }
  });

  async function handleSubmit() {
    if (!form.title.trim()) {
      error = "Title is required";
      return;
    }

    saving = true;
    error = "";

    try {
      const data = {
        title: form.title.trim(),
        description: form.description.trim() || null,
        level: form.level.trim() || null,
        prerequisite_topic_id: form.prerequisite_topic_id || null,
      };

      const topic = await adminTopicsAPI.create(data);
      goto(`/admin/topics/${topic.id}`);
    } catch (err) {
      error = err.message || "Failed to create topic";
      saving = false;
    }
  }

  function handleCancel() {
    goto("/admin/topics");
  }
</script>

<h1 class="page-title">New Topic</h1>

{#if error}
  <div class="error-banner">{error}</div>
{/if}

<form class="card" on:submit|preventDefault={handleSubmit}>
  <label>
    Title *
    <input
      type="text"
      bind:value={form.title}
      placeholder="Topic title"
      required
      disabled={saving}
    />
  </label>

  <label>
    Description
    <textarea
      bind:value={form.description}
      placeholder="Topic description"
      rows="3"
      disabled={saving}
    />
  </label>

  <label>
    Level
    <input
      type="text"
      bind:value={form.level}
      placeholder="e.g., A1, A2, B1"
      disabled={saving}
    />
  </label>

  <label>
    Prerequisite Topic
    <select bind:value={form.prerequisite_topic_id} disabled={saving}>
      <option value={null}>None</option>
      {#each allTopics as topic}
        <option value={topic.id}>{topic.title}</option>
      {/each}
    </select>
  </label>

  <div class="actions">
    <button type="submit" disabled={saving || loading}>
      {saving ? "Creating…" : "Create Topic"}
    </button>
    <button type="button" on:click={handleCancel} disabled={saving}>
      Cancel
    </button>
  </div>
</form>

<style>
  .page-title {
    font-size: 1.4rem;
    margin-bottom: 1rem;
  }

  .error-banner {
    padding: 0.75rem 1rem;
    background: #fee;
    color: #c33;
    border-radius: 6px;
    margin-bottom: 1rem;
  }

  .card {
    max-width: 640px;
    margin: 0 auto;
    padding: 1.5rem;
    border-radius: 12px;
    background: var(--card-bg);
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-weight: 500;
  }

  textarea,
  input,
  select {
    padding: 0.5rem;
    border-radius: 6px;
    border: 1px solid var(--border);
  }

  .actions {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    margin-top: 1rem;
  }

  button {
    padding: 0.5rem 1rem;
    border-radius: 6px;
    border: 1px solid var(--border);
    cursor: pointer;
    background: white;
  }

  button[type="submit"] {
    background: var(--accent);
    color: white;
    border: none;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
