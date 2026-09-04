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

  function getTelegramUser() {
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
      const u = tg.initDataUnsafe.user;
      return { id: u.id, username: u.username || "", full_name: u.first_name + (u.last_name ? " " + u.last_name : "") };
    }
    return null;
  }

  function withUser(body) {
    const u = getTelegramUser();
    if (!u) return body || {};
    return Object.assign({}, body || {}, { user: u });
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

    // Mini App user info (from Telegram WebApp SDK)
    const userLine = tg && tg.initDataUnsafe && tg.initDataUnsafe.user
      ? el("div", { class: "hero__user", text: "Salom, " + (tg.initDataUnsafe.user.first_name || "foydalanuvchi") + "!" })
      : null;

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

      // Simulator & essay quick links
      const quickCards = [
        el("button", {
          class: "card card--gradient card--success",
          onclick: () => { tap(); nav("#/exam/info"); },
        }, [
          el("div", { class: "card__icon", text: "⏱️" }),
          el("div", { class: "card__body" }, [
            el("div", { class: "card__title", text: "Imtihon simulyatori" }),
            el("div", { class: "card__meta", text: "45 ta savol · 180 daqiqa · haqiqiy sertifikat formati" }),
          ]),
          el("div", { class: "card__chevron", text: "›" }),
        ]),
        el("button", {
          class: "card card--gradient card--warm",
          onclick: () => { tap(); nav("#/essay/list"); },
        }, [
          el("div", { class: "card__icon", text: "✍️" }),
          el("div", { class: "card__body" }, [
            el("div", { class: "card__title", text: "Esse mashqi" }),
            el("div", { class: "card__meta", text: "12 ta esse mavzusi · AI tomonidan 12 mezon bo'yicha tekshirish" }),
          ]),
          el("div", { class: "card__chevron", text: "›" }),
        ]),
      ];

      const view = el("div", null, [
        el("div", { class: "hero" }, [
          userLine,
          el("h1", { class: "hero__title", text: "Milliy Sertifikat" }),
          el("p", { class: "hero__subtitle", text: "5-sinfdan 11-sinfgacha — darslar va interaktiv testlar" }),
        ]),
        el("div", { class: "section-title", text: "Tayyorlov vositalari" }),
        ...quickCards,
        el("div", { class: "section-title", text: "Fanlar" }),
        ...cards,
        tg && tg.initDataUnsafe && tg.initDataUnsafe.user ? el("button", {
          class: "card card--gradient",
          style: "background: var(--gradient-2); color: #fff;",
          onclick: () => { tap(); nav("#/profile"); },
        }, [
          el("div", { class: "card__icon", text: "📊" }),
          el("div", { class: "card__body" }, [
            el("div", { class: "card__title", text: "Mening statistikam" }),
            el("div", { class: "card__meta", text: "Testlar, esselar, imtihonlar natijalari" }),
          ]),
          el("div", { class: "card__chevron", text: "›" }),
        ]) : null,
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

    const body = withUser({
      answers: state.answers.map((sel, i) => ({ index: i, selected: sel || "" })),
    });
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

  // ----------------------- Essay Pages -----------------------
  async function renderEssayList() {
    backButton("#/");
    document.getElementById("header-subtitle").textContent = "Esse mavzulari";

    let topics;
    try {
      topics = await api("/essay/topics");
    } catch (e) {
      showToast("Mavzularni yuklab bo'lmadi");
      nav("#/");
      return;
    }

    const view = el("div", null, [
      el("button", { class: "btn-ghost", onclick: () => nav("#/") }, "‹ Bosh menyuga"),
      el("div", { class: "hero", style: "background: var(--gradient-warm); color: #0f172a" }, [
        el("h1", { class: "hero__title", text: "Esse mashqi" }),
        el("p", { class: "hero__subtitle", text: "Haqiqiy sertifikat mavzulari. AI sizning essengizni 12 mezon bo'yicha tekshiradi." }),
      ]),
      el("div", { class: "section-title", text: "Mavzular ro'yxati" }),
      ...topics.map((t, i) =>
        el("button", {
          class: "topic-card",
          onclick: () => { tap(); nav("#/essay/write/" + t.id); },
        }, [
          el("div", { class: "topic-card__num", text: String(i + 1).padStart(2, "0") }),
          el("div", { class: "topic-card__title", text: t.title }),
          el("span", { class: "badge badge--ai", text: "✍️ Esse" }),
        ])
      ),
    ]);
    const target = document.getElementById("view");
    target.innerHTML = "";
    target.appendChild(view);
    target.style.opacity = "1";
  }

  async function renderEssayWrite(topicId) {
    backButton("#/essay/list");
    let topic;
    try {
      topic = await api("/essay/topic/" + topicId);
    } catch (e) {
      showToast("Mavzu topilmadi");
      nav("#/essay/list");
      return;
    }
    document.getElementById("header-subtitle").textContent = topic.title;

    const textarea = el("textarea", {
      class: "essay-textarea",
      placeholder: "Esse matnini shu yerga yozing... (kamida 100 so'z)",
      rows: "12",
    });

    const submit = el("button", {
      class: "btn-primary",
      onclick: async () => {
        const text = textarea.value.trim();
        if (text.length < 100) {
          showToast("Kamida 100 so'z yozing. Hozir: " + text.split(/\s+/).filter(Boolean).length);
          return;
        }
        tap();
        // Show loading
        const view = document.getElementById("view");
        view.innerHTML = "";
        view.appendChild(el("div", { class: "loading-screen" }, [
          el("div", { class: "loader loading-screen__spinner" }),
          el("h2", { class: "loading-screen__title", text: "AI esseni tekshirmoqda..." }),
          el("p", { class: "loading-screen__hint", text: "12 mezon bo'yicha 30-60 soniya kuting." }),
        ]));
        view.style.opacity = "1";

        try {
          const result = await api("/essay/grade", {
            method: "POST",
            body: JSON.stringify(withUser({ topic_id: parseInt(topicId, 10), text: text })),
          });
          ok();
          // Save result to localStorage so we can reload it
          try { localStorage.setItem("essay_result_" + topicId, JSON.stringify(result)); } catch (e) {}
          nav("#/essay/result/" + topicId);
        } catch (e) {
          bad();
          showToast("Xatolik: " + e.message);
          nav("#/essay/write/" + topicId);
        }
      },
    }, "📤 Tekshirishga yuborish");

    const view = el("div", null, [
      el("div", { class: "hero", style: "background: var(--gradient-warm); color: #0f172a" }, [
        el("h1", { class: "hero__title", text: topic.title }),
      ]),
      el("div", { class: "essay-prompt" }, [
        el("div", { class: "essay-prompt__label", text: "📋 VAZIYAT" }),
        el("p", { text: topic.situation }),
        el("div", { class: "essay-prompt__views" }, [
          el("div", { class: "essay-prompt__view" }, [
            el("strong", { text: "Qarash A: " }),
            el("span", { text: topic.viewpoint_a }),
          ]),
          el("div", { class: "essay-prompt__view" }, [
            el("strong", { text: "Qarash B: " }),
            el("span", { text: topic.viewpoint_b }),
          ]),
        ]),
        el("div", { class: "essay-prompt__hint", html: "<strong>Eslatma:</strong> publitsistik uslubda, kirish + asosiy qism + xulosa shaklida, vaziyat yuzasidan ikkala qarashni yoritib, dalillar keltiring va shaxsiy fikringizni bildiring." }),
      ]),
      textarea,
      el("div", { class: "lesson-actions" }, [submit]),
    ]);
    const target = document.getElementById("view");
    target.innerHTML = "";
    target.appendChild(view);
    target.style.opacity = "1";
  }

  async function renderEssayResult(topicId) {
    backButton("#/essay/list");
    let result;
    try {
      const raw = localStorage.getItem("essay_result_" + topicId);
      if (!raw) throw new Error("no cached result");
      result = JSON.parse(raw);
    } catch (e) {
      showToast("Natija topilmadi");
      nav("#/essay/list");
      return;
    }

    const total = result.total_score || 0;
    const max = result.max_score || 24;
    const pct = result.percentage || Math.round((total / max) * 100);
    const heroClass = pct >= 71 ? "result__hero--good" : pct >= 50 ? "result__hero--mid" : "result__hero--bad";
    const levelLabel = result.level || (pct >= 86 ? "A+" : pct >= 71 ? "A" : pct >= 56 ? "B+" : pct >= 41 ? "B" : "C");

    const disqual = result.disqualification_reason;
    const criteriaRows = (result.criteria || []).map((c) =>
      el("div", { class: "result-row" }, [
        el("div", { class: "result-row__icon", text: c.score >= 1.5 ? "✅" : c.score >= 1 ? "🟡" : "❌" }),
        el("div", { class: "result-row__body" }, [
          el("p", { class: "result-row__q", text: c.id + ". " + c.name + " — " + c.score + " / 2" }),
          el("div", { class: "result-row__ans", text: c.justification || "" }),
        ]),
      ])
    );

    const view = el("div", { class: "result" }, [
      el("div", { class: "result__hero " + heroClass }, [
        el("div", { class: "result__score", text: total + " / " + max }),
        el("div", { class: "result__of", text: "ball" }),
        el("div", { class: "result__percent", text: pct + "% · " + levelLabel }),
        el("p", { class: "result__msg", text: disqual || result.feedback_summary || "" }),
      ]),
      disqual ? null : el("div", { class: "section-title", text: "Mezonlar bo'yicha tahlil" }),
      disqual ? null : el("div", { class: "result__list" }, criteriaRows),
      el("button", { class: "btn-primary", onclick: () => { tap(); nav("#/essay/write/" + topicId); } }, "✍️ Qayta yozish"),
      el("button", { class: "btn-ghost", onclick: () => nav("#/essay/list") }, "‹ Boshqa mavzu tanlash"),
    ]);
    const target = document.getElementById("view");
    target.innerHTML = "";
    target.appendChild(view);
    target.style.opacity = "1";
  }

  // ----------------------- Exam Simulator Pages -----------------------
  async function renderExamInfo() {
    backButton("#/");
    let meta;
    try {
      meta = await api("/exam/meta");
    } catch (e) {
      showToast("Imtihon ma'lumotini yuklab bo'lmadi");
      nav("#/");
      return;
    }
    document.getElementById("header-subtitle").textContent = "Imtihon simulyatori";

    const sections = (meta.sections || []).map((s) =>
      el("div", { class: "exam-section" }, [
        el("div", { class: "exam-section__name", text: s.name }),
        el("div", { class: "exam-section__count", text: s.question_count + " ta · " + s.points_per_question + " b." }),
      ])
    );

    const view = el("div", null, [
      el("button", { class: "btn-ghost", onclick: () => nav("#/") }, "‹ Bosh menyuga"),
      el("div", { class: "hero", style: "background: var(--gradient-success); color: #0f172a" }, [
        el("h1", { class: "hero__title", text: "Imtihon simulyatori" }),
        el("p", { class: "hero__subtitle", text: meta.subject + " · " + meta.total_questions + " ta savol · " + meta.duration_minutes + " daqiqa · " + meta.total_score + " ball" }),
      ]),
      el("div", { class: "exam-info" }, [
        el("h3", { text: "📋 Imtihon formati" }),
        el("p", { text: "Bu simulyator Davlat test markazi tomonidan haqiqiy sertifikat imtihoni uchun belgilangan formatga to'liq mos." }),
        el("h3", { text: "📚 Bo'limlar" }),
        el("div", { class: "exam-sections" }, sections),
        el("h3", { text: "⚠️ Muhim" }),
        el("ul", null, [
          el("li", { text: "Vaqt tugaganda imtihon avtomatik yakunlanadi" }),
          el("li", { text: "Yopiq testlar (Y-1, Y-2) avtomatik tekshiriladi" }),
          el("li", { text: "Esse (O-2) AI tomonidan 12 mezon bo'yicha baholanadi" }),
          el("li", { text: "Yozma savodxonlik (esse) — 24 ball" }),
        ]),
      ]),
      el("div", { class: "lesson-actions" }, [
        el("button", {
          class: "btn-primary",
          onclick: () => { tap(); nav("#/exam/run"); },
        }, "🚀 Imtihonni boshlash"),
      ]),
    ]);
    const target = document.getElementById("view");
    target.innerHTML = "";
    target.appendChild(view);
    target.style.opacity = "1";
  }

  async function renderExamRun() {
    backButton(null);

    // Generate a fresh exam
    let exam;
    try {
      exam = await api("/exam/generate?seed=" + Date.now());
    } catch (e) {
      showToast("Imtihonni yuklab bo'lmadi");
      nav("#/");
      return;
    }

    // Persist exam for grading
    try { localStorage.setItem("current_exam", JSON.stringify(exam)); } catch (e) {}

    const state = {
      exam: exam,
      current: 0,
      answers: {},
      essayText: "",
      essayTopicId: null,
      startedAt: Date.now(),
      durationSec: exam.duration_minutes * 60,
    };

    backButton(null); // no back during exam
    drawExam(state);

    // Timer
    if (state._timer) clearInterval(state._timer);
    state._timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - state.startedAt) / 1000);
      const remaining = state.durationSec - elapsed;
      const tEl = document.getElementById("exam-timer");
      if (tEl) {
        if (remaining <= 0) {
          tEl.textContent = "⏰ VAQT TUGADI";
          tEl.classList.add("exam-timer--danger");
          clearInterval(state._timer);
          submitExam(state);
        } else {
          const m = Math.floor(remaining / 60);
          const s = remaining % 60;
          tEl.textContent = `⏱️ ${m}:${String(s).padStart(2, "0")}`;
          if (remaining < 300) tEl.classList.add("exam-timer--danger");
        }
      }
    }, 1000);

    window._examState = state;
  }

  function drawExam(state) {
    const view = document.getElementById("view");
    view.innerHTML = "";
    view.appendChild(el("div", { class: "exam-header" }, [
      el("div", { class: "exam-header__info" }, [
        el("div", { class: "exam-header__title", text: "Milliy sertifikat imtihoni" }),
        el("div", { class: "exam-header__progress", text: `Savol ${state.current + 1} / ${state.exam.total_questions}` }),
      ]),
      el("div", { id: "exam-timer", class: "exam-timer", text: "⏱️ ..." }),
    ]));

    const q = state.exam.questions[state.current];
    const isEssay = q.type === "O-2";

    const sectionLabel = el("div", { class: "exam-section-tag", text: "Bo'lim: " + q.section_name });

    const questionBlock = el("div", { class: "exam-question" }, [
      el("div", { class: "exam-question__num", text: "Savol " + (state.current + 1) }),
      el("h2", { class: "exam-question__text", text: q.question }),
    ]);

    const answerBlock = el("div", { class: "exam-answer" });
    if (isEssay) {
      // For essay questions, load topics into the textarea placeholder
      api("/essay/topics").then((topics) => {
        if (topics && topics.length) {
          const topicId = state.essayTopicId || topics[0].id;
          state.essayTopicId = topicId;
          const topic = topics.find((t) => t.id === topicId) || topics[0];
          const select = el("select", {
            class: "essay-topic-select",
            onchange: (e) => { state.essayTopicId = parseInt(e.target.value, 10); },
          }, topics.map((t) => {
            const opt = el("option", { value: t.id, text: t.title });
            if (t.id === topicId) opt.selected = true;
            return opt;
          }));
          const ta = el("textarea", {
            class: "essay-textarea",
            rows: "10",
            placeholder: "Esse matnini shu yerga yozing...",
            oninput: (e) => { state.essayText = e.target.value; },
          });
          ta.value = state.essayText;
          const prompt = el("div", { class: "essay-prompt" }, [
            el("p", { text: topic.situation }),
            el("div", { class: "essay-prompt__view" }, [
              el("strong", { text: "A: " }),
              el("span", { text: topic.viewpoint_a }),
            ]),
            el("div", { class: "essay-prompt__view" }, [
              el("strong", { text: "B: " }),
              el("span", { text: topic.viewpoint_b }),
            ]),
          ]);
          // clear and rebuild
          answerBlock.innerHTML = "";
          answerBlock.appendChild(el("div", { class: "essay-topic-picker" }, [
            el("label", { text: "Mavzu: " }),
            select,
          ]));
          answerBlock.appendChild(prompt);
          answerBlock.appendChild(ta);
        }
      });
    } else if (q.options) {
      const optionsEl = el("div", { class: "quiz-options" });
      q.options.forEach((opt, i) => {
        const letter = "ABCD"[i];
        const isSelected = state.answers[q.id] === letter;
        const optBtn = el("button", {
          class: "quiz-option" + (isSelected ? " quiz-option--selected" : ""),
          onclick: () => {
            tap();
            state.answers[q.id] = letter;
            drawExam(state);
          },
        }, [
          el("div", { class: "quiz-option__letter", text: letter }),
          el("div", { text: opt }),
        ]);
        optionsEl.appendChild(optBtn);
      });
      answerBlock.appendChild(optionsEl);
    } else {
      // Open-ended (O-1) — short answer
      const inp = el("input", {
        type: "text",
        class: "essay-topic-select",
        placeholder: "Javobingizni kiriting",
        oninput: (e) => { state.answers[q.id] = e.target.value; },
      });
      inp.value = state.answers[q.id] || "";
      answerBlock.appendChild(inp);
    }

    view.appendChild(el("div", { class: "exam-body" }, [
      sectionLabel,
      questionBlock,
      answerBlock,
    ]));

    // Navigation
    const navBtns = el("div", { class: "exam-nav" });
    if (state.current > 0) {
      navBtns.appendChild(el("button", {
        class: "btn-ghost",
        onclick: () => { tap(); state.current--; drawExam(state); },
      }, "‹ Oldingi"));
    }
    if (state.current < state.exam.total_questions - 1) {
      navBtns.appendChild(el("button", {
        class: "btn-primary",
        onclick: () => { tap(); state.current++; drawExam(state); },
      }, "Keyingi ›"));
    } else {
      navBtns.appendChild(el("button", {
        class: "btn-primary",
        onclick: () => { tap(); submitExam(state); },
      }, "✅ Imtihonni yakunlash"));
    }
    view.appendChild(navBtns);

    // Save state to window for access from submit
    window._examState = state;
  }

  async function submitExam(state) {
    if (state._timer) clearInterval(state._timer);
    if (state._submitted) return;
    state._submitted = true;

    const view = document.getElementById("view");
    view.innerHTML = "";
    view.appendChild(el("div", { class: "loading-screen" }, [
      el("div", { class: "loader loading-screen__spinner" }),
      el("h2", { class: "loading-screen__title", text: "Imtihon natijalari hisoblanmoqda..." }),
      el("p", { class: "loading-screen__hint", text: "Esse AI tomonidan tekshirilmoqda. 30-60 soniya kuting." }),
    ]));

    let result;
    try {
      result = await api("/exam/grade", {
        method: "POST",
        body: JSON.stringify(withUser({
          questions: state.exam.questions,
          closed_answers: state.answers,
          essay_topic_id: state.essayTopicId,
          essay_text: state.essayText || null,
        })),
      });
      ok();
      try { localStorage.setItem("exam_result", JSON.stringify(result)); } catch (e) {}
      nav("#/exam/result");
    } catch (e) {
      bad();
      showToast("Natijani hisoblashda xatolik: " + e.message);
      nav("#/");
    }
  }

  async function renderExamResult() {
    backButton("#/");
    let result;
    try {
      const raw = localStorage.getItem("exam_result");
      if (!raw) throw new Error("no result");
      result = JSON.parse(raw);
    } catch (e) {
      showToast("Natija topilmadi");
      nav("#/");
      return;
    }
    const total = result.total_earned || 0;
    const max = result.total_max || 76.8;
    const pct = result.percentage || 0;
    const level = result.level || {};
    const heroClass = pct >= 71 ? "result__hero--good" : pct >= 50 ? "result__hero--mid" : "result__hero--bad";

    const closed = result.closed || {};
    const essay = result.essay || null;
    const closedRows = (closed.per_question || []).map((p) =>
      el("div", { class: "result-row" }, [
        el("div", { class: "result-row__icon", text: p.is_correct ? "✅" : "❌" }),
        el("div", { class: "result-row__body" }, [
          el("p", { class: "result-row__q", text: "Savol " + p.id + " — " + (p.is_correct ? "To'g'ri" : "Noto'g'ri") + " (" + p.points_earned + "/" + p.points_possible + ")" }),
        ]),
      ])
    );

    const view = el("div", { class: "result" }, [
      el("div", { class: "result__hero " + heroClass }, [
        el("div", { class: "result__score", text: total + " / " + max }),
        el("div", { class: "result__of", text: "ball · " + pct + "%" }),
        el("div", { class: "result__percent", text: (level.label || "") }),
        el("p", { class: "result__msg", text: level.comment || "" }),
      ]),
      el("div", { class: "result__summary" }, [
        el("div", { class: "result__summary-row" }, [
          el("span", { text: "Yopiq testlar (Y-1, Y-2)" }),
          el("strong", { text: (closed.closed_score || 0) + " / " + (closed.closed_max || 0) }),
        ]),
        el("div", { class: "result__summary-row" }, [
          el("span", { text: "Esse (Yozma savodxonlik)" }),
          el("strong", { text: essay ? (essay.total_score + " / " + essay.max_score) : "Tekshirilmagan" }),
        ]),
      ]),
      closedRows.length ? el("div", null, [
        el("div", { class: "section-title", text: "Yopiq test natijalari" }),
        el("div", { class: "result__list" }, closedRows),
      ]) : null,
      essay && essay.criteria && essay.criteria.length ? el("div", null, [
        el("div", { class: "section-title", text: "Esse mezonlari" }),
        el("div", { class: "result__list" }, essay.criteria.map((c) =>
          el("div", { class: "result-row" }, [
            el("div", { class: "result-row__icon", text: c.score >= 1.5 ? "✅" : c.score >= 1 ? "🟡" : "❌" }),
            el("div", { class: "result-row__body" }, [
              el("p", { class: "result-row__q", text: c.id + ". " + c.name + " — " + c.score + "/2" }),
              el("div", { class: "result-row__ans", text: c.justification || "" }),
            ]),
          ])
        )),
      ]) : null,
      el("button", { class: "btn-primary", onclick: () => { tap(); nav("#/exam/run"); } }, "🔄 Qayta topshirish"),
      el("button", { class: "btn-ghost", onclick: () => nav("#/") }, "‹ Bosh menyuga"),
    ]);
    const target = document.getElementById("view");
    target.innerHTML = "";
    target.appendChild(view);
    target.style.opacity = "1";
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
    if (parts[0] === "essay" && parts[1] === "list") return renderEssayList();
    if (parts[0] === "essay" && parts[1] === "write" && parts[2]) return renderEssayWrite(parts[2]);
    if (parts[0] === "essay" && parts[1] === "result" && parts[2]) return renderEssayResult(parts[2]);
    if (parts[0] === "exam" && parts[1] === "info") return renderExamInfo();
    if (parts[0] === "exam" && parts[1] === "run") return renderExamRun();
    if (parts[0] === "exam" && parts[1] === "result") return renderExamResult();
    if (parts[0] === "profile") return renderProfile();
    if (parts[0] === "leaderboard") return renderLeaderboard();
    return renderHome();
  }

  // ----------------------- Profile & Leaderboard -----------------------
  async function renderProfile() {
    backButton("#/");
    const u = getTelegramUser();
    if (!u) {
      showToast("Faqat Telegram ichida ishlaydi");
      nav("#/");
      return;
    }
    document.getElementById("header-subtitle").textContent = "Mening statistikam";

    let stats, attempts;
    try {
      [stats, attempts] = await Promise.all([
        api("/user/" + u.id + "/stats"),
        api("/user/" + u.id + "/attempts?limit=20"),
      ]);
    } catch (e) {
      showToast("Statistikani yuklab bo'lmadi");
      nav("#/");
      return;
    }

    const stat = (icon, label, value) =>
      el("div", { class: "stat-tile" }, [
        el("div", { class: "stat-tile__icon", text: icon }),
        el("div", { class: "stat-tile__value", text: value }),
        el("div", { class: "stat-tile__label", text: label }),
      ]);

    const attemptRows = (attempts || []).map((a) => {
      const icon = { quiz: "🧪", essay: "✍️", exam: "⏱" }[a.kind] || "•";
      return el("div", { class: "result-row" }, [
        el("div", { class: "result-row__icon", text: icon }),
        el("div", { class: "result-row__body" }, [
          el("p", { class: "result-row__q", text: (a.kind === "quiz" ? "Test" : a.kind === "essay" ? "Esse" : "Imtihon") + " — " + a.score + " / " + a.max_score + (a.level ? " · " + a.level : "") }),
          el("div", { class: "result-row__ans", text: a.percentage + "% · " + (a.created_at || "") }),
        ]),
      ]);
    });

    const view = el("div", null, [
      el("button", { class: "btn-ghost", onclick: () => nav("#/") }, "‹ Bosh menyuga"),
      el("div", { class: "hero", style: "background: var(--gradient-2); color: #fff;" }, [
        el("h1", { class: "hero__title", text: stats.full_name || "Foydalanuvchi" }),
        el("p", { class: "hero__subtitle", text: "Statistika va urinishlar tarixi" }),
      ]),
      el("div", { class: "section-title", text: "Umumiy ko'rsatkichlar" }),
      el("div", { class: "stat-grid" }, [
        stat("🧪", "Testlar", (stats.quizzes?.taken || 0) + " ta · " + (stats.quizzes?.accuracy_percent || 0) + "%"),
        stat("✍️", "Esselar", (stats.essays?.graded || 0) + " ta · " + (stats.essays?.average_percent || 0) + "%"),
        stat("⏱", "Imtihonlar", (stats.exams?.taken || 0) + " ta · " + (stats.exams?.average_percent || 0) + "%"),
      ]),
      el("div", { class: "section-title", text: "So'nggi urinishlar" }),
      attemptRows.length ? el("div", { class: "result__list" }, attemptRows) : el("div", { class: "lesson-empty", text: "Hali urinishlar yo'q" }),
      el("button", { class: "btn-ghost", onclick: () => { tap(); nav("#/leaderboard"); } }, "🏆 Eng yaxshilarni ko'rish"),
    ]);
    const target = document.getElementById("view");
    target.innerHTML = "";
    target.appendChild(view);
    target.style.opacity = "1";
  }

  async function renderLeaderboard() {
    backButton("#/");
    document.getElementById("header-subtitle").textContent = "Top foydalanuvchilar";
    let rows;
    try {
      rows = await api("/leaderboard?limit=20");
    } catch (e) {
      showToast("Liderlar jadvalini yuklab bo'lmadi");
      nav("#/");
      return;
    }
    if (!rows || !rows.length) {
      const target = document.getElementById("view");
      target.innerHTML = "";
      target.appendChild(el("div", { class: "lesson-empty", text: "Hali hech kim imtihon topshirmagan. Birinchi siz bo'ling!" }));
      target.style.opacity = "1";
      return;
    }
    const medals = ["🥇", "🥈", "🥉"];
    const rowsEl = rows.map((r, i) =>
      el("div", { class: "result-row" }, [
        el("div", { class: "result-row__icon", text: medals[i] || String(i + 1) }),
        el("div", { class: "result-row__body" }, [
          el("p", { class: "result-row__q", text: (i + 1) + ". " + r.full_name }),
          el("div", { class: "result-row__ans", text: r.avg_percent + "% · " + r.exams_taken + " ta imtihon" }),
        ]),
      ])
    );
    const view = el("div", null, [
      el("button", { class: "btn-ghost", onclick: () => nav("#/") }, "‹ Bosh menyuga"),
      el("div", { class: "hero", style: "background: var(--gradient-warm); color: #0f172a;" }, [
        el("h1", { class: "hero__title", text: "🏆 TOP foydalanuvchilar" }),
        el("p", { class: "hero__subtitle", text: "Imtihon natijalari bo'yicha" }),
      ]),
      el("div", { class: "result__list" }, rowsEl),
    ]);
    const target = document.getElementById("view");
    target.innerHTML = "";
    target.appendChild(view);
    target.style.opacity = "1";
  }

  window.addEventListener("hashchange", router);
  document.addEventListener("DOMContentLoaded", router);
  if (document.readyState !== "loading") router();
})();