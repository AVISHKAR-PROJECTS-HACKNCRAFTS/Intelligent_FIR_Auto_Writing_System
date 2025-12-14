"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import {
  Header,
  ComplaintForm,
  ResultSummary,
  ResultTabs,
  ErrorMessage,
  Footer,
  FIRResponse,
  RealtimeAnalysis,
  TabType,
  ApiStatus,
  API_BASE_URL,
} from "@/components/fir";

export default function Home() {
  // Form state
  const [name, setName] = useState("");
  const [contact, setContact] = useState("");
  const [description, setDescription] = useState("");
  const [witnessName, setWitnessName] = useState("");
  const [witnessContact, setWitnessContact] = useState("");
  const [showWitness, setShowWitness] = useState(false);

  // Result state
  const [result, setResult] = useState<FIRResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>("fir");

  // Analysis state
  const [realtimeAnalysis, setRealtimeAnalysis] = useState<RealtimeAnalysis | null>(null);
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");

  // Refs
  const resultRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        setApiStatus(data.status === "healthy" ? "online" : "offline");
      } catch {
        setApiStatus("offline");
      }
    };
    checkHealth();
  }, []);

  // Real-time analysis with debounce
  const analyzeRealtime = useCallback(async (text: string) => {
    if (text.length < 20) {
      setRealtimeAnalysis(null);
      return;
    }

    try {
      const analysisRes = await fetch(`${API_BASE_URL}/analyze_realtime`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const analysisData = await analysisRes.json();

      if (analysisData.success) {
        setRealtimeAnalysis(analysisData);
      }
    } catch {
      // Silent fail for real-time analysis
    }
  }, []);

  // Debounced description change handler
  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setDescription(text);

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      analyzeRealtime(text);
    }, 500);
  };

  // Form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setCopied(false);

    try {
      const response = await fetch(`${API_BASE_URL}/generate_fir`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          contact,
          description,
          witness_name: witnessName,
          witness_contact: witnessContact,
        }),
      });

      const data: FIRResponse = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Failed to generate FIR");
      }

      setResult(data);
      setActiveTab("fir");

      // Scroll to results
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An error occurred. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  // Copy FIR to clipboard
  const handleCopyFIR = async () => {
    if (result?.fir_text) {
      try {
        await navigator.clipboard.writeText(result.fir_text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch {
        setError("Failed to copy to clipboard");
      }
    }
  };

  // Print FIR
  const handlePrint = () => {
    if (result?.fir_text) {
      const printWindow = window.open("", "_blank");
      if (printWindow) {
        printWindow.document.write(`
          <html>
            <head>
              <title>FIR - ${result.fir_id}</title>
              <style>
                body { font-family: monospace; white-space: pre-wrap; padding: 20px; }
              </style>
            </head>
            <body>${result.fir_text}</body>
          </html>
        `);
        printWindow.document.close();
        printWindow.print();
      }
    }
  };

  // Clear form
  const handleClearForm = () => {
    setName("");
    setContact("");
    setDescription("");
    setWitnessName("");
    setWitnessContact("");
    setResult(null);
    setError("");
    setCopied(false);
    setRealtimeAnalysis(null);
    setShowWitness(false);
  };

  return (
    <main className="min-h-screen py-8 px-4 bg-gradient-to-b from-background via-background to-muted/30">
      <div className="max-w-2xl mx-auto">
        <Header apiStatus={apiStatus} />

        <ComplaintForm
          name={name}
          setName={setName}
          contact={contact}
          setContact={setContact}
          description={description}
          onDescriptionChange={handleDescriptionChange}
          witnessName={witnessName}
          setWitnessName={setWitnessName}
          witnessContact={witnessContact}
          setWitnessContact={setWitnessContact}
          showWitness={showWitness}
          setShowWitness={setShowWitness}
          realtimeAnalysis={realtimeAnalysis}
          loading={loading}
          apiStatus={apiStatus}
          onSubmit={handleSubmit}
          onClear={handleClearForm}
        />

        {error && <ErrorMessage error={error} />}

        {result && (
          <div ref={resultRef} className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <ResultSummary result={result} />

            <ResultTabs
              result={result}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              copied={copied}
              onCopy={handleCopyFIR}
              onPrint={handlePrint}
            />

            {/* New FIR Button */}
            <div className="text-center">
              <Button
                variant="outline"
                onClick={handleClearForm}
                className="px-8 py-5 h-auto rounded-xl border-2 hover:bg-primary/5 hover:border-primary/30 hover:text-primary transition-all"
              >
                <span className="flex items-center gap-2">
                  <span>➕</span>
                  Generate New FIR
                </span>
              </Button>
            </div>
          </div>
        )}

        <Footer />
      </div>
    </main>
  );
}
