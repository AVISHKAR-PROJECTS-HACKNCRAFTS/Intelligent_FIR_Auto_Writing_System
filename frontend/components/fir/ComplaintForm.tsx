"use client";

import { RealtimeAnalysis } from "./types";
import { getConfidenceColor } from "./utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface ComplaintFormProps {
  name: string;
  setName: (value: string) => void;
  contact: string;
  setContact: (value: string) => void;
  description: string;
  onDescriptionChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  witnessName: string;
  setWitnessName: (value: string) => void;
  witnessContact: string;
  setWitnessContact: (value: string) => void;
  showWitness: boolean;
  setShowWitness: (value: boolean) => void;
  realtimeAnalysis: RealtimeAnalysis | null;
  loading: boolean;
  apiStatus: "checking" | "online" | "offline";
  onSubmit: (e: React.FormEvent) => void;
  onClear: () => void;
}

export function ComplaintForm({
  name,
  setName,
  contact,
  setContact,
  description,
  onDescriptionChange,
  witnessName,
  setWitnessName,
  witnessContact,
  setWitnessContact,
  showWitness,
  setShowWitness,
  realtimeAnalysis,
  loading,
  apiStatus,
  onSubmit,
  onClear,
}: ComplaintFormProps) {
  return (
    <div className="bg-card rounded-xl border border-border shadow-sm hover:shadow-md transition-shadow p-6 mb-6">
      <div className="flex items-center gap-2 mb-5 pb-4 border-b border-border">
        <div className="w-6 h-6 rounded-md bg-chart-1/10 flex items-center justify-center">
          <span className="text-chart-1 text-xs">📝</span>
        </div>
        <h2 className="text-sm font-medium text-foreground">Complaint Details</h2>
      </div>
      <form onSubmit={onSubmit} className="space-y-5">
        {/* Name and Contact */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-foreground flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-chart-1"></span>
              Complainant Name
            </Label>
            <Input
              id="name"
              type="text"
              placeholder="Enter full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="focus-visible:ring-chart-1"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="contact" className="text-foreground flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-chart-2"></span>
              Contact Number
            </Label>
            <Input
              id="contact"
              type="tel"
              placeholder="Enter phone number"
              value={contact}
              onChange={(e) => setContact(e.target.value)}
              required
              className="focus-visible:ring-chart-2"
            />
          </div>
        </div>

        {/* Description */}
        <div className="space-y-2">
          <Label htmlFor="description" className="text-foreground flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-chart-3"></span>
            Complaint Description
          </Label>
          <Textarea
            id="description"
            placeholder="Describe the incident in detail. Include:&#10;• Date and time of incident&#10;• Location where it occurred&#10;• Names of people involved&#10;• What happened step by step&#10;• Any witnesses or evidence"
            value={description}
            onChange={onDescriptionChange}
            required
            rows={8}
            className="resize-none focus-visible:ring-chart-3"
          />
          <div className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">{description.length} characters</p>
            {description.length > 50 && (
              <span className="text-xs text-chart-2 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-chart-2 animate-pulse"></span>
                Analyzing...
              </span>
            )}
          </div>
        </div>

        {/* Real-time Analysis */}
        {realtimeAnalysis && (
          <div className="p-4 bg-gradient-to-br from-primary/5 to-chart-1/5 rounded-xl border border-primary/10 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-md bg-primary/10 flex items-center justify-center">
                  <span className="text-xs">⚡</span>
                </div>
                <p className="text-xs font-semibold text-primary uppercase tracking-wide">
                  Live Analysis
                </p>
              </div>
              {realtimeAnalysis.offence_type && (
                <span
                  className={`px-3 py-1 rounded-lg text-xs font-semibold border ${getConfidenceColor(
                    realtimeAnalysis.confidence_level
                  )}`}
                >
                  {realtimeAnalysis.offence_type} • {(realtimeAnalysis.confidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {realtimeAnalysis.preview.persons.map((p, i) => (
                <span
                  key={`p-${i}`}
                  className="px-2.5 py-1 bg-chart-1/15 text-chart-1 text-xs rounded-lg border border-chart-1/20 font-medium"
                >
                  👤 {p}
                </span>
              ))}
              {realtimeAnalysis.preview.locations.map((l, i) => (
                <span
                  key={`l-${i}`}
                  className="px-2.5 py-1 bg-chart-2/15 text-chart-2 text-xs rounded-lg border border-chart-2/20 font-medium"
                >
                  📍 {l}
                </span>
              ))}
              {realtimeAnalysis.preview.organizations && realtimeAnalysis.preview.organizations.map((o, i) => (
                <span
                  key={`o-${i}`}
                  className="px-2.5 py-1 bg-chart-3/15 text-chart-3 text-xs rounded-lg border border-chart-3/20 font-medium"
                >
                  🏢 {o}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Witness Toggle */}
        <div>
          <button
            type="button"
            onClick={() => setShowWitness(!showWitness)}
            className="text-sm text-chart-5 hover:text-chart-5/80 font-medium flex items-center gap-2 px-3 py-2 rounded-lg bg-chart-5/5 border border-chart-5/10 hover:border-chart-5/20 transition-all"
          >
            <span className="w-4 h-4 rounded-full bg-chart-5/10 flex items-center justify-center text-xs">
              {showWitness ? "−" : "+"}
            </span>
            {showWitness ? "Hide witness details" : "Add witness details (optional)"}
          </button>
        </div>

        {/* Witness Fields */}
        {showWitness && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 bg-gradient-to-br from-chart-5/5 to-muted rounded-xl border border-chart-5/10">
            <div className="space-y-2">
              <Label htmlFor="witnessName" className="text-foreground flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-chart-5"></span>
                Witness Name
              </Label>
              <Input
                id="witnessName"
                type="text"
                placeholder="Enter witness name"
                value={witnessName}
                onChange={(e) => setWitnessName(e.target.value)}
                className="focus-visible:ring-chart-5"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="witnessContact" className="text-foreground flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-chart-5"></span>
                Witness Contact
              </Label>
              <Input
                id="witnessContact"
                type="tel"
                placeholder="Enter witness phone"
                value={witnessContact}
                onChange={(e) => setWitnessContact(e.target.value)}
                className="focus-visible:ring-chart-5"
              />
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 pt-2">
          <Button
            type="submit"
            disabled={loading || !description.trim() || apiStatus === "offline"}
            className="flex-1 bg-gradient-to-r from-primary to-chart-1 hover:from-primary/90 hover:to-chart-1/90 text-primary-foreground shadow-md hover:shadow-lg transition-all"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></span>
                Analyzing...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <span>✨</span>
                Generate FIR
              </span>
            )}
          </Button>
          {(name || contact || description) && (
            <Button
              type="button"
              variant="outline"
              onClick={onClear}
              className="px-4 hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20"
            >
              Clear
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
