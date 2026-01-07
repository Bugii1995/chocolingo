<script>
  import { createEventDispatcher } from "svelte";

  export let topics = [];
  export let initialData = null; // null = create, object = edit
  export let loading = false;

  const dispatch = createEventDispatcher();

  let form = {
    topic_id: "",
    prompt: "",
    question_type: "fill_blank",
    choices: [],
    correct_answer: "",
    explanation: "",
    hint: "",
    difficulty: "easy",
    tags: "",
    is_active: true,
  };

  // Populate form if editing
  if (initialData) {
    form = {
      ...form,
      ...initialData,
      topic_id: initialData.topic_id ? String(initialData.topic_id) : "",
      tags: (initialData.tags || []).join(", "),
    };
  }

  function addChoice() {
    form.choices = [...form.choices, ""];
  }

  function removeChoice(index) {
    form.choices = form.choices.filter((_, i) => i !== index);
  }

  function submitForm() {
    if (!form.topic_id || !form.prompt || !form.correct_answer) {
      alert("Topic, prompt, and correct answer are required.");
      return;
    }

    if (
      form.question_type === "multiple_choice" &&
      form.choices.length < 2
    ) {
      alert("Multiple choice questions need at least 2 choices.");
      return;
    }

    dispatch("submit", {
      ...form,
      topic_id: Number(form.topic_id),
      tags: form.tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
    });
  }
</script>

<form class="card" on:submit|preventDefault={submitForm}>
  <h2>{initialData ? "Edit Question" : "New Question"}</h2>

  <!-- Topic -->
  <label>
    Topic
    <select bind:value={form.topic_id} required>
      <option value="">Select topic</option>
      {#each topics as topic}
        <option value={topic.id}>{topic.title}</option>
      {/each}
    </select>
  </label>

  <!-- Prompt -->
  <label>
    Prompt
    <textarea bind:value={form.prompt} rows="3" required />
  </label>

  <!-- Type -->
  <label>
    Question Type
    <select bind:value={form.question_type}>
      <option value="fill_blank">Fill in the blank</option>
      <option value="multiple_choice">Multiple choice</option>
    </select>
  </label>

  <!-- Choices -->
  {#if form.question_type === "multiple_choice"}
    <div class="choices">
      <label>Choices</label>

      {#each form.choices as choice, i}
        <div class="choice-row">
          <input
            type="text"
            bind:value={form.choices[i]}
            placeholder={`Choice ${i + 1}`}
            required
          />
          <button type="button" on:click={() => removeChoice(i)}>✕</button>
        </div>
      {/each}

      <button type="button" on:click={addChoice}>+ Add choice</button>
    </div>
  {/if}

  <!-- Correct answer -->
  <label>
    Correct Answer
    <input type="text" bind:value={form.correct_answer} required />
  </label>

  <!-- Hint -->
  <label>
    Hint (optional)
    <input type="text" bind:value={form.hint} />
  </label>

  <!-- Explanation -->
  <label>
    Explanation
    <textarea bind:value={form.explanation} rows="2" />
  </label>

  <!-- Difficulty -->
  <label>
    Difficulty
    <select bind:value={form.difficulty}>
      <option value="easy">Easy</option>
      <option value="medium">Medium</option>
      <option value="hard">Hard</option>
    </select>
  </label>

  <!-- Tags -->
  <label>
    Tags (comma separated)
    <input type="text" bind:value={form.tags} />
  </label>

  <!-- Actions -->
  <div class="actions">
    <button type="submit" disabled={loading}>
      {loading ? "Saving…" : "Save"}
    </button>
    <button type="button" on:click={() => dispatch("cancel")}>
      Cancel
    </button>
  </div>
</form>

<style>
  .card {
    max-width: 640px;
    margin: 0 auto;
    padding: 1.5rem;
    border-radius: 12px;
    background: var(--card-bg);
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-weight: 500;
  }

  textarea,
  input,
  select {
    padding: 0.5rem;
    border-radius: 6px;
    border: 1px solid var(--border);
  }

  .choices {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .choice-row {
    display: flex;
    gap: 0.5rem;
  }

  .actions {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    margin-top: 1rem;
  }
</style>
