// Byte Sized Academy: quizzes and quiz progress. Progress is kept only in this browser (localStorage).
(function () {
  var KEY = "bsa:quiz:";
  function load(slug) {
    try { return JSON.parse(localStorage.getItem(KEY + slug)); } catch (e) { return null; }
  }
  function save(slug, score, total) {
    try {
      var prev = load(slug);
      var best = prev && prev.best > score ? prev.best : score;
      localStorage.setItem(KEY + slug, JSON.stringify({ last: score, best: best, total: total, at: new Date().toISOString() }));
    } catch (e) { /* storage blocked: the quiz still works */ }
  }

  // Badges on lesson cards
  document.querySelectorAll(".card[data-slug]").forEach(function (card) {
    var p = load(card.getAttribute("data-slug"));
    if (!p) return;
    var badge = document.createElement("span");
    badge.className = "quiz-badge" + (p.best === p.total ? " is-perfect" : "");
    badge.textContent = (p.best === p.total ? "✓ Quiz " : "Quiz ") + p.best + "/" + p.total;
    card.querySelector(".card-media").appendChild(badge);
  });

  // Quizzes
  document.querySelectorAll(".quiz[data-quiz]").forEach(function (quiz) {
    var slug = quiz.getAttribute("data-quiz");
    var form = quiz.querySelector("form");
    var qs = Array.prototype.slice.call(form.querySelectorAll(".q"));
    var score = form.querySelector(".score");
    var retry = form.querySelector("[data-retry]");
    var check = form.querySelector("button[type=submit]");
    var prev = load(slug);
    if (prev) score.textContent = "Your best so far: " + prev.best + " of " + prev.total + ".";

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var missing = qs.filter(function (q) { return !q.querySelector("input:checked"); });
      qs.forEach(function (q) { q.classList.toggle("is-missing", missing.indexOf(q) !== -1); });
      if (missing.length) {
        score.textContent = "Pick an answer for every question first (" + missing.length + " left).";
        missing[0].querySelector("input").focus();
        return;
      }
      var right = 0;
      qs.forEach(function (q) {
        var answer = q.getAttribute("data-answer");
        var picked = q.querySelector("input:checked").value;
        var ok = picked === answer;
        if (ok) right++;
        q.classList.add(ok ? "is-right" : "is-wrong");
        q.querySelectorAll("input").forEach(function (inp) {
          inp.disabled = true;
          if (inp.value === answer) inp.parentNode.classList.add("is-answer");
          else if (inp.checked) inp.parentNode.classList.add("is-picked");
        });
        var ex = q.querySelector(".explain");
        ex.querySelector(".verdict").textContent = ok ? "Correct!" : "Not quite.";
        ex.hidden = false;
      });
      save(slug, right, qs.length);
      var msg = right === qs.length ? "Perfect score! That's your bite. 🍪"
        : right >= qs.length / 2 ? "Nice work. Check the explanations, then try again for a perfect score."
        : "Good start. Rewatch the video, then give it another go.";
      score.textContent = "You got " + right + " of " + qs.length + ". " + msg;
      check.hidden = true;
      retry.hidden = false;
      quiz.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    retry.addEventListener("click", function () {
      form.reset();
      qs.forEach(function (q) {
        q.classList.remove("is-right", "is-wrong", "is-missing");
        q.querySelectorAll("input").forEach(function (inp) { inp.disabled = false; inp.parentNode.classList.remove("is-answer", "is-picked"); });
        q.querySelector(".explain").hidden = true;
      });
      score.textContent = "";
      check.hidden = false;
      retry.hidden = true;
      qs[0].querySelector("input").focus();
    });
  });
})();
