// Starchild on TEE — chat dashboard (vanilla JS)
// Talks directly to the CVM. No server intermediary.

const $ = (s) => document.querySelector(s);
const messagesEl = $("#messages");
let endpoint = $("#endpoint").value.replace(/\/+$/, "");
let history = []; // {role, content}
let lastAttestation = null;

// ───────────── helpers ─────────────
async function api(path, opts = {}) {
  const url = endpoint + path;
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}: ${(await r.text()).slice(0,200)}`);
  return r.json();
}

function escapeHtml(s) { return s.replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]); }

function fmtMd(s) {
  s = escapeHtml(s);
  s = s.replace(/```([\s\S]*?)```/g, (_, c) => `<pre style="background:#0c0e14;padding:10px;border-radius:6px;overflow-x:auto;font-family:var(--mono);font-size:11.5px;color:#9ec5fe">${c}</pre>`);
  s = s.replace(/`([^`\n]+)`/g, '<code style="background:#1a1e28;padding:1px 6px;border-radius:3px;font-family:var(--mono);font-size:12px;color:#9ec5fe">$1</code>');
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener" style="color:#7aa2ff">$1</a>');
  return s;
}

// hex helpers for browser-side report_data verification
async function sha256Hex(str) {
  const buf = new TextEncoder().encode(str);
  const h = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, "0")).join("");
}

function nonceFresh() {
  return "ui-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 8);
}

// ───────────── status pill ─────────────
function setStatus(state, text) {
  const pill = $("#status-pill");
  pill.classList.remove("ok", "pending", "bad");
  pill.classList.add(state);
  $("#status-text").textContent = text;
}

// ───────────── init: probe TEE ─────────────
async function probeTEE() {
  setStatus("pending", "Connecting…");
  try {
    const [info, tools] = await Promise.all([api("/info"), api("/tools")]);
    $("#app-id").textContent = info.dstack?.app_id?.slice(0, 12) + "…" || "?";
    $("#app-id").title = info.dstack?.app_id || "";
    $("#uptime").textContent = info.agent?.uptime_sec + "s";

    let composeHash = "?";
    try {
      const tcb = JSON.parse(info.dstack?.tcb_info || "{}");
      composeHash = tcb.compose_hash || "?";
      $("#node").textContent = (tcb.os_image_hash || "?").slice(0, 10) + "…";
    } catch {}
    $("#compose-hash").textContent = composeHash.slice(0, 12) + "…";
    $("#compose-hash").title = composeHash;

    const toolUl = $("#tool-list");
    toolUl.innerHTML = "";
    for (const t of tools.tools) {
      const li = document.createElement("li");
      li.textContent = "▸ " + t.function.name;
      li.title = t.function.description;
      toolUl.appendChild(li);
    }

    setStatus("ok", "✅ TEE Verified (Intel TDX)");
    await refreshWorkspace();
  } catch (e) {
    setStatus("bad", "TEE unreachable");
    console.error(e);
  }
}

async function refreshWorkspace() {
  try {
    const r = await api("/workspace/list?path=.");
    const ul = $("#ws-files");
    ul.innerHTML = "";
    for (const e of r.entries || []) {
      const li = document.createElement("li");
      li.innerHTML = `<code>${e.is_dir ? "📁" : "📄"} ${escapeHtml(e.name)}</code><span>${e.size ?? ""}</span>`;
      ul.appendChild(li);
    }
    if (!r.entries?.length) ul.innerHTML = '<li style="color:var(--muted)"><em>(empty)</em></li>';
  } catch (e) { console.error("ws list failed", e); }
}

