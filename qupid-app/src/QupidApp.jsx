import React, { useMemo, useState } from "react";
import {
  Activity,
  Atom,
  Heart,
  Sparkles,
  Upload,
  User,
  UserRound,
  Waves,
  Shield,
  Zap,
} from "lucide-react";
import quantumGradient from "./assets/pink-holographic.avif";

const parameterSections = [
  {
    title: "mutual dynamic - the floquet driver",
    icon: Activity,
    items: [
      ["mutualEmpathy", "mutual empathy"],
      ["mutualCompatability", "compatibility"],
      ["mutualFrequency", "frequency of interactions"],
      ["mutualStrength", "strength of interactions"],
      ["mutualSync", "how in sync you both are"],
      ["mutualCodependence", "how negatively codependent you are"],
    ],
  },
  {
    title: "person a",
    icon: User,
    items: [
      ["personATemperarment", "temperament"],
      ["personAHotCold", "how hot/cold they are"],
      ["personADistant", "how distant they are"],
      ["personABurnedOut", "how burned out they are"],
    ],
  },
  {
    title: "person b",
    icon: UserRound,
    items: [
      ["personBTemperarment", "temperament"],
      ["personBHotCold", "how hot/cold they are"],
      ["personBDistant", "how distant they are"],
      ["personBBurnedOut", "how burned out they are"],
    ],
  },
];

const neoGlassPanel =
  "rounded-[24px] border border-white/26 bg-gradient-to-br from-white/15 via-white/9 to-white/13 backdrop-blur-2xl shadow-[inset_0_1px_1px_rgba(255,255,255,0.2),inset_0_-8px_16px_rgba(0,0,0,0.16),0_12px_22px_rgba(6,10,30,0.3),0_0_10px_rgba(255,255,255,0.06)]";
const neoGlassInner =
  "rounded-xl border border-white/20 bg-gradient-to-br from-white/12 via-white/7 to-white/10 shadow-[inset_0_1px_1px_rgba(255,255,255,0.16),inset_0_-6px_10px_rgba(0,0,0,0.14),0_8px_14px_rgba(6,10,30,0.24)]";

