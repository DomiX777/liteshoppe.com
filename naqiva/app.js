(function () {
  "use strict";
  var C = window.NAQIVA_CONFIG || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- URL params: variant + UTM ---------- */
  var params = new URLSearchParams(location.search);
  var variantKey = (params.get("v") || C.DEFAULT_VARIANT || "a").toLowerCase();
  var variants = C.VARIANTS || {};
  if (!variants[variantKey]) variantKey = C.DEFAULT_VARIANT || "a";
  var variant = variants[variantKey];
  if (variant) {
    if (variant.title) $("[data-v-title]").textContent = variant.title;
    if (variant.sub) $("[data-v-sub]").textContent = variant.sub;
  }
  var tracking = {
    variant: variantKey,
    utm_source: params.get("utm_source") || "",
    utm_medium: params.get("utm_medium") || "",
    utm_campaign: params.get("utm_campaign") || "",
    utm_content: params.get("utm_content") || ""
  };

  /* ---------- discount + price ---------- */
  var disc = Number(C.EARLY_DISCOUNT) || 20;
  $$("[data-discount]").forEach(function (el) { el.textContent = disc; });
  var price = Number(C.PRICE);
  if (price > 0) {
    var now = Math.round(price * (1 - disc / 100));
    $("[data-price-now]").textContent = now + " DH";
    var old = $("[data-price-old]");
    old.textContent = price + " DH";
    old.hidden = false;
  } else {
    $("[data-price-now]").textContent = "الثمن قريب";
    $("[data-price-now]").style.fontFamily = "var(--font-ar)";
    $("[data-price-now]").style.fontSize = "34px";
  }

  /* ---------- links ---------- */
  var wa = String(C.WHATSAPP || "").replace(/\D/g, "");
  var waLink = function (text) { return "https://wa.me/" + wa + (text ? "?text=" + encodeURIComponent(text) : ""); };
  if (wa) {
    var f = $("#wa-float");
    f.href = waLink("السلام، بغيت نعرف أكثر على Naqiva");
    f.style.display = "grid";
    var lw = $("#l-wa"); lw.href = waLink(""); lw.hidden = false;
  }
  if (C.INSTAGRAM_URL) { var li = $("#l-ig"); li.href = C.INSTAGRAM_URL; li.hidden = false; }
  if (C.TIKTOK_URL) { var lt = $("#l-tt"); lt.href = C.TIKTOK_URL; lt.hidden = false; }
  $("#year").textContent = new Date().getFullYear();

  /* ---------- pixels (loaded only when configured) ---------- */
  if (C.META_PIXEL_ID) {
    !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    window.fbq("init", C.META_PIXEL_ID);
    window.fbq("track", "PageView");
    window.fbq("track", "ViewContent", { content_name: "Naqiva Detox", variant: variantKey });
  }
  if (C.TIKTOK_PIXEL_ID) {
    !function (w, d, t) { w.TiktokAnalyticsObject = t; var ttq = w[t] = w[t] || []; ttq.methods = ["page", "track", "identify", "instances", "debug", "on", "off", "once", "ready", "alias", "group", "enableCookie", "disableCookie"]; ttq.setAndDefer = function (t, e) { t[e] = function () { t.push([e].concat(Array.prototype.slice.call(arguments, 0))); }; }; for (var i = 0; i < ttq.methods.length; i++) ttq.setAndDefer(ttq, ttq.methods[i]); ttq.instance = function (t) { for (var e = ttq._i[t] || [], n = 0; n < ttq.methods.length; n++) ttq.setAndDefer(e, ttq.methods[n]); return e; }; ttq.load = function (e, n) { var i = "https://analytics.tiktok.com/i18n/pixel/events.js"; ttq._i = ttq._i || {}; ttq._i[e] = []; ttq._i[e]._u = i; ttq._t = ttq._t || {}; ttq._t[e] = +new Date(); ttq._o = ttq._o || {}; ttq._o[e] = n || {}; var o = d.createElement("script"); o.type = "text/javascript"; o.async = !0; o.src = i + "?sdkid=" + e + "&lib=" + t; var a = d.getElementsByTagName("script")[0]; a.parentNode.insertBefore(o, a); }; ttq.load(C.TIKTOK_PIXEL_ID); ttq.page(); }(window, document, "ttq");
    window.ttq.track("ViewContent", { content_name: "Naqiva Detox" });
  }
  var trackEvent = function (meta, tiktok, data) {
    try { if (window.fbq) window.fbq("track", meta, data || {}); } catch (e) {}
    try { if (window.ttq) window.ttq.track(tiktok, data || {}); } catch (e) {}
  };
  $$("[data-cta]").forEach(function (a) {
    a.addEventListener("click", function () { trackEvent("InitiateCheckout", "ClickButton", { position: a.getAttribute("data-cta") }); });
  });

  /* ---------- sticky mobile CTA ---------- */
  var sticky = $("#mobile-cta");
  var hero = $(".hero");
  var reserve = $("#reserve");
  var heroOut = false, reserveIn = false;
  var updateSticky = function () { sticky.classList.toggle("show", heroOut && !reserveIn); };
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (e) { heroOut = !e[0].isIntersecting; updateSticky(); }).observe(hero);
    new IntersectionObserver(function (e) { reserveIn = e[0].isIntersecting; updateSticky(); }, { threshold: 0.15 }).observe(reserve);
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.12 });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    $$(".reveal").forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- form ---------- */
  var form = $("#lead-form");
  var btn = $("#f-submit");
  var normalizePhone = function (v) {
    var d = String(v).replace(/[\s\-.()]/g, "");
    d = d.replace(/^\+212/, "0").replace(/^00212/, "0").replace(/^212(?=[5-7]\d{8}$)/, "0");
    return d;
  };
  var setErr = function (id, msg) {
    $("#e-" + id).textContent = msg || "";
    var input = $("#f-" + id);
    if (msg) input.setAttribute("aria-invalid", "true"); else input.removeAttribute("aria-invalid");
  };

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var name = $("#f-name").value.trim();
    var phone = normalizePhone($("#f-phone").value);
    var city = $("#f-city").value;
    var concernEl = $("input[name=concern]:checked");
    var ok = true;
    setErr("name"); setErr("phone"); setErr("city");
    if (name.length < 2) { setErr("name", "كتب السمية ديالك عافاك"); ok = false; }
    if (!/^0[5-7]\d{8}$/.test(phone)) { setErr("phone", "الرقم ماشي صحيح. مثال: 0612345678"); ok = false; }
    if (!city) { setErr("city", "اختار المدينة ديالك"); ok = false; }
    if (!ok) { var first = $("[aria-invalid=true]"); if (first) first.focus(); return; }

    var data = {
      date: new Date().toISOString(),
      name: name, phone: phone, city: city,
      concern: concernEl ? concernEl.value : "",
      variant: tracking.variant,
      utm_source: tracking.utm_source, utm_medium: tracking.utm_medium,
      utm_campaign: tracking.utm_campaign, utm_content: tracking.utm_content,
      quiz_score: window.NAQIVA_QUIZ_SCORE == null ? "" : String(window.NAQIVA_QUIZ_SCORE),
      page: location.href.split("?")[0]
    };

    btn.disabled = true;
    btn.textContent = "كنسجلو…";

    var done = function () {
      trackEvent("Lead", "SubmitForm", { content_name: "Naqiva Detox", variant: tracking.variant });
      form.style.display = "none";
      var s = $("#success");
      s.style.display = "block";
      s.focus();
      var share = "شفت هاد الشامبو المغربي الجديد ضد الكالكير، Naqiva. سجل وخود -" + disc + "%: " + location.href.split("?")[0];
      $("#success-share").href = "https://wa.me/?text=" + encodeURIComponent(share);
      $("#success-share").target = "_blank";
    };

    if (C.SHEET_ENDPOINT) {
      fetch(C.SHEET_ENDPOINT, { method: "POST", mode: "no-cors", body: new URLSearchParams(data) })
        .then(done)
        .catch(function () {
          btn.disabled = false;
          btn.textContent = "عاود جرب";
          setErr("phone", "وقع مشكل فالاتصال. عاود جرب من بعد شوية.");
        });
    } else if (wa) {
      var msg = "السلام، بغيت نسجل فـ Naqiva\nالسمية: " + name + "\nالتيليفون: " + phone + "\nالمدينة: " + city + (data.concern ? "\nالمشكل: " + data.concern : "");
      window.open(waLink(msg), "_blank");
      done();
    } else {
      console.warn("Naqiva: SHEET_ENDPOINT and WHATSAPP are both empty in config.js. Lead not stored:", data);
      done();
    }
  });
})();