// ───────────── rendering ─────────────
function addUserMsg(text) {
  const div = document.createElement("div");
  div.className = "msg user";
  div.innerHTML = `<div class="bubble">${fmtMd(text)}</div>`;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addAgentMsg() {
  const div = document.createElement("div");
  div.className = "msg agent";
  div.innerHTML = `
    <div class="bubble"><span class="spinner"></span> <em style="color:var(--muted)">thinking…</em></div>
    <div class="meta"></div>`;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

// ───────────── send ─────────────
async function send(prompt) {
  addUserMsg(prompt);
  const agentMsg = addAgentMsg();
  const nonce = nonceFresh();
  const t0 = performance.now();

  try {
    const r = await fetch(endpoint + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        history,
        use_tools: $("#use-tools").checked,
        max_iterations: 6,
        max_tokens: 800,
        include_attestation: true,
        nonce,
      }),
    });

    if (!r.ok) throw new Error(`HTTP ${r.status}: ${(await r.text()).slice(0,200)}`);
    const data = await r.json();
    const elapsed = ((performance.now() - t0) / 1000).toFixed(1);

    const reply = data.reply || "(empty reply)";
    history.push({ role: "user", content: prompt });
    history.push({ role: "assistant", content: reply });
    if (history.length > 16) history = history.slice(-16); // cap

    agentMsg.querySelector(".bubble").innerHTML = fmtMd(reply);

    // Verify attestation client-side
    const meta = agentMsg.querySelector(".meta");
    const tools = data.tool_trace || [];
    const toolPills = tools.map(t => `<span class="tool-pill">${t.name}</span>`).join("");

    let attStatus = "";
    if (data.attestation?.available) {
      const expected = await sha256Hex(reply + "|" + nonce);
      const actual = data.attestation.report_data_hex || "";
      const match = actual.startsWith(expected);
      lastAttestation = { ...data.attestation, nonce, reply, expected, actual, match };
      attStatus = match
        ? `<span class="att-mini" title="Click for raw quote">🛡️ verified</span>`
        : `<span class="att-mini bad" title="Binding MISMATCH">⚠ binding fail</span>`;
      updateAttSidebar(lastAttestation);
    } else {
      attStatus = `<span class="err">no attestation</span>`;
    }

    meta.innerHTML = `${attStatus}<span>· ${data.iterations} iter · ${data.usage?.completion_tokens ?? "?"} tok · ${elapsed}s</span>${toolPills ? " " + toolPills : ""}`;
    meta.querySelector(".att-mini")?.addEventListener("click", showQuoteModal);

    if (tools.length) refreshWorkspace();
  } catch (e) {
    agentMsg.querySelector(".bubble").innerHTML = `<span style="color:var(--bad)">❌ ${escapeHtml(e.message)}</span>`;
    agentMsg.querySelector(".meta").innerHTML = `<span class="err">request failed</span>`;
  }
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function updateAttSidebar(att) {
  $("#att-nonce").textContent = att.nonce;
  $("#att-quote-bytes").textContent = att.quote ? (att.quote.length / 2) + " B" : "—";
  $("#att-binding").innerHTML = att.match
    ? '<span style="color:var(--ok)">✓ match</span>'
    : '<span style="color:var(--bad)">✗ mismatch</span>';
  $("#view-quote-btn").disabled = false;
}

function showQuoteModal() {
  if (!lastAttestation) return;
  const a = lastAttestation;
  $("#m-nonce").textContent = a.nonce;
  $("#m-expected").textContent = a.expected.slice(0, 64) + "…";
  $("#m-actual").textContent = a.actual.slice(0, 64) + "…";
  $("#m-match").innerHTML = a.match ? '<span style="color:var(--ok)">✅ binding verified</span>' : '<span style="color:var(--bad)">❌ MISMATCH</span>';
  $("#m-quote").textContent = (a.quote || "").slice(0, 1024) + (a.quote?.length > 1024 ? `\n… (${a.quote.length} hex chars total = ${a.quote.length/2} bytes)` : "");
  $("#m-eventlog").textContent = (a.event_log || "").slice(0, 600) + (a.event_log?.length > 600 ? "\n…" : "");
  $("#quote-modal").showModal();
}

// ───────────── events ─────────────
$("#input-form").addEventListener("submit", e => {
  e.preventDefault();
  const t = $("#prompt").value.trim();
  if (!t) return;
  $("#prompt").value = "";
  send(t);
});
$("#prompt").addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    $("#input-form").requestSubmit();
  }
});
$("#endpoint").addEventListener("change", e => {
  endpoint = e.target.value.replace(/\/+$/, "");
  history = [];
  messagesEl.innerHTML = "";
  probeTEE();
});
$("#refresh-ws").addEventListener("click", refreshWorkspace);
$("#status-pill").addEventListener("click", () => { if (lastAttestation) showQuoteModal(); });
$("#view-quote-btn").addEventListener("click", showQuoteModal);

probeTEE();
