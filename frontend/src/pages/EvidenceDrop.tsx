import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileText, Upload } from "lucide-react";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { StepFooter } from "../components/AppShell";
import ErrorBanner from "../components/ErrorBanner";

interface Tile {
  id: string;
  filename: string;
  status: string;
  sourceLabel?: string;
}

export default function EvidenceDrop() {
  const navigate = useNavigate();
  const { merchantId, incidentId } = useCase();
  const [tiles, setTiles] = useState<Tile[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  const loadExisting = useCallback(() => {
    setLoadError(null);
    api.getEvidence(incidentId).then((data) => {
      setTiles(
        data.artifacts.map((a: any) => ({
          id: a.id,
          filename: a.filename,
          status: a.extraction_status === "extracted" ? "Processed" : "Processing",
          sourceLabel: a.source_label,
        }))
      );
      setLoaded(true);
    }).catch((e) => { setLoadError(String(e.message || e)); setLoaded(true); });
  }, [incidentId]);

  useEffect(() => { loadExisting(); }, [loadExisting]);

  const handleFiles = useCallback(
    async (files: FileList) => {
      for (const file of Array.from(files)) {
        const tempId = `pending_${file.name}_${Date.now()}`;
        setTiles((t) => [...t, { id: tempId, filename: file.name, status: "Processing" }]);
        try {
          const uploaded = await api.uploadEvidence(file, merchantId, incidentId, "upload");
          setTiles((t) => t.map((tile) => (tile.id === tempId ? { ...tile, id: uploaded.artifact_id } : tile)));
          if (uploaded.extraction_status === "text_ready") {
            await api.analyzeEvidence(uploaded.artifact_id);
            setTiles((t) => t.map((tile) => (tile.id === uploaded.artifact_id ? { ...tile, status: "Processed" } : tile)));
          } else {
            setTiles((t) => t.map((tile) => (tile.id === uploaded.artifact_id ? { ...tile, status: "Queued for review" } : tile)));
          }
        } catch {
          setTiles((t) => t.map((tile) => (tile.id === tempId ? { ...tile, status: "Could not process" } : tile)));
        }
      }
    },
    [merchantId, incidentId]
  );

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <div className="max-w-[640px] mb-10">
        <p className="label-eyebrow mb-4">Step 2 of 3 &middot; Evidence</p>
        <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-4">Bring what you have.</h1>
        <p className="text-[15px] leading-relaxed text-forest/70 max-w-[500px]">
          Screenshots, PDFs, bank statements, SMS or email exports &mdash; whatever you have is
          enough to start. We already pulled in what came through your Finance Ops thread.
        </p>
      </div>

      {loadError && <ErrorBanner message={loadError} onRetry={loadExisting} />}
      {loaded && !loadError && tiles.length === 0 && (
        <p className="text-[13px] text-forest/45 mb-6">
          No evidence ingested yet for this case &mdash; drop a file below to get started.
        </p>
      )}

      <label
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files); }}
        className={`flex flex-col items-center justify-center gap-3 border-2 border-dashed rounded-[4px]
                    px-8 py-14 mb-8 max-w-[720px] cursor-pointer transition-colors duration-250 ${
          dragOver ? "border-gold bg-gold/5" : "border-forest/20 hover:border-forest/35"
        }`}
      >
        <Upload size={22} className="text-forest/40" />
        <p className="text-[14px] font-ui text-forest/60">Drop files here, or click to browse</p>
        <input
          type="file"
          multiple
          className="hidden"
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
        />
      </label>

      {tiles.length > 0 && (
        <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 max-w-[900px] mb-10">
          {tiles.map((tile) => (
            <li key={tile.id} className="paper-card px-4 py-4 flex items-start gap-3">
              <FileText size={18} className="text-gold mt-0.5 shrink-0" />
              <div className="min-w-0">
                <p className="text-[13px] font-ui truncate">{tile.filename}</p>
                {tile.sourceLabel && <p className="text-[11px] text-forest/40 uppercase tracking-wide">{tile.sourceLabel}</p>}
                <p className={`text-[12px] mt-1 ${tile.status === "Processed" ? "text-emerald" : "text-forest/50"}`}>
                  {tile.status}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}

      <button className="btn-primary" onClick={() => navigate("/reconstruction")}>
        Continue to reconstruction
      </button>

      <StepFooter current="/evidence" />
    </div>
  );
}
