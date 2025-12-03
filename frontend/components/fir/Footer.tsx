"use client";

export function Footer() {
  return (
    <div className="text-center mt-12 pb-4">
      <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-muted/50 border border-border">
        <div className="w-2 h-2 rounded-full bg-gradient-to-r from-primary to-chart-1 animate-pulse"></div>
        <p className="text-xs text-muted-foreground font-medium">
          Intelligent FIR Auto Writing System
        </p>
      </div>
    </div>
  );
}
