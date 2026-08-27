/* Was die Tafel lebendig macht.
 *
 * Zwei Dinge, mehr nicht: Abschnitte kommen herein, wenn sie ins Bild
 * geraten, und die Kennzahlen zaehlen einmal hoch. Beides ohne Bibliothek —
 * die Seite soll auch dann laufen, wenn nichts nachgeladen werden kann.
 *
 * Ohne JavaScript bleibt die Seite vollstaendig lesbar: Die Abschnitte
 * bekommen ihre Sichtbarkeit sofort zurueck, die Zahlen stehen ohnehin im
 * HTML. Bewegung ist Zugabe, nie Voraussetzung.
 */

(function () {
  "use strict";

  var ruhe = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var abschnitte = document.querySelectorAll("[data-auftritt]");

  if (ruhe || !("IntersectionObserver" in window)) {
    abschnitte.forEach(function (teil) { teil.classList.add("da"); });
    return;
  }

  var beobachter = new IntersectionObserver(function (eintraege) {
    eintraege.forEach(function (eintrag) {
      if (!eintrag.isIntersecting) return;
      eintrag.target.classList.add("da");
      beobachter.unobserve(eintrag.target);
      zaehleHoch(eintrag.target);
    });
  }, { rootMargin: "0px 0px -12% 0px", threshold: 0.08 });

  abschnitte.forEach(function (teil) { beobachter.observe(teil); });

  /* Die Kennzahlen zaehlen von null hoch — dasselbe, was ein Punktestand
   * auf anderen Auswertungen tut. Nur steht hier seine eigene Zahl.
   *
   * Gezaehlt wird ausschliesslich die fuehrende Ziffernfolge. „70 oder 80
   * E-Mails" wird zu „70 oder 80", nicht zu Unsinn: Der Rest des Textes
   * bleibt unangetastet stehen. */
  function zaehleHoch(bereich) {
    bereich.querySelectorAll(".kennzahlen b").forEach(function (feld) {
      var text = feld.textContent;
      var treffer = text.match(/^(\D*)(\d+)/);
      if (!treffer) return;

      var vorspann = treffer[1];
      var ziel = parseInt(treffer[2], 10);
      var rest = text.slice(treffer[0].length);
      if (ziel > 100000) return;

      var beginn = null;
      var dauer = 900;

      function schritt(jetzt) {
        if (beginn === null) beginn = jetzt;
        var anteil = Math.min((jetzt - beginn) / dauer, 1);
        /* Schnell anfangen, weich auslaufen — eine Zahl, die gleichmaessig
         * hochzaehlt, wirkt wie ein Ladebalken. */
        var weich = 1 - Math.pow(1 - anteil, 3);
        feld.textContent = vorspann + Math.round(ziel * weich) + rest;
        if (anteil < 1) requestAnimationFrame(schritt);
      }

      feld.textContent = vorspann + "0" + rest;
      requestAnimationFrame(schritt);
    });
  }
})();
