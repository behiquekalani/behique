import { useState } from "react";

const nodes = {
  kalani:    { label: "Kalani",        sub: "The decision maker",                    color: "#7C3AED", x: 380, y: 30  },
  behiquebot:{ label: "BehiqueBot",    sub: "Bridge — Telegram capture\ntext + voice → Notion", color: "#2563EB", x: 150, y: 150 },
  ceiba:     { label: "Ceiba",         sub: "Brain — full context\nplanning + execution",       color: "#059669", x: 610, y: 150 },
  vault:     { label: "Vault / Notion",sub: "Memory — ideas + patterns\nbreadcrumbs + state",   color: "#D97706", x: 150, y: 290 },
  computer2: { label: "Computer 2",    sub: "Worker — n8n + Ollama\nruns 24/7",                 color: "#DC2626", x: 610, y: 290 },
  ebay:      { label: "eBay Engine",   sub: "Research → list → sell",               color: "#0891B2", x: 120, y: 430 },
  n8n:       { label: "n8n Agency",    sub: "Sell automations to companies",         color: "#7C3AED", x: 380, y: 430 },
  shopify:   { label: "Shopify",       sub: "eBay winners migrate here",             color: "#16A34A", x: 630, y: 430 },
  revenue:   { label: "💰 Revenue",    sub: "$100K by Q3 2026",                      color: "#CA8A04", x: 380, y: 540 },
};

const edges = [
  { from: "kalani",     to: "behiquebot", label: "Telegram input",       dashed: false },
  { from: "kalani",     to: "ceiba",      label: "Cowork sessions",       dashed: false },
  { from: "behiquebot", to: "vault",      label: "saves + classifies",    dashed: false },
  { from: "vault",      to: "ceiba",      label: "reads at session start",dashed: false },
  { from: "ceiba",      to: "computer2",  label: "delegates tasks",       dashed: false },
  { from: "computer2",  to: "behiquebot", label: "morning briefing / nudge", dashed: true },
  { from: "computer2",  to: "ebay",       label: "runs overnight",        dashed: true  },
  { from: "computer2",  to: "n8n",        label: "automation engine",     dashed: false },
  { from: "ebay",       to: "revenue",    label: "listings → sales",      dashed: false },
  { from: "n8n",        to: "revenue",    label: "client fees",           dashed: false },
  { from: "shopify",    to: "revenue",    label: "store sales",           dashed: false },
  { from: "ebay",       to: "shopify",    label: "winners migrate",       dashed: true  },
];

const details = {
  kalani:     { title: "Kalani — The Operator", color: "#7C3AED", items: [
    "✅ Makes all decisions",
    "✅ Inputs via Telegram or Cowork",
    "✅ Reviews outputs, approves listings",
    "🔨 TODO: set up daily review habit using BehiqueBot check-ins",
  ]},
  behiquebot: { title: "BehiqueBot — The Bridge", color: "#2563EB", items: [
    "✅ Captures text + voice via Telegram",
    "✅ Classifies into 5 categories + 4 life pillars",
    "✅ Saves to Notion permanently",
    "✅ Ollama-first (free), OpenAI fallback",
    "🔨 BUILDING: proactive morning briefing",
    "🔨 BUILDING: evening check-in + nudges",
    "⬜ TODO: /status, /checkin, /focus commands",
    "⬜ TODO: actually replies intelligently",
    "⬜ TODO: notices when you go quiet on a project",
  ]},
  ceiba:      { title: "Ceiba — The Brain", color: "#059669", items: [
    "✅ Full project context at session start",
    "✅ Vault memory — index + breadcrumbs",
    "✅ Accountability from psychologist framework",
    "✅ Ceiba Lite offline fallback",
    "⬜ TODO: reads BehiqueBot captures between sessions",
    "⬜ TODO: multi-agent coordination with Computer 2",
  ]},
  vault:      { title: "Vault / Notion — The Memory", color: "#D97706", items: [
    "✅ VAULT_INDEX.md — every file in one scan",
    "✅ Project breadcrumbs — past Ceiba leaves notes",
    "✅ observations.md — Kalani's patterns",
    "✅ primer.md — live session state",
    "✅ Syncthing — real-time sync to Computer 2",
    "⬜ TODO: wiki links woven into notes",
    "⬜ TODO: session start tree hook",
  ]},
  computer2:  { title: "Computer 2 — The Worker", color: "#DC2626", items: [
    "✅ IP: 192.168.0.151",
    "✅ n8n running via pm2 at :5678",
    "✅ Ollama llama3.2 at :11434",
    "✅ Syncthing syncing ~/behique",
    "✅ Cowork working",
    "⚠️  Cloudflare tunnel URL rotates on restart",
    "⬜ TODO: named tunnel with fixed URL",
    "⬜ TODO: n8n workflows actually running overnight",
    "⬜ TODO: product research pipeline",
  ]},
  ebay:       { title: "eBay Engine", color: "#0891B2", items: [
    "✅ types.py + pipeline.py skeleton built",
    "❌ BLOCKED: eBay Developer API keys — NOT done",
    "❌ developer.ebay.com has been 'next action' for 3+ days",
    "⬜ TODO: research module — sold listings → price range",
    "⬜ TODO: AI listing generator",
    "⬜ TODO: auto-publish via Trading API",
    "⬜ TODO: Telegram confirmation on publish",
  ]},
  n8n:        { title: "n8n Agency", color: "#7C3AED", items: [
    "✅ n8n running on Computer 2",
    "✅ Cold outreach draft written",
    "❌ Zero clients — outreach never sent",
    "⬜ TODO: send the draft (5 minutes of work)",
    "⬜ TODO: first paid workflow → document → template",
  ]},
  shopify:    { title: "Shopify Store", color: "#16A34A", items: [
    "✅ Store exists, logo done",
    "⚠️  Monthly cost, zero products, zero sales",
    "Waiting for eBay proven products to migrate",
    "⬜ TODO: first 3 eBay winners → Shopify listings",
  ]},
  revenue:    { title: "Revenue — The Only Goal", color: "#CA8A04", items: [
    "🎯 Target: $100,000 by Q3 2026",
    "💰 Current: $0",
    "Gap: $100,000",
    "Fastest unblocked path: eBay API keys → listing → sale",
    "Second path: send the n8n outreach draft",
    "Both are less than 1 hour of actual work",
  ]},
};

