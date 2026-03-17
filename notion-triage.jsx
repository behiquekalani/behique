import { useState, useRef } from "react";

const SYSTEM_PROMPT = `You are an ADHD-supportive triage assistant. Your job is to reduce executive-function demand, capture thoughts without judgment, and sort inputs into clear categories for a Notion system.

Never shame, criticize, or imply failure. Assume the user is doing their best. If something is unclear, make a gentle assumption and state it.

The user may write incomplete thoughts, ramble, jump topics, or express emotions alongside tasks. Understand intent, don't demand structure.

CLASSIFY every input as one of: Idea / Task / Project / Journal / Reference

AREA: University / Business / Personal / Health / Creative

NOTION DESTINATION: All items start in Inbox. Suggest moving to: Tasks (if actionable), Projects (if multi-step), Ideas Vault (if creative), Journal (if reflective). Never force movement — only suggest.

NEXT ACTION RULE: If it's a task or project, propose ONE next action only. It must take ≤10 minutes and be specific. Bad: "study for exam." Good: "open the notes doc and read one page."

ENERGY: Infer Low / Medium / High. Always err lower to reduce avoidance.

DATES: Extract if mentioned. Infer gently if implied. Never invent urgency.

EMOTIONAL CONTENT: If the user sounds overwhelmed or is being hard on themselves, acknowledge it briefly and warmly before anything else. Do not problem-solve unless asked.

OVERLOAD PROTOCOL: If the user says "I did nothing" or expresses shame or avoidance, reframe effort as progress, suggest capture only, and do not create tasks unless explicitly asked.

OUTPUT FORMAT — always respond with ONLY this JSON structure, no extra text:
{
  "type": "Idea | Task | Project | Journal | Reference",
  "area": "University | Business | Personal | Health | Creative",
  "title": "short clear summary",
  "rawInput": "verbatim or lightly cleaned original text",
  "suggestedLocation": "Tasks | Projects | Ideas Vault | Journal | Inbox",
  "nextAction": "one concrete ≤10 min step, or null",
  "energy": "Low | Medium | High",
  "timeBlock": "≤10 min | 25 min | 45+ min",
  "dueDate": "date string or null",
  "notes": "optional warm clarification or reassurance, or null",
  "emotionalAck": "warm acknowledgment if emotional content detected, or null"
}`;

const TYPE_COLORS = {
  Idea: { bg: "#f0fdf4", border: "#86efac", text: "#166534", icon: "💡" },
  Task: { bg: "#eff6ff", border: "#93c5fd", text: "#1e40af", icon: "✅" },
  Project: { bg: "#faf5ff", border: "#c4b5fd", text: "#5b21b6", icon: "🗂️" },
  Journal: { bg: "#fff7ed", border: "#fdba74", text: "#9a3412", icon: "📓" },
  Reference: { bg: "#f8fafc", border: "#94a3b8", text: "#334155", icon: "📎" },
};

const LOCATION_ICONS = {
  Tasks: "✅",
  Projects: "🗂️",
  "Ideas Vault": "💡",
  Journal: "📓",
  Inbox: "📥",
};

