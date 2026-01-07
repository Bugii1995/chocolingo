<script>
  import { onMount } from 'svelte';
  import { progressAPI, topicsAPI, quizAPI } from '$lib/api.js';
  import { goto } from '$app/navigation';
  import { isAuthenticated } from '$lib/auth.js';

  let today = {
    goal: 5,
    completed: 0,
    streak: 0
  };

  let progress = {
    answered: 0,
    accuracy: 0
  };

  let loading = true;
  let error = '';

  onMount(async () => {
    // Redirect to login if not authenticated
    isAuthenticated.subscribe((auth) => {
      if (!auth) {
        goto('/auth/login');
      }
    });

    try {
      const stats = await progressAPI.getDashboard();
      today = {
        goal: stats.today_goal,
        completed: stats.today_completed,
        streak: stats.streak
      };
      progress = {
        answered: stats.total_answered,
        accuracy: stats.accuracy
      };
      loading = false;
    } catch (err) {
      error = err.message || 'Failed to load dashboard';
      loading = false;
    }
  });

  async function continueLearning() {
    try {
      // Get first available topic
      const topics = await topicsAPI.list();
      if (topics.length > 0) {
        const session = await quizAPI.createSession(topics[0].id, 'normal');
        goto(`/quiz/${session.id}`);
      } else {
        goto('/topics');
      }
    } catch (err) {
      error = err.message || 'Failed to start quiz';
    }
  }
</script>

<main class="page">
  <!-- Header -->
  <header class="page-header">
    <h1>Dashboard</h1>
    <p class="subtitle">
      Small steps, taken consistently.
    </p>
  </header>

  {#if loading}
    <div class="loading">Loading dashboard...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <!-- Today / Continue -->
    <section class="card highlight">
      <h2>Today</h2>

      <p class="muted">
        {today.completed} / {today.goal} questions completed · 🔥 {today.streak}-day streak
      </p>

      <button class="primary" on:click={continueLearning}>
        Continue learning
      </button>
    </section>

    <!-- Progress snapshot -->
    <section class="card">
      <h2>Progress</h2>

      <div class="stats">
        <div class="stat">
          <strong>{progress.answered}</strong>
          <span class="muted">answered</span>
        </div>

        <div class="stat">
          <strong>{Math.round(progress.accuracy)}%</strong>
          <span class="muted">accuracy</span>
        </div>
      </div>
    </section>

    <!-- Explore -->
    <section class="card">
      <h2>Explore</h2>

      <div class="links">
        <a href="/map" class="link-card">
          <span class="emoji">🧠</span>
          <div>
            <strong>Knowledge Map</strong>
            <p class="muted">See how your knowledge grows</p>
          </div>
        </a>

        <a href="/topics" class="link-card">
          <span class="emoji">📚</span>
          <div>
            <strong>Topics</strong>
            <p class="muted">Browse what you can learn</p>
          </div>
        </a>
      </div>
    </section>
  {/if}
</main>

<style>
  /* Page container */
  .page {
    max-width: 640px;
    margin: 0 auto;
    padding: 2rem 1rem 3rem;
    display: flex;
    flex-direction: column;
    gap: 1.6rem;
  }

  /* Header */
  .page-header h1 {
    margin-bottom: 0.25rem;
  }

  .subtitle {
    color: var(--muted);
    font-size: 0.95rem;
  }

  .loading,
  .error {
    text-align: center;
    padding: 2rem;
    color: var(--muted);
  }

  .error {
    color: #c33;
  }

  /* Cards */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.2rem;
  }

  .card h2 {
    margin-top: 0;
    margin-bottom: 0.6rem;
    font-size: 1rem;
  }

  .highlight {
    background: var(--accent-soft);
  }

  /* Text */
  .muted {
    color: var(--muted);
    font-size: 0.9rem;
  }

  /* Primary CTA */
  .primary {
    margin-top: 0.8rem;
    padding: 0.6rem 1.4rem;
    border-radius: 999px;
    border: none;
    background: var(--accent);
    color: white;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .primary:hover {
    background: var(--accent-hover);
  }

  /* Stats */
  .stats {
    display: flex;
    gap: 2.5rem;
    margin-top: 0.6rem;
  }

  .stat {
    display: flex;
    flex-direction: column;
  }

  .stat strong {
    font-size: 1.4rem;
  }

  /* Explore links */
  .links {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    margin-top: 0.6rem;
  }

  .link-card {
    display: flex;
    gap: 0.8rem;
    padding: 0.8rem;
    border-radius: 14px;
    text-decoration: none;
    color: var(--text);
    background: #f9f9f8;
  }

  .link-card:hover {
    background: #f3f3f2;
  }

  .emoji {
    font-size: 1.4rem;
  }
</style>
