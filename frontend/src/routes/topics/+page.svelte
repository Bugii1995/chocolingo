<script>
  import { onMount } from 'svelte';
  import { topicsAPI, quizAPI, progressAPI } from '$lib/api.js';
  import { goto } from '$app/navigation';

  let topics = [];
  let progress = {};
  let loading = true;
  let error = '';
  let startingQuiz = false;

  onMount(async () => {
    try {
      [topics, progressData] = await Promise.all([
        topicsAPI.list(),
        progressAPI.getMap()
      ]);

      // Create progress map
      progressData.clusters.forEach(cluster => {
        cluster.levels.forEach(level => {
          level.nodes.forEach(node => {
            progress[node.id] = {
              mastery: node.mastery,
              status: node.status
            };
          });
        });
      });

      loading = false;
    } catch (err) {
      error = err.message || 'Failed to load topics';
      loading = false;
    }
  });

  async function startQuiz(topicId) {
    if (startingQuiz) return;

    startingQuiz = true;
    error = '';

    try {
      const session = await quizAPI.createSession(topicId, 'normal');
      goto(`/quiz/${session.id}`);
    } catch (err) {
      error = err.message || 'Failed to start quiz';
      startingQuiz = false;
    }
  }

  function getStatusClass(status) {
    if (status === 'completed') return 'completed';
    if (status === 'active') return 'active';
    return 'locked';
  }
</script>

<main class="page">
  <header class="page-header">
    <h1>Topics</h1>
    <p class="subtitle">Choose a topic to start learning</p>
  </header>

  {#if loading}
    <div class="loading">Loading topics...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <div class="topics-grid">
      {#each topics as topic}
        {@const topicProgress = progress[topic.id] || { mastery: 0, status: 'active' }}
        <div class="topic-card" class:locked={topicProgress.status === 'locked'}>
          <div class="topic-header">
            <h2>{topic.title}</h2>
            {#if topic.level}
              <span class="level-badge">{topic.level}</span>
            {/if}
          </div>

          {#if topic.description}
            <p class="topic-description">{topic.description}</p>
          {/if}

          <div class="topic-progress">
            <div class="progress-bar">
              <div
                class="progress-fill"
                style="width: {topicProgress.mastery}%"
              ></div>
            </div>
            <span class="progress-text">{Math.round(topicProgress.mastery)}% mastery</span>
          </div>

          <button
            class="start-button"
            class:primary={topicProgress.status !== 'locked'}
            on:click={() => startQuiz(topic.id)}
            disabled={topicProgress.status === 'locked' || startingQuiz}
          >
            {topicProgress.status === 'locked' ? 'Locked' : 'Start Quiz'}
          </button>
        </div>
      {/each}
    </div>
  {/if}
</main>

<style>
  .page {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  .page-header {
    margin-bottom: 2rem;
  }

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
    padding: 3rem;
    color: var(--muted);
  }

  .error {
    color: #c33;
  }

  .topics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
  }

  .topic-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .topic-card:hover:not(.locked) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .topic-card.locked {
    opacity: 0.6;
  }

  .topic-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    gap: 1rem;
  }

  .topic-header h2 {
    margin: 0;
    font-size: 1.2rem;
  }

  .level-badge {
    background: var(--accent-soft);
    color: var(--accent);
    padding: 0.25rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
  }

  .topic-description {
    color: var(--muted);
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.5;
  }

  .topic-progress {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .progress-bar {
    width: 100%;
    height: 6px;
    background: var(--border);
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--accent);
    transition: width 0.3s ease;
  }

  .progress-text {
    font-size: 0.85rem;
    color: var(--muted);
  }

  .start-button {
    width: 100%;
    padding: 0.7rem;
    border-radius: 999px;
    border: none;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: background 0.2s ease;
  }

  .start-button.primary {
    background: var(--accent);
    color: white;
  }

  .start-button.primary:hover:not(:disabled) {
    background: var(--accent-hover);
  }

  .start-button:not(.primary) {
    background: var(--surface);
    color: var(--muted);
    border: 1px solid var(--border);
    cursor: not-allowed;
  }

  .start-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>