export default function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef(null);

  const handleSubmit = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          system: SYSTEM_PROMPT,
          messages: [{ role: "user", content: input }],
        }),
      });

      const data = await response.json();
      const text = data.content?.map(i => i.text || "").join("") || "";
      const clean = text.replace(/```json|```/g, "").trim();
      const parsed = JSON.parse(clean);
      setResult(parsed);
    } catch (err) {
      setError("Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const buildNotionBlock = (r) => {
    return `TYPE: ${r.type}
AREA: ${r.area}
TITLE: ${r.title}

RAW INPUT:
${r.rawInput}

SUGGESTED NOTION LOCATION: Inbox → ${r.suggestedLocation}

NEXT ACTION: ${r.nextAction || "None"}
ENERGY / TIME: ${r.energy} – ${r.timeBlock}
DUE DATE: ${r.dueDate || "None"}
${r.notes ? `\nNOTES: ${r.notes}` : ""}`.trim();
  };

  const handleCopy = () => {
    if (!result) return;
    navigator.clipboard.writeText(buildNotionBlock(result));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReset = () => {
    setInput("");
    setResult(null);
    setError(null);
    textareaRef.current?.focus();
  };

  const colors = result ? TYPE_COLORS[result.type] || TYPE_COLORS["Reference"] : null;

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0f0f1a 0%, #1a1025 50%, #0f1a1a 100%)",
      fontFamily: "'Georgia', serif",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      padding: "40px 20px",
    }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: "36px" }}>
        <div style={{
          fontSize: "11px",
          letterSpacing: "0.3em",
          color: "#6ee7b7",
          textTransform: "uppercase",
          marginBottom: "10px",
          fontFamily: "monospace",
        }}>
          NOTION TRIAGE ASSISTANT
        </div>
        <h1 style={{
          fontSize: "clamp(28px, 5vw, 42px)",
          fontWeight: "400",
          color: "#f1f5f9",
          margin: "0 0 10px",
          lineHeight: 1.2,
          fontStyle: "italic",
        }}>
          Just say what's on your mind.
        </h1>
        <p style={{
          color: "#94a3b8",
          fontSize: "15px",
          margin: 0,
          maxWidth: "420px",
          lineHeight: 1.6,
        }}>
          Messy, emotional, half-formed — all of it counts. I'll sort it for you.
        </p>
      </div>

      {/* Main card */}
      <div style={{
        width: "100%",
        maxWidth: "620px",
        background: "rgba(255,255,255,0.04)",
        borderRadius: "20px",
        border: "1px solid rgba(255,255,255,0.08)",
        backdropFilter: "blur(12px)",
        padding: "28px",
        boxShadow: "0 25px 60px rgba(0,0,0,0.4)",
      }}>
        {/* Input area */}
        {!result && (
          <>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && e.metaKey) handleSubmit(); }}
              placeholder="e.g. "I keep thinking about this business idea but also I have an exam Thursday and I'm kind of overwhelmed…""
              style={{
                width: "100%",
                minHeight: "140px",
                background: "rgba(255,255,255,0.06)",
                border: "1px solid rgba(255,255,255,0.12)",
                borderRadius: "12px",
                color: "#f1f5f9",
                fontSize: "16px",
                lineHeight: "1.6",
                padding: "16px",
                resize: "vertical",
                outline: "none",
                fontFamily: "inherit",
                boxSizing: "border-box",
                transition: "border-color 0.2s",
              }}
              onFocus={e => e.target.style.borderColor = "rgba(110,231,183,0.4)"}
              onBlur={e => e.target.style.borderColor = "rgba(255,255,255,0.12)"}
            />
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginTop: "14px",
            }}>
              <span style={{ color: "#475569", fontSize: "12px", fontFamily: "monospace" }}>
                ⌘+Enter to send
              </span>
              <button
                onClick={handleSubmit}
                disabled={loading || !input.trim()}
                style={{
                  background: loading || !input.trim()
                    ? "rgba(110,231,183,0.15)"
                    : "linear-gradient(135deg, #6ee7b7, #3b82f6)",
                  color: loading || !input.trim() ? "#6ee7b7" : "#0f0f1a",
                  border: "none",
                  borderRadius: "10px",
                  padding: "10px 24px",
                  fontSize: "14px",
                  fontWeight: "600",
                  cursor: loading || !input.trim() ? "not-allowed" : "pointer",
                  fontFamily: "monospace",
                  letterSpacing: "0.05em",
                  transition: "all 0.2s",
                }}
              >
                {loading ? "sorting…" : "Sort this →"}
              </button>
            </div>
          </>
        )}

        {/* Loading state */}
        {loading && (
          <div style={{ textAlign: "center", padding: "20px 0", color: "#6ee7b7", fontSize: "14px", fontFamily: "monospace" }}>
            <div style={{ marginBottom: "8px", fontSize: "24px" }}>🧠</div>
            thinking…
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{ color: "#fca5a5", fontSize: "14px", marginTop: "10px", textAlign: "center" }}>
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div>
            {/* Emotional acknowledgment */}
            {result.emotionalAck && (
              <div style={{
                background: "rgba(253,186,116,0.1)",
                border: "1px solid rgba(253,186,116,0.25)",
                borderRadius: "12px",
                padding: "14px 16px",
                marginBottom: "18px",
                color: "#fed7aa",
                fontSize: "14px",
                lineHeight: "1.6",
                fontStyle: "italic",
              }}>
                💛 {result.emotionalAck}
              </div>
            )}

            {/* Type badge + title */}
            <div style={{ marginBottom: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px", flexWrap: "wrap" }}>
                <span style={{
                  background: colors.bg,
                  color: colors.text,
                  border: `1px solid ${colors.border}`,
                  borderRadius: "20px",
                  padding: "3px 12px",
                  fontSize: "12px",
                  fontWeight: "600",
                  fontFamily: "monospace",
                  letterSpacing: "0.05em",
                }}>
                  {colors.icon} {result.type}
                </span>
                <span style={{
                  background: "rgba(148,163,184,0.1)",
                  color: "#94a3b8",
                  borderRadius: "20px",
                  padding: "3px 12px",
                  fontSize: "12px",
                  fontFamily: "monospace",
                }}>
                  {result.area}
                </span>
              </div>
              <div style={{ color: "#f1f5f9", fontSize: "18px", fontWeight: "500" }}>
                {result.title}
              </div>
            </div>

            {/* Details grid */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "10px",
              marginBottom: "18px",
            }}>
              {[
                { label: "Goes to", value: `${LOCATION_ICONS[result.suggestedLocation] || "📥"} Inbox → ${result.suggestedLocation}` },
                { label: "Energy / Time", value: `${result.energy} · ${result.timeBlock}` },
                { label: "Due date", value: result.dueDate || "None" },
                { label: "Next action", value: result.nextAction || "None", full: true },
              ].map((item, i) => (
                <div key={i} style={{
                  gridColumn: item.full ? "1 / -1" : "auto",
                  background: "rgba(255,255,255,0.04)",
                  borderRadius: "10px",
                  padding: "12px 14px",
                  border: "1px solid rgba(255,255,255,0.07)",
                }}>
                  <div style={{ color: "#64748b", fontSize: "10px", textTransform: "uppercase", letterSpacing: "0.1em", fontFamily: "monospace", marginBottom: "4px" }}>
                    {item.label}
                  </div>
                  <div style={{ color: "#e2e8f0", fontSize: "14px", lineHeight: "1.4" }}>
                    {item.value}
                  </div>
                </div>
              ))}
            </div>

            {/* Notes */}
            {result.notes && (
              <div style={{
                background: "rgba(99,102,241,0.08)",
                border: "1px solid rgba(99,102,241,0.2)",
                borderRadius: "10px",
                padding: "12px 14px",
                marginBottom: "18px",
                color: "#c7d2fe",
                fontSize: "13px",
                lineHeight: "1.6",
              }}>
                📝 {result.notes}
              </div>
            )}

            {/* Action buttons */}
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <button
                onClick={handleCopy}
                style={{
                  flex: 1,
                  background: copied
                    ? "rgba(110,231,183,0.15)"
                    : "linear-gradient(135deg, #6ee7b7, #3b82f6)",
                  color: copied ? "#6ee7b7" : "#0f0f1a",
                  border: copied ? "1px solid rgba(110,231,183,0.3)" : "none",
                  borderRadius: "10px",
                  padding: "11px 20px",
                  fontSize: "14px",
                  fontWeight: "600",
                  cursor: "pointer",
                  fontFamily: "monospace",
                  letterSpacing: "0.04em",
                  transition: "all 0.2s",
                  minWidth: "160px",
                }}
              >
                {copied ? "✓ Copied!" : "📋 Copy for Notion"}
              </button>
              <button
                onClick={handleReset}
                style={{
                  background: "rgba(255,255,255,0.06)",
                  color: "#94a3b8",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "10px",
                  padding: "11px 20px",
                  fontSize: "14px",
                  cursor: "pointer",
                  fontFamily: "monospace",
                  transition: "all 0.2s",
                }}
              >
                ← New thought
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{
        marginTop: "28px",
        color: "#334155",
        fontSize: "12px",
        fontFamily: "monospace",
        textAlign: "center",
        lineHeight: "1.8",
      }}>
        capture → sort → paste into Notion Inbox<br />
        that's all you have to do
      </div>
    </div>
  );
}
