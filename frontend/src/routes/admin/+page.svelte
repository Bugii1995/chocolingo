<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { adminDashboardAPI } from "$lib/api.js";

  let stats = null;
  let loading = true;
  let error = "";

  onMount(async () => {
    try {
      stats = await adminDashboardAPI.getStats();
    } catch (err) {
      error = err.message || "Failed to load dashboard statistics";
    } finally {
      loading = false;
    }
  });
</script>

<h1 class="page-title">Admin Dashboard</h1>

{#if loading}
  <div class="state">Loading dashboard…</div>

{:else if error}
  <div class="state error">{error}</div>

{:else if stats}
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-icon">📚</div>
      <div class="stat-content">
        <div class="stat-value">{stats.total_topics}</div>
        <div class="stat-label">Total Topics</div>
      </div>
      <button class="stat-action" on:click={() => goto("/admin/topics")}>
        View →
      </button>
    </div>

    <div class="stat-card">
      <div class="stat-icon">❓</div>
      <div class="stat-content">
        <div class="stat-value">{stats.total_questions}</div>
        <div class="stat-label">Total Questions</div>
        <div class="stat-sublabel">
          {stats.active_questions} active, {stats.inactive_questions} inactive
        </div>
      </div>
      <button class="stat-action" on:click={() => goto("/admin/questions")}>
        View →
      </button>
    </div>

    <div class="stat-card">
      <div class="stat-icon">👥</div>
      <div class="stat-content">
        <div class="stat-value">{stats.total_users}</div>
        <div class="stat-label">Total Users</div>
      </div>
    </div>

    <div class="stat-card highlight">
      <div class="stat-icon">✅</div>
      <div class="stat-content">
        <div class="stat-value">{stats.active_questions}</div>
        <div class="stat-label">Active Questions</div>
      </div>
    </div>
  </div>

  <div class="quick-actions">
    <h2>Quick Actions</h2>
    <div class="actions-grid">
      <button class="action-btn" on:click={() => goto("/admin/topics/new")}>
        <span class="action-icon">➕</span>
        <span>Create Topic</span>
      </button>
      <button class="action-btn" on:click={() => goto("/admin/questions/new")}>
        <span class="action-icon">➕</span>
        <span>Create Question</span>
      </button>
      <button class="action-btn" on:click={() => goto("/admin/topics")}>
        <span class="action-icon">📋</span>
        <span>Manage Topics</span>
      </button>
      <button class="action-btn" on:click={() => goto("/admin/questions")}>
        <span class="action-icon">📋</span>
        <span>Manage Questions</span>
      </button>
    </div>
  </div>
{/if}

<style>
  .page-title {
    font-size: 1.8rem;
    margin-bottom: 2rem;
    font-weight: 600;
  }

  .state {
    padding: 2rem;
    text-align: center;
    color: var(--muted);
  }

  .state.error {
    color: #c33;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .stat-card {
    background: var(--panel);
    border-radius: 12px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    border: 1px solid var(--border);
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .stat-card.highlight {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
  }

  .stat-icon {
    font-size: 2.5rem;
    line-height: 1;
  }

  .stat-content {
    flex: 1;
  }

  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.25rem;
  }

  .stat-label {
    font-size: 0.9rem;
    opacity: 0.8;
    font-weight: 500;
  }

  .stat-sublabel {
    font-size: 0.75rem;
    opacity: 0.7;
    margin-top: 0.25rem;
  }

  .stat-action {
    background: none;
    border: 1px solid var(--border);
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    color: var(--accent);
  }

  .stat-card.highlight .stat-action {
    border-color: rgba(255, 255, 255, 0.3);
    color: white;
  }

  .quick-actions {
    margin-top: 2rem;
  }

  .quick-actions h2 {
    font-size: 1.2rem;
    margin-bottom: 1rem;
    font-weight: 600;
  }

  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .action-btn {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .action-btn:hover {
    background: var(--hover);
    border-color: var(--accent);
    transform: translateY(-2px);
  }

  .action-icon {
    font-size: 1.5rem;
  }
</style>

