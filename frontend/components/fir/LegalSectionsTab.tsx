"use client";

import { FIRResponse } from "./types";

interface LegalSectionsTabProps {
  result: FIRResponse;
}

export function LegalSectionsTab({ result }: LegalSectionsTabProps) {
  return (
    <div>
      {result.ipc_sections?.length > 0 ? (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-3 bg-chart-5/5 rounded-xl border border-chart-5/10">
            <div className="w-10 h-10 rounded-xl bg-chart-5/10 flex items-center justify-center">
              <span className="text-lg">⚖️</span>
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Applicable Legal Sections</p>
              <p className="text-xs text-muted-foreground">
                Based on detected offence:{" "}
                <span className="text-chart-5 font-medium">{result.offence_type}</span>
              </p>
            </div>
          </div>
          <div className="space-y-3">
            {result.ipc_sections.map((section, idx) => (
              <div
                key={idx}
                className="flex items-start gap-4 p-4 bg-gradient-to-r from-muted to-muted/50 rounded-xl border border-border hover:border-chart-5/20 transition-colors"
              >
                <span className="px-3 py-1.5 bg-gradient-to-br from-chart-5 to-primary text-white text-sm font-bold rounded-lg shadow-sm">
                  §{section.section}
                </span>
                <p className="text-sm text-foreground leading-relaxed">{section.description}</p>
              </div>
            ))}
          </div>
          <div className="flex items-start gap-2 p-3 bg-chart-4/5 rounded-lg border border-chart-4/10 text-xs text-chart-4">
            <span>⚠️</span>
            <p>
              These are AI-suggested sections. Final determination should be made by legal
              authorities.
            </p>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
            <span className="text-2xl opacity-50">⚖️</span>
          </div>
          <p className="text-sm text-muted-foreground">No applicable legal sections identified.</p>
        </div>
      )}
    </div>
  );
}