/* ---------- water quiz ---------- */
(function () {
  var box = document.getElementById("quiz-box");
  if (!box) return;
  box.addEventListener("change", function () {
    var vals = ["q1", "q2", "q3"].map(function (n) {
      var el = box.querySelector("input[name=" + n + "]:checked");
      return el ? Number(el.value) : null;
    });
    if (vals.indexOf(null) !== -1) return;
    var score = vals[0] + vals[1] + vals[2];
    var res = [
      ["الما ديالك غالباً خفيف", "مزيان! ولكن الكالكير كيتجمع مع الوقت، خصوصاً إلا كتسافر ولا كتبدل المدينة. Naqiva مرة فالسيمانة كيحافظ على شعرك نقي.", 25],
      ["ممكن يكون فيه شوية ديال الكالكير", "كاينين علامات صغار. إلا كان شعرك ناشف ولا ما فيهش اللمعة، جرب Detox مرة فالسيمانة وشوف الفرق.", 55],
      ["الما ديالك غالباً فيه الكالكير", "العلامات كاملين كيبينو أن الما قاصح. هادشي كيقدر يخلي الشعر ناشف وخشين. Naqiva مصنوع بالضبط لهاد الحالة.", 80],
      ["الما ديالك غالباً فيه الكالكير بزاف", "العلامات كاملين كيبينو أن الما قاصح بزاف. هادشي كيقدر يخلي الشعر ناشف وخشين. Naqiva مصنوع بالضبط لهاد الحالة.", 95]
    ][score];
    document.getElementById("quiz-title-r").textContent = res[0];
    document.getElementById("quiz-text").textContent = res[1];
    var r = document.getElementById("quiz-result");
    r.style.display = "block";
    setTimeout(function () { document.getElementById("quiz-meter").style.width = res[2] + "%"; }, 50);
    try { if (window.fbq) window.fbq("trackCustom", "QuizDone", { score: score }); } catch (e) {}
    try { if (window.ttq) window.ttq.track("ClickButton", { content_name: "quiz", value: score }); } catch (e) {}
    window.NAQIVA_QUIZ_SCORE = score;
  });
})();
