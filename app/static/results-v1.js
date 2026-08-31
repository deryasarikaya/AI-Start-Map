/* Interaktion erweitert die lesbare Basisdarstellung nur um Auswahl und Filter.
   Sie trifft keine fachlichen Entscheidungen und erzeugt keinen Inhalt. */
(function () {
  "use strict";

  const root = document.querySelector("[data-results-root]");
  if (!root) return;

  const html = document.documentElement;
  const nodeButtons = Array.from(root.querySelectorAll("[data-map-node]"));
  const details = Array.from(root.querySelectorAll("[data-map-detail]"));
  const filters = Array.from(root.querySelectorAll("[data-map-filter]"));

  /** Zeigt die geprüften Details des gewählten Moduls. */
  function selectNode(key) {
    nodeButtons.forEach((button) => {
      const selected = button.dataset.mapNode === key;
      button.classList.toggle("is-selected", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
    details.forEach((detail) => {
      detail.classList.toggle("is-active", detail.dataset.mapDetail === key);
    });
  }

  /** Filtert nur die sichtbare Kartendarstellung, nicht die Inhalte selbst. */
  function filterNodes(state) {
    nodeButtons.forEach((button) => {
      button.hidden = state !== "all" && button.dataset.mapState !== state;
    });
    filters.forEach((filter) => {
      const active = filter.dataset.mapFilter === state;
      filter.classList.toggle("is-active", active);
      filter.setAttribute("aria-pressed", String(active));
    });
    const selected = nodeButtons.find((button) => button.classList.contains("is-selected"));
    if (selected?.hidden) {
      const firstVisible = nodeButtons.find((button) => !button.hidden);
      if (firstVisible) selectNode(firstVisible.dataset.mapNode);
    }
  }

  nodeButtons.forEach((button) => {
    button.addEventListener("click", () => selectNode(button.dataset.mapNode));
  });
  filters.forEach((filter) => {
    filter.addEventListener("click", () => filterNodes(filter.dataset.mapFilter));
  });
  html.dataset.resultsEnhanced = "true";
}());
