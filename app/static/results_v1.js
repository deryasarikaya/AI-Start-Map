(() => {
  document.documentElement.classList.add("has-js");
  const workspace = document.querySelector("[data-map-workspace]");
  if (!workspace) return;
  const nodes = [...workspace.querySelectorAll("[data-map-node]")];
  const details = [...workspace.querySelectorAll("[data-module-detail]")];
  const filters = [...workspace.querySelectorAll("[data-map-filter]")];
  const select = (key) => {
    nodes.forEach((node) => {
      const selected = node.dataset.moduleKey === key;
      node.classList.toggle("is-selected", selected);
      node.setAttribute("aria-pressed", String(selected));
    });
    details.forEach((detail) => detail.classList.toggle("is-detail-hidden", detail.dataset.moduleDetail !== key));
  };
  nodes.forEach((node) => node.addEventListener("click", () => select(node.dataset.moduleKey)));
  filters.forEach((filter) => filter.addEventListener("click", () => {
    const state = filter.dataset.mapFilter;
    filters.forEach((item) => item.setAttribute("aria-pressed", String(item === filter)));
    nodes.forEach((node) => node.classList.toggle("is-state-muted", node.dataset.state !== state));
    const first = nodes.find((node) => node.dataset.state === state);
    if (first) select(first.dataset.moduleKey);
  }));
})();
