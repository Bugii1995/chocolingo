<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { adminQuestionsAPI, topicsAPI } from "$lib/api.js";

  let questions = [];
  let topics = [];
  let loading = true;
  let error = "";

  let selectedTopic = "";
  let currentPage = 1;
  let pageSize = 20;
  let total = 0;
  let totalPages = 0;

  async function load() {
    loading = true;
    error = "";

    try {
      const response = await adminQuestionsAPI.list({
        topicId: selectedTopic ? Number(selectedTopic) : null,
        page: currentPage,
        pageSize: pageSize,
      });

      // Handle both paginated and non-paginated responses
      if (response.items) {
        questions = response.items;
        total = response.total;
        totalPages = response.total_pages;
      } else {
        // Fallback for non-paginated response
        questions = Array.isArray(response) ? response : [];
        total = questions.length;
        totalPages = 1;
      }

      if (topics.length === 0) {
        topics = await topicsAPI.list();
      }
    } catch (err) {
      error = err.message || "Failed to load questions";
    } finally {
      loading = false;
    }
  }

  onMount(load);

  function handleTopicChange() {
    currentPage = 1;
    load();
  }

  function goToPage(page) {
    currentPage = page;
    load();
  }

  async function disableQuestion(id) {
    if (!confirm("Disable this question?")) return;

    try {
      await adminQuestionsAPI.disable(id);
      questions = questions.filter((q) => q.id !== id);
      total -= 1;
    } catch (err) {
      alert(err.message || "Failed to disable question");
    }
  }
</script>

<h1 class="page-title">Questions</h1>

<div class="toolbar">
  <select bind:value={selectedTopic} on:change={handleTopicChange}>
    <option value="">All topics</option>
    {#each topics as t}
      <option value={t.id}>{t.title}</option>
    {/each}
  </select>

  <button class="primary" on:click={() => goto("/admin/questions/new")}>
    + New Question
  </button>
</div>

{#if loading}
  <div class="state">Loading questions…</div>

{:else if error}
  <div class="error">{error}</div>

{:else if questions.length === 0}
  <div class="state">No questions found.</div>

{:else}
  <div class="table-container">
    <table class="table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Prompt</th>
          <th>Topic</th>
          <th>Type</th>
          <th>Difficulty</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        {#each questions as q}
          <tr class:q-disabled={!q.is_active}>
            <td>{q.id}</td>
            <td class="prompt">{q.prompt}</td>
            <td>{q.topic?.title ?? q.topic_id}</td>
            <td class="badge">{q.question_type}</td>
            <td class="badge {q.difficulty}">
              {q.difficulty}
            </td>
            <td>
              {#if q.is_active}
                <span class="status active">Active</span>
              {:else}
                <span class="status disabled">Disabled</span>
              {/if}
            </td>
            <td class="actions">
              <button on:click={() => goto(`/admin/questions/${q.id}`)}>
                Edit
              </button>
              {#if q.is_active}
                <button class="danger" on:click={() => disableQuestion(q.id)}>
                  Disable
                </button>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>

    {#if totalPages > 1}
      <div class="pagination">
        <button
          disabled={currentPage === 1}
          on:click={() => goToPage(currentPage - 1)}
        >
          ← Previous
        </button>

        <div class="page-info">
          Page {currentPage} of {totalPages} ({total} total)
        </div>

        <div class="page-numbers">
          {#each Array(Math.min(5, totalPages)) as _, i}
            {@const pageNum = currentPage <= 3
              ? i + 1
              : currentPage >= totalPages - 2
                ? totalPages - 4 + i
                : currentPage - 2 + i}
            {#if pageNum >= 1 && pageNum <= totalPages}
              <button
                class:active={currentPage === pageNum}
                on:click={() => goToPage(pageNum)}
              >
                {pageNum}
              </button>
            {/if}
          {/each}
        </div>

        <button
          disabled={currentPage === totalPages}
          on:click={() => goToPage(currentPage + 1)}
        >
          Next →
        </button>
      </div>
    {/if}
  </div>
{/if}

<style>
  .page-title {
    font-size: 1.4rem;
    margin-bottom: 1rem;
  }

  .toolbar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
    gap: 1rem;
  }

  select {
    padding: 0.4rem;
    border-radius: 6px;
  }

  .primary {
    background: var(--accent);
    color: white;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    border: none;
    cursor: pointer;
  }

  .state,
  .error {
    padding: 2rem;
    text-align: center;
    color: var(--muted);
  }

  .error {
    color: #c33;
  }

  .table-container {
    background: var(--panel);
    border-radius: 8px;
    overflow-x: auto;
    overflow-y: visible;
  }

  .table {
    width: 100%;
    border-collapse: collapse;
  }

  th,
  td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
    text-align: left;
    vertical-align: top;
  }

  th {
    font-size: 0.8rem;
    text-transform: uppercase;
    color: var(--muted);
    background: var(--hover);
  }

  .prompt {
    max-width: 360px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .badge {
    font-size: 0.75rem;
    padding: 0.15rem 0.4rem;
    border-radius: 6px;
    background: #eee;
  }

  .badge.easy {
    background: #e6f7ec;
  }

  .badge.medium {
    background: #fff3cd;
  }

  .badge.hard {
    background: #fdecea;
  }

  .status {
    font-size: 0.75rem;
    font-weight: 600;
  }

  .status.active {
    color: #2e7d32;
  }

  .status.disabled {
    color: #999;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
  }

  button {
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: white;
    cursor: pointer;
    font-size: 0.85rem;
  }


  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .danger {
    color: #c33;
    border-color: #c33;
  }

  tr.q-disabled {
    opacity: 0.5;
  }

  .pagination {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-top: 1px solid var(--border);
    gap: 1rem;
    flex-wrap: wrap;
  }

  .page-info {
    color: var(--muted);
    font-size: 0.9rem;
  }

  .page-numbers {
    display: flex;
    gap: 0.5rem;
  }

  .page-numbers button {
    min-width: 2.5rem;
    padding: 0.4rem 0.6rem;
  }

  .page-numbers button.active {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
  }
</style>
