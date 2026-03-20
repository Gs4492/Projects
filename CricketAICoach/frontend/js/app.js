const API = {
  playerBase: "http://127.0.0.1:8001",
  matchBase: "http://127.0.0.1:8002",
  gatewayBase: "http://127.0.0.1:8000",
};

const state = {
  role: "batting",
  playerId: null,
  matchId: null,
  playerCreated: false,
  matchCreated: false,
  deliveriesUploaded: false,
  analyticsFetched: false,
  coachingFetched: false,
  queuedDeliveries: [],
  analyticsData: null,
  coachingData: null,
  videoSessionId: null,
  videoAnalysisData: null,
};

const phaseLabels = ["powerplay", "middle", "death"];
const videoSessionsCache = [];

function clearVideoSessionPicker(message = "No saved sessions loaded") {
  const select = document.getElementById("videoSessionSelect");
  if (!select) return;
  videoSessionsCache.length = 0;
  select.innerHTML = "";
  const option = document.createElement("option");
  option.value = "";
  option.textContent = message;
  select.appendChild(option);
}

function populateVideoSessionPicker(sessions) {
  const select = document.getElementById("videoSessionSelect");
  if (!select) return;
  videoSessionsCache.length = 0;
  select.innerHTML = "";

  if (!Array.isArray(sessions) || sessions.length === 0) {
    clearVideoSessionPicker("No saved sessions found for this player");
    return;
  }

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Choose a saved session";
  select.appendChild(placeholder);

  sessions.forEach((session) => {
    videoSessionsCache.push(session);
    const option = document.createElement("option");
    option.value = session.session_id;
    const created = session.created_at ? new Date(session.created_at).toLocaleString() : "unknown time";
    const analysisTag = session.analysis ? "analysis ready" : "uploaded only";
    option.textContent = `${session.session_name || "Net Session"} | ${created} | ${analysisTag}`;
    select.appendChild(option);
  });
}

async function refreshVideoSessions(autoSelectLatest = false) {
  if (!state.playerId) {
    clearVideoSessionPicker("Load a player first");
    return;
  }

  const data = await requestJson(`${API.gatewayBase}/video/player/${state.playerId}/sessions`, "GET");
  const sessions = Array.isArray(data?.sessions) ? data.sessions : [];
  populateVideoSessionPicker(sessions);

  if (autoSelectLatest && sessions.length > 0) {
    document.getElementById("videoSessionSelect").value = sessions[0].session_id;
  }
}

function syncVideoFormFromSession(session) {
  document.getElementById("videoSessionName").value = session?.session_name || "Net Session";
  document.getElementById("videoCameraAngle").value = session?.camera_angle || "side_on";
  document.getElementById("videoExpectedBalls").value = session?.expected_balls || 24;
  document.getElementById("videoNotes").value = session?.notes || "";
}
function toLabel(value) {
  if (!value) return "-";
  return String(value).replace(/_/g, " ");
}

function setVideoTransfer(label, percent = 0, indeterminate = false) {
  const labelEl = document.getElementById("videoTransferLabel");
  const percentEl = document.getElementById("videoTransferPercent");
  const fillEl = document.getElementById("videoTransferFill");
  if (!labelEl || !percentEl || !fillEl) return;

  labelEl.textContent = label;
  percentEl.textContent = indeterminate ? "..." : `${Math.max(0, Math.min(100, Math.round(percent)))}%`;
  fillEl.classList.toggle("indeterminate", indeterminate);
  fillEl.style.width = indeterminate ? "38%" : `${Math.max(0, Math.min(100, percent))}%`;
}
function renderQuickSummary() {
  const summaryId = state.role === "bowling" ? "bowQuickSummary" : "batQuickSummary";
  const el = document.getElementById(summaryId);
  if (!el) return;

  const analytics = state.analyticsData;
  const coaching = state.coachingData;
  if (!analytics) {
    el.textContent = state.role === "bowling"
      ? "Run analytics to get a clear sentence on where the bowler is leaking or taking wickets."
      : "Run analytics to get a clear sentence on what is going wrong and what to fix next.";
    return;
  }

  const clusters = Array.isArray(analytics.dismissal_clusters) ? analytics.dismissal_clusters : [];
  const top = clusters[0] || null;
  const balls = analytics.total_balls ?? 0;
  const dismissals = analytics.dismissals ?? 0;
  const riskPhase = analytics.high_risk_phase || "middle";

  if (state.role === "batting") {
    const core = top
      ? `In recent matches (${balls} balls), you were out ${top.count} time(s) to ${toLabel(top.length)} balls on ${toLabel(top.line)}, mostly ${toLabel(top.dismissal)}.`
      : `In recent matches (${balls} balls), you had ${dismissals} dismissal(s).`;
    const next = coaching?.improvements?.[0] ? ` Next training focus: ${coaching.improvements[0]}.` : "";
    el.textContent = `${core} Pressure is highest in the ${toLabel(riskPhase)} phase.${next}`;
    return;
  }

  const core = top
    ? `In recent matches (${balls} balls), the main leak was ${top.count} event(s) at ${toLabel(top.length)} on ${toLabel(top.line)}.`
    : `In recent matches (${balls} balls), wicket pressure moments were ${dismissals}.`;
  const next = coaching?.improvements?.[0] ? ` Next bowling focus: ${coaching.improvements[0]}.` : "";
  el.textContent = `${core} Pressure is highest in the ${toLabel(riskPhase)} phase.${next}`;
}


