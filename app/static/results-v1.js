/* Die Karte öffnet ausschließlich bereits gerenderte DTO-Details. */
(function () {
  "use strict";

  const root = document.querySelector("[data-results-root]");
  if (!root) return;

  const nodes = Array.from(root.querySelectorAll("[data-map-node]"));
  const details = Array.from(root.querySelectorAll("[data-map-detail]"));
  const popup = root.querySelector("[data-map-popup]");
  const closeButton = root.querySelector("[data-map-detail-close]");

  function selectNode(key) {
    nodes.forEach((node) => {
      const selected = node.dataset.mapNode === key;
      node.classList.toggle("is-selected", selected);
      node.setAttribute("aria-expanded", String(selected));
    });
    details.forEach((detail) => {
      detail.classList.toggle("is-active", detail.dataset.mapDetail === key);
    });
    if (popup) popup.classList.add("is-open");
  }

  function closeDetails() {
    nodes.forEach((node) => {
      node.classList.remove("is-selected");
      node.setAttribute("aria-expanded", "false");
    });
    details.forEach((detail) => detail.classList.remove("is-active"));
    if (popup) popup.classList.remove("is-open");
  }

  nodes.forEach((node) => {
    node.addEventListener("click", () => selectNode(node.dataset.mapNode));
  });
  if (closeButton) closeButton.addEventListener("click", closeDetails);
  document.documentElement.dataset.resultsEnhanced = "true";
}());