function getCenter(id) {
  const n = nodes[id];
  return { x: n.x, y: n.y + 35 };
}

export default function SystemMap() {
  const [selected, setSelected] = useState(null);

  return (
    <div style={{ background: "#0f172a", minHeight: "100vh", fontFamily: "system-ui, sans-serif", padding: 16, color: "white" }}>
      <h1 style={{ textAlign: "center", fontSize: 18, marginBottom: 2, color: "white" }}>🌳 Ceiba System Map</h1>
      <p style={{ textAlign: "center", fontSize: 11, color: "#64748b", marginBottom: 12 }}>Click any node to see its state and what's missing</p>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>

        {/* MAP */}
        <div style={{ flex: "1 1 420px" }}>
          <svg viewBox="0 0 760 610" width="100%" style={{ display: "block" }}>
            <defs>
              <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">
                <path d="M0 0 L10 5 L0 10z" fill="#475569" />
              </marker>
              <marker id="arr2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">
                <path d="M0 0 L10 5 L0 10z" fill="#7C3AED" />
              </marker>
            </defs>

            {edges.map((e, i) => {
              const f = getCenter(e.from);
              const t = getCenter(e.to);
              const mx = (f.x + t.x) / 2;
              const my = (f.y + t.y) / 2 - 8;
              return (
                <g key={i}>
                  <line x1={f.x} y1={f.y + 18} x2={t.x} y2={t.y - 18}
                    stroke={e.dashed ? "#7C3AED" : "#334155"}
                    strokeWidth={1.5}
                    strokeDasharray={e.dashed ? "5,3" : "0"}
                    markerEnd={e.dashed ? "url(#arr2)" : "url(#arr)"}
                  />
                  <text x={mx} y={my} textAnchor="middle" fontSize={8.5} fill={e.dashed ? "#6d28d9" : "#475569"}>{e.label}</text>
                </g>
              );
            })}

            {Object.entries(nodes).map(([id, n]) => {
              const w = 148, h = 62;
              const isSelected = selected === id;
              const lines = n.sub.split("\n");
              return (
                <g key={id} onClick={() => setSelected(id)} style={{ cursor: "pointer" }}>
                  <rect x={n.x - w / 2} y={n.y} width={w} height={h} rx={8}
                    fill={isSelected ? n.color + "33" : "#1e293b"}
                    stroke={n.color} strokeWidth={isSelected ? 2.5 : 1.5} />
                  <text x={n.x} y={n.y + 20} textAnchor="middle" fontSize={12} fontWeight="bold" fill="white">{n.label}</text>
                  {lines.map((l, i) => (
                    <text key={i} x={n.x} y={n.y + 34 + i * 13} textAnchor="middle" fontSize={9} fill="#94a3b8">{l}</text>
                  ))}
                </g>
              );
            })}
          </svg>
        </div>

        {/* DETAIL PANEL */}
        <div style={{ flex: "1 1 240px", background: "#1e293b", borderRadius: 10, padding: 14 }}>
          {selected ? (() => {
            const d = details[selected];
            return (
              <>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <div style={{ width: 10, height: 10, borderRadius: "50%", background: d.color }} />
                  <span style={{ fontSize: 13, fontWeight: "bold", color: "white" }}>{d.title}</span>
                </div>
                {d.items.map((item, i) => {
                  const c = item.startsWith("✅") ? "#4ade80"
                    : item.startsWith("❌") ? "#f87171"
                    : item.startsWith("⚠️") ? "#fbbf24"
                    : item.startsWith("🔨") ? "#60a5fa"
                    : item.startsWith("⬜") ? "#94a3b8"
                    : item.startsWith("🎯") ? "#fbbf24"
                    : item.startsWith("💰") ? "#4ade80"
                    : "#64748b";
                  return (
                    <div key={i} style={{ fontSize: 11, color: c, marginBottom: 6, paddingLeft: 8, borderLeft: `2px solid ${c}33` }}>
                      {item}
                    </div>
                  );
                })}
              </>
            );
          })() : (
            <div style={{ color: "#334155", textAlign: "center", paddingTop: 80, fontSize: 12 }}>
              ← tap a node
            </div>
          )}
        </div>
      </div>

      {/* LEGEND */}
      <div style={{ display: "flex", gap: 20, justifyContent: "center", marginTop: 10, flexWrap: "wrap" }}>
        {[["─── solid", "#475569", "data flow"], ["╌╌╌ dashed", "#7C3AED", "automated / runs overnight"]].map(([s, c, l]) => (
          <span key={l} style={{ fontSize: 10, color: c }}>{s} = {l}</span>
        ))}
      </div>
    </div>
  );
}
