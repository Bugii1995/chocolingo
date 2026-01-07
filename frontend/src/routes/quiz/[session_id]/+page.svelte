<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { quizAPI } from '$lib/api.js';
  import Quiz from '$lib/components/Quiz.svelte';
  import { page } from '$app/stores';

  let session = null;
  let loading = true;
  let error = '';

  // ✅ Correct reactive access to route params
  $: sessionId = Number($page.params.session_id);

  onMount(async () => {
    if (!sessionId) {
      error = 'Invalid quiz session';
      loading = false;
      return;
    }

    try {
      session = await quizAPI.getSession(sessionId);
    } catch (err) {
      error = err.message || 'Failed to load quiz';
    } finally {
      loading = false;
    }
  });

  // ✅ Svelte event handler (NOT a prop callback)
  function handleComplete(event) {
    // event.detail can contain results later
    goto('/dashboard');
  }
</script>

<main class="page">
  {#if loading}
    <div class="loading">Loading quiz…</div>

  {:else if error}
    <div class="error">
      <p>{error}</p>
      <button on:click={() => goto('/dashboard')}>
        Back to dashboard
      </button>
    </div>

  {:else if session}
    <header class="quiz-header">
      <h1>{session.topic?.title ?? 'Quiz'}</h1>
      <p class="meta">
        {session.total_questions} questions
      </p>
    </header>

    <!-- ✅ CORRECT SVELTE EVENT LISTENING -->
    <Quiz
      sessionId={session.id}
      questions={session.questions}
      on:complete={handleComplete}
    />
  {/if}
</main>

<style>
  .page {
    min-height: 60vh;
    padding: 1.5rem;
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

  .quiz-header {
    margin-bottom: 1.5rem;
    text-align: center;
  }

  .quiz-header h1 {
    font-size: 1.5rem;
    margin-bottom: 0.25rem;
  }

  .meta {
    font-size: 0.9rem;
    color: var(--muted);
  }

  button {
    margin-top: 1rem;
  }
</style>