const QupidApp = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [revealed, setRevealed] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [serverResult, setServerResult] = useState(null);
  const [serverError, setServerError] = useState("");

  const inferredValues = serverResult?.inferred_params || null;
  const displayScore = serverResult?.health_score;
  const displayCoherent = displayScore !== undefined ? displayScore >= 70 : false;
  const displayAdvice = serverResult?.report_text || "upload a text conversation and run analysis to predict the trajectory.";

  const topSummary = useMemo(() => {
    if (!inferredValues) return [];
    return [
      ["messages analyzed", serverResult?.messages_analyzed ?? "-"],
      ["person a", inferredValues.personAName || "person A"],
      ["person b", inferredValues.personBName || "person B"],
    ];
  }, [inferredValues, serverResult]);

  const handleAnalyzeAndEvolve = async () => {
    setServerError("");
    setRevealed(true);
    if (!selectedFile) {
      setServerError("please upload a conversation file first (.txt, .csv, or .json).");
      return;
    }

    setIsRunning(true);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("/analyze-run", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "backend error");
      }
      setServerResult(data);
    } catch (error) {
      setServerError(error.message || "unable to reach the quantum backend.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div
      className="relative min-h-screen overflow-hidden bg-[#070914] text-white"
      style={{ fontFamily: '"Nunito", "Avenir Next", sans-serif' }}
    >
      <div
        className="pointer-events-none absolute inset-0 bg-cover bg-center opacity-35"
        style={{
          backgroundImage: `url(${quantumGradient})`,
          filter: "contrast(1.12) saturate(1.18) brightness(0.95)",
        }}
      />
      <div className="pointer-events-none absolute inset-0 opacity-50 mix-blend-screen">
        <div className="absolute left-0 top-0 h-full w-full bg-[radial-gradient(circle_at_20%_20%,rgba(0,255,255,0.12),transparent_45%),radial-gradient(circle_at_80%_30%,rgba(255,182,193,0.14),transparent_40%),radial-gradient(circle_at_50%_80%,rgba(255,255,255,0.08),transparent_45%)]" />
      </div>

      <div className="relative z-10 flex min-h-screen items-center justify-center px-4 py-12">
        <div className="w-full max-w-5xl rounded-[36px] bg-gradient-to-r from-cyan-300/35 via-white/15 to-pink-200/35 p-[1px] shadow-[0_0_70px_rgba(0,255,255,0.2)]">
          <div className="relative rounded-[35px] border border-white/30 bg-white/12 p-6 backdrop-blur-3xl shadow-[inset_0_1px_1px_rgba(255,255,255,0.25),inset_0_-16px_30px_rgba(0,0,0,0.25),0_25px_50px_rgba(6,10,30,0.45)] md:p-10">
            <header className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/15">
                  <Atom className="h-6 w-6 text-cyan-200" />
                </div>
                <div>
                  <h1 className="text-3xl font-semibold tracking-wide text-white drop-shadow-[0_0_14px_rgba(0,255,255,0.4)] md:text-4xl">
                    qupid.cloud
                  </h1>
                </div>
              </div>
              <p className="text-white/70">
                upload your text convo and let qupid analyze and evolve your relationship's quantum state. 
              </p>
              <div className="flex flex-wrap items-center gap-2 text-xs tracking-[0.2em] text-white/60">
                <Badge icon={Sparkles} label="entanglement" />
                <Badge icon={Waves} label="coherence" />
                <Badge icon={Shield} label="stability" />
              </div>
            </header>

            <div className="my-6 h-px w-full bg-gradient-to-r from-transparent via-white/25 to-transparent" />

            <section className={`${neoGlassPanel} p-4 md:p-5`}>
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="text-sm font-semibold tracking-[0.18em] text-white/80">
                    upload text message conversation
                  </p>
                  <p className="mt-1 text-xs text-white/60">
                    accepted formats: .txt, .csv, .json
                  </p>
                </div>
                <label className="inline-flex cursor-pointer items-center gap-2 rounded-full border border-white/25 bg-white/10 px-4 py-2 text-xs tracking-[0.14em] text-white/80 transition hover:border-white/40">
                  <Upload className="h-4 w-4 text-cyan-200" />
                  choose file
                  <input
                    type="file"
                    accept=".txt,.csv,.json,application/json,text/plain,text/csv"
                    className="hidden"
                    onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
                  />
                </label>
              </div>
              <div className="mt-3 text-sm text-white/70">
                {selectedFile ? `selected: ${selectedFile.name}` : "no file selected"}
              </div>
            </section>

            {inferredValues && (
              <>
                <div className="my-6 h-px w-full bg-gradient-to-r from-transparent via-white/25 to-transparent" />

                <section className="grid gap-5 lg:grid-cols-3">
                  {parameterSections.map((section) => (
                    <div key={section.title} className={`${neoGlassPanel} p-4`}>
                      <div className="mb-3 flex items-center gap-2 text-sm font-semibold tracking-[0.18em] text-white/80">
                        <section.icon className="h-4 w-4 text-cyan-200" />
                        <h3>{section.title}</h3>
                      </div>
                      <div className="grid gap-2">
                        {section.items.map(([key, label]) => (
                          <ParamRow key={key} label={label} value={inferredValues[key]} />
                        ))}
                      </div>
                    </div>
                  ))}
                </section>
              </>
            )}

            <div className="mt-8 flex flex-col items-center gap-4 md:flex-row md:justify-between">
              <div className="flex items-center gap-3 text-sm text-white/70">
                <Heart className="h-5 w-5 text-pink-200" />
                <span>qupid creates a unique hamiltonian and quantum state based on your texts.</span>
              </div>
              <button
                type="button"
                onClick={handleAnalyzeAndEvolve}
                disabled={isRunning}
                className="group relative flex items-center gap-3 rounded-full bg-gradient-to-r from-[#00ffff] via-white/85 to-[#ffb6c1] px-8 py-3 text-sm font-semibold tracking-[0.18em] text-[#101027] shadow-[0_0_28px_rgba(0,255,255,0.35)] transition hover:shadow-[0_0_42px_rgba(255,182,193,0.55)] disabled:cursor-not-allowed disabled:opacity-70"
              >
                <Zap className={`h-5 w-5 ${isRunning ? "animate-pulse" : ""}`} />
                {isRunning ? "analyzing + evolving..." : "analyze & evolve quantum state"}
                <span className="absolute inset-0 -z-10 rounded-full bg-white/20 blur-xl transition duration-500 group-hover:opacity-70" />
              </button>
            </div>

            <div className="my-6 h-px w-full bg-gradient-to-r from-transparent via-white/25 to-transparent" />

            {revealed && (
              <section className={`mt-10 ${neoGlassPanel} p-6`}>
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <span
                      className={`rounded-full px-4 py-1 text-xs font-semibold tracking-[0.2em] ${
                        displayCoherent
                          ? "bg-cyan-200/20 text-cyan-100 shadow-[0_0_18px_rgba(0,255,255,0.45)]"
                          : "bg-pink-200/20 text-pink-100 shadow-[0_0_18px_rgba(255,182,193,0.45)]"
                      }`}
                    >
                      state: {displayCoherent ? "coherent" : "decohered"}
                    </span>
                  </div>
                  <div className="text-right">
                    <p className="text-xs tracking-[0.3em] text-white/60">predicted purity score</p>
                    <p
                      className="text-4xl font-semibold text-white"
                      style={{ fontFamily: '"Space Mono", "JetBrains Mono", monospace' }}
                    >
                      {displayScore !== undefined ? `${Number(displayScore).toFixed(1)}% purity` : "--"}
                    </p>
                  </div>
                </div>

                {topSummary.length > 0 && (
                  <div className="mt-4 grid gap-2 md:grid-cols-3">
                    {topSummary.map(([label, value]) => (
                      <ParamRow key={label} label={label} value={value} compact />
                    ))}
                  </div>
                )}

                {/* {serverResult?.analyzer_debug && (
                  <div className={`mt-6 ${neoGlassPanel} p-5 text-sm text-white/80`}>
                    <p className="mb-3 text-xs uppercase tracking-[0.22em] text-white/60">
                      analyzer debug
                    </p>
                    <div className="grid gap-2 md:grid-cols-2">
                      {Object.entries(serverResult.analyzer_debug).map(([key, value]) => (
                        <ParamRow key={key} label={key.replace(/_/g, " ")} value={value} compact />
                      ))}
                    </div>
                  </div>
                )} */}

                <div className={`mt-6 ${neoGlassPanel} p-5 text-sm text-white/80`}>
                  {serverError ? (
                    <p style={{ fontFamily: '"Space Mono", "JetBrains Mono", monospace' }}>
                      {serverError}
                    </p>
                  ) : (
                    <pre
                      className="whitespace-pre-wrap text-sm text-white/80"
                      style={{ fontFamily: '"Space Mono", "JetBrains Mono", monospace' }}
                    >
                      {displayAdvice}
                    </pre>
                  )}
                </div>

                {serverResult?.plot_base64 && (
                  <div className={`mt-6 overflow-hidden ${neoGlassPanel} p-4`}>
                    <img
                      alt="relationship dynamics plot"
                      src={`data:image/png;base64,${serverResult.plot_base64}`}
                      className="h-auto w-full rounded-2xl"
                    />
                  </div>
                )}
              </section>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const Badge = ({ icon: Icon, label }) => (
  <div className="flex items-center gap-2 rounded-full border border-white/25 bg-white/10 px-3 py-1 text-[11px] tracking-[0.25em] text-white/70 shadow-[inset_0_1px_2px_rgba(255,255,255,0.22),0_10px_18px_rgba(6,10,30,0.3)]">
    <Icon className="h-3.5 w-3.5 text-cyan-200" />
    <span>{label}</span>
  </div>
);

const ParamRow = ({ label, value, compact = false }) => {
  const displayValue =
    value === null || value === undefined
      ? "-"
      : typeof value === "object"
        ? JSON.stringify(value)
        : value;
  return (
    <div className={`flex items-center justify-between ${neoGlassInner} px-3 py-2 ${compact ? "text-xs" : "text-sm"}`}>
      <span className="text-white/70">{label}</span>
      <span className="font-mono text-white">{displayValue}</span>
    </div>
  );
};

export default QupidApp;
