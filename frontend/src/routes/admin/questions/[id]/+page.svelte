<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { adminQuestionsAPI, topicsAPI } from "$lib/api.js";
  import QuestionForm from "../../QuestionForm.svelte";

  let question = null;
  let topics = [];
  let loading = true;
  let saving = false;
  let error = "";

  $: questionId = Number($page.params.id);

  onMount(async () => {
    if (!questionId) {
      error = "Invalid question ID";
      loading = false;
      return;
    }

    try {
      [question, topics] = await Promise.all([
        adminQuestionsAPI.get(questionId),
        topicsAPI.list(),
      ]);
    } catch (err) {
      error = err.message || "Failed to load question";
    } finally {
      loading = false;
    }
  });

  async function handleSubmit(data) {
    saving = true;
    error = "";

    try {
      await adminQuestionsAPI.update(questionId, data);
      goto("/admin/questions");
    } catch (err) {
      error = err.message || "Failed to update question";
      saving = false;
    }
  }

  function handleCancel() {
    goto("/admin/questions");
  }
</script>

{#if loading}
  <div class="state">Loading question…</div>

{:else if error && !question}
  <div class="state error">
    <p>{error}</p>
    <button on:click={() => goto("/admin/questions")}>
      ← Back to questions
    </button>
  </div>

{:else if question}
  <h1 class="page-title">Edit Question</h1>

  {#if error}
    <div class="error-banner">{error}</div>
  {/if}

  <QuestionForm
    {topics}
    initialData={question}
    {loading}
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
