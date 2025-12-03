"use client";

import { FIRResponse } from "./types";

interface EntitiesTabProps {
  result: FIRResponse;
}

export function EntitiesTab({ result }: EntitiesTabProps) {
  const hasEntities =
    result.extracted_persons?.length ||
    result.extracted_entities?.locations?.length ||
    result.extracted_phone_numbers?.length ||
    result.extracted_emails?.length ||
    result.extracted_aadhar?.length ||
    result.extracted_vehicle_numbers?.length ||
    result.extracted_pan_numbers?.length ||
    result.extracted_entities?.organizations?.length ||
    result.extracted_entities?.money?.length;

  return (
    <div className="space-y-4">
      {/* Persons */}
      {result.extracted_persons?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Persons Mentioned
          </p>
          <div className="flex flex-wrap gap-2">
            {result.extracted_persons.map((person, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-chart-1/10 text-chart-1 text-sm rounded-md border border-chart-1/20"
              >
                {person}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Locations */}
      {result.extracted_entities?.locations?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Locations
          </p>
          <div className="flex flex-wrap gap-2">
            {result.extracted_entities.locations.map((loc, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-chart-2/10 text-chart-2 text-sm rounded-md border border-chart-2/20"
              >
                {loc}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Dates & Times */}
      {(result.extracted_entities?.dates?.length > 0 ||
        result.extracted_entities?.times?.length > 0) && (
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Dates & Times
          </p>
          <div className="flex flex-wrap gap-2">
            {result.extracted_entities.dates?.map((date, idx) => (
              <span
                key={`date-${idx}`}
                className="px-2.5 py-1 bg-chart-3/10 text-chart-3 text-sm rounded-md border border-chart-3/20"
              >
                {date}
              </span>
            ))}
            {result.extracted_entities.times?.map((time, idx) => (
              <span
                key={`time-${idx}`}
                className="px-2.5 py-1 bg-chart-3/10 text-chart-3 text-sm rounded-md border border-chart-3/20"
              >
                {time}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Phone Numbers */}
      {result.extracted_phone_numbers?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Phone Numbers
          </p>
          <div className="flex flex-wrap gap-2">
            {result.extracted_phone_numbers.map((phone, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-chart-4/10 text-chart-4 text-sm rounded-md border border-chart-4/20 font-mono"
              >
                {phone}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Emails */}
      {result.extracted_emails?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Email Addresses
          </p>
          <div className="flex flex-wrap gap-2">
            {result.extracted_emails.map((email, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-accent text-accent-foreground text-sm rounded-md border border-border font-mono"
              >
                {email}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Aadhaar Numbers */}
      {result.extracted_aadhar?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Aadhaar Numbers
          </p>
          <div className="flex flex-wrap gap-2">
            {result.extracted_aadhar.map((aadhar, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-chart-5/10 text-chart-5 text-sm rounded-md border border-chart-5/20 font-mono"
              >
                {aadhar}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Vehicle Numbers */}
      {result.extracted_vehicle_numbers?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Vehicle Numbers
          </p>
          <div className="flex flex-wrap gap-2">
            {result.extracted_vehicle_numbers.map((vehicle, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-primary/10 text-primary text-sm rounded-md border border-primary/20 font-mono"
              >
                🚗 {vehicle}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* PAN Numbers */}
      {result.extracted_pan_numbers?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            PAN Numbers
          </p>
          <div className="flex flex-wrap gap-2">
            {result.extracted_pan_numbers.map((pan, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-chart-4/10 text-chart-4 text-sm rounded-md border border-chart-4/20 font-mono"
              >
                {pan}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Organizations */}
      {result.extracted_entities?.organizations?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Organizations
          </p>
          <div className="flex flex-wrap gap-2">
            {result.extracted_entities.organizations.map((org, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-chart-5/10 text-chart-5 text-sm rounded-md border border-chart-5/20"
              >
                {org}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Money */}
      {result.extracted_entities?.money?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Monetary Amounts
          </p>
          <div className="flex flex-wrap gap-2">
            {result.extracted_entities.money.map((amount, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-primary/10 text-primary text-sm rounded-md border border-primary/20"
              >
                ₹{amount}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!hasEntities && (
        <div className="text-center py-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
            <span className="text-2xl opacity-50">🏷️</span>
          </div>
          <p className="text-sm text-muted-foreground">
            No specific entities were extracted from the description.
          </p>
        </div>
      )}
    </div>
  );
}
