<script>
  import { login, isAuthenticated } from '$lib/auth.js';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  let username = '';
  let password = '';
  let error = '';
  let loading = false;

  onMount(() => {
    // Redirect if already authenticated
    isAuthenticated.subscribe((auth) => {
      if (auth) {
        goto('/dashboard');
      }
    });
  });

  async function handleSubmit() {
    error = '';
    loading = true;

    const result = await login(username, password);

    if (result.success) {
      goto('/dashboard');
    } else {
      error = result.error || 'Login failed';
      loading = false;
    }
  }
</script>

<main class="page">
  <header class="page-header">
    <h1>Welcome back</h1>
    <p class="subtitle">Sign in to continue learning</p>
  </header>

  <form class="card" on:submit|preventDefault={handleSubmit}>
    {#if error}
      <div class="error">{error}</div>
    {/if}

    <div class="form-group">
      <label for="username">Username</label>
      <input
        id="username"
        type="text"
        bind:value={username}
        required
        disabled={loading}
        autocomplete="username"
      />
    </div>

    <div class="form-group">
      <label for="password">Password</label>
      <input
        id="password"
        type="password"
        bind:value={password}
        required
        disabled={loading}
        autocomplete="current-password"
      />
    </div>

    <button type="submit" class="primary" disabled={loading}>
      {loading ? 'Signing in...' : 'Sign in'}
    </button>

    <p class="form-footer">
      Don't have an account? <a href="/auth/register">Sign up</a>
    </p>
  </form>
</main>

<style>
  .page {
    max-width: 400px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  .page-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .page-header h1 {
    margin-bottom: 0.5rem;
  }

  .subtitle {
    color: var(--muted);
    font-size: 0.95rem;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.5rem;
  }

  .error {
    background: #fee;
    color: #c33;
    padding: 0.75rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }

  .form-group {
    margin-bottom: 1.2rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    font-weight: 500;
  }

  .form-group input {
    width: 100%;
    padding: 0.6rem 0.8rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 1rem;
    box-sizing: border-box;
  }

  .form-group input:focus {
    outline: none;
    border-color: var(--accent);
  }

  .form-group input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .primary {
    width: 100%;
    margin-top: 0.5rem;
    padding: 0.7rem;
    border-radius: 999px;
    border: none;
    background: var(--accent);
    color: white;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
  }

  .primary:hover:not(:disabled) {
    background: var(--accent-hover);
  }

  .primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .form-footer {
    text-align: center;
    margin-top: 1.5rem;
    color: var(--muted);
    font-size: 0.9rem;
  }

  .form-footer a {
    color: var(--accent);
    text-decoration: none;
  }

  .form-footer a:hover {
    text-decoration: underline;
  }
</style>
