<script>
  /**
   * @typedef {'locked'|'active'|'completed'} Status
   * @typedef {{ id:number, title:string, status:Status, mastery:number }} Node
   * @typedef {{ level:'A0'|'A1'|'A2', nodes:Node[] }} Level
   * @typedef {{ id:number, title:string, levels:Level[], open:boolean }} Cluster
   */

  /** @type {Cluster[]} */
  let clusters = [
    {
      id: 1,
      title: "Verbs & Tenses",
      open: true,
      levels: [
        {
          level: "A0",
          nodes: [
            { id: 101, title: "What is a verb?", status: "completed", mastery: 100 }
          ]
        },
        {
          level: "A1",
          nodes: [
            { id: 102, title: "Present tense", status: "active", mastery: 56 },
            { id: 103, title: "Past tense", status: "locked", mastery: 0 }
          ]
        },
        {
          level: "A2",
          nodes: [
            { id: 104, title: "Future tense", status: "locked", mastery: 0 }
          ]
        }
      ]
    },
    {
      id: 2,
      title: "Pronouns",
      open: false,
      levels: [
        {
          level: "A0",
          nodes: [
            { id: 201, title: "What is a pronoun?", status: "active", mastery: 34 }
          ]
        },
        {
          level: "A1",
          nodes: [
            { id: 202, title: "Subject pronouns", status: "locked", mastery: 0 },
            { id: 203, title: "Object pronouns", status: "locked", mastery: 0 }
          ]
        },
        {
          level: "A2",
          nodes: [
            { id: 204, title: "Possessive pronouns", status: "locked", mastery: 0 }
          ]
        }
      ]
    }
  ];

  function toggleCluster(cluster) {
    cluster.open = !cluster.open;
  }

  function isLevelLocked(level) {
    return level.nodes.every((n) => n.status === "locked");
  }

  function levelMastery(level) {
    const total = level.nodes.reduce((sum, n) => sum + n.mastery, 0);
    return Math.round(total / level.nodes.length);
  }
</script>

<main class="page">
  <header class="header">
    <h1>Knowledge Map</h1>
    <p class="subtitle">
      Mastery grows gradually, not all at once.
    </p>
  </header>

  {#each clusters as cluster}
    <section class="cluster">
      <!-- Collapsible header -->
      <button
        class="cluster-header"
        on:click={() => toggleCluster(cluster)}
        aria-expanded={cluster.open}
      >
        <h2>{cluster.title}</h2>
        <span class="chevron" class:open={cluster.open}>▾</span>
      </button>

      <!-- Collapsible content -->
      {#if cluster.open}
        <div class="cluster-content">
          {#each cluster.levels as level}
            <div class="level" class:dimmed={isLevelLocked(level)}>
              <div class="level-header">
                <span class="level-label">{level.level}</span>
                <span class="level-mastery">{levelMastery(level)}%</span>
              </div>

              <div class="nodes">
                {#each level.nodes as node, i}
                  <div class="node-wrapper">
                    <div class="node {node.status}">
                      <span class="node-title">{node.title}</span>
                      <span class="node-mastery">
                        {node.mastery === 100 ? '⭐' : `${node.mastery}%`}
                      </span>
                    </div>

                    {#if i < level.nodes.length - 1}
                      <span class="connector"></span>
                    {/if}
                  </div>
                {/each}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </section>
  {/each}
</main>

<style>
  /* Page */
  .page {
    max-width: 720px;
    margin: 0 auto;
    padding: 2rem 1rem 3rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .subtitle {
    color: var(--muted);
    font-size: 0.95rem;
  }

  /* Cluster */
  .cluster {
    border-left: 2px solid var(--border);
    padding-left: 1rem;
  }

  .cluster-header {
    width: 100%;
    background: none;
    border: none;
    padding: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    margin-bottom: 0.8rem;
  }

  .cluster-header h2 {
    font-size: 1.05rem;
    margin: 0;
  }

  .chevron {
    font-size: 1rem;
    transition: transform 0.2s ease;
    color: var(--muted);
  }

  .chevron.open {
    transform: rotate(180deg);
  }

  /* Level */
  .level {
    margin-bottom: 1.6rem;
    transition: opacity 0.2s ease;
  }

  .level.dimmed {
    opacity: 0.4;
  }

  .level-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }

  .level-label,
  .level-mastery {
    font-size: 0.75rem;
    color: var(--muted);
  }

  /* Nodes */
  .nodes {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .node-wrapper {
    position: relative;
    padding-left: 1rem;
  }

  .node {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0.75rem;
    border-radius: 10px;
    font-size: 0.85rem;
    background: var(--surface);
    border: 1px solid var(--border);
    transition:
      box-shadow 0.2s ease,
      transform 0.2s ease,
      background-color 0.2s ease;
  }

  .node-mastery {
    font-size: 0.75rem;
    color: var(--muted);
  }

  .node.completed {
    background: var(--accent-soft);
    color: var(--accent);
    border-color: transparent;
  }

  .node.active {
    background: var(--accent);
    color: white;
    border-color: transparent;
    box-shadow:
      0 0 0 2px rgba(124, 74, 45, 0.25),
      0 6px 14px rgba(0, 0, 0, 0.08);
    transform: translateY(-1px);
  }

  .node.active .node-mastery {
    color: rgba(255, 255, 255, 0.9);
  }

  .node.active .node-title {
    font-weight: 600;
  }

  .node.locked {
    background: #f5f5f4;
    color: var(--muted);
    cursor: not-allowed;
  }

  /* Hover */
  @media (hover: hover) {
    .node.completed:hover,
    .node.active:hover {
      transform: translateY(-2px);
      box-shadow:
        0 0 0 2px rgba(124, 74, 45, 0.3),
        0 8px 18px rgba(0, 0, 0, 0.1);
    }
  }

  /* Connectors */
  .connector {
    position: absolute;
    left: 0.45rem;
    top: 100%;
    height: 0.5rem;
    width: 1px;
    background: var(--border);
  }
</style>
