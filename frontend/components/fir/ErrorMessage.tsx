"use client";

interface ErrorMessageProps {
  error: string;
}

export function ErrorMessage({ error }: ErrorMessageProps) {
  return (
    <div className="bg-destructive/10 rounded-xl border border-destructive/20 p-4 mb-6 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-destructive/20 flex items-center justify-center shrink-0">
          <span className="text-destructive">⚠</span>
        </div>
        <div>
          <p className="text-destructive text-sm font-semibold">Error Occurred</p>
          <p className="text-destructive/80 text-sm mt-1">{error}</p>
        </div>
      </div>
    </div>
  );
}
