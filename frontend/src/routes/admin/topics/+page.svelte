<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { adminTopicsAPI } from '$lib/api.js';

  let topics = [];
  let loading = true;
  let error = '';

  async function load() {
    loading = true;
    error = '';

    try {
      topics = await adminTopicsAPI.list();
    } catch (err) {
      error = err.message || 'Failed to load topics';
    } finally {
      loading = false;
    }
  }

  onMount(load);

  function openTopic(topicId) {
    goto(`/admin/topics/${topicId}`);
  }

  async function deleteTopic(topicId, event) {
    event.stopPropagation();
    
    if (!confirm('Delete this topic? This action cannot be undone.')) {
      return;
    }

    try {
      await adminTopicsAPI.delete(topicId);
      topics = topics.filter((t) => t.id !== topicId);
    } catch (err) {
      alert(err.message || 'Failed to delete topic');
    }
  }
</script>

<h1 class="page-title">Topics</h1>

<div class="toolbar">
  <button class="primary" on:click={() => goto("/admin/topics/new")}>
    + New Topic
  </button>
</div>

{#if loading}
  <div class="state">Loading topics…</div>

{:else if error}
  <div class="state error">{error}</div>

{:else if topics.length === 0}
  <div class="state">No topics found.</div>

{:else}
  <table class="topics-table">
    <thead>
      <tr>
        <th>Title</th>
        <th>Level</th>
        <th>Questions</th>
        <th>Status</th>
        <th></th>
      </tr>
    </thead>

    <tbody>
      {#each topics as topic}
        <tr>
          <td>{topic.title}</td>
          <td>{topic.level ?? '—'}</td>
          <td>{topic.question_count ?? '—'}</td>
          <td>
            <span class="status active">
              Active
            </span>
          </td>
          <td class="actions">
            <button
              class="link"
              on:click={() => openTopic(topic.id)}
            >
              View →
            </button>
            <button
              class="link"
              on:click={() => goto(`/admin/topics/${topic.id}`)}
            >
              Edit
            </button>
            <button
              class="link danger"
              on:click={(e) => deleteTopic(topic.id, e)}
            >
              Delete
            </button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}

<style>
  .page-title {
    font-size: 1.4rem;
    margin-bottom: 1rem;
  }

  .state {
    padding: 2rem;
    text-align: center;
    color: var(--muted);
  }

  .state.error {
    color: #c33;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background: var(--panel);
    border-radius: 8px;
    overflow: hidden;
  }

  th, td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
    text-align: left;
  }

  th {
    font-size: 0.8rem;
    text-transform: uppercase;
    color: var(--muted);
  }

  tr:hover {
    background: var(--hover);
  }

  .status {
    font-size: 0.75rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
  }

  .status.active {
    background: #e6f6ea;
    color: #1e7f4f;
  }

  .toolbar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1rem;
  }

  .primary {
    background: var(--accent);
    color: white;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    border: none;
    cursor: pointer;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
  }

  .link {
    background: none;
    border: none;
    color: var(--accent);
    cursor: pointer;
    font-size: 0.9rem;
  }

  .link.danger {
    color: #c33;
  }
</style>
