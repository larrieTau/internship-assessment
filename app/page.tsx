"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

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

    const output = candidate.output;
    if (output && typeof output === "object") {
      const nested = output as Record<string, unknown>;
      const nestedUrl = nested.audio_url ?? nested.url ?? nested.href;
      if (typeof nestedUrl === "string") {
        return nestedUrl;
      }
    }

    const data = candidate.data;
    if (Array.isArray(data) && data.length > 0 && typeof data[0] === "object") {
      const first = data[0] as Record<string, unknown>;
      const listUrl = first.audio_url ?? first.url ?? first.href;
      if (typeof listUrl === "string") {
        return listUrl;
      }
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
  const [theme, setTheme] = useState<"light" | "dark">("light");
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

  useEffect(() => {
    const storedTheme = window.localStorage.getItem("sunbird-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const nextTheme = storedTheme === "dark" || storedTheme === "light"
      ? storedTheme
      : prefersDark
        ? "dark"
        : "light";

    setTheme(nextTheme);
  }, []);

  useEffect(() => {
    document.body.dataset.theme = theme;
    window.localStorage.setItem("sunbird-theme", theme);
  }, [theme]);

  function toggleTheme() {
    setTheme((currentTheme) => (currentTheme === "dark" ? "light" : "dark"));
  }

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
  const isMockMode = Boolean(result && typeof result === "object" && (result as Record<string, unknown>).mock_mode);

  return (
    <main className="page-shell">
      <section className="hero-card">
        <div className="hero-copy">
          <p className="eyebrow">Sunbird AI studio</p>
          <h1>Turn content into speech.</h1>
          <p className="lede">A refined workspace for translation, transcription, and voice.</p>
          <div className="hero-badges">
            <span>Text</span>
            <span>Audio</span>
            <span>Classic orange</span>
          </div>
        </div>

        <form className="panel" onSubmit={handleSubmit}>
          <div className="panel-toolbar">
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

            <button
              type="button"
              className="theme-toggle"
              onClick={toggleTheme}
              aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            >
              {theme === "dark" ? "Light mode" : "Dark mode"}
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
          ) : isMockMode ? (
            <p>Mock mode is active. Add a valid <strong>SUNBIRD_API_TOKEN</strong> in Vercel to generate real audio.</p>
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
