(function () {
  // Persist cursor state on window so it survives across MkDocs
  // instant-navigation script re-evaluations.
  var S = window.__rcv;
  if (!S) {
    S = { mx: 0, my: 0, has: false, init: false };
    window.__rcv = S;
  }

  var EL = { cx: 228, cy: 332 };
  var ER = { cx: 373, cy: 332 };
  var BC = { x: 300, y: 350 };
  var VBW = 601.3;
  var VBH = 595;
  var MAX_PUPIL = 8;
  var MAX_TILT = 3;

  function clamp(dx, dy, max) {
    var d = Math.sqrt(dx * dx + dy * dy);
    if (d === 0) return { dx: 0, dy: 0 };
    var s = Math.min(1, max / d);
    return { dx: dx * s, dy: dy * s };
  }

  function tick() {
    requestAnimationFrame(tick);
    if (!S.has) return;

    var svgs = document.querySelectorAll(".rendercv-logo-svg");
    for (var i = 0; i < svgs.length; i++) {
      var svg = svgs[i];
      var rect = svg.getBoundingClientRect();
      if (rect.width === 0) continue;

      // Screen coords to SVG viewBox coords (same approach as the web app)
      var px = ((S.mx - rect.left) / rect.width) * VBW;
      var py = ((S.my - rect.top) / rect.height) * VBH;

      var li = svg.querySelector('[data-eye="left"] .rendercv-iris');
      var ri = svg.querySelector('[data-eye="right"] .rendercv-iris');
      var body = svg.querySelector(".rendercv-body");

      if (li) {
        var c = clamp(px - EL.cx, py - EL.cy, MAX_PUPIL);
        li.setAttribute("transform", "translate(" + c.dx + "," + c.dy + ")");
      }
      if (ri) {
        var c2 = clamp(px - ER.cx, py - ER.cy, MAX_PUPIL);
        ri.setAttribute("transform", "translate(" + c2.dx + "," + c2.dy + ")");
      }

      if (body) {
        var cx = rect.left + rect.width / 2;
        var nx = Math.max(-1, Math.min(1, (S.mx - cx) / (window.innerWidth / 2)));
        var ny = Math.max(-1, Math.min(1,
          (S.my - (rect.top + rect.height / 2)) / (window.innerHeight / 2)));
        body.setAttribute(
          "transform",
          "translate(" + (nx * 2) + "," + (ny * 1.5) + ") " +
          "rotate(" + (nx * MAX_TILT) + "," + BC.x + "," + BC.y + ")"
        );
      }
    }
  }

  // Only set up the listener and animation loop once
  if (!S.init) {
    S.init = true;

    function capture(e) {
      S.mx = e.clientX;
      S.my = e.clientY;
      S.has = true;
    }

    // pointermove: primary tracking
    document.addEventListener("pointermove", capture);
    // mouseover: fires when new DOM appears under cursor (instant navigation)
    document.addEventListener("mouseover", capture);

    requestAnimationFrame(tick);
  }
})();
