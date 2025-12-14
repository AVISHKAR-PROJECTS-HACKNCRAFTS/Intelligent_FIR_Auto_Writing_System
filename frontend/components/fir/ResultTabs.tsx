"use client";

import { FIRResponse, TabType } from "./types";
import { FIRDocumentTab } from "./FIRDocumentTab";
import { EntitiesTab } from "./EntitiesTab";
import { LegalSectionsTab } from "./LegalSectionsTab";

interface ResultTabsProps {
  result: FIRResponse;
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  copied: boolean;
  onCopy: () => void;
  onPrint: () => void;
}

export function ResultTabs({
  result,
  activeTab,
  setActiveTab,
  copied,
  onCopy,
  onPrint,
}: ResultTabsProps) {
  return (
    <div className="bg-card rounded-xl border border-border shadow-sm">
      {/* Tab Headers */}
      <div className="flex border-b border-border overflow-x-auto bg-muted/30">
        <button
          onClick={() => setActiveTab("fir")}
          className={`flex-1 px-4 py-3.5 text-sm font-medium transition-all whitespace-nowrap flex items-center justify-center gap-2 ${
            activeTab === "fir"
              ? "text-primary border-b-2 border-primary bg-background"
              : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
          }`}
        >
          <span className={activeTab === "fir" ? "" : "opacity-60"}>📄</span>
          FIR Document
        </button>
        <button
          onClick={() => setActiveTab("entities")}
          className={`flex-1 px-4 py-3.5 text-sm font-medium transition-all whitespace-nowrap flex items-center justify-center gap-2 ${
            activeTab === "entities"
              ? "text-chart-1 border-b-2 border-chart-1 bg-background"
              : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
          }`}
        >
          <span className={activeTab === "entities" ? "" : "opacity-60"}>🏷️</span>
          Extracted
        </button>
        <button
          onClick={() => setActiveTab("legal")}
          className={`flex-1 px-4 py-3.5 text-sm font-medium transition-all whitespace-nowrap flex items-center justify-center gap-2 ${
            activeTab === "legal"
              ? "text-chart-5 border-b-2 border-chart-5 bg-background"
              : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
          }`}
        >
          <span className={activeTab === "legal" ? "" : "opacity-60"}>⚖️</span>
          Legal
        </button>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === "fir" && (
          <FIRDocumentTab result={result} copied={copied} onCopy={onCopy} onPrint={onPrint} />
        )}
        {activeTab === "entities" && <EntitiesTab result={result} />}
        {activeTab === "legal" && <LegalSectionsTab result={result} />}
      </div>
    </div>
  );
}