function activePrefix() {
  return state.role === "bowling" ? "bow" : "bat";
}

function idFor(name) {
  return `${activePrefix()}${name}`;
}

function byId(name) {
  return document.getElementById(idFor(name));
}

function setStatus(msg, kind = "info") {
  const el = document.getElementById("statusBanner");
  el.textContent = msg;
  el.className = "status-banner";
  if (kind === "success") el.classList.add("ok");
  if (kind === "error") el.classList.add("error");
}

function capitalize(text) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function toNumberOrNull(value) {
  if (value === "" || value === null || value === undefined) return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function switchModeViews() {
  const bat = document.getElementById("battingView");
  const bow = document.getElementById("bowlingView");
  const batting = state.role === "batting";
  bat.classList.toggle("active", batting);
  bow.classList.toggle("active", !batting);
  document.body.classList.toggle("mode-bowling", !batting);
}

function updateRoleLabels() {
  const roleWord = state.role === "bowling" ? "Bowler" : "Batsman";
  document.getElementById("rolePill").textContent = `${roleWord} Mode`;
  document.getElementById("playerSelectTitle").textContent = `Step 1: Choose ${roleWord}`;
  document.getElementById("playerName").placeholder = `${roleWord} Name`;
  document.getElementById("matchDataHint").textContent = state.role === "bowling"
    ? "for fresh bowling spells"
    : "for fresh dismissals";
  switchModeViews();
}

function updateFlowUI() {
  const step2On = state.playerCreated;
  const step3On = state.matchCreated;
  const step4On = state.playerCreated;

  ["opponent", "matchDate", "matchFormat", "createMatchBtn"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.disabled = !step2On;
  });

  [
    "dOver", "dBall", "dBowlerType", "dLine", "dLength", "dShot", "dOutcome", "dDismissal",
    "dPitchX", "dPitchY", "dReleaseX", "dSpeedKph",
    "addDeliveryBtn", "loadSampleBtn", "clearDeliveriesBtn", "uploadDeliveriesBtn"
  ].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.disabled = !step3On;
  });

  ["queryLastMatches", "queryPhase2Btn", "queryPhase3Btn", "analysisMode"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.disabled = !step4On && id !== "analysisMode";
  });

  const hint = document.getElementById("flowHint");
  if (!hint) return;
  if (!state.playerCreated) hint.textContent = "Step 1: Enter Player ID and press Load (or create a new player).";
  else if (!state.matchCreated) hint.textContent = "Step 2: Click Run Analytics now. Create match only if adding fresh balls.";
  else if (!state.deliveriesUploaded) hint.textContent = "Optional: Upload queued balls, then run analytics.";
  else hint.textContent = "Now click Run Analytics, then Get Coaching Advice.";
}

function refreshChecklist() {
  const roleText = capitalize(state.role);
  document.getElementById("statusPlayer").textContent = `${state.playerCreated ? "[x]" : "[ ]"} ${roleText} selected`;
  document.getElementById("statusMatch").textContent = `${state.matchCreated ? "[x]" : "[ ]"} Match created`;
  document.getElementById("statusDeliveries").textContent = `${state.deliveriesUploaded ? "[x]" : "[ ]"} Deliveries uploaded`;
  document.getElementById("statusAnalytics").textContent = `${state.analyticsFetched ? "[x]" : "[ ]"} Analytics ready`;
  document.getElementById("statusCoaching").textContent = `${state.coachingFetched ? "[x]" : "[ ]"} Coaching ready`;
  document.getElementById("idsSummary").textContent = `Role: ${roleText} | Player: ${state.playerId ?? "-"}, Match: ${state.matchId ?? "-"}`;
  updateFlowUI();
}

function renderDeliveryQueue() {
  document.getElementById("deliveryCount").textContent = String(state.queuedDeliveries.length);
  const tbody = document.getElementById("deliveryRows");
  tbody.innerHTML = "";

  state.queuedDeliveries.slice(-8).forEach((d) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${d.over}.${d.ball}</td><td>${d.bowler_type}</td><td>${d.line}/${d.length}</td><td>${d.outcome}${d.dismissal ? ` (${d.dismissal})` : ""}</td>`;
    tbody.appendChild(tr);
  });
}

function buildDeliveryFromForm() {
  return {
    player_id: state.playerId,
    over: Number(document.getElementById("dOver").value),
    ball: Number(document.getElementById("dBall").value),
    bowler_type: document.getElementById("dBowlerType").value,
    line: document.getElementById("dLine").value,
    length: document.getElementById("dLength").value,
    shot: document.getElementById("dShot").value,
    outcome: document.getElementById("dOutcome").value,
    dismissal: document.getElementById("dDismissal").value || null,
    pitch_x: toNumberOrNull(document.getElementById("dPitchX").value),
    pitch_y: toNumberOrNull(document.getElementById("dPitchY").value),
    release_x: toNumberOrNull(document.getElementById("dReleaseX").value),
    release_y: null,
    speed_kph: toNumberOrNull(document.getElementById("dSpeedKph").value),
  };
}

async function requestJson(url, method, body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const raw = await res.text();
  let data;
  try {
    data = raw ? JSON.parse(raw) : {};
  } catch {
    data = { raw };
  }

  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText} - ${JSON.stringify(data)}`);
  }
  return data;
}

