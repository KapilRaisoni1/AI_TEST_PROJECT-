"use client";

import React, { useCallback, useRef, useState } from "react";
import api from "./services/api";

const FONT_DISPLAY = "'Segoe UI', system-ui, -apple-system, sans-serif";
const FONT_BODY = "'Segoe UI', system-ui, -apple-system, sans-serif";
const FONT_MONO = "'Consolas', 'SF Mono', 'Cascadia Code', monospace";

const STAGES = [
  { key: "requirement", label: "Requirement" },
  { key: "acceptance", label: "Acceptance Criteria" },
  { key: "testcase", label: "Test Case" },
  { key: "script", label: "Test Script" },
  { key: "git", label: "Git Push" },
] as const;

type RunState = "idle" | "running" | "success" | "error";

const DEMO_MODE = false;

type ResultSummary = {
  requirements: number;
  acceptanceCriteria: number;
  testCases: number;
  testScripts: number;
  repo: string;
  commitUrl?: string | null;
  isDemo: boolean;
};

type PipelineStatusValue =
  | "pending"
  | "extracting"
  | "orchestrating"
  | "generating_requirements"
  | "generating_acceptance_criteria"
  | "generating_test_cases"
  | "generating_test_scripts"
  | "pushing_to_github"
  | "completed"
  | "failed";

interface PipelineStateResponse {
  job_id: string;
  status: PipelineStatusValue;
  requirements: unknown[];
  acceptance_criteria: unknown[];
  test_cases: unknown[];
  test_scripts: unknown[];
  git_result: { repo: string; commit_url: string | null } | null;
  error: string | null;
  progress: number;
}

interface StatusResponse {
  job_id: string;
  status: PipelineStatusValue;
  progress: number;
  data: PipelineStateResponse | null;
  error: string | null;
}

interface UploadResponse {
  job_id: string;
  filename: string;
  message: string;
}

