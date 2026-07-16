"use client";
import { useState, useRef } from "react";
import { api } from "@/lib/api";
import { UploadCloud, Loader2 } from "lucide-react";

const MODELS = [
  { value: "mobilenet_v3", label: "MobileNetV3 (fast)" },
  { value: "resnet50", label: "ResNet50 (accurate)" },
  { value: "efficientnet_b3", label: "EfficientNet-B3 (balanced)" },
];

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [model, setModel] = useState("mobilenet_v3");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function pickFile(f: File) {
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  }

  async function runPredict() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.predict(file, model);
      setResult(data);
    } catch (e: any) {
      setError(e.message || "Prediction failed. Are you logged in, and is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h1 className="font-display text-3xl font-bold mb-2">Classify an image</h1>
      <p className="text-slate-400 mb-8 text-sm">Requires an authenticated session — log in first if you get a 401.</p>

      <div className="glass rounded-2xl p-6 mb-6 flex items-center gap-4">
        <label className="text-sm text-slate-400">Model</label>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="bg-bg2 border border-white/10 rounded-lg px-3 py-2 text-sm"
        >
          {MODELS.map((m) => (
            <option key={m.value} value={m.value}>{m.label}</option>
          ))}
        </select>
      </div>

      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (e.dataTransfer.files[0]) pickFile(e.dataTransfer.files[0]);
        }}
        className="glass rounded-2xl border-dashed border-2 border-white/10 p-12 text-center cursor-pointer hover:border-cyan/40 transition"
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && pickFile(e.target.files[0])}
        />
        {preview ? (
          <img src={preview} alt="preview" className="max-h-64 mx-auto rounded-xl" />
        ) : (
          <>
            <UploadCloud className="mx-auto mb-3 text-glow" size={32} />
            <p className="font-medium">Drag & drop an image, or click to browse</p>
            <p className="text-xs text-slate-500 mt-1">JPG, PNG or WEBP, up to 8MB</p>
          </>
        )}
      </div>

      {file && (
        <button
          onClick={runPredict}
          disabled={loading}
          className="mt-6 w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold bg-gradient-to-r from-electric to-glow disabled:opacity-60"
        >
          {loading ? <><Loader2 className="animate-spin" size={16} /> Running inference…</> : "Classify image"}
        </button>
      )}

      {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

      {result && (
        <div className="glass rounded-2xl p-6 mt-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-xl capitalize">{result.predicted_label}</h2>
            <span className="font-mono text-cyan text-lg">{Math.round(result.confidence * 100)}%</span>
          </div>
          <div className="space-y-3 mb-4">
            {result.top5.map((c: any) => (
              <div key={c.label}>
                <div className="flex justify-between text-xs mb-1 capitalize">
                  <span>{c.label}</span>
                  <span className="font-mono text-slate-400">{(c.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-electric to-cyan" style={{ width: `${c.confidence * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-slate-500">
            Model: {result.model_name} · Inference: {Math.round(result.inference_time_ms)}ms
          </p>
          {result.gradcam_path && (
            <img src={api.fileUrl(result.gradcam_path)} alt="Grad-CAM" className="mt-4 rounded-xl w-48" />
          )}
        </div>
      )}
    </div>
  );
}
