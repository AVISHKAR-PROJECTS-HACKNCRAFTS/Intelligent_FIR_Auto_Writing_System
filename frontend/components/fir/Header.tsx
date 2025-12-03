"use client";

import { ApiStatus } from "./types";

interface HeaderProps {
  apiStatus: ApiStatus;
}

export function Header({ apiStatus }: HeaderProps) {
  return (
    <div className="text-center mb-8">
      <div className="inline-flex items-center gap-3 mb-3 px-4 py-2 rounded-full bg-primary/5 border border-primary/10">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-chart-1 flex items-center justify-center">
          <span className="text-primary-foreground text-sm font-bold">FIR</span>
        </div>
        <h1 className="text-2xl font-semibold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
          FIR Generator
        </h1>
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            apiStatus === "online"
              ? "bg-chart-2/10 text-chart-2 border-chart-2/20"
              : apiStatus === "offline"
              ? "bg-destructive/10 text-destructive border-destructive/20"
              : "bg-muted text-muted-foreground border-border"
          }`}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              apiStatus === "online"
                ? "bg-chart-2 animate-pulse"
                : apiStatus === "offline"
                ? "bg-destructive"
                : "bg-muted-foreground animate-pulse"
            }`}
          />
          {apiStatus === "online" ? "Online" : apiStatus === "offline" ? "Offline" : "..."}
        </span>
      </div>
      <p className="text-sm text-muted-foreground">
        AI-powered First Information Report generation system
      </p>
    </div>
  );
}
