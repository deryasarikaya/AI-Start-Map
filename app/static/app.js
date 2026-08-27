(() => {
    "use strict";

    const setHidden = (element, hidden) => { if (element) element.hidden = hidden; };

    document.querySelectorAll("form[data-disable-on-submit]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (form.dataset.submitted === "true") {
                event.preventDefault();
                return;
            }
            form.dataset.submitted = "true";
            form.querySelectorAll("button[type='submit']").forEach((button) => {
                button.disabled = true;
                button.setAttribute("aria-disabled", "true");
                if (form.dataset.submittingLabel) button.textContent = form.dataset.submittingLabel;
            });
            const layer = document.querySelector("[data-processing-layer]");
            if (layer) {
                const title = layer.querySelector("[data-processing-title]");
                const copy = layer.querySelector("[data-processing-copy]");
                if (title && form.dataset.processingTitle) {
                    title.textContent = form.dataset.processingTitle;
                }
                if (copy && form.dataset.processingCopy) {
                    copy.textContent = form.dataset.processingCopy;
                }
                layer.hidden = false;
                document.body.classList.add("is-processing");
            }
        });
    });

    document.querySelectorAll("[data-voice-input]").forEach((container) => {
        const target = document.getElementById(container.dataset.voiceTarget);
        const status = container.querySelector("[data-voice-status]");
        const support = container.querySelector("[data-voice-support]");
        const start = container.querySelector("[data-voice-start]");
        const stop = container.querySelector("[data-voice-stop]");
        const retry = container.querySelector("[data-voice-retry]");
        const write = container.querySelector("[data-voice-write]");
        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        let finalText = "";
        // Der Browser beendet die Erkennung nach einer laengeren Pause von
        // selbst. Ob jemand fertig ist oder nur Luft geholt hat, weiss nur
        // dieser Merker.
        let selbstBeendet = false;

        const update = (state, message) => {
            container.dataset.voiceState = state;
            if (status) status.textContent = message;
            setHidden(start, state === "recording");
            setHidden(stop, state !== "recording");
            setHidden(retry, state !== "error" && state !== "done");
        };

        if (!Recognition) {
            if (support) support.textContent = "Ihr Browser unterstützt die Spracheingabe hier nicht. Sie können direkt losschreiben.";
            if (start) start.disabled = true;
            update("error", "Spracheingabe ist in diesem Browser nicht verfügbar. Ihre Texteingabe funktioniert weiterhin.");
        } else {
            recognition = new Recognition();
            recognition.lang = "de-DE";
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.onstart = () => {
                // Vorhandenen Text uebernehmen statt ersetzen: Wer
                // weitererzaehlt, soll nicht von vorn anfangen.
                finalText = target?.value.trim() || "";
                selbstBeendet = false;
                update("recording", "Ich höre zu …");
            };
            recognition.onresult = (event) => {
                let interim = "";
                for (let index = event.resultIndex; index < event.results.length; index += 1) {
                    const transcript = event.results[index][0].transcript.trim();
                    if (event.results[index].isFinal) finalText = `${finalText} ${transcript}`.trim();
                    else interim += ` ${transcript}`;
                }
                if (target) target.value = `${finalText}${interim}`.trim();
            };
            recognition.onend = () => update(
                "done",
                selbstBeendet
                    ? "Das haben wir verstanden. Sie können den Text direkt bearbeiten."
                    : "Aufnahme pausiert. Sie können weiter erzählen oder den Text direkt bearbeiten.",
            );
            recognition.onerror = () => update("error", "Das hat gerade nicht geklappt. Sie können es erneut versuchen oder einfach schreiben.");
        }

        start?.addEventListener("click", () => {
            if (!recognition) return target?.focus();
            try { recognition.start(); } catch (_error) { update("error", "Das hat gerade nicht geklappt. Sie können es erneut versuchen oder einfach schreiben."); }
        });
        stop?.addEventListener("click", () => {
            selbstBeendet = true;
            update("processing", "Wir bringen Ihre Erzählung gerade in Text.");
            recognition?.stop();
        });
        retry?.addEventListener("click", () => start?.click());
        write?.addEventListener("click", () => target?.focus());
    });

    document.querySelectorAll("[data-step-editor]").forEach((editor) => {
        const list = editor.querySelector("[data-step-list]");
        const renumber = () => list?.querySelectorAll(".step-editor").forEach((row, index) => {
            const number = row.querySelector("span");
            const input = row.querySelector("input");
            if (number) number.textContent = String(index + 1);
            if (input) input.setAttribute("aria-label", `Schritt ${index + 1}`);
        });
        editor.querySelector("[data-add-step]")?.addEventListener("click", () => {
            if (!list || list.children.length >= 5) return;
            const row = document.createElement("div");
            row.className = "step-editor";
            row.innerHTML = '<span></span><input name="steps" required placeholder="Was passiert als Nächstes?" aria-label="Neuer Schritt"><button type="button" aria-label="Schritt entfernen" data-remove-step>×</button>';
            list.append(row);
            renumber();
            row.querySelector("input")?.focus();
        });
        list?.addEventListener("click", (event) => {
            const button = event.target.closest("[data-remove-step]");
            if (!button || list.children.length <= 2) return;
            button.closest(".step-editor")?.remove();
            renumber();
        });
    });

    document.querySelectorAll("[data-show-correction]").forEach((button) => {
        button.addEventListener("click", () => {
            const panel = document.querySelector("[data-correction-panel]");
            if (!panel) return;
            panel.hidden = false;
            button.hidden = true;
            panel.querySelector("input, textarea")?.focus();
            panel.scrollIntoView({ behavior: "smooth", block: "start" });
        });
    });
})();

/* Sanftes Einblenden. Der Startzustand wird erst hier gesetzt: ohne
   JavaScript bleibt die Seite vollstaendig sichtbar. Bei reduzierter
   Bewegung wird gar nichts angefasst. */
(() => {
    const elemente = document.querySelectorAll("[data-reveal]");
    if (!elemente.length) return;
    const ruhig = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (ruhig || !("IntersectionObserver" in window)) return;
    document.documentElement.classList.add("reveal-armed");
    const beobachter = new IntersectionObserver((eintraege) => {
        eintraege.forEach((eintrag) => {
            if (!eintrag.isIntersecting) return;
            eintrag.target.classList.add("revealed");
            beobachter.unobserve(eintrag.target);
        });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    elemente.forEach((element) => beobachter.observe(element));
    window.addEventListener("beforeprint", () => {
        document.documentElement.classList.remove("reveal-armed");
    });
})();
