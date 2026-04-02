const form = document.getElementById("planner-form");
const statusText = document.getElementById("status-text");
const resultGrid = document.getElementById("result-grid");
const summaryPanel = document.getElementById("summary-panel");
const summaryText = document.getElementById("summary-text");
const nextStepsPanel = document.getElementById("next-steps-panel");
const nextStepsList = document.getElementById("next-steps-list");
const alternativesPanel = document.getElementById("alternatives-panel");
const alternativesList = document.getElementById("alternatives-list");
const architecturePanel = document.getElementById("architecture-panel");
const architectureText = document.getElementById("architecture-text");
const structurePanel = document.getElementById("structure-panel");
const structureList = document.getElementById("structure-list");
const notesPanel = document.getElementById("notes-panel");
const notesList = document.getElementById("notes-list");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await generatePlan();
});

async function generatePlan() {
  const appType = document.getElementById("appType").value;
  const appIdea = document.getElementById("appIdea").value.trim();
  const selectedStack = buildSelectedStack();

  setLoadingState("Planning the simplest good setup...");

  const payload = {
    appTemplate: mapTemplate(appType),
    productBrief: appIdea || `Build a ${readableAppType(appType)} with this stack.`,
    mustHaves: selectedStack
      ? `Preferred stack: ${selectedStack}. Keep it simple. Only change parts if there is a strong reason.`
      : "Keep it simple. Pick the fastest good setup.",
    productType: mapProductType(appType),
    priority: "A",
    frontendComfort: "B",
    backendPreference: inferBackendPreference(selectedStack),
    region: inferRegion(`${selectedStack} ${appIdea}`),
    features: inferFeatures(`${selectedStack} ${appIdea}`),
  };

  try {
    const response = await fetch("/api/custom-builder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    renderResult(data);
  } catch (error) {
    statusText.textContent = error.message;
  }
}

function buildSelectedStack() {
  const ids = ["frontend", "backend", "auth", "database", "realtime", "ai", "storage", "payments", "deployment"];
  return ids
    .map((id) => document.getElementById(id).value)
    .filter(Boolean)
    .join(", ");
}

function renderResult(data) {
  const items = [
    ["Frontend", data.stack.frontend],
    ["Backend", data.stack.backend],
    ["Auth", data.stack.auth],
    ["Database", data.stack.database],
    ["Realtime", data.stack.realtime],
    ["AI", data.stack.ai],
    ["Storage", data.stack.storage],
    ["Payments", data.stack.payments],
    ["Deployment", data.stack.deployment],
  ];

  resultGrid.classList.remove("empty");
  resultGrid.innerHTML = items
    .map(
      ([label, value]) => `
        <article class="result-item">
          <strong>${escapeHtml(label)}</strong>
          <span>${escapeHtml(value || "Not needed")}</span>
        </article>
      `
    )
    .join("");

  summaryPanel.classList.remove("hidden");
  summaryText.textContent = data.summary || "A setup has been generated.";

  renderList(nextStepsPanel, nextStepsList, data.nextSteps);
  renderAlternatives(data.alternatives || []);
  renderArchitecture(data.architecture);
  renderList(structurePanel, structureList, data.projectStructure);
  renderList(notesPanel, notesList, data.notes);

  statusText.textContent = "Plan ready.";
}

function renderAlternatives(items) {
  if (!items || items.length === 0) {
    alternativesPanel.classList.add("hidden");
    alternativesList.innerHTML = "";
    return;
  }

  alternativesPanel.classList.remove("hidden");
  alternativesList.innerHTML = items
    .map(
      (item) => `
        <article class="list-item">
          <strong>${escapeHtml(item.name || "Alternative")}</strong>
          <p>${escapeHtml(item.whenToChoose || "")}</p>
          <p class="muted-line">${escapeHtml(item.stackFocus || "")}</p>
        </article>
      `
    )
    .join("");
}

function renderArchitecture(architecture) {
  if (!architecture || (!architecture.style && !architecture.reason)) {
    architecturePanel.classList.add("hidden");
    architectureText.textContent = "";
    return;
  }

  architecturePanel.classList.remove("hidden");
  architectureText.textContent = `${architecture.style}: ${architecture.reason}`;
}

function renderList(panel, container, items) {
  if (!items || items.length === 0) {
    panel.classList.add("hidden");
    container.innerHTML = "";
    return;
  }

  panel.classList.remove("hidden");
  container.innerHTML = items
    .map(
      (item) => `
        <article class="list-item">
          <p>${escapeHtml(item)}</p>
        </article>
      `
    )
    .join("");
}

function setLoadingState(message) {
  statusText.textContent = message;
  summaryPanel.classList.add("hidden");
  nextStepsPanel.classList.add("hidden");
  alternativesPanel.classList.add("hidden");
  architecturePanel.classList.add("hidden");
  structurePanel.classList.add("hidden");
  notesPanel.classList.add("hidden");
}

function readableAppType(value) {
  const mapping = {
    "simple-website": "simple website or internal tool",
    "saas-dashboard": "SaaS or dashboard app",
    "ai-app": "AI app",
    "mobile-app": "mobile app",
    "enterprise-system": "enterprise system",
    "marketplace": "marketplace app",
  };
  return mapping[value] || "app";
}

function mapTemplate(value) {
  const mapping = {
    "simple-website": "custom",
    "saas-dashboard": "saas-dashboard",
    "ai-app": "ai-chat-app",
    "mobile-app": "mobile-companion",
    "enterprise-system": "internal-admin-tool",
    "marketplace": "marketplace",
  };
  return mapping[value] || "custom";
}

function mapProductType(value) {
  const mapping = {
    "simple-website": "A",
    "saas-dashboard": "B",
    "ai-app": "C",
    "mobile-app": "D",
    "enterprise-system": "E",
    "marketplace": "B",
  };
  return mapping[value] || "A";
}

function inferBackendPreference(text) {
  const value = (text || "").toLowerCase();
  if (value.includes("python") || value.includes("fastapi") || value.includes("flask") || value.includes("django")) return "A";
  if (value.includes("node") || value.includes("express") || value.includes("nestjs") || value.includes("typescript") || value.includes("javascript")) return "B";
  return "C";
}

function inferRegion(text) {
  return text.toLowerCase().includes("razorpay") || text.toLowerCase().includes("india") ? "india" : "global";
}

function inferFeatures(text) {
  const value = text.toLowerCase();
  return {
    login: /(auth|login|user|account|jwt|clerk|auth0|firebase auth)/.test(value),
    realtime: /(real[- ]?time|chat|live|socket|websocket|supabase realtime|firebase realtime)/.test(value),
    ai: /(ai|llm|agent|gpt|rag|embedding|nvidia api|openai)/.test(value),
    uploads: /(upload|file|image|document|pdf|media|cloudinary|s3|storage)/.test(value),
    payments: /(payment|billing|subscription|stripe|razorpay|checkout|paddle)/.test(value),
    seo: /(seo|next\.js|blog|landing page|marketing site)/.test(value),
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