async function requestForm(url, formData, onProgress) {
  return await new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);

    xhr.upload.onprogress = (event) => {
      if (!event.lengthComputable || typeof onProgress !== "function") return;
      const pct = Math.max(1, Math.min(100, Math.round((event.loaded / event.total) * 100)));
      onProgress(pct, event.loaded, event.total);
    };

    xhr.onload = () => {
      const raw = xhr.responseText || "";
      let data;
      try {
        data = raw ? JSON.parse(raw) : {};
      } catch {
        data = { raw };
      }
      if (xhr.status >= 200 && xhr.status < 300) resolve(data);
      else reject(new Error(`${xhr.status} ${xhr.statusText} - ${JSON.stringify(data)}`));
    };

    xhr.onerror = () => reject(new Error("Network error during upload"));
    xhr.onabort = () => reject(new Error("Upload aborted"));
    xhr.send(formData);
  });
}

function renderVideoInsights(analysis) {
  const summaryId = state.role === "bowling" ? "bowVideoSummary" : "batVideoSummary";
  const listId = state.role === "bowling" ? "bowVideoList" : "batVideoList";
  const summaryEl = document.getElementById(summaryId);
  const listEl = document.getElementById(listId);
  if (!summaryEl || !listEl) return;

  if (!analysis) {
    summaryEl.textContent = state.role === "bowling"
      ? "Upload a net-session video to get bowling practice feedback from recorded footage."
      : "Upload a net-session video to get shot-selection feedback from practice footage.";
    listEl.innerHTML = "<li>No video analysis yet.</li>";
    document.getElementById("videoSessionStatus").textContent = state.videoSessionId || "none";
    setVideoTransfer("Waiting", 0, false);
    return;
  }

  summaryEl.textContent = analysis.summary || "Video analysis ready.";
  listEl.innerHTML = "";

  const sections = [
    {
      title: "Main Issue",
      items: [analysis.primary_weakness].filter(Boolean),
    },
    {
      title: "Why It Is Happening",
      items: [analysis.cause].filter(Boolean),
    },
    {
      title: state.role === "bowling" ? "Action Breakdown" : "Body Mechanics",
      items: [
        ...(Array.isArray(analysis.video_observations) ? analysis.video_observations.slice(0, 4) : []),
        ...(Array.isArray(analysis.shot_selection_issues) ? analysis.shot_selection_issues.slice(0, 3) : []),
        ...(Array.isArray(analysis.execution_issues) ? analysis.execution_issues.slice(0, 3) : []),
      ],
    },
    {
      title: "What To Work On",
      items: Array.isArray(analysis.technical_workons) ? analysis.technical_workons.slice(0, 5) : [],
    },
    {
      title: "Drills",
      items: Array.isArray(analysis.recommended_drills) ? analysis.recommended_drills.slice(0, 3) : [],
    },
    {
      title: "Mindset Cues",
      items: Array.isArray(analysis.mental_cues) ? analysis.mental_cues.slice(0, 3) : [],
    },
    {
      title: "Progress Signs",
      items: Array.isArray(analysis.progress_markers) ? analysis.progress_markers.slice(0, 2) : [],
    },
  ].filter((section) => Array.isArray(section.items) && section.items.length > 0);

  if (sections.length === 0) {
    listEl.innerHTML = "<li>Video analysis complete, but no cricket-specific insights were returned.</li>";
  } else {
    sections.forEach((section) => {
      const li = document.createElement("li");
      li.className = "video-section";

      const title = document.createElement("div");
      title.className = "video-section-title";
      title.textContent = section.title;
      li.appendChild(title);

      const inner = document.createElement("ul");
      inner.className = "video-section-list";
      section.items.forEach((item) => {
        const point = document.createElement("li");
        point.textContent = item;
        inner.appendChild(point);
      });
      li.appendChild(inner);
      listEl.appendChild(li);
    });
  }

  document.getElementById("videoSessionStatus").textContent = state.videoSessionId || "none";
}
function getSampleDeliveries(playerId) {
  if (state.role === "bowling") {
    return [
      { player_id: playerId, over: 1, ball: 1, bowler_type: "pace", line: "outside_off", length: "good", shot: "none", outcome: "dot", dismissal: null, pitch_x: -0.7, pitch_y: 8.2, release_x: -0.3, release_y: 2.1, speed_kph: 136.4 },
      { player_id: playerId, over: 1, ball: 2, bowler_type: "pace", line: "outside_off", length: "full", shot: "none", outcome: "boundary", dismissal: null, pitch_x: -1.2, pitch_y: 5.0, release_x: -0.4, release_y: 2.0, speed_kph: 134.1 },
      { player_id: playerId, over: 1, ball: 3, bowler_type: "pace", line: "middle", length: "full", shot: "none", outcome: "wicket", dismissal: "bowled", pitch_x: 0.1, pitch_y: 6.1, release_x: -0.2, release_y: 2.2, speed_kph: 137.9 },
      { player_id: playerId, over: 17, ball: 4, bowler_type: "pace", line: "leg", length: "full", shot: "none", outcome: "boundary", dismissal: null, pitch_x: 1.1, pitch_y: 4.7, release_x: 0.0, release_y: 2.0, speed_kph: 131.7 },
      { player_id: playerId, over: 18, ball: 1, bowler_type: "pace", line: "outside_off", length: "short", shot: "none", outcome: "run", dismissal: null, pitch_x: -0.9, pitch_y: 10.4, release_x: -0.1, release_y: 2.1, speed_kph: 133.2 },
    ];
  }

  return [
    { player_id: playerId, over: 1, ball: 1, bowler_type: "pace", line: "outside_off", length: "good", shot: "leave", outcome: "dot", dismissal: null, pitch_x: -0.8, pitch_y: 7.8, release_x: -0.2, release_y: 2.1, speed_kph: 138.8 },
    { player_id: playerId, over: 1, ball: 2, bowler_type: "pace", line: "outside_off", length: "good", shot: "drive", outcome: "dot", dismissal: null, pitch_x: -0.6, pitch_y: 7.2, release_x: -0.3, release_y: 2.0, speed_kph: 139.6 },
    { player_id: playerId, over: 1, ball: 3, bowler_type: "pace", line: "outside_off", length: "good", shot: "drive", outcome: "wicket", dismissal: "caught", pitch_x: -0.5, pitch_y: 7.0, release_x: -0.2, release_y: 2.2, speed_kph: 140.5 },
    { player_id: playerId, over: 8, ball: 2, bowler_type: "spin", line: "middle", length: "good", shot: "sweep", outcome: "dot", dismissal: null, pitch_x: 0.0, pitch_y: 6.8, release_x: 0.3, release_y: 1.7, speed_kph: 88.4 },
    { player_id: playerId, over: 17, ball: 4, bowler_type: "pace", line: "leg", length: "full", shot: "flick", outcome: "wicket", dismissal: "lbw", pitch_x: 0.9, pitch_y: 5.2, release_x: 0.0, release_y: 2.1, speed_kph: 136.1 },
  ];
}

