"use client";

import { FormEvent, useMemo, useState } from "react";

type ResultData = Record<string, unknown> | null;

const languageOptions = [
  { label: "Luganda", value: "luganda" },
  { label: "Runyankole", value: "runyankole" },
  { label: "Ateso", value: "ateso" },
  { label: "Lugbara", value: "lugbara" },
  { label: "Acholi", value: "acholi" },
];

function resolveApiUrl(path: string) {
  // In production (Vercel), use relative paths to /api
  // In development, use the configured backend URL
  if (typeof window !== "undefined" && window.location.hostname === "localhost") {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:5000";
    return `${baseUrl}${path}`;
  }
  // Production: use Vercel's /api routes
  return path;
}

function extractAudioUrl(payload: ResultData) {
  const audio = payload?.pipeline ? (payload.pipeline as Record<string, unknown>).audio : undefined;

  if (typeof audio === "string") {
    return audio;
  }

  if (audio && typeof audio === "object") {
    const candidate = audio as Record<string, unknown>;
    const rawUrl = candidate.audio_url ?? candidate.url ?? candidate.href;
    if (typeof rawUrl === "string") {
      return rawUrl;
    }
  }

  return null;
}

function extractAudioMessage(payload: ResultData) {
  const audio = payload?.pipeline ? (payload.pipeline as Record<string, unknown>).audio : undefined;

  if (audio && typeof audio === "object") {
    const candidate = audio as Record<string, unknown>;
    if (typeof candidate.message === "string" && candidate.message.trim()) {
      return candidate.message;
    }
  }

  return null;
}

export default function Home() {
  const [mode, setMode] = useState<"text" | "audio">("text");
  const [text, setText] = useState(
    "Climate change is affecting crop yields, water availability, and communities across East Africa.",
  );
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [targetLanguage, setTargetLanguage] = useState("luganda");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ResultData>(null);

  const audioPreview = useMemo(() => {
    if (!audioFile) {
      return null;
    }

    return {
      name: audioFile.name,
      sizeKb: Math.max(1, Math.round(audioFile.size / 1024)),
      type: audioFile.type || "unknown",
    };
  }, [audioFile]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);

    try {
      if (mode === "text") {
        if (!text.trim()) {
          throw new Error("Enter some text before processing.");
        }

        const response = await fetch(resolveApiUrl("/api/process-text"), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: text.trim(),
            target_language: targetLanguage,
          }),
        });

        const payload = (await response.json()) as ResultData;

        if (!response.ok) {
          throw new Error(
            typeof payload?.error === "string" ? payload.error : "Text processing failed.",
          );
        }

        setResult(payload);
      } else {
        if (!audioFile) {
          throw new Error("Choose an audio file before processing.");
        }

        const formData = new FormData();
        formData.append("audio", audioFile);
        formData.append("target_language", targetLanguage);

        const response = await fetch(resolveApiUrl("/api/process-audio"), {
          method: "POST",
          body: formData,
        });

        const payload = (await response.json()) as ResultData;

        if (!response.ok) {
          throw new Error(
            typeof payload?.error === "string" ? payload.error : "Audio processing failed.",
          );
        }

        setResult(payload);
      }
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unexpected error.");
    } finally {
      setLoading(false);
    }
  }

  const transcript = result?.pipeline && typeof result.pipeline === "object"
    ? (result.pipeline as Record<string, unknown>).transcript
    : null;
  const summary = result?.pipeline && typeof result.pipeline === "object"
    ? (result.pipeline as Record<string, unknown>).summary
    : null;
  const translation = result?.pipeline && typeof result.pipeline === "object"
    ? (result.pipeline as Record<string, unknown>).translation
    : null;
  const audioUrl = extractAudioUrl(result);
  const audioMessage = extractAudioMessage(result);

  return (
    <main className="page-shell">
      <section className="hero-card">
        <div className="hero-copy">
          <p className="eyebrow">Sunbird AI pipeline</p>
          <h1>Turn text or audio into a translated, spoken result.</h1>
          <p className="lede">
            Process content through transcription, summarization, translation, and text-to-speech in
            one flow. The page uses the backend at <code>/api/process-text</code> and
            <code> /api/process-audio</code>, or a custom base URL if you set
            <code> NEXT_PUBLIC_API_URL</code>.
          </p>
          <div className="hero-badges">
            <span>Text input</span>
            <span>Audio upload</span>
            <span>5 Ugandan languages</span>
          </div>
        </div>

        <form className="panel" onSubmit={handleSubmit}>
          <div className="mode-switch" role="tablist" aria-label="Input mode">
            <button
              type="button"
              className={mode === "text" ? "active" : ""}
              onClick={() => setMode("text")}
            >
              Text
            </button>
            <button
              type="button"
              className={mode === "audio" ? "active" : ""}
              onClick={() => setMode("audio")}
            >
              Audio
            </button>
          </div>

          <label>
            <span>Target language</span>
            <select value={targetLanguage} onChange={(event) => setTargetLanguage(event.target.value)}>
              {languageOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          {mode === "text" ? (
            <label>
              <span>Input text</span>
              <textarea
                rows={8}
                value={text}
                onChange={(event) => setText(event.target.value)}
                placeholder="Paste or type your content here"
              />
            </label>
          ) : (
            <label>
              <span>Audio file</span>
              <input
                type="file"
                accept="audio/*"
                onChange={(event) => setAudioFile(event.target.files?.[0] ?? null)}
              />
            </label>
          )}

          {audioPreview ? (
            <div className="file-chip">
              <strong>{audioPreview.name}</strong>
              <span>
                {audioPreview.sizeKb} KB · {audioPreview.type}
              </span>
            </div>
          ) : null}

          <button className="submit-button" type="submit" disabled={loading}>
            {loading ? "Processing..." : "Process now"}
          </button>

          {error ? <p className="error-box">{error}</p> : null}
        </form>
      </section>

      <section className="results-grid">
        <article className="result-card">
          <h2>Transcript</h2>
          <p>{typeof transcript === "string" && transcript ? transcript : "No transcript yet."}</p>
        </article>

        <article className="result-card">
          <h2>Summary</h2>
          <p>{typeof summary === "string" && summary ? summary : "No summary yet."}</p>
        </article>

        <article className="result-card wide">
          <h2>Translation</h2>
          <p>
            {typeof translation === "string" && translation ? translation : "No translation yet."}
          </p>
        </article>

        <article className="result-card wide">
          <h2>Audio output</h2>
          {audioUrl ? (
            <audio controls src={audioUrl} />
          ) : audioMessage ? (
            <p>{audioMessage}</p>
          ) : (
            <p>No audio generated yet.</p>
          )}
        </article>
      </section>
    </main>
  );
}
