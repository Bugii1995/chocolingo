<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated } from '$lib/auth.js';

  onMount(() => {
    // Redirect authenticated users to dashboard
    isAuthenticated.subscribe((auth) => {
      if (auth) {
        goto('/dashboard');
      }
    });
  });
</script>

<h1>Welcome to Chocolingo</h1>

<p class="intro">
  Learn languages calmly, one small step at a time.
</p>

<a class="cta" href="/auth/register">
  Get Started →
</a>

<style>
  h1 {
    margin-bottom: 0.5rem;
  }

  .intro {
    color: var(--muted);
  }

  .cta {
    display: inline-block;
    margin-top: 1.5rem;
    padding: 0.6rem 1.4rem;
    border-radius: 999px;
    background: var(--accent);
    color: white;
    text-decoration: none;
  }

  .cta:hover {
    background: var(--accent-hover);
  }
</style>