function setMetrics(analytics) {
  byId("MetricBalls").textContent = analytics?.total_balls ?? "-";
  byId("MetricDismissals").textContent = analytics?.dismissals ?? "-";
  const rate = typeof analytics?.false_shot_rate === "number" ? `${(analytics.false_shot_rate * 100).toFixed(1)}%` : "-";
  byId("MetricFalseRate").textContent = rate;
  byId("MetricHighRisk").textContent = analytics?.high_risk_phase ?? "-";
}

function setProMetrics(analytics) {
  const m = analytics?.pro_metrics;
  byId("ProControl").textContent = typeof m?.control_score === "number" ? `${m.control_score.toFixed(1)} / 100` : "-";
  byId("ProPressure").textContent = typeof m?.pressure_score === "number" ? `${m.pressure_score.toFixed(1)} / 100` : "-";
  byId("ProAvgSpeed").textContent = typeof m?.avg_speed_kph === "number" ? `${m.avg_speed_kph.toFixed(1)} kph` : "-";
  byId("ProStability").textContent = typeof m?.speed_stability === "number" ? `${m.speed_stability.toFixed(1)}%` : "-";

  const lineC = m?.consistency?.line_consistency;
  const lengthC = m?.consistency?.length_consistency;
  const linePct = typeof lineC === "number" ? Math.max(0, Math.min(100, Math.round(lineC * 100))) : 0;
  const lengthPct = typeof lengthC === "number" ? Math.max(0, Math.min(100, Math.round(lengthC * 100))) : 0;

  byId("LineConsistencyBar").style.width = `${linePct}%`;
  byId("LengthConsistencyBar").style.width = `${lengthPct}%`;
  byId("LineConsistencyText").textContent = typeof lineC === "number" ? `${linePct}% repeated on same line` : "-";
  byId("LengthConsistencyText").textContent = typeof lengthC === "number" ? `${lengthPct}% repeated on same length` : "-";
}

function _eventClass(item) {
  if (item.dismissal) return "dismissal";
  const outcome = (item.outcome || "").toLowerCase();
  if (outcome === "boundary" || outcome === "wicket") return "boundary";
  return "dot";
}

function renderScatter(points, hostName, dotClassPrefix, emptyMsg, yMax, xMin, xMax) {
  const host = byId(hostName);
  if (!host) return;
  host.innerHTML = "";

  if (!Array.isArray(points) || points.length === 0) {
    const empty = document.createElement("div");
    empty.className = "mini muted p-2";
    empty.textContent = emptyMsg;
    host.appendChild(empty);
    return;
  }

  points.slice(0, 350).forEach((p) => {
    const dot = document.createElement("span");
    const xSource = dotClassPrefix === "pitch" ? Number(p.pitch_x) : Number(p.release_x);
    const ySource = dotClassPrefix === "pitch" ? Number(p.pitch_y) : Number(p.release_y || 2.0);
    const x = ((xSource - xMin) / (xMax - xMin)) * 100;
    const y = (1 - (ySource / yMax)) * 100;

    dot.className = `${dotClassPrefix}-dot ${_eventClass(p)} i${Math.min(3, Math.max(1, Number(p.intensity || 1)))}`;
    dot.style.left = `${Math.max(0, Math.min(100, x))}%`;
    dot.style.top = `${Math.max(0, Math.min(100, y))}%`;
    host.appendChild(dot);
  });
}

function renderPitchScatter(points) {
  renderScatter(points, "PitchScatter", "pitch", "No pitch coordinates yet. Add pitch_x and pitch_y while uploading deliveries.", 22, -2, 2);
}

function renderReleaseScatter(points) {
  renderScatter(points, "ReleaseScatter", "release", "No release coordinates yet. Add release_x while uploading deliveries.", 3, -2, 2);
}

