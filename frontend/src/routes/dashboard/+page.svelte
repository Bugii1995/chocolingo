<script>
  /**
   * Message returned from backend
   * @type {string}
   */
  let message = "Loading...";

  fetch("http://127.0.0.1:8000/ping")
    .then((res) => res.json())
    .then((data) => {
      message = data.message;
    })
    .catch((err) => {
      console.error(err);
      message = "Backend not reachable";
    });
</script>

<main class="page">
  <h1>🍫 Chocolingo Dashboard</h1>
  <p>Backend says: <strong>{message}</strong></p>
</main>

<style>
  .page {
    max-width: 480px;
    margin: auto;
    padding: 2rem;
    font-family: system-ui, sans-serif;
  }
</style>
