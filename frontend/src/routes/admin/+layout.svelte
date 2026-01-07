<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authAPI } from '$lib/api.js';
  import AdminSidebar from '$lib/components/admin/AdminSidebar.svelte';

  let loading = true;
  let user = null;
  let error = '';
  let isAdmin = false;

  onMount(async () => {
    try {
      user = await authAPI.getCurrentUser();

      /**
       * TEMP RULE (until roles are added):
       * any logged-in user can access admin
       *
       * FINAL RULE (later):
       * user.role === 'admin' || user.role === 'superadmin'
       */
      isAdmin = true;

      if (!isAdmin) {
        goto('/dashboard');
      }
    } catch (err) {
      goto('/login');
    } finally {
      loading = false;
    }
  });
</script>

{#if loading}
  <div class="admin-loading">
    Checking admin access…
  </div>

{:else}
  <div class="admin-layout">
    <AdminSidebar />

    <main class="admin-content">
      <slot />
    </main>
  </div>
{/if}

<style>
  .admin-loading {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    color: var(--muted);
  }

  .admin-layout {
    min-height: 100vh;
    display: flex;
    background: var(--bg);
  }

  .admin-content {
    flex: 1;
    padding: 1.5rem;
    overflow-y: auto;
  }
</style>
