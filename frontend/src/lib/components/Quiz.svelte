<script>
  import { quizAPI } from '$lib/api.js';
  import { goto } from '$app/navigation';

  export let sessionId;
  export let questions = [];
  export let onComplete = () => {};

  let currentQuestionIndex = 0;
  let answers = {};
  let submitted = false;
  let loading = false;
  let error = '';
  let results = null;

  function selectAnswer(questionId, answer) {
    if (submitted) return;
    answers[questionId] = answer;
    answers = answers; // Trigger reactivity
  }

  function nextQuestion() {
    if (currentQuestionIndex < questions.length - 1) {
      currentQuestionIndex++;
    }
  }

  function previousQuestion() {
    if (currentQuestionIndex > 0) {
      currentQuestionIndex--;
    }
  }

  async function submitQuiz() {
    if (submitted) return;

    // Check all questions answered
    const unanswered = questions.filter(q => !answers[q.id]);
    if (unanswered.length > 0) {
      error = `Please answer all questions. ${unanswered.length} remaining.`;
      return;
    }

    loading = true;
    error = '';

    try {
      const answerArray = questions.map(q => ({
        question_id: q.id,
        user_answer: answers[q.id]
      }));

      results = await quizAPI.submitAnswers(sessionId, answerArray);
      submitted = true;
      onComplete(results);
    } catch (err) {
      error = err.message || 'Failed to submit quiz';
      loading = false;
    }
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;
  const allAnswered = questions.every(q => answers[q.id]);
</script>

<div class="quiz-container">
  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if results}
    <!-- Results View -->
    <div class="results">
      <h2>Quiz Complete!</h2>
      <div class="score">
        <div class="score-value">{Math.round(results.score)}%</div>
        <div class="score-label">
          {results.correct_answers} / {results.total_questions} correct
        </div>
      </div>

      <div class="answers-review">
        <h3>Review</h3>
        {#each questions as question, idx}
          {@const answer = results.answers.find(a => a.question_id === question.id)}
          <div class="answer-item" class:correct={answer?.is_correct} class:incorrect={answer && !answer.is_correct}>
            <div class="answer-header">
              <span class="question-num">Question {idx + 1}</span>
              <span class="answer-status">
                {answer?.is_correct ? '✓ Correct' : '✗ Incorrect'}
              </span>
            </div>
            <div class="answer-prompt">{question.prompt}</div>
            <div class="answer-details">
              <div>Your answer: <strong>{answer?.user_answer || 'Not answered'}</strong></div>
              {#if answer && !answer.is_correct && answer.correct_answer}
                <div>Correct answer: <strong>{answer.correct_answer}</strong></div>
              {/if}
            </div>
          </div>
        {/each}
      </div>

      <button class="primary" on:click={() => onComplete(results)}>
        Continue
      </button>
    </div>
  {:else if currentQuestion}
    <!-- Quiz View -->
    <div class="quiz">
      <div class="progress-bar">
        <div class="progress-fill" style="width: {progress}%"></div>
      </div>

      <div class="question-header">
        <span class="question-number">
          Question {currentQuestionIndex + 1} of {questions.length}
        </span>
      </div>

      <div class="question">
        <h2>{currentQuestion.prompt}</h2>

        {#if currentQuestion.question_type === 'multiple_choice'}
          <div class="choices">
            {#each currentQuestion.choices || [] as choice, idx}
              <button
                class="choice"
                class:selected={answers[currentQuestion.id] === choice}
                on:click={() => selectAnswer(currentQuestion.id, choice)}
                disabled={submitted}
              >
                {choice}
              </button>
            {/each}
          </div>
        {:else if currentQuestion.question_type === 'fill_blank'}
          <div class="fill-blank">
            <input
              type="text"
              bind:value={answers[currentQuestion.id]}
              placeholder="Type your answer"
              disabled={submitted}
              class="fill-input"
            />
          </div>
        {/if}
      </div>

      <div class="quiz-actions">
        <button
          class="secondary"
          on:click={previousQuestion}
          disabled={currentQuestionIndex === 0 || submitted}
        >
          Previous
        </button>

        {#if currentQuestionIndex === questions.length - 1}
          <button
            class="primary"
            on:click={submitQuiz}
            disabled={!allAnswered || loading || submitted}
          >
            {loading ? 'Submitting...' : 'Submit Quiz'}
          </button>
        {:else}
          <button
            class="primary"
            on:click={nextQuestion}
            disabled={submitted}
          >
            Next
          </button>
        {/if}
      </div>
    </div>
  {:else}
    <div class="loading">Loading quiz...</div>
  {/if}
</div>

<style>
  .quiz-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  .error {
    background: #fee;
    color: #c33;
    padding: 0.75rem;
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .progress-bar {
    width: 100%;
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    margin-bottom: 2rem;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--accent);
    transition: width 0.3s ease;
  }

  .question-header {
    margin-bottom: 1.5rem;
  }

  .question-number {
    color: var(--muted);
    font-size: 0.9rem;
  }

  .question h2 {
    margin-bottom: 1.5rem;
    font-size: 1.3rem;
    line-height: 1.5;
  }

  .choices {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
  }

  .choice {
    padding: 1rem;
    border: 2px solid var(--border);
    border-radius: 12px;
    background: var(--surface);
    cursor: pointer;
    text-align: left;
    font-size: 1rem;
    transition: all 0.2s ease;
  }

  .choice:hover:not(:disabled) {
    border-color: var(--accent);
    background: var(--accent-soft);
  }

  .choice.selected {
    border-color: var(--accent);
    background: var(--accent-soft);
    color: var(--accent);
    font-weight: 500;
  }

  .choice:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }

  .fill-blank {
    margin-top: 1rem;
  }

  .fill-input {
    width: 100%;
    padding: 0.8rem;
    border: 2px solid var(--border);
    border-radius: 8px;
    font-size: 1rem;
    box-sizing: border-box;
  }

  .fill-input:focus {
    outline: none;
    border-color: var(--accent);
  }

  .fill-input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .quiz-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 2rem;
    gap: 1rem;
  }

  .primary,
  .secondary {
    padding: 0.7rem 1.5rem;
    border-radius: 999px;
    border: none;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
  }

  .primary {
    background: var(--accent);
    color: white;
  }

  .primary:hover:not(:disabled) {
    background: var(--accent-hover);
  }

  .secondary {
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
  }

  .secondary:hover:not(:disabled) {
    background: #f9f9f8;
  }

  .primary:disabled,
  .secondary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .results {
    text-align: center;
  }

  .results h2 {
    margin-bottom: 1.5rem;
  }

  .score {
    margin: 2rem 0;
  }

  .score-value {
    font-size: 3rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.5rem;
  }

  .score-label {
    color: var(--muted);
    font-size: 1.1rem;
  }

  .answers-review {
    text-align: left;
    margin: 2rem 0;
  }

  .answers-review h3 {
    margin-bottom: 1rem;
  }

  .answer-item {
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    border: 2px solid var(--border);
  }

  .answer-item.correct {
    background: #f0f9f0;
    border-color: #4caf50;
  }

  .answer-item.incorrect {
    background: #fff5f5;
    border-color: #f44336;
  }

  .answer-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }

  .question-num {
    font-weight: 500;
    color: var(--muted);
  }

  .answer-status {
    font-weight: 500;
  }

  .answer-item.correct .answer-status {
    color: #4caf50;
  }

  .answer-item.incorrect .answer-status {
    color: #f44336;
  }

  .answer-prompt {
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .answer-details {
    font-size: 0.9rem;
    color: var(--muted);
  }

  .loading {
    text-align: center;
    padding: 3rem;
    color: var(--muted);
  }
</style>
