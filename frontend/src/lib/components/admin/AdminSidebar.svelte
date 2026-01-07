<script>
  import { goto } from '$app/navigation';
</script>

<aside class="sidebar">
  <h2 class="title">Admin</h2>

  <nav>
    <button on:click={() => goto('/admin')}>
      Dashboard
    </button>

    <button on:click={() => goto('/admin/topics')}>
      Topics
    </button>

    <button on:click={() => goto('/admin/questions')}>
      Questions
    </button>

    <!-- super-admin only later -->
    <!--
    <button on:click={() => goto('/admin/users')}>
      Users
    </button>
    -->
  </nav>
</aside>

<style>
  .sidebar {
    width: 220px;
    padding: 1.25rem;
    border-right: 1px solid var(--border);
    background: var(--panel);
  }

  .title {
    font-size: 1.1rem;
    margin-bottom: 1rem;
  }

  nav button {
    display: block;
    width: 100%;
    text-align: left;
    padding: 0.5rem 0.75rem;
    margin-bottom: 0.25rem;
    border-radius: 6px;
    background: transparent;
  }

  nav button:hover {
    background: var(--hover);
  }
</style>
