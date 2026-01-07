<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { quizAPI } from '$lib/api.js';
  import Quiz from '$lib/components/Quiz.svelte';
  import { page } from '$app/stores';

  let session = null;
  let loading = true;
  let error = '';

  const sessionId = parseInt($page.params.session_id);

  onMount(async () => {
    try {
      session = await quizAPI.getSession(sessionId);
      loading = false;
    } catch (err) {
      error = err.message || 'Failed to load quiz';
      loading = false;
    }
  });

  function handleComplete(results) {
    // Navigate to dashboard or topic page
    goto('/dashboard');
  }
</script>

<main class="page">
  {#if loading}
    <div class="loading">Loading quiz...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else if session}
    <Quiz
      sessionId={session.id}
      questions={session.questions}
      onComplete={handleComplete}
    />
  {/if}
</main>

<style>
  .page {
    min-height: 60vh;
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
</style>
