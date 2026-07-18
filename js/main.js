/* Nkosi Thatchers — main.js
   Vanilla JS: current year, scroll reveal, lightbox, form validation + submit.
   The page is fully usable with this file absent (gallery links open the image
   directly; the form falls back to a normal Formspree POST). */
(function () {
  "use strict";

  /* ---------- current year ---------- */
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();

  /* ---------- close mobile menu after choosing a link ---------- */
  var navToggle = document.getElementById("nav-toggle");
  document.querySelectorAll(".site-nav a").forEach(function (a) {
    a.addEventListener("click", function () { if (navToggle) navToggle.checked = false; });
  });

  /* ---------- scroll reveal (respects reduced motion) ---------- */
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce && "IntersectionObserver" in window) {
    var targets = document.querySelectorAll(".section, .hero-body");
    targets.forEach(function (el) { el.classList.add("reveal"); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.08 });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* ================= LIGHTBOX ================= */
  var items = Array.prototype.slice.call(document.querySelectorAll(".gallery-item"));
  var lb = document.getElementById("lightbox");
  if (lb && items.length) {
    var lbImg = document.getElementById("lb-img");
    var btnClose = document.getElementById("lb-close");
    var btnPrev = document.getElementById("lb-prev");
    var btnNext = document.getElementById("lb-next");
    var current = 0;
    var lastFocus = null;

    function show(i) {
      current = (i + items.length) % items.length;
      var link = items[current];
      var img = link.querySelector("img");
      var full = link.getAttribute("data-full");
      if (!full || full === "#") full = img ? (img.currentSrc || img.src) : link.getAttribute("href");
      lbImg.src = full;
      lbImg.alt = img ? img.alt : "";
    }
    function open(i, trigger) {
      lastFocus = trigger || document.activeElement;
      show(i);
      lb.hidden = false;
      document.body.style.overflow = "hidden";
      btnClose.focus();
      document.addEventListener("keydown", onKey);
    }
    function close() {
      lb.hidden = true;
      document.body.style.overflow = "";
      document.removeEventListener("keydown", onKey);
      if (lastFocus) lastFocus.focus();
    }
    function onKey(e) {
      if (e.key === "Escape") close();
      else if (e.key === "ArrowRight") show(current + 1);
      else if (e.key === "ArrowLeft") show(current - 1);
      else if (e.key === "Tab") {
        // simple focus trap across the three controls
        var f = [btnClose, btnPrev, btnNext];
        var idx = f.indexOf(document.activeElement);
        e.preventDefault();
        var dir = e.shiftKey ? -1 : 1;
        f[(idx + dir + f.length) % f.length].focus();
      }
    }

    items.forEach(function (link, i) {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        open(i, link);
      });
    });
    btnClose.addEventListener("click", close);
    btnPrev.addEventListener("click", function () { show(current - 1); });
    btnNext.addEventListener("click", function () { show(current + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
  }

  /* ================= CONTACT FORM ================= */
  var form = document.getElementById("quote-form");
  if (!form) return;

  var success = document.getElementById("form-success");
  var topError = document.getElementById("form-top-error");

  function setError(name, msg) {
    var input = form.querySelector('[name="' + name + '"]');
    var err = document.getElementById("err-" + name);
    if (input) input.setAttribute("aria-invalid", msg ? "true" : "false");
    if (err) err.textContent = msg || "";
    return !msg;
  }

  function validate() {
    var ok = true;
    var v = function (n) { var el = form.querySelector('[name="' + n + '"]'); return el ? el.value.trim() : ""; };

    ok = setError("name", v("name") ? "" : "Please enter your name.") && ok;
    ok = setError("phone", v("phone") ? "" : "Please enter a phone number so we can call you back.") && ok;
    ok = setError("town", v("town") ? "" : "Please tell us your suburb or town.") && ok;
    ok = setError("message", v("message") ? "" : "Please tell us briefly what you need.") && ok;

    var email = v("email");
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      ok = setError("email", "That email address doesn't look right.") && ok;
    } else {
      setError("email", "");
    }
    return ok;
  }

  // live-clear errors as the user fixes fields
  form.addEventListener("input", function (e) {
    if (e.target.getAttribute("aria-invalid") === "true") {
      setError(e.target.name, "");
    }
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    topError.hidden = true;

    // honeypot — if filled, silently pretend success (drop the bot)
    var hp = form.querySelector('[name="company"]');
    if (hp && hp.value) { form.hidden = true; success.hidden = false; return; }

    if (!validate()) {
      var firstBad = form.querySelector('[aria-invalid="true"]');
      if (firstBad) firstBad.focus();
      return;
    }

    var action = form.getAttribute("action");
    var submitBtn = form.querySelector(".form-submit");

    // If the Formspree ID hasn't been pasted yet, don't pretend to send.
    if (action.indexOf("YOUR_FORM_ID") !== -1) {
      topError.textContent = "This form isn't connected yet. Please call 078 166 4646 or WhatsApp us.";
      topError.hidden = false;
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Sending…";

    fetch(action, {
      method: "POST",
      body: new FormData(form),
      headers: { Accept: "application/json" }
    })
      .then(function (res) {
        if (res.ok) {
          form.reset();
          form.hidden = true;
          success.hidden = false;
          success.focus && success.focus();
        } else {
          return res.json().then(function (data) {
            throw new Error((data && data.errors && data.errors.map(function (x) { return x.message; }).join(", ")) || "send failed");
          });
        }
      })
      .catch(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = "Send request";
        topError.textContent = "Sorry — something went wrong sending that. Please call 078 166 4646 or WhatsApp us.";
        topError.hidden = false;
      });
  });
})();
