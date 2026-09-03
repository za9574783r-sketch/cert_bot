/* =========================================================
   Milliy Sertifikat Mini App — SPA logic
   ========================================================= */

(function () {
  "use strict";

  const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;

  // ----------------------- Init -----------------------
  if (tg) {
    try {
      tg.ready();
      tg.expand();
      bindTheme();
      tg.onEvent("themeChanged", bindTheme);
    } catch (e) { /* not in Telegram, dev mode */ }
  } else {
    document.documentElement.dataset.colorScheme =
      window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
  }

  function bindTheme() {
    if (!tg || !tg.themeParams) return;
    const p = tg.themeParams;
    const root = document.documentElement;
    if (p.bg_color) root.style.setProperty("--bg", p.bg_color);
    if (p.secondary_bg_color) root.style.setProperty("--secondary-bg", p.secondary_bg_color);
    if (p.text_color) root.style.setProperty("--text", p.text_color);
    if (p.hint_color) root.style.setProperty("--hint", p.hint_color);
    if (p.link_color) root.style.setProperty("--link", p.link_color);
    if (p.button_color) root.style.setProperty("--btn", p.button_color);
    if (p.button_text_color) root.style.setProperty("--btn-text", p.button_text_color);
    root.dataset.colorScheme = tg.colorScheme || "dark";
  }

  // ----------------------- Helpers -----------------------
  function tap() { if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred("light"); }
  function ok()  { if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("success"); }
  function bad() { if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("error"); }

  function showToast(msg) {
    const t = document.getElementById("toast");
    if (!t) return;
    t.textContent = msg;
    t.hidden = false;
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => { t.hidden = true; }, 2200);
  }

  async function api(path, opts) {
    opts = opts || {};
    const headers = Object.assign(
      { "Content-Type": "application/json" },
      opts.headers || {}
    );
    if (tg && tg.initData) headers["X-Telegram-Init-Data"] = tg.initData;
    const res = await fetch("/api" + path, Object.assign({}, opts, { headers }));
    if (!res.ok) {
      let detail = "";
      try { detail = (await res.json()).error || ""; } catch (e) {}
      throw new Error(detail || ("HTTP " + res.status));
    }
    return res.json();
  }

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    if (attrs) {
      for (const k in attrs) {
        if (k === "class") node.className = attrs[k];
        else if (k === "html") node.innerHTML = attrs[k];
        else if (k === "text") node.textContent = attrs[k];
        else if (k.startsWith("on") && typeof attrs[k] === "function") {
          node.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
        } else if (attrs[k] !== null && attrs[k] !== undefined) {
          node.setAttribute(k, attrs[k]);
        }
      }
    }
    if (children) {
      (Array.isArray(children) ? children : [children]).forEach((c) => {
        if (c == null) return;
        node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
      });
    }
    return node;
  }

  function setView(html) {
    const view = document.getElementById("view");
    view.style.opacity = "0";
    setTimeout(() => {
      view.innerHTML = html;
      view.style.opacity = "1";
    }, 80);
  }

  function backButton(path) {
    if (!tg || !tg.BackButton) return;
    if (path) {
      tg.BackButton.show();
      tg.BackButton.onClick(() => { location.hash = path; });
    } else {
      tg.BackButton.hide();
    }
  }

  function nav(hash) {
    if (location.hash === hash) {
      router();
    } else {
      location.hash = hash;
    }
  }

  // ----------------------- Pages -----------------------
  function renderHome() {
    backButton(null);
    document.getElementById("header-subtitle").textContent = "Fan tanlang";

    api("/subjects").then((subjects) => {
      const gradientClasses = ["card--g2", "card--g3", "card--warm"];
      const cards = subjects.map((s, idx) => {
        const cls = idx === 0 ? "" : " card--" + gradientClasses[idx % gradientClasses.length];
        return el(
          "button",
          { class: "card card--gradient" + cls, onclick: () => { tap(); nav("#/subject/" + s.name); } },
          [
            el("div", { class: "card__icon", text: s.icon }),
            el("div", { class: "card__body" }, [
              el("div", { class: "card__title", text: s.display_name }),
              el("div", { class: "card__meta", text: "5-sinf → 11-sinf" }),
            ]),
            el("div", { class: "card__chevron", text: "›" }),
          ]
        );
      });

      const view = el("div", null, [
        el("div", { class: "hero" }, [
          el("h1", { class: "hero__title", text: "Milliy Sertifikat" }),
          el("p", { class: "hero__subtitle", text: "5-sinfdan 11-sinfgacha — darslar va interaktiv testlar" }),
        ]),
        el("div", { class: "section-title", text: "Fanlar" }),
        ...cards,
        el("div", { class: "footer", text: "🎓 Telegram Mini App · v1.0" }),
      ]);
      setView("");
      const target = document.getElementById("view");
      target.innerHTML = "";
      target.appendChild(view);
      target.style.opacity = "1";
    }).catch((e) => { showToast("Xatolik: " + e.message); });
  }

  function renderGrades(subjectName) {
    backButton("#/");
    api("/grades?subject=" + encodeURIComponent(subjectName)).then((grades) => {
      const view = el("div", null, [
        el("button", { class: "btn-ghost", onclick: () => nav("#/") }, "‹ Fanlarga qaytish"),
        el("div", { class: "hero", style: "background: var(--gradient-2)" }, [
          el("h1", { class: "hero__title", text: subjectDisplay(subjectName) }),
          el("p", { class: "hero__subtitle", text: "Sinfni tanlang (5 — 11)" }),
        ]),
        el("div", { class: "section-title", text: "Sinflar" }),
        ...grades.map((g, i) => {
          const gradients = ["", "card--g2", "card--g3", "card--warm", "card--success"];
          const cls = "card card--gradient" + (gradients[i % gradients.length] ? " " + gradients[i % gradients.length] : "");
          return el(
            "button",
            { class: cls, onclick: () => { tap(); nav("#/grade/" + g.id); } },
            [
              el("div", { class: "card__icon", text: g.grade_num.toString() }),
              el("div", { class: "card__body" }, [
                el("div", { class: "card__title", text: g.display_name }),
                el("div", { class: "card__meta", text: "Mavzular va testlar" }),
              ]),
              el("div", { class: "card__chevron", text: "›" }),
            ]
          );
        }),
      ]);
      const target = document.getElementById("view");
      target.innerHTML = "";
      target.appendChild(view);
      target.style.opacity = "1";
      document.getElementById("header-subtitle").textContent = subjectDisplay(subjectName);
    }).catch((e) => { showToast("Xatolik: " + e.message); });
  }

  function renderTopics(gradeId) {
    backButton("#/");
    api("/topics?grade_id=" + gradeId).then((topics) => {
      const topicButtons = topics.map((t, idx) => {
        const badge = t.has_quizzes
          ? el("span", { class: "badge badge--ok", text: "✅ Test bor" })
          : (t.is_ai_generated
              ? el("span", { class: "badge badge--ai", text: "🤖 AI" })
              : el("span", { class: "badge badge--empty", text: "⏳ Tayyorlanm" }));
        return el(
          "button",
          { class: "topic-card", onclick: () => { tap(); nav("#/topic/" + t.id); } },
          [
            el("div", { class: "topic-card__num", text: String(idx + 1).padStart(2, "0") }),
            el("div", { class: "topic-card__title", text: t.title }),
            badge,
          ]
        );
      });

      const view = el("div", null, [
        el("button", { class: "btn-ghost", onclick: () => nav("#/") }, "‹ Sinflarga qaytish"),
        el("div", { class: "hero", style: "background: var(--gradient-3); color: #0f172a" }, [
          el("h1", { class: "hero__title", text: topics[0] ? "Mavzular" : "Hech nima topilmadi" }),
          el("p", { class: "hero__subtitle", text: "Mavzu tanlang yoki AI generatsiya qiling" }),
        ]),
        el("div", { class: "section-title", text: "Mavzular ro'yxati" }),
        ...(topicButtons.length ? topicButtons : [
          el("div", { class: "lesson-empty", text: "Bu sinf uchun mavzular hali yo'q" }),
        ]),
      ]);
      const target = document.getElementById("view");
      target.innerHTML = "";
      target.appendChild(view);
      target.style.opacity = "1";
      document.getElementById("header-subtitle").textContent = topics.length + " ta mavzu";
    }).catch((e) => { showToast("Xatolik: " + e.message); });
  }

  async function renderTopic(topicId) {
    backButton(null);
    const view = document.getElementById("view");
    view.innerHTML = skeletonLesson();
    view.style.opacity = "1";

    let topic;
    try {
      topic = await api("/topic/" + topicId);
    } catch (e) {
      showToast("Mavzu topilmadi");
      nav("#/");
      return;
    }

    backButton("#/grade/" + topic.grade_id);
    document.getElementById("header-subtitle").textContent = topic.title;

    const hasContent = topic.content && topic.content.trim().length > 0;
    const lessonHtml = hasContent
      ? sanitizeHtml(topic.content)
      : '<div class="lesson-empty">'
        + '<div style="font-size:48px;margin-bottom:12px;">🤖</div>'
        + '<p>Bu mavzu uchun dars hali tayyorlanmagan.</p>'
        + '<p style="font-size:13px;">AI yordamida yaratish uchun quyidagi tugmani bosing.</p>'
        + '</div>';

    const buttons = [];
    if (!hasContent) {
      buttons.push(el("button", {
        class: "btn-primary",
        onclick: () => { tap(); nav("#/generating/" + topicId); },
      }, "✨ AI bilan dars yaratish"));
    } else if (topic.has_quizzes) {
      buttons.push(el("button", {
        class: "btn-primary",
        onclick: () => { tap(); nav("#/quiz/" + topicId); },
      }, "🧪 Test yechish (5 ta savol)"));
    } else {
      buttons.push(el("button", {
        class: "btn-primary",
        onclick: () => { tap(); nav("#/generating/" + topicId); },
      }, "🤖 AI bilan testlar yaratish"));
    }
    buttons.push(el("button", {
      class: "btn-ghost",
      onclick: () => { nav("#/grade/" + topic.grade_id); },
    }, "‹ Mavzularga qaytish"));

    const viewEl = el("div", null, [
      el("div", { class: "hero" }, [
        el("h1", { class: "hero__title", text: topic.title }),
        el("p", { class: "hero__subtitle", text: hasContent ? "Dars tayyor" : "Dars hali tayyorlanmagan" }),
      ]),
      el("article", { class: "lesson", html: lessonHtml }),
      el("div", { class: "lesson-actions" }, buttons),
    ]);
    view.innerHTML = "";
    view.appendChild(viewEl);
  }

  function renderGenerating(topicId) {
    backButton(null);
    const view = document.getElementById("view");
    view.innerHTML = "";
    view.appendChild(el("div", { class: "loading-screen" }, [
      el("div", { class: "loader loading-screen__spinner" }),
      el("h2", { class: "loading-screen__title", text: "AI dars tayyorlamoqda..." }),
      el("p", { class: "loading-screen__hint", text: "10-30 soniya kuting. Dars va 5 ta test yaratilmoqda." }),
    ]));
    view.style.opacity = "1";

    api("/topic/" + topicId + "/generate", { method: "POST" }).then((res) => {
      ok();
      if (res && res.topic) {
        showToast(res.generated ? "✅ Yangi dars yaratildi!" : "✅ Testlar yaratildi!");
        nav("#/topic/" + topicId);
      } else {
        showToast("AI xatolik qaytardi");
        nav("#/topic/" + topicId);
      }
    }).catch((e) => {
      bad();
      showToast("Xatolik: OPENROUTER_API_KEY tekshiring");
      nav("#/topic/" + topicId);
    });
  }

  async function renderQuiz(topicId) {
    backButton(null);
    const view = document.getElementById("view");
    view.innerHTML = "";
    view.appendChild(el("div", { class: "loading-screen" }, [
      el("div", { class: "loader loading-screen__spinner" }),
      el("p", { class: "loading-screen__hint", text: "Testlar yuklanmoqda..." }),
    ]));
    view.style.opacity = "1";

    let quizzes;
    try {
      quizzes = await api("/quiz/" + topicId);
    } catch (e) {
      showToast("Testlarni yuklab bo'lmadi");
      nav("#/topic/" + topicId);
      return;
    }
    if (!quizzes || !quizzes.length) {
      showToast("Bu mavzu uchun testlar yo'q");
      nav("#/topic/" + topicId);
      return;
    }

    const state = {
      topic_id: parseInt(topicId, 10),
      quizzes: quizzes,
      current: 0,
      answers: [],
      submitted: false,
      reveal: false,
    };

    backButton("#/topic/" + topicId);

    const draw = () => {
      view.innerHTML = "";
      view.appendChild(quizMarkup(state, draw));
    };
    draw();
  }

  function quizMarkup(state, draw) {
    const q = state.quizzes[state.current];
    const total = state.quizzes.length;
    const progress = Math.round(((state.current + (state.reveal ? 1 : 0)) / total) * 100);

    const optionsEl = el("div", { class: "quiz-options" });
    q.options.forEach((opt, i) => {
      const letter = "ABCD"[i];
      const isSelected = state.answers[state.current] === letter;
      const cls = ["quiz-option"];
      if (state.reveal) {
        if (letter === q.correct_option) cls.push("quiz-option--correct");
        else if (isSelected) cls.push("quiz-option--incorrect");
        cls.push("quiz-option--disabled");
      } else if (isSelected) {
        cls.push("quiz-option--selected");
      }
      const optBtn = el("button", {
        class: cls.join(" "),
        onclick: () => {
          if (state.reveal) return;
          tap();
          state.answers[state.current] = letter;
          draw();
        },
      }, [
        el("div", { class: "quiz-option__letter", text: letter }),
        el("div", { text: opt }),
      ]);
      optionsEl.appendChild(optBtn);
    });

    const explanationEl = state.reveal && q.explanation
      ? el("div", { class: "quiz-explanation" }, [
          el("div", { class: "quiz-explanation__icon", text: "💡" }),
          el("div", { text: q.explanation }),
        ])
      : null;

    const actionBtn = state.reveal
      ? (state.current === total - 1
          ? el("button", {
              class: "btn-primary",
              onclick: () => { tap(); submitQuiz(state); },
            }, "📊 Natijani ko'rish")
          : el("button", {
              class: "btn-primary",
              onclick: () => { tap(); state.current++; state.reveal = false; draw(); },
            }, "Keyingi savol →"))
      : el("button", {
          class: "btn-primary",
          disabled: !state.answers[state.current] ? "" : null,
          onclick: () => {
            if (!state.answers[state.current]) {
              showToast("Variantni tanlang");
              return;
            }
            tap();
            state.reveal = true;
            draw();
          },
        }, "Javobni tekshirish");

    return el("div", null, [
      el("div", { class: "quiz-progress" }, [
        el("span", { text: "Test " + (state.current + 1) + " / " + total }),
        el("span", { text: progress + "%" }),
      ]),
      el("div", { class: "quiz-progress__bar" }, [
        el("div", { class: "quiz-progress__fill", style: "width:" + progress + "%" }),
      ]),
      el("div", { class: "quiz-question" }, [
        el("div", { class: "quiz-question__num", text: "Savol " + (state.current + 1) }),
        el("h2", { class: "quiz-question__text", text: q.question }),
      ]),
      optionsEl,
      explanationEl,
      el("div", { class: "lesson-actions" }, [actionBtn]),
    ]);
  }

  async function submitQuiz(state) {
    const view = document.getElementById("view");
    view.innerHTML = "";
    view.appendChild(el("div", { class: "loading-screen" }, [
      el("div", { class: "loader loading-screen__spinner" }),
      el("p", { class: "loading-screen__hint", text: "Tekshirilmoqda..." }),
    ]));

    const body = {
      answers: state.answers.map((sel, i) => ({ index: i, selected: sel || "" })),
    };
    let result;
    try {
      result = await api("/quiz/" + state.topic_id + "/submit", {
        method: "POST",
        body: JSON.stringify(body),
      });
    } catch (e) {
      showToast("Xatolik yuz berdi");
      nav("#/topic/" + state.topic_id);
      return;
    }
    if (result.percentage >= 80) ok();
    else if (result.percentage >= 60) tap();
    else bad();

    nav("#/result/" + state.topic_id + "?score=" + result.score + "&total=" + result.total);
  }

  async function renderResult(topicId) {
    backButton("#/topic/" + topicId);
    const params = parseHashQuery();
    const score = parseInt(params.score || "0", 10);
    const total = parseInt(params.total || "0", 10);
    const percent = total ? Math.round((score / total) * 100) : 0;

    let quiz = null;
    try {
      const qs = await api("/quiz/" + topicId);
      quiz = qs;
    } catch (e) {}

    const heroClass = percent >= 80 ? "result__hero--good" : percent >= 60 ? "result__hero--mid" : "result__hero--bad";
    const message = percent >= 80
      ? "🎉 Ajoyib natija!"
      : percent >= 60
        ? "👍 Yaxshi, lekin takrorlash kerak"
        : "📚 Ko'proq o'qib, qayta urinib ko'ring";

    const rows = (quiz || []).map((q, i) => {
      const stored = JSON.parse(sessionStorage.getItem("quiz_state_" + topicId) || "null");
      let sel = "";
      if (stored && stored.answers) sel = stored.answers[i] || "";
      const ok = sel === q.correct_option;
      return el("div", { class: "result-row" }, [
        el("div", { class: "result-row__icon", text: ok ? "✅" : "❌" }),
        el("div", { class: "result-row__body" }, [
          el("p", { class: "result-row__q", text: (i + 1) + ". " + q.question }),
          el("div", { class: "result-row__ans", text: "Sizning javob: " + (sel || "—") + " · To'g'ri: " + q.correct_option }),
        ]),
      ]);
    });

    const viewEl = el("div", { class: "result" }, [
      el("div", { class: "result__hero " + heroClass }, [
        el("div", { class: "result__score", text: score + " / " + total }),
        el("div", { class: "result__of", text: "to'g'ri javob" }),
        el("div", { class: "result__percent", text: percent + "%" }),
        el("p", { class: "result__msg", text: message }),
      ]),
      el("div", { class: "section-title", text: "Tafsilotlar" }),
      el("div", { class: "result__list" }, rows),
      el("button", { class: "btn-primary", onclick: () => { tap(); nav("#/quiz/" + topicId); } }, "🔄 Qayta ishlash"),
      el("button", { class: "btn-ghost", onclick: () => { nav("#/topic/" + topicId); } }, "‹ Mavzuga qaytish"),
    ]);
    const view = document.getElementById("view");
    view.innerHTML = "";
    view.appendChild(viewEl);
    view.style.opacity = "1";
  }

  // ----------------------- Helpers -----------------------
  function subjectDisplay(name) {
    const map = {
      native_language: "Ona tili",
      literature: "Adabiyot",
      history: "Tarix",
    };
    return map[name] || name;
  }

  function parseHashQuery() {
    const hash = location.hash.slice(1);
    const qIdx = hash.indexOf("?");
    if (qIdx < 0) return {};
    const parts = hash.slice(qIdx + 1).split("&");
    const out = {};
    parts.forEach((p) => {
      const [k, v] = p.split("=");
      out[decodeURIComponent(k)] = decodeURIComponent(v || "");
    });
    return out;
  }

  function sanitizeHtml(html) {
    // Minimal sanitizer: drop <script>, <style>, <iframe>, on* attributes, javascript: URLs.
    // For production-grade safety, replace with DOMPurify. The OpenRouter output is
    // controlled, but defense-in-depth.
    let s = String(html || "");
    s = s.replace(/<\s*script[^>]*>[\s\S]*?<\s*\/\s*script\s*>/gi, "");
    s = s.replace(/<\s*style[^>]*>[\s\S]*?<\s*\/\s*style\s*>/gi, "");
    s = s.replace(/<\s*iframe[^>]*>[\s\S]*?<\s*\/\s*iframe\s*>/gi, "");
    s = s.replace(/ on\w+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "");
    s = s.replace(/javascript:/gi, "");
    return s;
  }

  function skeletonLesson() {
    return '<div class="lesson">'
      + '<div class="skeleton skeleton--title"></div>'
      + '<div class="skeleton skeleton--line"></div>'
      + '<div class="skeleton skeleton--line"></div>'
      + '<div class="skeleton skeleton--short"></div>'
      + '</div>';
  }

  // ----------------------- Router -----------------------
  function router() {
    const hash = (location.hash || "#/").slice(1);
    const path = hash.split("?")[0];
    if (path === "/" || path === "") return renderHome();
    const parts = path.split("/").filter(Boolean);
    if (parts[0] === "subject" && parts[1]) return renderGrades(parts[1]);
    if (parts[0] === "grade" && parts[1]) return renderTopics(parts[1]);
    if (parts[0] === "topic" && parts[1]) return renderTopic(parts[1]);
    if (parts[0] === "quiz" && parts[1]) return renderQuiz(parts[1]);
    if (parts[0] === "result" && parts[1]) return renderResult(parts[1]);
    if (parts[0] === "generating" && parts[1]) return renderGenerating(parts[1]);
    return renderHome();
  }

  window.addEventListener("hashchange", router);
  document.addEventListener("DOMContentLoaded", router);
  if (document.readyState !== "loading") router();
})();