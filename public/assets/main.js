/* 경기광주 재가복지센터 - 공통 스크립트 */

/* 상담 신청서를 받을 주소. 구글 Apps Script 웹앱 URL(또는 Formspree 주소)을 넣으면 접수가 시작돼요.
   비워 두면 "전화로 연락 주세요" 안내가 떠요. 설정 방법은 README.md 참고. */
var FORM_ENDPOINT = "";
var TEL = "031-000-0000";

(function () {
  /* ---------- 비용 계산기 ---------- */
  var LIMITS = [["1등급", 2512900], ["2등급", 2331200], ["3등급", 1528200], ["4등급", 1409700], ["5등급", 1208900], ["인지지원", 676320]];
  var TYPES = [["일반 15%", .15], ["감경 9%", .09], ["감경 6%", .06], ["기초수급", 0]];
  var won = function (n) { return Math.round(n).toLocaleString("ko-KR") + "원"; };
  var gEl = document.getElementById("grades"), tEl = document.getElementById("types");
  if (gEl && tEl) {
    var seg = function (el, list, name, idx) {
      list.forEach(function (it, i) {
        var l = document.createElement("label");
        l.innerHTML = '<input type="radio" name="' + name + '" id="' + name + '-' + i + '" value="' + i + '"' + (i === idx ? " checked" : "") + '><span>' + it[0] + '</span>';
        el.appendChild(l);
      });
    };
    seg(gEl, LIMITS, "cg", 2); seg(tEl, TYPES, "ct", 0);
    var calc = function () {
      var g = LIMITS[+document.querySelector("input[name=cg]:checked").value][1];
      var r = TYPES[+document.querySelector("input[name=ct]:checked").value][1];
      document.getElementById("r-limit").textContent = won(g);
      document.getElementById("r-gov").textContent = won(g * (1 - r));
      document.getElementById("r-me").textContent = won(g * r);
    };
    gEl.addEventListener("change", calc); tEl.addEventListener("change", calc); calc();
    var tb = document.getElementById("gradeTable");
    LIMITS.forEach(function (g) {
      var tr = document.createElement("tr");
      tr.innerHTML = "<td>" + g[0] + "</td><td>" + won(g[1]) + "</td><td>" + won(g[1] * .15) + "</td><td>" + won(g[1] * .09) + "</td><td>" + won(g[1] * .06) + "</td>";
      tb.appendChild(tr);
    });
  }

  /* ---------- FAQ 탭 ---------- */
  var tabs = document.querySelectorAll(".faq .tabs button"), items = document.querySelectorAll("#faqList details");
  tabs.forEach(function (b) {
    b.addEventListener("click", function () {
      tabs.forEach(function (x) { x.setAttribute("aria-selected", x === b ? "true" : "false"); });
      var g = b.dataset.g;
      items.forEach(function (d) { d.hidden = !(g === "all" || d.dataset.g === g); });
    });
  });

  /* ---------- 번호 복사 ---------- */
  var cp = document.getElementById("copyPhone");
  if (cp) cp.addEventListener("click", function () {
    var ok = function () { cp.textContent = "복사했어요"; setTimeout(function () { cp.textContent = "번호 복사"; }, 1800); };
    try { navigator.clipboard.writeText(TEL).then(ok, function () { cp.textContent = TEL; }); } catch (e) { cp.textContent = TEL; }
  });

  /* ---------- 상담 신청 ---------- */
  var form = document.getElementById("inq");
  if (form) {
    var ph = document.getElementById("f-phone"), errEl = document.getElementById("formErr"), btn = document.getElementById("submitBtn");
    ph.addEventListener("input", function () {
      var d = ph.value.replace(/\D/g, "").slice(0, 11);
      ph.value = d.length > 7 ? d.slice(0, 3) + "-" + d.slice(3, d.length - 4) + "-" + d.slice(-4) : d.length > 3 ? d.slice(0, 3) + "-" + d.slice(3) : d;
    });
    var showErr = function (m) { errEl.textContent = m; errEl.hidden = false; };
    form.addEventListener("submit", function (e) {
      e.preventDefault(); errEl.hidden = true;
      var name = form.name.value.trim(), phone = ph.value.trim();
      if (!name) { showErr("성함을 적어 주세요."); form.name.focus(); return; }
      if (phone.replace(/\D/g, "").length < 9) { showErr("연락받을 번호를 끝까지 적어 주세요."); ph.focus(); return; }
      if (!form.agree.checked) { showErr("연락처 수집에 동의해 주셔야 접수돼요."); return; }
      if (!FORM_ENDPOINT) { showErr("지금은 온라인 접수 준비 중이에요. " + TEL + "으로 전화 주시면 바로 상담해 드려요."); return; }
      var data = new URLSearchParams({
        name: name, phone: phone, rel: form.rel.value, area: form.area.value, grade: form.grade.value,
        time: form.time.value, msg: form.msg.value.trim(), page: location.href, createdAt: new Date().toISOString()
      });
      btn.disabled = true; btn.textContent = "보내는 중…";
      fetch(FORM_ENDPOINT, { method: "POST", mode: "no-cors", body: data }).then(function () {
        var area = document.getElementById("formArea"); area.innerHTML = "";
        var d = document.createElement("div"); d.className = "done"; d.setAttribute("role", "status");
        var h = document.createElement("h3"); h.textContent = "접수됐어요";
        var p = document.createElement("p"); p.textContent = (data.get("time") === "아무 때나" ? "최대한 빨리" : data.get("time") + "에") + " 센터장이 " + phone + "으로 직접 전화드릴게요.";
        var p2 = document.createElement("p"); p2.textContent = "급하면 " + TEL + "으로 바로 전화 주세요.";
        d.append(h, p, p2); area.appendChild(d);
      }).catch(function () {
        btn.disabled = false; btn.textContent = "상담 신청 보내기";
        showErr("전송이 안 됐어요. 잠시 뒤 다시 시도하거나 " + TEL + "으로 전화 주세요.");
      });
    });
  }

  /* ---------- 요양 정보 목록: 분류·검색 ---------- */
  var hubCards = document.getElementById("hubCards");
  if (hubCards) {
    var NAMES = window.CAT_NAMES || {};
    var cards = [].slice.call(hubCards.querySelectorAll(".card"));
    var links = [].slice.call(document.querySelectorAll(".side a"));
    var q = document.getElementById("hubQ"), picks = document.getElementById("picks");
    var state = { cat: new URLSearchParams(location.search).get("cat") || "all", q: "", n: 24 };
    var moreWrap = document.getElementById("hubMoreWrap"), moreBtn = document.getElementById("hubMore");
    if (!NAMES[state.cat]) state.cat = "all";
    var apply = function () {
      var n = 0;
      cards.forEach(function (c) {
        var ok = (state.cat === "all" || c.dataset.c === state.cat) && (!state.q || c.dataset.q.indexOf(state.q) >= 0);
        if (ok) n++;
        c.hidden = !ok || n > state.n;
      });
      moreWrap.hidden = n <= state.n;
      moreBtn.textContent = (n - state.n) + "개 더 보기";
      links.forEach(function (a) { a.setAttribute("aria-current", a.dataset.c === state.cat ? "true" : "false"); });
      document.getElementById("hubHead").textContent = state.q ? "‘" + state.q + "’ 검색 결과" : (state.cat === "all" ? "전체 글" : NAMES[state.cat]);
      document.getElementById("hubCount").textContent = n + "개";
      document.getElementById("hubEmpty").hidden = n > 0;
      picks.hidden = state.cat !== "all" || !!state.q;
      document.title = (state.cat === "all" ? "요양 정보" : NAMES[state.cat] + " · 요양 정보") + " | 경기광주 재가복지센터";
    };
    links.forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault(); state.cat = a.dataset.c; state.q = ""; state.n = 24; q.value = "";
        history.replaceState(null, "", state.cat === "all" ? "./" : "?cat=" + state.cat);
        apply(); window.scrollTo({ top: 0 });
      });
    });
    q.addEventListener("input", function () { state.q = q.value.trim(); state.n = 24; apply(); });
    moreBtn.addEventListener("click", function () { state.n += 24; apply(); });
    apply();
  }
})();
