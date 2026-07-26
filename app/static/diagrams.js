const cleanLabel = (value) => String(value)
    .replace(/[<>"&;{}\[\]()`]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 72);

const renderDiagrams = async () => {
    const diagrams = [...document.querySelectorAll(".process-diagram")];
    if (!diagrams.length) return;
    try {
        const { default: mermaid } = await import("https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs");
        mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "base", flowchart: { htmlLabels: false, useMaxWidth: true }, themeVariables: { primaryColor: "#DDE7DE", primaryTextColor: "#28322C", primaryBorderColor: "#6C8870", lineColor: "#6C8870", tertiaryColor: "#F7F3EA" } });
        for (const [diagramIndex, container] of diagrams.entries()) {
            const data = container.querySelector("[data-diagram-steps]");
            const output = container.querySelector("[data-mermaid-output]");
            const fallback = container.querySelector("[data-diagram-fallback]");
            if (!data || !output) continue;
            const steps = JSON.parse(data.textContent).map(cleanLabel).filter(Boolean).slice(0, 7);
            const problemIndexes = JSON.parse(container.dataset.problemIndexes || "[]");
            if (steps.length < 2) continue;
            const nodes = steps.map((step, index) => `S${index}["${step}"]${index < steps.length - 1 ? ` --> S${index + 1}` : ""}`);
            const problemClasses = problemIndexes.filter((index) => Number.isInteger(index) && index >= 0 && index < steps.length).map((index) => `class S${index} problem;`);
            const source = `flowchart TD\n${nodes.join("\n")}\nclassDef problem fill:#F7E8C8,stroke:#D3A34A,color:#28322C;\n${problemClasses.join("\n")}`;
            const { svg } = await mermaid.render(`process-map-${diagramIndex}`, source);
            output.innerHTML = svg;
            if (fallback) fallback.hidden = true;
            container.classList.add("diagram-ready");
        }
    } catch (_error) {
        document.querySelectorAll(".process-diagram").forEach((container) => container.classList.add("diagram-fallback-active"));
    }
};

renderDiagrams();
