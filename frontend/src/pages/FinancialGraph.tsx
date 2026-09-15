import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";
import { StepFooter } from "../components/AppShell";

const COLUMN_ORDER = ["Evidence", "Communication", "Merchant", "Payout", "Contact", "FundAccount"];
const NODE_COLOR: Record<string, string> = {
  Merchant: "#071510",
  Payout: "#B83A32",
  Contact: "#C9A45C",
  FundAccount: "#C58A27",
  Communication: "#19A974",
  Evidence: "#8a8375",
};

export default function FinancialGraph() {
  const navigate = useNavigate();
  const { incidentId } = useCase();
  const { data: graph, loading, error, reload } = useApiData(
    () => api.getGraph(incidentId),
    [incidentId]
  );
  const [selected, setSelected] = useState<any>(null);

  const layout = useMemo(() => {
    if (!graph) return { positions: {} as Record<string, { x: number; y: number }>, width: 900, height: 400 };
    const columns: Record<string, any[]> = {};
    for (const node of graph.nodes) {
      columns[node.type] = columns[node.type] || [];
      columns[node.type].push(node);
    }
    const colWidth = 160;
    const width = COLUMN_ORDER.length * colWidth + 40;
    const positions: Record<string, { x: number; y: number }> = {};
    COLUMN_ORDER.forEach((type, colIdx) => {
      const nodes = columns[type] || [];
      const rowHeight = 90;
      nodes.forEach((node, rowIdx) => {
        positions[node.id] = {
          x: 40 + colIdx * colWidth,
          y: 50 + rowIdx * rowHeight,
        };
      });
    });
    const maxRows = Math.max(1, ...COLUMN_ORDER.map((t) => (columns[t] || []).length));
    return { positions, width, height: 50 + maxRows * 90 + 40 };
  }, [graph]);

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <p className="label-eyebrow mb-4">Step 4 &middot; Financial Graph</p>
      <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-4">
        How the money and the evidence connect.
      </h1>
      <p className="text-[15px] leading-relaxed text-text_primary/70 mb-10 max-w-[560px]">
        Every line here is a real relationship pulled from your records &mdash; not a suggestion.
        Click any node to see where it came from.
      </p>

      {error && <ErrorBanner message={error} onRetry={reload} />}
      {loading && <p className="text-text_primary/40 text-[14px] mb-8">Loading the graph&hellip;</p>}

      {!error && !loading && graph && graph.nodes.length === 0 && (
        <p className="text-text_primary/45 text-[14px] mb-8">No graph data yet for this case.</p>
      )}

      {!error && !loading && graph && graph.nodes.length > 0 && (
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-8">
        <div className="paper-card p-6 overflow-x-auto">
          {graph && (
            <svg width={layout.width} height={layout.height} role="img" aria-label="Financial graph">
              {graph.edges.map((edge: any) => {
                const a = layout.positions[edge.source];
                const b = layout.positions[edge.target];
                if (!a || !b) return null;
                return (
                  <line
                    key={edge.id}
                    x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                    stroke="#C9A45C" strokeOpacity={0.35} strokeWidth={1.25}
                  />
                );
              })}
              {graph.nodes.map((node: any) => {
                const pos = layout.positions[node.id];
                if (!pos) return null;
                const isSelected = selected?.id === node.id;
                return (
                  <g
                    key={node.id}
                    transform={`translate(${pos.x}, ${pos.y})`}
                    onClick={() => setSelected(node)}
                    style={{ cursor: "pointer" }}
                    tabIndex={0}
                    role="button"
                    aria-label={`${node.type}: ${node.label}`}
                    onKeyDown={(e) => e.key === "Enter" && setSelected(node)}
                  >
                    <circle r={isSelected ? 9 : 7} fill={NODE_COLOR[node.type] || "#666"}
                            stroke={isSelected ? "#071510" : "none"} strokeWidth={2} />
                    <text x={0} y={22} textAnchor="middle" fontSize={10.5} fill="#071510" fontFamily="Aptos, sans-serif">
                      {node.label.length > 16 ? node.label.slice(0, 16) + "â€¦" : node.label}
                    </text>
                  </g>
                );
              })}
            </svg>
          )}
        </div>

        <aside className="paper-card px-6 py-6 h-fit">
          <p className="label-eyebrow mb-4">Provenance sheet</p>
          {selected ? (
            <div>
              <p className="text-[11px] uppercase tracking-wide mb-1" style={{ color: NODE_COLOR[selected.type] }}>
                {selected.type}
              </p>
              <p className="font-display text-[18px] mb-3">{selected.label}</p>
              <dl className="space-y-2 text-[13px]">
                {Object.entries(selected.data || {}).map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-4">
                    <dt className="text-text_primary/45">{k}</dt>
                    <dd className="text-text_primary text-right break-all">{String(v)}</dd>
                  </div>
                ))}
              </dl>
              <p className="text-[11px] text-text_primary/40 mt-4">ID: {selected.id}</p>
            </div>
          ) : (
            <p className="text-[13px] text-text_primary/45">Select a node to inspect its source record.</p>
          )}
        </aside>
      </div>
      )}

      <div className="mt-12">
        <button className="btn-primary" disabled={loading || !!error} onClick={() => navigate("/witness")}>
          Continue to human witness
        </button>
      </div>

      <StepFooter current="/graph" />
    </div>
  );
}