function statusToStageIndex(status: PipelineStatusValue): number {
  switch (status) {
    case "pending":
    case "extracting":
    case "orchestrating":
    case "generating_requirements":
      return 0;
    case "generating_acceptance_criteria":
      return 1;
    case "generating_test_cases":
      return 2;
    case "generating_test_scripts":
      return 3;
    case "pushing_to_github":
    case "completed":
      return 4;
    case "failed":
      return -1;
    default:
      return 0;
  }
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function buildMockSummary(): ResultSummary {
  const requirements = 6 + Math.floor(Math.random() * 5);
  return {
    requirements,
    acceptanceCriteria: requirements,
    testCases: requirements * 2,
    testScripts: requirements,
    repo: "your-org/api-tests (demo)",
    isDemo: true,
  };
}

function buildRealSummary(data: PipelineStateResponse): ResultSummary {
  return {
    requirements: data.requirements.length,
    acceptanceCriteria: data.acceptance_criteria.length,
    testCases: data.test_cases.length,
    testScripts: data.test_scripts.length,
    repo: data.git_result?.repo ?? "not pushed",
    commitUrl: data.git_result?.commit_url ?? null,
    isDemo: false,
  };
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [runState, setRunState] = useState<RunState>("idle");
  const [activeStage, setActiveStage] = useState(-1);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [mockSummary, setMockSummary] = useState<ResultSummary | null>(null);
  const [, setJobId] = useState("");
  const [, setPipelineData] = useState<PipelineStateResponse | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const validateAndSetFile = useCallback((candidate: File | null | undefined) => {
    if (!candidate) return;
    if (candidate.type !== "application/pdf") {
      setFileError("Only PDF files are accepted.");
      return;
    }
    if (candidate.size > 25 * 1024 * 1024) {
      setFileError("File exceeds the 25 MB limit.");
      return;
    }
    setFileError(null);
    setFile(candidate);
    setRunState("idle");
    setActiveStage(-1);
    setErrorMessage(null);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      validateAndSetFile(e.dataTransfer.files?.[0]);
    },
    [validateAndSetFile]
  );

  const clearFile = () => {
    setFile(null);
    setFileError(null);
    setRunState("idle");
    setActiveStage(-1);
    setMockSummary(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleGenerateDemo = () => {
    setRunState("running");
    setErrorMessage(null);
    setMockSummary(null);
    setActiveStage(0);

    let stage = 0;
    intervalRef.current = setInterval(() => {
      stage += 1;
      if (stage >= STAGES.length) {
        if (intervalRef.current) clearInterval(intervalRef.current);
        setActiveStage(STAGES.length - 1);
        setMockSummary(buildMockSummary());
        setRunState("success");
        return;
      }
      setActiveStage(stage);
    }, 700);
  };

  const handleGenerateLive = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setRunState("running");
    setErrorMessage(null);
    setMockSummary(null);
    setPipelineData(null);
    setActiveStage(0);

    try {
      const response = await api.post<UploadResponse>("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      console.log("Upload Response:", response.data);
      setJobId(response.data.job_id);
      pollStatus(response.data.job_id);
    } catch (error) {
      console.error(error);
      setRunState("error");
      setErrorMessage("Pipeline failed to start. Check the API connection and try again.");
    }
  };

  const pollStatus = (id: string) => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    intervalRef.current = setInterval(async () => {
      try {
        const response = await api.get<StatusResponse>(`/status/${id}`);
        console.log("Pipeline Status:", response.data);

        if (response.data.data) {
          setPipelineData(response.data.data);
        }

        const stageIndex = statusToStageIndex(response.data.status);

        if (stageIndex >= 0) {
          setActiveStage(stageIndex);
        }

        if (response.data.status === "completed") {
          if (intervalRef.current) clearInterval(intervalRef.current);
          setMockSummary(buildRealSummary(response.data.data!));
          setRunState("success");
        }

        if (response.data.status === "failed") {
          if (intervalRef.current) clearInterval(intervalRef.current);
          setRunState("error");
          setErrorMessage(response.data.error ?? "Pipeline failed.");
        }
      } catch (err) {
        console.error(err);
        if (intervalRef.current) clearInterval(intervalRef.current);
        setRunState("error");
        setErrorMessage("Unable to fetch pipeline status.");
      }
    }, 2000);
  };

  const handleGenerate = DEMO_MODE ? handleGenerateDemo : handleGenerateLive;

  return (
    <main
      className="shell"
      style={{
        ["--font-display" as string]: FONT_DISPLAY,
        ["--font-body" as string]: FONT_BODY,
        ["--font-mono" as string]: FONT_MONO,
      } as React.CSSProperties}
    >
      <div className="grid-backdrop" aria-hidden="true" />

      <div className="console">
        <div className="console-bar">
          <div className="dots">
            <span className="dot dot-a" />
            <span className="dot dot-b" />
            <span className="dot dot-c" />
          </div>
          <span className="console-title">brd-agent.pipeline</span>
          {DEMO_MODE && <span className="demo-badge">DEMO MODE</span>}
          <span className="console-version">v0.1.0</span>
        </div>

        <div className="console-body">
          <div className="eyebrow">SOFTWARE ENGINEERING · AGENTIC AI</div>
          <h1 className="headline">AI-Assisted API Test Generation</h1>
          <p className="subhead">
            Upload a BRD. Five agents turn it into requirements, test cases, scripts, and a pull request.
          </p>

          <div
            className={`dropzone ${isDragging ? "dropzone-active" : ""} ${file ? "dropzone-filled" : ""}`}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
            }}
            aria-label="Upload BRD PDF"
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={(e) => validateAndSetFile(e.target.files?.[0])}
              hidden
            />
            <svg className="upload-icon" width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path d="M12 16V4M12 4L7 9M12 4l5 5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <p className="dropzone-text">
              {isDragging ? "Release to attach" : "Drop BRD PDF here, or click to browse"}
            </p>
            <p className="dropzone-hint">PDF only · up to 25 MB</p>
          </div>

          {fileError && <div className="inline-error">{fileError}</div>}

          {file && (
            <div className="file-chip">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="file-icon">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" strokeWidth="1.5" />
                <path d="M14 2v6h6" stroke="currentColor" strokeWidth="1.5" />
              </svg>
              <span className="file-name">{file.name}</span>
              <span className="file-size">{formatBytes(file.size)}</span>
              <button className="file-remove" onClick={clearFile} aria-label="Remove file" disabled={runState === "running"}>
                ×
              </button>
            </div>
          )}

          <button
            className="run-button"
            onClick={handleGenerate}
            disabled={!file || runState === "running"}
          >
            {runState === "running" ? "Running pipeline…" : "Run pipeline →"}
          </button>

          {errorMessage && <div className="inline-error inline-error-block">{errorMessage}</div>}

          <div className="pipeline" role="list" aria-label="Agent pipeline status">
            {STAGES.map((stage, i) => {
              const isDone = runState === "success" || (runState !== "idle" && i < activeStage);
              const isActive = runState === "running" && i === activeStage;
              const isErrored = runState === "error" && i === activeStage;
              const status = isErrored ? "errored" : isDone ? "done" : isActive ? "active" : "idle";
              return (
                <div className="pipeline-node-wrap" key={stage.key} role="listitem">
                  <div className={`pipeline-node node-${status}`}>
                    <span className="node-dot" />
                    <span className="node-label">{stage.label}</span>
                  </div>
                  {i < STAGES.length - 1 && <span className={`pipeline-connector connector-${status}`} />}
                </div>
              );
            })}
          </div>

          {mockSummary && runState === "success" && (
            <div className="summary-panel">
              <div className="summary-header">
                <span className="summary-dot" />
                Pipeline complete — output
              </div>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-value">{mockSummary.requirements}</span>
                  <span className="summary-label">Requirements</span>
                </div>
                <div className="summary-item">
                  <span className="summary-value">{mockSummary.acceptanceCriteria}</span>
                  <span className="summary-label">Acceptance Criteria</span>
                </div>
                <div className="summary-item">
                  <span className="summary-value">{mockSummary.testCases}</span>
                  <span className="summary-label">Test Cases</span>
                </div>
                <div className="summary-item">
                  <span className="summary-value">{mockSummary.testScripts}</span>
                  <span className="summary-label">Test Scripts</span>
                </div>
              </div>
              <div className="summary-repo">→ pushed to {mockSummary.repo}</div>
            </div>
          )}
        </div>
      </div>

      <style jsx global>{`
        * {
          box-sizing: border-box;
        }
        html,
        body {
          margin: 0;
          padding: 0;
          background: #0a0c10;
        }
      `}</style>

      <style jsx>{`
        .shell {
          position: relative;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 32px 20px;
          font-family: var(--font-body), system-ui, sans-serif;
          color: #e8eaed;
          overflow: hidden;
        }

        .grid-backdrop {
          position: absolute;
          inset: 0;
          background-image: radial-gradient(circle, #1b2029 1px, transparent 1px);
          background-size: 28px 28px;
          mask-image: radial-gradient(ellipse 70% 60% at 50% 35%, black 40%, transparent 100%);
          pointer-events: none;
        }

        .console {
          position: relative;
          width: 100%;
          max-width: 600px;
          background: #12151c;
          border: 1px solid #232732;
          border-radius: 14px;
          box-shadow: 0 30px 80px -20px rgba(0, 0, 0, 0.6);
          overflow: hidden;
        }

        .console-bar {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 13px 18px;
          background: #15181f;
          border-bottom: 1px solid #232732;
        }

        .dots {
          display: flex;
          gap: 6px;
        }
        .dot {
          width: 9px;
          height: 9px;
          border-radius: 50%;
          opacity: 0.7;
        }
        .dot-a {
          background: #f87171;
        }
        .dot-b {
          background: #f5b544;
        }
        .dot-c {
          background: #4ade80;
        }

        .console-title {
          font-family: var(--font-mono), monospace;
          font-size: 12.5px;
          color: #7e879a;
          margin-left: 4px;
        }

        .console-version {
          margin-left: auto;
          font-family: var(--font-mono), monospace;
          font-size: 11px;
          color: #4a5266;
        }

        .demo-badge {
          margin-left: auto;
          font-family: var(--font-mono), monospace;
          font-size: 10px;
          letter-spacing: 0.06em;
          color: #f5b544;
          background: rgba(245, 181, 68, 0.12);
          border: 1px solid rgba(245, 181, 68, 0.3);
          padding: 3px 7px;
          border-radius: 5px;
        }

        .console-body {
          padding: 40px 36px 36px;
        }

        .eyebrow {
          font-family: var(--font-mono), monospace;
          font-size: 11px;
          letter-spacing: 0.12em;
          color: #5eead4;
          margin-bottom: 14px;
        }

        .headline {
          font-family: var(--font-display), sans-serif;
          font-weight: 700;
          font-size: 30px;
          line-height: 1.15;
          letter-spacing: -0.01em;
          margin: 0 0 12px;
          color: #f4f5f7;
        }

        .subhead {
          font-size: 14.5px;
          line-height: 1.55;
          color: #8d96a8;
          margin: 0 0 30px;
          max-width: 46ch;
        }

        .dropzone {
          border: 1.5px dashed #2b3140;
          border-radius: 10px;
          padding: 30px 20px;
          text-align: center;
          cursor: pointer;
          transition: border-color 0.15s ease, background 0.15s ease;
          background: #0e1116;
        }
        .dropzone:hover {
          border-color: #3b4456;
        }
        .dropzone:focus-visible {
          outline: 2px solid #5eead4;
          outline-offset: 2px;
        }
        .dropzone-active {
          border-color: #5eead4;
          background: rgba(94, 234, 212, 0.05);
        }
        .dropzone-filled {
          border-style: solid;
          border-color: #2b3140;
        }

        .upload-icon {
          color: #5eead4;
          margin-bottom: 10px;
        }

        .dropzone-text {
          font-size: 14px;
          color: #c4cad6;
          margin: 0 0 4px;
          font-weight: 500;
        }
        .dropzone-hint {
          font-family: var(--font-mono), monospace;
          font-size: 11.5px;
          color: #5a6478;
          margin: 0;
        }

        .inline-error {
          margin-top: 12px;
          font-size: 13px;
          color: #f87171;
          font-family: var(--font-mono), monospace;
        }
        .inline-error-block {
          margin-top: 16px;
          padding: 10px 12px;
          background: rgba(248, 113, 113, 0.08);
          border: 1px solid rgba(248, 113, 113, 0.25);
          border-radius: 8px;
        }

        .file-chip {
          margin-top: 16px;
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 11px 14px;
          background: #161a22;
          border: 1px solid #232732;
          border-radius: 9px;
        }
        .file-icon {
          color: #5eead4;
          flex-shrink: 0;
        }
        .file-name {
          font-size: 13.5px;
          color: #dde1e8;
          font-weight: 500;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .file-size {
          font-family: var(--font-mono), monospace;
          font-size: 11.5px;
          color: #5a6478;
          margin-left: auto;
          flex-shrink: 0;
        }
        .file-remove {
          background: transparent;
          border: none;
          color: #5a6478;
          font-size: 18px;
          line-height: 1;
          cursor: pointer;
          padding: 2px 4px;
          flex-shrink: 0;
        }
        .file-remove:hover {
          color: #f87171;
        }
        .file-remove:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .run-button {
          width: 100%;
          margin-top: 22px;
          padding: 14px;
          font-size: 14.5px;
          font-weight: 600;
          font-family: var(--font-body), sans-serif;
          color: #0a0c10;
          background: #5eead4;
          border: none;
          border-radius: 9px;
          cursor: pointer;
          transition: background 0.15s ease, transform 0.1s ease;
        }
        .run-button:hover:not(:disabled) {
          background: #7af2e0;
        }
        .run-button:active:not(:disabled) {
          transform: scale(0.99);
        }
        .run-button:disabled {
          background: #2b3140;
          color: #5a6478;
          cursor: not-allowed;
        }
        .run-button:focus-visible {
          outline: 2px solid #5eead4;
          outline-offset: 3px;
        }

        .pipeline {
          margin-top: 32px;
          display: flex;
          align-items: center;
          padding: 16px 4px 4px;
          border-top: 1px solid #1d212b;
        }
        .pipeline-node-wrap {
          display: flex;
          align-items: center;
          flex: 1;
        }
        .pipeline-node {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          flex-shrink: 0;
        }
        .node-dot {
          width: 9px;
          height: 9px;
          border-radius: 50%;
          background: #2b3140;
          transition: background 0.2s ease, box-shadow 0.2s ease;
        }
        .node-label {
          font-family: var(--font-mono), monospace;
          font-size: 9.5px;
          color: #5a6478;
          text-align: center;
          line-height: 1.3;
          max-width: 64px;
        }
        .node-active .node-dot {
          background: #f5b544;
          box-shadow: 0 0 0 4px rgba(245, 181, 68, 0.18);
          animation: pulse 1.1s ease-in-out infinite;
        }
        .node-active .node-label {
          color: #f5b544;
        }
        .node-done .node-dot {
          background: #4ade80;
        }
        .node-done .node-label {
          color: #8d96a8;
        }
        .node-errored .node-dot {
          background: #f87171;
          box-shadow: 0 0 0 4px rgba(248, 113, 113, 0.18);
        }
        .node-errored .node-label {
          color: #f87171;
        }

        .pipeline-connector {
          height: 1.5px;
          flex: 1;
          background: #232732;
          margin: 0 4px;
          margin-bottom: 17px;
          transition: background 0.2s ease;
        }
        .connector-done {
          background: #2f6e4d;
        }

        .summary-panel {
          margin-top: 20px;
          padding: 16px 18px;
          background: rgba(74, 222, 128, 0.05);
          border: 1px solid rgba(74, 222, 128, 0.2);
          border-radius: 10px;
        }
        .summary-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          font-weight: 600;
          color: #c4cad6;
          margin-bottom: 14px;
        }
        .summary-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #4ade80;
          flex-shrink: 0;
        }
        .summary-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 8px;
        }
        .summary-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 2px;
          padding: 10px 4px;
          background: #0e1116;
          border: 1px solid #1d212b;
          border-radius: 8px;
        }
        .summary-value {
          font-family: var(--font-display), sans-serif;
          font-size: 20px;
          font-weight: 700;
          color: #4ade80;
        }
        .summary-label {
          font-family: var(--font-mono), monospace;
          font-size: 9px;
          color: #5a6478;
          text-align: center;
        }
        .summary-repo {
          margin-top: 12px;
          font-family: var(--font-mono), monospace;
          font-size: 11.5px;
          color: #8d96a8;
        }

        @keyframes pulse {
          0%,
          100% {
            opacity: 1;
          }
          50% {
            opacity: 0.45;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .node-active .node-dot {
            animation: none;
          }
        }

        @media (max-width: 480px) {
          .console-body {
            padding: 30px 22px 28px;
          }
          .headline {
            font-size: 24px;
          }
          .node-label {
            display: none;
          }
          .summary-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      `}</style>
    </main>
  );
}