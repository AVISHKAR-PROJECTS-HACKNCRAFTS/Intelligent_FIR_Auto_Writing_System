export const API_BASE_URL = "http://localhost:5000";

export const getConfidenceColor = (level: string) => {
  switch (level) {
    case "High":
      return "text-primary bg-primary/10 border-primary/20";
    case "Medium":
      return "text-chart-4 bg-chart-4/10 border-chart-4/20";
    default:
      return "text-destructive bg-destructive/10 border-destructive/20";
  }
};

export const getOffenceIcon = (offenceType: string) => {
  switch (offenceType) {
    case "Theft":
      return "🔓";
    case "Assault":
      return "⚔️";
    case "Cyber Crime":
      return "💻";
    case "Cheating":
      return "🎭";
    case "Harassment":
      return "⚠️";
    default:
      return "📋";
  }
};
