<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { adminTopicsAPI, adminQuestionsAPI } from '$lib/api.js';

  let topic = null;
  let questions = [];
  let loading = true;
  let error = '';
  let editing = false;
  let saving = false;

  $: topicId = Number($page.params.id);

  let editForm = {
    title: '',
    description: '',
    level: '',
    prerequisite_topic_id: null,
  };

  let allTopics = [];

  async function load() {
    loading = true;
    error = '';

    if (!topicId) {
      error = 'Invalid topic';
      loading = false;
      return;
    }

    try {
      [topic, questionsResponse, allTopics] = await Promise.all([
        adminTopicsAPI.get(topicId),
        adminQuestionsAPI.list({ topicId: topicId, page: 1, pageSize: 100 }),
        adminTopicsAPI.list(),
      ]);

      // Handle paginated response
      questions = questionsResponse.items || questionsResponse || [];

      // Initialize edit form
      editForm = {
        title: topic.title || '',
        description: topic.description || '',
        level: topic.level || '',
        prerequisite_topic_id: topic.prerequisite_topic_id || null,
      };
    } catch (err) {
      error = err.message || 'Failed to load topic';
    } finally {
      loading = false;
    }
  }

  onMount(load);

  function addQuestion() {
    goto(`/admin/questions/new?topic=${topicId}`);
  }

  function startEdit() {
    editing = true;
  }

  function cancelEdit() {
    editing = false;
    // Reset form
    editForm = {
      title: topic.title || '',
      description: topic.description || '',
      level: topic.level || '',
      prerequisite_topic_id: topic.prerequisite_topic_id || null,
    };
  }

  async function saveEdit() {
    saving = true;
    error = '';

    try {
      const updateData = {};
      if (editForm.title !== topic.title) updateData.title = editForm.title;
      if (editForm.description !== topic.description) updateData.description = editForm.description;
      if (editForm.level !== topic.level) updateData.level = editForm.level;
      if (editForm.prerequisite_topic_id !== topic.prerequisite_topic_id) {
        updateData.prerequisite_topic_id = editForm.prerequisite_topic_id || null;
      }

      topic = await adminTopicsAPI.update(topicId, updateData);
      editing = false;
    } catch (err) {
      error = err.message || 'Failed to update topic';
    } finally {
      saving = false;
    }
  }
</script>

{#if loading}
  <div class="state">Loading topic…</div>

{:else if error}
  <div class="state error">
    <p>{error}</p>
    <button on:click={() => goto('/admin/topics')}>
      ← Back to topics
    </button>
  </div>

{:else if topic}
  {#if error}
    <div class="error-banner">{error}</div>
  {/if}

  <header class="topic-header">
    <div>
      {#if editing}
        <div class="edit-form">
          <input
            type="text"
            bind:value={editForm.title}
            placeholder="Title"
            class="title-input"
          />
          <textarea
            bind:value={editForm.description}
            placeholder="Description"
            rows="2"
            class="desc-input"
          />
        </div>
      {:else}
        <h1>{topic.title}</h1>
        <p class="desc">{topic.description ?? 'No description'}</p>
      {/if}
    </div>

    <div class="header-actions">
      {#if editing}
        <button class="primary" on:click={saveEdit} disabled={saving}>
          {saving ? 'Saving…' : 'Save'}
        </button>
        <button on:click={cancelEdit} disabled={saving}>Cancel</button>
      {:else}
        <button on:click={startEdit}>Edit Topic</button>
        <button class="primary" on:click={addQuestion}>
          + Add Question
        </button>
      {/if}
    </div>
  </header>

  <section class="meta">
    {#if editing}
      <div class="meta-edit">
        <label>
          Level:
          <input
            type="text"
            bind:value={editForm.level}
            placeholder="e.g., A1, A2"
          />
        </label>
        <label>
          Prerequisite Topic:
          <select bind:value={editForm.prerequisite_topic_id}>
            <option value={null}>None</option>
            {#each allTopics.filter((t) => t.id !== topicId) as t}
              <option value={t.id}>{t.title}</option>
            {/each}
          </select>
        </label>
      </div>
    {:else}
      <span><strong>Level:</strong> {topic.level ?? '—'}</span>
      <span><strong>Questions:</strong> {topic.question_count ?? questions.length}</span>
      {#if topic.prerequisite_topic_id}
        <span>
          <strong>Prerequisite:</strong> {
            allTopics.find((t) => t.id === topic.prerequisite_topic_id)?.title ??
            topic.prerequisite_topic_id
          }
        </span>
      {/if}
    {/if}
  </section>

  {#if questions.length === 0}
    <div class="state">No questions yet.</div>

  {:else}
    <table class="questions-table">
      <thead>
        <tr>
          <th>Prompt</th>
          <th>Type</th>
          <th>Difficulty</th>
          <th>Status</th>
        </tr>
      </thead>

      <tbody>
        {#each questions as q}
          <tr>
            <td class="prompt">
              <a href="/admin/questions/{q.id}">{q.prompt}</a>
            </td>
            <td>{q.question_type}</td>
            <td>
              <span class="badge">{q.difficulty ?? 'easy'}</span>
            </td>
            <td>
              {#if q.is_active}
                <span class="status active">Active</span>
              {:else}
                <span class="status inactive">Inactive</span>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
{/if}

<style>
  .state {
    padding: 2rem;
    text-align: center;
    color: var(--muted);
  }

  .state.error {
    color: #c33;
  }

  .error-banner {
    padding: 0.75rem 1rem;
    background: #fee;
    color: #c33;
    border-radius: 6px;
    margin-bottom: 1rem;
  }

  .topic-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .topic-header h1 {
    font-size: 1.4rem;
    margin-bottom: 0.25rem;
  }

  .desc {
    color: var(--muted);
    font-size: 0.9rem;
  }

  .edit-form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
  }

  .title-input,
  .desc-input {
    padding: 0.5rem;
    border-radius: 6px;
    border: 1px solid var(--border);
    font-size: 1rem;
  }

  .title-input {
    font-weight: 600;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
  }

  .meta-edit {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .meta-edit label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.85rem;
  }

  .meta-edit input,
  .meta-edit select {
    padding: 0.4rem;
    border-radius: 4px;
    border: 1px solid var(--border);
  }

  .meta {
    display: flex;
    gap: 2rem;
    font-size: 0.85rem;
    margin-bottom: 1.25rem;
    color: var(--muted);
  }

  .primary {
    background: var(--accent);
    color: white;
    padding: 0.5rem 0.9rem;
    border-radius: 6px;
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
    vertical-align: top;
  }

  th {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--muted);
  }

  tr:hover {
    background: var(--hover);
  }

  .prompt {
    max-width: 420px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .prompt a {
    color: var(--accent);
    text-decoration: none;
  }

  .prompt a:hover {
    text-decoration: underline;
  }

  .badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    background: #eef;
  }

  .status {
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
  }

  .status.active {
    background: #e6f6ea;
    color: #1e7f4f;
  }

  .status.inactive {
    background: #fdeaea;
    color: #b23b3b;
  }
</style>
