<script>
  import "../app.css";
  import { page } from '$app/stores';
  import { fade } from 'svelte/transition';
  import { isAuthenticated, logout } from '$lib/auth.js';
  import { goto } from '$app/navigation';

  function handleLogout() {
    logout();
    goto('/auth/login');
  }
</script>

<header class="header">
  <nav class="nav">
    <a href="/" class="logo">🍫 Chocolingo</a>

    <div class="links">
      <a
        href="/"
        class:active={$page.url.pathname === '/'}
      >
        Home
      </a>

      {#if $isAuthenticated}
        <a
          href="/dashboard"
          class:active={$page.url.pathname.startsWith('/dashboard')}
        >
          Dashboard
        </a>

        <a
          href="/topics"
          class:active={$page.url.pathname.startsWith('/topics')}
        >
          Topics
        </a>

        <a
          href="/map"
          class:active={$page.url.pathname.startsWith('/map')}
        >
          Map
        </a>

        <button class="logout-btn" on:click={handleLogout}>
          Logout
        </button>
      {:else}
        <a
          href="/auth/login"
          class:active={$page.url.pathname.startsWith('/auth/login')}
        >
          Login
        </a>

        <a
          href="/auth/register"
          class:active={$page.url.pathname.startsWith('/auth/register')}
        >
          Sign Up
        </a>
      {/if}
    </div>
  </nav>
</header>

<main class="content">
  {#key $page.url.pathname}
    <div in:fade={{ duration: 250 }}>
      <slot />
    </div>
  {/key}
</main>

<style>
  .header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
  }

  .nav {
    max-width: 900px;
    margin: auto;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .logo {
    font-weight: 700;
    text-decoration: none;
    color: var(--text);
  }

  .links {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .links a {
    text-decoration: none;
    color: var(--muted);
    padding-bottom: 0.25rem;
  }

  .links a:hover {
    color: var(--accent);
  }

  /* ⭐ Active link styling */
  .links a.active {
    color: var(--accent);
    border-bottom: 2px solid var(--accent);
  }

  .logout-btn {
    background: none;
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .logout-btn:hover {
    color: var(--accent);
    border-color: var(--accent);
  }

  .content {
    max-width: 900px;
    margin: auto;
    padding: 1.5rem;
  }
</style>
