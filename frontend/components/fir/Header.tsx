"use client";

import { ApiStatus } from "./types";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { useLanguage } from "@/contexts/LanguageContext";

interface HeaderProps {
  apiStatus: ApiStatus;
}

export function Header({ apiStatus }: HeaderProps) {
  const { t } = useLanguage();

  return (
    <div className="mb-8">
      <div className="flex justify-end mb-4">
        <LanguageSwitcher />
      </div>
      <div className="text-center">
        <div className="inline-flex items-center gap-3 mb-3 px-4 py-2 rounded-full bg-primary/5 border border-primary/10">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-chart-1 flex items-center justify-center">
            <span className="text-primary-foreground text-sm font-bold">FIR</span>
          </div>
          <h1 className="text-2xl font-semibold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
            {t("header.title")}
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
            {apiStatus === "online" ? t("header.online") : apiStatus === "offline" ? t("header.offline") : "..."}
          </span>
        </div>
        <p className="text-sm text-muted-foreground">
          {t("header.subtitle")}
        </p>
      </div>
    </div>
  );
}
