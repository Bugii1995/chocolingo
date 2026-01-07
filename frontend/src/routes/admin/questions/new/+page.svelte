<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { adminQuestionsAPI, topicsAPI } from "$lib/api.js";
  import QuestionForm from "../../QuestionForm.svelte";

  let topics = [];
  let loading = true;
  let saving = false;
  let error = "";

  $: topicParam = $page.url.searchParams.get("topic");

  onMount(async () => {
    try {
      topics = await topicsAPI.list();
    } catch (err) {
      error = err.message || "Failed to load topics";
    } finally {
      loading = false;
    }
  });

  async function handleSubmit(data) {
    saving = true;
    error = "";

    try {
      // If topic param is provided, use it
      if (topicParam && !data.topic_id) {
        data.topic_id = Number(topicParam);
      }

      await adminQuestionsAPI.create(data);
      goto("/admin/questions");
    } catch (err) {
      error = err.message || "Failed to create question";
      saving = false;
    }
  }

  function handleCancel() {
    goto("/admin/questions");
  }
</script>

{#if loading}
  <div class="state">Loading…</div>

{:else if error && topics.length === 0}
  <div class="state error">
    <p>{error}</p>
    <button on:click={() => goto("/admin/questions")}>
      ← Back to questions
    </button>
  </div>

{:else}
  <h1 class="page-title">New Question</h1>

  {#if error}
    <div class="error-banner">{error}</div>
  {/if}

  <QuestionForm
    {topics}
    initialData={topicParam ? { topic_id: Number(topicParam) } : null}
    loading={saving}
    on:submit={(e) => handleSubmit(e.detail)}
    on:cancel={handleCancel}
  />
{/if}

<style>
  .page-title {
    font-size: 1.4rem;
    margin-bottom: 1rem;
  }

  .state {
    padding: 2rem;
    text-align: center;
    color: var(--muted);
  }

  .state.error {
    color: #c33;
  }

  .error-banner {
    padding: 0.75rem 1rem;
    background: #fee;
    color: #c33;
    border-radius: 6px;
    margin-bottom: 1rem;
  }
</style>
