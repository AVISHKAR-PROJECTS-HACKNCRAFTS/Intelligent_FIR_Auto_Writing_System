"use client";

import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import { Languages } from "lucide-react";

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  const toggleLanguage = () => {
    setLanguage(language === "en" ? "te" : "en");
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={toggleLanguage}
      className="flex items-center gap-2 hover:bg-primary/10 transition-colors"
      aria-label="Switch language"
    >
      <Languages className="h-4 w-4" />
      <span className="font-medium">{language === "en" ? "తెలుగు" : "English"}</span>
    </Button>
  );
}
