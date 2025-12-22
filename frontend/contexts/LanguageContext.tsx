"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

type Language = "en" | "te";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  // Initialize with saved language or default to "en"
  const [language, setLanguage] = useState<Language>(() => {
    if (typeof window !== "undefined") {
      const savedLanguage = localStorage.getItem("language") as Language;
      if (savedLanguage && (savedLanguage === "en" || savedLanguage === "te")) {
        return savedLanguage;
      }
    }
    return "en";
  });

  // Save language preference to localStorage
  const handleSetLanguage = (lang: Language) => {
    setLanguage(lang);
    if (typeof window !== "undefined") {
      localStorage.setItem("language", lang);
    }
  };

  // Translation function
  const t = (key: string): string => {
    const keys = key.split(".");
    let value: Record<string, unknown> | string = translations[language];
    
    for (const k of keys) {
      if (value && typeof value === "object" && k in value) {
        value = value[k] as Record<string, unknown> | string;
      } else {
        return key; // Return key if translation not found
      }
    }
    
    return typeof value === "string" ? value : key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage: handleSetLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}

// Translations
const translations = {
  en: {
    header: {
      title: "FIR Generator",
      subtitle: "AI-powered First Information Report generation system",
      online: "Online",
      offline: "Offline",
    },
    form: {
      title: "Complaint Details",
      name: "Complainant Name",
      namePlaceholder: "Enter full name",
      contact: "Contact Number",
      contactPlaceholder: "Enter phone number",
      description: "Complaint Description",
      descriptionPlaceholder: "Describe the incident in detail. Include:\n• Date and time of incident\n• Location where it occurred\n• Names of people involved\n• What happened step by step\n• Any witnesses or evidence",
      witnessName: "Witness Name",
      witnessNamePlaceholder: "Enter witness name",
      witnessContact: "Witness Contact",
      witnessContactPlaceholder: "Enter witness contact",
      addWitness: "Add Witness Information",
      removeWitness: "Remove Witness",
      analyzing: "Analyzing...",
      generateFIR: "Generate FIR",
      clear: "Clear",
    },
    analysis: {
      confidence: "Confidence",
      high: "High",
      medium: "Medium",
      low: "Low",
      severity: "Severity",
      crimeType: "Crime Type",
      detectedEntities: "Detected Entities",
      analyzing: "Analyzing your complaint...",
    },
    results: {
      title: "Generated Report",
      copyToClipboard: "Copy",
      copied: "Copied!",
      tabs: {
        fir: "FIR Document",
        entities: "Entities",
        legalSections: "Legal Sections",
      },
    },
    footer: {
      madeWith: "Made with",
      by: "by",
      disclaimer: "This is an AI-powered tool for educational purposes. Always consult with legal authorities for official FIR filing.",
    },
    error: {
      title: "Error",
      tryAgain: "Please try again or contact support if the issue persists.",
    },
  },
  te: {
    header: {
      title: "ఎఫ్‌ఐఆర్ జనరేటర్",
      subtitle: "కృత్రిమ మేధస్సు ఆధారిత మొదటి సమాచార నివేదిక ఉత్పత్తి వ్యవస్థ",
      online: "ఆన్‌లైన్",
      offline: "ఆఫ్‌లైన్",
    },
    form: {
      title: "ఫిర్యాదు వివరాలు",
      name: "ఫిర్యాదుదారు పేరు",
      namePlaceholder: "పూర్తి పేరు నమోదు చేయండి",
      contact: "సంప్రదింపు నంబర్",
      contactPlaceholder: "ఫోన్ నంబర్ నమోదు చేయండి",
      description: "ఫిర్యాదు వివరణ",
      descriptionPlaceholder: "సంఘటన గురించి వివరంగా వివరించండి. చేర్చండి:\n• సంఘటన తేదీ మరియు సమయం\n• ఇది జరిగిన స్థలం\n• పాల్గొన్న వ్యక్తుల పేర్లు\n• దశల వారీగా ఏమి జరిగింది\n• ఏదైనా సాక్షులు లేదా సాక్ష్యం",
      witnessName: "సాక్షి పేరు",
      witnessNamePlaceholder: "సాక్షి పేరు నమోదు చేయండి",
      witnessContact: "సాక్షి సంప్రదింపు",
      witnessContactPlaceholder: "సాక్షి సంప్రదింపు నమోదు చేయండి",
      addWitness: "సాక్షి సమాచారం జోడించండి",
      removeWitness: "సాక్షిని తొలగించు",
      analyzing: "విశ్లేషిస్తోంది...",
      generateFIR: "ఎఫ్‌ఐఆర్ రూపొందించండి",
      clear: "క్లియర్",
    },
    analysis: {
      confidence: "నమ్మకం",
      high: "అధికం",
      medium: "మధ్యస్థం",
      low: "తక్కువ",
      severity: "తీవ్రత",
      crimeType: "నేర రకం",
      detectedEntities: "గుర్తించబడిన సంస్థలు",
      analyzing: "మీ ఫిర్యాదును విశ్లేషిస్తోంది...",
    },
    results: {
      title: "రూపొందించిన నివేదిక",
      copyToClipboard: "కాపీ",
      copied: "కాపీ చేయబడింది!",
      tabs: {
        fir: "ఎఫ్‌ఐఆర్ పత్రం",
        entities: "సంస్థలు",
        legalSections: "చట్టపరమైన విభాగాలు",
      },
    },
    footer: {
      madeWith: "తయారు చేయబడింది",
      by: "ద్వారా",
      disclaimer: "ఇది విద్యా ప్రయోజనాల కోసం కృత్రిమ మేధస్సు ఆధారిత సాధనం. అధికారిక ఎఫ్‌ఐఆర్ దాఖలు కోసం ఎల్లప్పుడూ చట్టపరమైన అధికారులతో సంప్రదించండి.",
    },
    error: {
      title: "లోపం",
      tryAgain: "దయచేసి మళ్లీ ప్రయత్నించండి లేదా సమస్య కొనసాగితే మద్దతుని సంప్రదించండి.",
    },
  },
};
