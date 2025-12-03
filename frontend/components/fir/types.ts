export interface IPCSection {
  section: string;
  description: string;
}

export interface ExtractedEntities {
  persons: string[];
  locations: string[];
  dates: string[];
  times: string[];
  organizations: string[];
  money: string[];
}

export interface RealtimeAnalysis {
  success: boolean;
  offence_type: string | null;
  confidence: number;
  confidence_level: string;
  entities_count: number;
  preview: {
    persons: string[];
    locations: string[];
    dates: string[];
  };
}

export interface FIRResponse {
  success: boolean;
  fir_id: string;
  name: string;
  contact: string;
  date: string;
  time: string;
  location: string;
  offence_type: string;
  confidence: number;
  confidence_level: string;
  all_offence_scores: Record<string, number>;
  extracted_entities: ExtractedEntities;
  extracted_persons: string[];
  extracted_phone_numbers: string[];
  extracted_emails: string[];
  extracted_aadhar: string[];
  extracted_vehicle_numbers: string[];
  extracted_pan_numbers: string[];
  ipc_sections: IPCSection[];
  fir_text: string;
  processing_time_seconds: number;
  generated_at: string;
  severity_score: number;
  severity_level: string;
  severity_factors: string[];
  witness_name?: string;
  witness_contact?: string;
  error?: string;
}

export type ApiStatus = "checking" | "online" | "offline";
export type TabType = "fir" | "entities" | "legal" | "severity";
