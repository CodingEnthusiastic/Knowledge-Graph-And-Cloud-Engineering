// Client-side interactions for CareSync AI Case Management
const API_BASE = ""; // Relative path proxied by Caddy (/api)

document.addEventListener("DOMContentLoaded", () => {
  const caseForm = document.getElementById("new-case-form");
  const aiForm = document.getElementById("ai-query-form");
  const refreshBtn = document.getElementById("refresh-cases");
  const casesContainer = document.getElementById("cases-container");
  const chatMessages = document.getElementById("chat-messages");
  const aiInput = document.getElementById("ai-input");
  const aiSubmitBtn = document.getElementById("ai-submit-btn");

  // Load existing cases on launch
  loadCases();

  // Handle new case submission
  caseForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const pseudonym = document.getElementById("client-pseudonym").value.trim();
    const category = document.getElementById("case-category").value;
    const content = document.getElementById("case-content").value.trim();

    if (!pseudonym || !content) return;

    try {
      const res = await fetch(`${API_BASE}/api/cases`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_pseudonym: pseudonym,
          category: category,
          content: content,
        }),
      });

      if (res.ok) {
        caseForm.reset();
        await loadCases();
      } else {
        alert("Failed to save case note. Please check backend connection.");
      }
    } catch (err) {
      console.error("Submission error:", err);
      alert("Error contacting backend service.");
    }
  });

  // Handle Refresh
  refreshBtn.addEventListener("click", loadCases);

  async function loadCases() {
    try {
      const res = await fetch(`${API_BASE}/api/cases`);
      if (!res.ok) throw new Error("Backend response error");
      const cases = await res.json();

      if (cases.length === 0) {
        casesContainer.innerHTML = '<p class="text-muted" style="padding: 10px;">No case notes recorded yet. Add one above.</p>';
        return;
      }

      casesContainer.innerHTML = cases
        .map(
          (c) => `
        <div class="case-card">
          <div class="case-card-header">
            <span class="case-pseudonym">${escapeHtml(c.client_pseudonym)}</span>
            <span class="case-cat">${escapeHtml(c.category)}</span>
          </div>
          <div class="case-text">${escapeHtml(c.content)}</div>
          ${
            c.summary
              ? `<div class="case-summary"><strong>AI Summary:</strong> ${escapeHtml(c.summary)}</div>`
              : `<div class="text-muted" style="font-size: 0.75rem;">⚡ Background worker summarization in progress...</div>`
          }
        </div>
      `
        )
        .join("");
    } catch (err) {
      casesContainer.innerHTML = '<p class="text-muted">Error loading cases from database.</p>';
    }
  }

  // Handle AI Chat Inquiries
  aiForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = aiInput.value.trim();
    if (!query) return;

    // Append User message
    appendMessage("User", query, "user-message");
    aiInput.value = "";
    aiSubmitBtn.disabled = true;
    aiSubmitBtn.innerText = "Thinking...";

    try {
      const res = await fetch(`${API_BASE}/api/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: query }),
      });

      if (!res.ok) throw new Error("AI Service Error");
      const data = await res.json();
      appendMessage("Llama 3.1 8B", data.response, "ai-message");
    } catch (err) {
      appendMessage(
        "CareSync System",
        "Could not generate AI response. GPU inference engine is busy or initializing.",
        "system-message"
      );
    } finally {
      aiSubmitBtn.disabled = false;
      aiSubmitBtn.innerText = "Send";
    }
  });

  function appendMessage(sender, text, className) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${className}`;
    msgDiv.innerHTML = `
      <div class="sender">${escapeHtml(sender)}</div>
      <div class="text">${escapeHtml(text)}</div>
    `;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function escapeHtml(str) {
    return (str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
