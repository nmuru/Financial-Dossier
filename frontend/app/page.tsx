"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Home() {
  const router = useRouter();
  const [mode, setMode] = useState<"code" | "financial">("code");

  function continueToAnalysis() {
    router.push(mode === "code" ? "/code-analysis" : "/financial-analysis");
  }

  return (
    <main className="landing">
      <div className="landing-card">
        <div className="eyebrow">ANALYSIS DOSSIER</div>
        <h1>Choose your analysis workspace.</h1>
        <p className="landing-copy">
          The same analysis harness can be used for different source types and domains.
          Select the workspace you want to explore.
        </p>

        <fieldset className="phase-selection" style={{ marginTop: 28 }}>
          <legend>Analysis type</legend>
          <div style={{ display: "grid", gap: 12 }}>
            <label className="phase-option" style={{ alignItems: "flex-start" }}>
              <input
                type="radio"
                name="analysis-type"
                value="code"
                checked={mode === "code"}
                onChange={() => setMode("code")}
              />
              <span>
                <strong>Code Base Analysis</strong><br />
                <span style={{ color: "var(--muted)", fontSize: 12 }}>
                  Reverse engineer a GitHub repository into an engineering dossier.
                </span>
              </span>
            </label>

            <label className="phase-option" style={{ alignItems: "flex-start" }}>
              <input
                type="radio"
                name="analysis-type"
                value="financial"
                checked={mode === "financial"}
                onChange={() => setMode("financial")}
              />
              <span>
                <strong>Financial Analysis</strong><br />
                <span style={{ color: "var(--muted)", fontSize: 12 }}>
                  Analyze SEC Company Facts data as a structured financial evidence source.
                </span>
              </span>
            </label>
          </div>
        </fieldset>

        <button type="button" onClick={continueToAnalysis} style={{ marginTop: 20, minHeight: 44, padding: "0 18px" }}>
          Continue
        </button>
      </div>
    </main>
  );
}
