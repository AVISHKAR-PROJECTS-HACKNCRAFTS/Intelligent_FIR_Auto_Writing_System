"use client";

import { FIRResponse } from "./types";
import { getSeverityColor } from "./utils";

interface SeverityTabProps {
  result: FIRResponse;
}

export function SeverityTab({ result }: SeverityTabProps) {
  return (
    <div className="space-y-6">
      {/* Severity Score Display */}
      <div className="text-center p-8 bg-gradient-to-br from-muted/50 to-muted rounded-xl border border-border">
        <div className="relative inline-block">
          <div
            className={`w-32 h-32 rounded-full border-8 flex items-center justify-center ${getSeverityColor(
              result.severity_level
            )} shadow-lg`}
          >
            <div className="text-center">
              <span className="text-4xl font-bold">{result.severity_score}</span>
              <span className="text-sm font-medium opacity-70">/100</span>
            </div>
          </div>
          <div
            className={`absolute -top-2 -right-2 w-8 h-8 rounded-full flex items-center justify-center text-lg shadow-md ${
              result.severity_level === "Critical"
                ? "bg-destructive"
                : result.severity_level === "High"
                ? "bg-chart-1"
                : result.severity_level === "Medium"
                ? "bg-chart-4"
                : "bg-chart-2"
            }`}
          >
            {result.severity_level === "Critical"
              ? "🔴"
              : result.severity_level === "High"
              ? "🟠"
              : result.severity_level === "Medium"
              ? "🟡"
              : "🟢"}
          </div>
        </div>
        <p
          className={`mt-4 text-xl font-bold ${
            getSeverityColor(result.severity_level).split(" ")[0]
          }`}
        >
          {result.severity_level} Severity
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          Based on offence type and extracted details
        </p>
      </div>

      {/* Severity Factors */}
      {result.severity_factors?.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-5 h-5 rounded-md bg-chart-4/10 flex items-center justify-center">
              <span className="text-xs">⚠️</span>
            </div>
            <p className="text-xs font-semibold text-chart-4 uppercase tracking-wide">
              Contributing Factors ({result.severity_factors.length})
            </p>
          </div>
          <div className="space-y-2">
            {result.severity_factors.map((factor, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3 p-3 bg-gradient-to-r from-chart-4/5 to-transparent rounded-lg border-l-4 border-chart-4"
              >
                <span className="w-6 h-6 rounded-full bg-chart-4/10 text-chart-4 text-xs flex items-center justify-center font-bold">
                  {idx + 1}
                </span>
                <span className="text-sm text-foreground">{factor}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Severity Scale Legend */}
      <div className="pt-4 border-t border-border">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-4">
          Severity Scale Reference
        </p>
        <div className="grid grid-cols-4 gap-3 text-center text-xs">
          <div
            className={`p-3 rounded-xl border-2 transition-all ${
              result.severity_level === "Low"
                ? "bg-chart-2/20 border-chart-2 scale-105"
                : "bg-chart-2/5 border-chart-2/20"
            }`}
          >
            <div className="text-2xl mb-1">🟢</div>
            <div className="font-bold text-chart-2">0-25</div>
            <div className="text-chart-2/70">Low</div>
          </div>
          <div
            className={`p-3 rounded-xl border-2 transition-all ${
              result.severity_level === "Medium"
                ? "bg-chart-4/20 border-chart-4 scale-105"
                : "bg-chart-4/5 border-chart-4/20"
            }`}
          >
            <div className="text-2xl mb-1">🟡</div>
            <div className="font-bold text-chart-4">26-50</div>
            <div className="text-chart-4/70">Medium</div>
          </div>
          <div
            className={`p-3 rounded-xl border-2 transition-all ${
              result.severity_level === "High"
                ? "bg-chart-1/20 border-chart-1 scale-105"
                : "bg-chart-1/5 border-chart-1/20"
            }`}
          >
            <div className="text-2xl mb-1">🟠</div>
            <div className="font-bold text-chart-1">51-75</div>
            <div className="text-chart-1/70">High</div>
          </div>
          <div
            className={`p-3 rounded-xl border-2 transition-all ${
              result.severity_level === "Critical"
                ? "bg-destructive/20 border-destructive scale-105"
                : "bg-destructive/5 border-destructive/20"
            }`}
          >
            <div className="text-2xl mb-1">🔴</div>
            <div className="font-bold text-destructive">76-100</div>
            <div className="text-destructive/70">Critical</div>
          </div>
        </div>
      </div>
    </div>
  );
}
