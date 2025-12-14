"use client";

import { FIRResponse } from "./types";
import { getConfidenceColor, getOffenceIcon } from "./utils";

interface ResultSummaryProps {
  result: FIRResponse;
}

export function ResultSummary({ result }: ResultSummaryProps) {
  return (
    <div className="bg-card rounded-xl border border-border shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-chart-2 to-chart-1 flex items-center justify-center shadow-sm">
            <span className="text-white text-lg">✓</span>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-foreground">Analysis Complete</h2>
            <p className="text-xs text-muted-foreground">
              Processed in {result.processing_time_seconds?.toFixed(2) || "N/A"}s
            </p>
          </div>
        </div>
      </div>

      {/* Offence Classification */}
      <div className="mb-4 p-4 rounded-xl bg-gradient-to-br from-muted to-muted/50 border border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
              <span className="text-2xl">{getOffenceIcon(result.offence_type)}</span>
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wide">
                Detected Offence
              </p>
              <p className="text-xl font-bold text-foreground mt-0.5">{result.offence_type}</p>
            </div>
          </div>
          <div
            className={`px-4 py-2 rounded-xl border text-sm font-semibold ${getConfidenceColor(
              result.confidence_level
            )}`}
          >
            {(result.confidence * 100).toFixed(0)}%
          </div>
        </div>

        {/* Confidence Breakdown */}
        {result.all_offence_scores && (
          <div className="mt-4 pt-4 border-t border-border">
            <p className="text-xs text-muted-foreground mb-2">Classification Scores</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {Object.entries(result.all_offence_scores)
                .sort(([, a], [, b]) => b - a)
                .map(([offence, score]) => (
                  <div key={offence} className="text-xs">
                    <div className="flex justify-between text-muted-foreground">
                      <span>{offence}</span>
                      <span className="font-medium">{(score * 100).toFixed(0)}%</span>
                    </div>
                    <div className="mt-1 h-1.5 bg-secondary rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full"
                        style={{ width: `${score * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>

      {/* Quick Info Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
        <div className="p-3 bg-chart-3/5 rounded-xl border border-chart-3/10 hover:border-chart-3/20 transition-colors">
          <p className="text-chart-3 text-xs font-medium flex items-center gap-1">
            <span>📅</span> Date
          </p>
          <p className="text-foreground font-semibold mt-1">{result.date}</p>
        </div>
        <div className="p-3 bg-chart-4/5 rounded-xl border border-chart-4/10 hover:border-chart-4/20 transition-colors">
          <p className="text-chart-4 text-xs font-medium flex items-center gap-1">
            <span>🕐</span> Time
          </p>
          <p className="text-foreground font-semibold mt-1">{result.time}</p>
        </div>
        <div className="p-3 bg-chart-2/5 rounded-xl border border-chart-2/10 hover:border-chart-2/20 transition-colors">
          <p className="text-chart-2 text-xs font-medium flex items-center gap-1">
            <span>📍</span> Location
          </p>
          <p className="text-foreground font-semibold mt-1">{result.location}</p>
        </div>
        <div className="p-3 bg-chart-1/5 rounded-xl border border-chart-1/10 hover:border-chart-1/20 transition-colors">
          <p className="text-chart-1 text-xs font-medium flex items-center gap-1">
            <span>👥</span> Persons
          </p>
          <p className="text-foreground font-semibold mt-1">
            {result.extracted_persons?.length || 0} found
          </p>
        </div>
      </div>
    </div>
  );
}