function renderSpeedTrend(series) {
  const host = byId("SpeedTrend");
  const hint = byId("SpeedTrendHint");
  if (!host) return;
  host.innerHTML = "";

  if (!Array.isArray(series) || series.length === 0) {
    if (hint) hint.textContent = "Run analytics to view speed progression.";
    return;
  }

  const maxSpeed = Math.max(...series.map((x) => Number(x.avg_speed_kph || 0)), 1);
  const minSpeed = Math.min(...series.map((x) => Number(x.avg_speed_kph || 0)), maxSpeed);
  const range = Math.max(1, maxSpeed - minSpeed);

  series.forEach((s) => {
    const speed = Number(s.avg_speed_kph || 0);
    const h = 24 + Math.round(((speed - minSpeed) / range) * 130);
    const col = document.createElement("div");
    col.className = "speed-col";
    col.innerHTML = `
      <div class="speed-value">${speed.toFixed(1)}</div>
      <div class="speed-bar" style="height:${h}px"></div>
      <div class="speed-label">O${s.over}</div>
    `;
    host.appendChild(col);
  });

  if (hint) hint.textContent = `Speed range ${minSpeed.toFixed(1)}-${maxSpeed.toFixed(1)} kph across ${series.length} over(s).`;
}

function renderBatDismissalMap(analytics) {
  const scatter = document.getElementById("batDismissalScatter");
  const rows = document.getElementById("batDismissalRows");
  if (!scatter || !rows) return;

  scatter.innerHTML = "";
  rows.innerHTML = "";

  const points = Array.isArray(analytics?.pitch_points)
    ? analytics.pitch_points.filter((p) => Boolean(p.dismissal))
    : [];

  if (points.length === 0) {
    const empty = document.createElement("div");
    empty.className = "mini muted p-2";
    empty.textContent = "No dismissal coordinates found in selected matches.";
    scatter.appendChild(empty);
  } else {
    points.slice(0, 200).forEach((p) => {
      const dot = document.createElement("span");
      const x = ((Number(p.pitch_x) + 2) / 4) * 100;
      const y = (1 - (Number(p.pitch_y) / 22)) * 100;
      dot.className = `pitch-dot dismissal i${Math.min(3, Math.max(1, Number(p.intensity || 2)))}`;
      dot.style.left = `${Math.max(0, Math.min(100, x))}%`;
      dot.style.top = `${Math.max(0, Math.min(100, y))}%`;
      scatter.appendChild(dot);
    });
  }

  const clusters = Array.isArray(analytics?.dismissal_clusters) ? analytics.dismissal_clusters : [];
  if (clusters.length === 0) {
    rows.innerHTML = '<tr><td colspan="4" class="text-muted">No dismissals found.</td></tr>';
    return;
  }

  clusters.slice(0, 8).forEach((c) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${c.line || "-"}</td><td>${c.length || "-"}</td><td>${c.dismissal || "-"}</td><td>${c.count ?? 0}</td>`;
    rows.appendChild(tr);
  });
}
function clearZones() {
  const board = byId("ZoneBoard");
  if (!board) return;
  board.querySelectorAll(".zone-cell").forEach((el) => {
    el.removeAttribute("data-level");
    const num = el.querySelector("em");
    if (num) num.textContent = "0";
    el.title = "";
  });
}

function renderZones(clusters) {
  clearZones();
  if (!clusters || clusters.length === 0) {
    byId("ClusterSummary").textContent = "Run analytics to populate zone map.";
    return;
  }

  const board = byId("ZoneBoard");
  const zoneCount = {};
  clusters.forEach((c) => {
    const key = `${c.line}-${c.length}`;
    zoneCount[key] = (zoneCount[key] || 0) + Number(c.count || 0);
  });

  const max = Math.max(...Object.values(zoneCount));
  Object.entries(zoneCount).forEach(([zone, count]) => {
    const el = board.querySelector(`.zone-cell[data-zone="${zone}"]`);
    if (!el) return;
    const ratio = count / max;
    let level = 1;
    if (ratio >= 0.8) level = 3;
    else if (ratio >= 0.45) level = 2;
    el.setAttribute("data-level", String(level));
    const num = el.querySelector("em");
    if (num) num.textContent = String(count);
    const tooltipLabel = state.role === "bowling" ? "events" : "dismissals";
    el.title = `${zone.replace("-", " / ")} ${tooltipLabel}: ${count}`;
  });

  const top = clusters[0];
  byId("ClusterSummary").textContent = state.role === "bowling"
    ? `Top pressure zone: ${top.count} event(s) at ${top.length} on ${top.line}.`
    : `Biggest weakness: ${top.count} dismissal(s) at ${top.length} on ${top.line} (${top.dismissal}).`;
}

function renderPhaseRisk(phaseRisk) {
  const host = byId("PhaseRiskBars");
  host.innerHTML = "";

  if (!phaseRisk) {
    host.innerHTML = "<div class='text-muted small'>Run analytics to view phase pressure.</div>";
    return;
  }

  phaseLabels.forEach((phase) => {
    const data = phaseRisk[phase] || { risk_index: 0, balls: 0, dismissals: 0, false_shots: 0, dots: 0 };
    const pct = Math.max(0, Math.min(100, Math.round((data.risk_index || 0) * 100)));
    const row = document.createElement("div");
    const eventLabel = state.role === "bowling" ? "wickets" : "dismissals";
    const leakLabel = state.role === "bowling" ? "boundaries" : "false shots";
    row.className = "risk-row";
    row.innerHTML = `
      <div class="risk-head">
        <span>${phase}</span>
        <span>risk ${(data.risk_index || 0).toFixed(3)}</span>
      </div>
      <div class="risk-track"><div class="risk-fill" style="width:${pct}%"></div></div>
      <div class="small text-muted">balls ${data.balls}, ${eventLabel} ${data.dismissals}, ${leakLabel} ${data.false_shots}</div>
    `;
    host.appendChild(row);
  });
}

function renderCoaching(coaching) {
  byId("CoachingWeakness").textContent = coaching?.primary_weakness || "-";
  byId("CoachingCause").textContent = coaching?.cause || "-";
  byId("CoachingExplanation").textContent = coaching?.explanation || "-";

  const evidence = byId("EvidenceList");
  evidence.innerHTML = "";
  const evidenceItems = Array.isArray(coaching?.evidence_points) ? coaching.evidence_points : [];
  const progressItems = Array.isArray(coaching?.progress_markers) ? coaching.progress_markers : [];
  if (evidenceItems.length === 0 && progressItems.length === 0) evidence.innerHTML = "<li>Run coaching to view evidence.</li>";
  else {
    evidenceItems.forEach((item) => { const li = document.createElement("li"); li.textContent = item; evidence.appendChild(li); });
    progressItems.forEach((item) => { const li = document.createElement("li"); li.textContent = `Progress marker: ${item}`; evidence.appendChild(li); });
  }

  const list = byId("ImprovementsList");
  list.innerHTML = "";
  const items = Array.isArray(coaching?.improvements) ? coaching.improvements : [];
  const drillItems = Array.isArray(coaching?.drill_routines) ? coaching.drill_routines : [];
  const mentalItems = Array.isArray(coaching?.mental_cues) ? coaching.mental_cues : [];
  if (items.length === 0 && drillItems.length === 0 && mentalItems.length === 0) list.innerHTML = "<li>Run coaching to view training focus.</li>";
  else {
    items.forEach((item) => { const li = document.createElement("li"); li.textContent = item; list.appendChild(li); });
    drillItems.forEach((item) => { const li = document.createElement("li"); li.textContent = `Drill: ${item}`; list.appendChild(li); });
    mentalItems.forEach((item) => { const li = document.createElement("li"); li.textContent = `Mental cue: ${item}`; list.appendChild(li); });
  }

  const plan = byId("MatchPlanList");
  plan.innerHTML = "";
  const planItems = Array.isArray(coaching?.next_match_plan) ? coaching.next_match_plan : [];
  if (planItems.length === 0) plan.innerHTML = "<li>Run coaching to view match rules.</li>";
  else planItems.forEach((item) => { const li = document.createElement("li"); li.textContent = item; plan.appendChild(li); });
}

function resetActiveViewCards() {
  setMetrics(null);
  setProMetrics(null);
  renderPitchScatter([]);
  renderReleaseScatter([]);
  renderSpeedTrend([]);
  renderPhaseRisk(null);
  renderBatDismissalMap(null);
  renderCoaching(null);
  clearZones();
}

function resetForRoleChange() {
  state.playerId = null;
  state.matchId = null;
  state.playerCreated = false;
  state.matchCreated = false;
  state.deliveriesUploaded = false;
  state.analyticsFetched = false;
  state.coachingFetched = false;
  state.queuedDeliveries = [];
  state.analyticsData = null;
  state.coachingData = null;
  state.videoSessionId = null;
  state.videoAnalysisData = null;

  document.getElementById("existingPlayerId").value = "";
  document.getElementById("playerName").value = "";
  clearVideoSessionPicker("Load a player first");
  renderVideoInsights(null);
  renderDeliveryQueue();
  resetActiveViewCards();
  renderQuickSummary();
  refreshChecklist();
}

document.getElementById("analysisMode").addEventListener("change", (e) => {
  state.role = e.target.value;
  updateRoleLabels();
  resetForRoleChange();
  setStatus(`Switched to ${state.role} mode. Select or create player.`, "info");
});

document.getElementById("loadPlayerBtn").addEventListener("click", async () => {
  try {
    const id = Number(document.getElementById("existingPlayerId").value);
    if (!id) return setStatus("Enter a valid player ID.", "error");
    const player = await requestJson(`${API.playerBase}/players/${id}`, "GET");
    state.playerId = player.id;
    state.playerCreated = true;
    state.matchCreated = false;
    state.deliveriesUploaded = false;
    state.analyticsFetched = false;
    state.coachingFetched = false;
    state.queuedDeliveries = [];
    state.analyticsData = null;
    state.coachingData = null;
    state.videoSessionId = null;
    state.videoAnalysisData = null;
    renderDeliveryQueue();
    refreshChecklist();
    await refreshVideoSessions(true);
    setStatus(`Loaded existing player: ${player.name} (ID ${player.id}).`, "success");
  } catch (err) {
    setStatus(`Load player failed: ${String(err)}`, "error");
  }
});

document.getElementById("createPlayerBtn").addEventListener("click", async () => {
  try {
    const payload = {
      name: document.getElementById("playerName").value.trim(),
      batting_hand: document.getElementById("battingHand").value,
      level: document.getElementById("playerLevel").value,
    };
    const data = await requestJson(`${API.playerBase}/players/`, "POST", payload);
    state.playerId = data.id;
    state.playerCreated = true;
    state.matchCreated = false;
    state.deliveriesUploaded = false;
    state.analyticsFetched = false;
    state.coachingFetched = false;
    state.queuedDeliveries = [];
    state.analyticsData = null;
    state.coachingData = null;
    state.videoSessionId = null;
    state.videoAnalysisData = null;
    renderDeliveryQueue();
    refreshChecklist();
    await refreshVideoSessions(false);
    setStatus(`Player created: ${data.name} (ID ${data.id}).`, "success");
  } catch (err) {
    setStatus(`Player creation failed: ${String(err)}`, "error");
  }
});

document.getElementById("createMatchBtn").addEventListener("click", async () => {
  try {
    const payload = {
      opponent: document.getElementById("opponent").value.trim(),
      match_date: document.getElementById("matchDate").value,
      format: document.getElementById("matchFormat").value,
    };
    const data = await requestJson(`${API.matchBase}/matches`, "POST", payload);
    state.matchId = data.match_id;
    state.matchCreated = true;
    state.deliveriesUploaded = false;
    state.analyticsFetched = false;
    state.coachingFetched = false;
    state.queuedDeliveries = [];
    state.analyticsData = null;
    state.coachingData = null;
    renderDeliveryQueue();
    refreshChecklist();
    setStatus(`Match created (ID ${data.match_id}).`, "success");
  } catch (err) {
    setStatus(`Match creation failed: ${String(err)}`, "error");
  }
});

document.getElementById("addDeliveryBtn").addEventListener("click", () => {
  const d = buildDeliveryFromForm();
  if (Number.isNaN(d.over) || Number.isNaN(d.ball)) return setStatus("Enter Over and Ball before adding.", "error");
  state.queuedDeliveries.push(d);
  renderDeliveryQueue();
  setStatus(`Added ball ${d.over}.${d.ball} to queue.`, "success");
});

document.getElementById("loadSampleBtn").addEventListener("click", () => {
  state.queuedDeliveries = getSampleDeliveries(state.playerId || 1);
  renderDeliveryQueue();
  setStatus("Sample balls loaded into queue.", "info");
});

document.getElementById("clearDeliveriesBtn").addEventListener("click", () => {
  state.queuedDeliveries = [];
  state.analyticsData = null;
  state.coachingData = null;
  renderDeliveryQueue();
  setStatus("Queued deliveries cleared.", "info");
});

document.getElementById("uploadDeliveriesBtn").addEventListener("click", async () => {
  try {
    if (!state.matchId || state.queuedDeliveries.length === 0) return setStatus("Create a match and add at least one ball before upload.", "error");
    const payload = { match_id: state.matchId, deliveries: state.queuedDeliveries };
    const data = await requestJson(`${API.matchBase}/matches/deliveries/bulk`, "POST", payload);
    state.deliveriesUploaded = true;
    refreshChecklist();
    setStatus(`Deliveries uploaded. Inserted: ${data.inserted}, Duplicates: ${data.ignored_duplicates}`, "success");
  } catch (err) {
    setStatus(`Delivery upload failed: ${String(err)}`, "error");
  }
});

document.getElementById("queryPhase2Btn").addEventListener("click", async () => {
  try {
    if (!state.playerId) return setStatus("Select a player first.", "error");
    const lastMatches = Number(document.getElementById("queryLastMatches").value || 5);
    const phase2Path = state.role === "bowling" ? "bowling" : "batting";
    const data = await requestJson(`${API.gatewayBase}/phase2/player/${state.playerId}/${phase2Path}?last_matches=${lastMatches}`, "GET");
    const analytics = data?.analytics || null;
    state.analyticsData = analytics;
    setMetrics(analytics);
    setProMetrics(analytics);
    renderPitchScatter(analytics?.pitch_points || []);
    renderReleaseScatter(analytics?.release_points || []);
    renderSpeedTrend(analytics?.speed_by_over || []);
    renderZones(analytics?.dismissal_clusters || []);
    renderPhaseRisk(analytics?.phase_risk || null);
    if (state.role === "batting") renderBatDismissalMap(analytics);
    else renderBatDismissalMap(null);
    state.analyticsFetched = true;
    renderQuickSummary();
    refreshChecklist();
    setStatus(`${capitalize(state.role)} analytics ready.`, "success");
  } catch (err) {
    setStatus(`Analytics failed: ${String(err)}`, "error");
  }
});

document.getElementById("queryPhase3Btn").addEventListener("click", async () => {
  try {
    if (!state.playerId) return setStatus("Select a player first.", "error");
    const lastMatches = Number(document.getElementById("queryLastMatches").value || 5);
    const phase3Path = state.role === "bowling" ? "bowling/coaching" : "coaching";
    const data = await requestJson(`${API.gatewayBase}/phase3/player/${state.playerId}/${phase3Path}?last_matches=${lastMatches}`, "GET");
    const coaching = data?.coaching || null;
    state.coachingData = coaching;
    renderCoaching(coaching);
    state.coachingFetched = true;
    renderQuickSummary();
    refreshChecklist();
    setStatus(`${capitalize(state.role)} coaching generated.`, "success");
  } catch (err) {
    setStatus(`Coaching failed: ${String(err)}`, "error");
  }
});

document.getElementById("refreshVideoSessionsBtn").addEventListener("click", async () => {
  try {
    await refreshVideoSessions(false);
    setStatus("Saved video sessions refreshed.", "info");
  } catch (err) {
    setStatus(`Could not refresh saved sessions: ${String(err)}`, "error");
  }
});

document.getElementById("loadVideoSessionBtn").addEventListener("click", async () => {
  try {
    if (!state.playerId) return setStatus("Load a player first.", "error");
    const sessionId = document.getElementById("videoSessionSelect").value;
    if (!sessionId) return setStatus("Choose a saved session first.", "error");

    const cached = videoSessionsCache.find((item) => item.session_id === sessionId);
    const session = cached || await requestJson(`${API.gatewayBase}/video/sessions/${sessionId}`, "GET");
    state.videoSessionId = session.session_id;
    state.videoAnalysisData = session.analysis || null;
    syncVideoFormFromSession(session);
    renderVideoInsights(session.analysis || null);
    document.getElementById("videoSessionStatus").textContent = session.analysis
      ? `loaded (${session.session_id})`
      : `uploaded (${session.session_id})`;
    setVideoTransfer(session.analysis ? "Analysis loaded" : "Uploaded session loaded", session.analysis ? 100 : 0, false);
    setStatus(session.analysis
      ? `Loaded saved session ${session.session_id} with analysis.`
      : `Loaded saved session ${session.session_id}. Run video analysis when ready.`, "success");
  } catch (err) {
    setStatus(`Could not load saved session: ${String(err)}`, "error");
  }
});

clearVideoSessionPicker("Load a player first");
updateRoleLabels();
renderDeliveryQueue();
resetActiveViewCards();
refreshChecklist();
setStatus("Start: select or create a player.", "info");













document.getElementById("uploadVideoBtn").addEventListener("click", async () => {
  try {
    if (!state.playerId) return setStatus("Select a player before uploading video.", "error");
    const fileInput = document.getElementById("videoFile");
    const file = fileInput.files?.[0];
    if (!file) return setStatus("Choose a practice video first.", "error");

    const fileSizeMb = file.size / (1024 * 1024);
    setStatus(`Preparing upload for ${file.name} (${fileSizeMb.toFixed(1)} MB)...`, "info");
    document.getElementById("videoSessionStatus").textContent = `uploading 0% (${fileSizeMb.toFixed(1)} MB)`;
    setVideoTransfer("Uploading video", 0, false);
    document.getElementById("uploadVideoBtn").disabled = true;
    document.getElementById("analyzeVideoBtn").disabled = true;

    const form = new FormData();
    form.append("role", state.role);
    form.append("session_name", document.getElementById("videoSessionName").value.trim() || "Net Session");
    form.append("camera_angle", document.getElementById("videoCameraAngle").value);
    form.append("notes", document.getElementById("videoNotes").value.trim());
    form.append("expected_balls", document.getElementById("videoExpectedBalls").value || "24");
    form.append("video", file);

    const data = await requestForm(
      `${API.gatewayBase}/video/player/${state.playerId}/sessions`,
      form,
      (pct) => {
        document.getElementById("videoSessionStatus").textContent = `uploading ${pct}%`;
        setVideoTransfer("Uploading video", pct, false);
        setStatus(`Uploading ${file.name}: ${pct}%`, "info");
      }
    );

    state.videoSessionId = data?.session_id || null;
    state.videoAnalysisData = null;
    renderVideoInsights(null);
    await refreshVideoSessions(true);
    document.getElementById("videoSessionSelect").value = state.videoSessionId;
    document.getElementById("videoSessionStatus").textContent = `uploaded (${state.videoSessionId})`;
    setVideoTransfer("Upload complete", 100, false);
    setStatus(`Practice video uploaded. Session ${state.videoSessionId} ready for analysis.`, "success");
  } catch (err) {
    document.getElementById("videoSessionStatus").textContent = "upload failed";
    setVideoTransfer("Upload failed", 0, false);
    setStatus(`Video upload failed: ${String(err)}`, "error");
  } finally {
    document.getElementById("uploadVideoBtn").disabled = false;
    document.getElementById("analyzeVideoBtn").disabled = false;
  }
});

document.getElementById("analyzeVideoBtn").addEventListener("click", async () => {
  try {
    if (!state.videoSessionId) return setStatus("Upload a practice video first.", "error");
    setStatus("Running video analysis...", "info");
    document.getElementById("videoSessionStatus").textContent = `analyzing ${state.videoSessionId}`;
    setVideoTransfer("Analyzing video", 0, true);
    const params = new URLSearchParams({
      dominant_hand: document.getElementById("battingHand").value || "right",
      practice_type: "nets",
      surface_type: "turf",
      bowling_type: "mixed",
      focus_area: state.role === "bowling" ? "release consistency" : "shot selection",
    });
    const data = await requestJson(`${API.gatewayBase}/video/sessions/${state.videoSessionId}/analyze?${params.toString()}`, "POST");
    state.videoAnalysisData = data;
    renderVideoInsights(data);
    document.getElementById("videoSessionStatus").textContent = `analysis ready (${state.videoSessionId})`;
    setVideoTransfer("Analysis ready", 100, false);
    setStatus(`${capitalize(state.role)} video analysis ready.`, "success");
  } catch (err) {
    try {
      const session = await requestJson(`${API.gatewayBase}/video/sessions/${state.videoSessionId}`, "GET");
      const savedAnalysis = session?.analysis || null;
      if (savedAnalysis) {
        state.videoAnalysisData = savedAnalysis;
        renderVideoInsights(savedAnalysis);
        document.getElementById("videoSessionStatus").textContent = `analysis recovered (${state.videoSessionId})`;
        setVideoTransfer("Analysis recovered", 100, false);
        setStatus(`${capitalize(state.role)} video analysis finished on the server and was recovered.`, "success");
        return;
      }
    } catch (recoveryErr) {
      console.warn("Video analysis recovery failed", recoveryErr);
    }
    setVideoTransfer("Analysis failed", 0, false);
    setStatus(`Video analysis failed: ${String(err)}`, "error");
  }
});

























