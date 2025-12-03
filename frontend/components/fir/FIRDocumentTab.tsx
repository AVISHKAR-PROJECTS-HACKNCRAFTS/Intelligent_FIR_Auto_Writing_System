"use client";

import { FIRResponse } from "./types";
import { Button } from "@/components/ui/button";
import { jsPDF } from "jspdf";

interface FIRDocumentTabProps {
  result: FIRResponse;
  copied: boolean;
  onCopy: () => void;
  onPrint: () => void;
}

export function FIRDocumentTab({ result, copied, onCopy, onPrint }: FIRDocumentTabProps) {
  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 20;
    const contentWidth = pageWidth - margin * 2;
    let yPos = margin;

    const addText = (
      text: string,
      fontSize: number,
      isBold: boolean = false,
      align: "left" | "center" = "left"
    ) => {
      doc.setFontSize(fontSize);
      doc.setFont("helvetica", isBold ? "bold" : "normal");
      const lines = doc.splitTextToSize(text, contentWidth);

      lines.forEach((line: string) => {
        if (yPos > pageHeight - margin) {
          doc.addPage();
          yPos = margin;
        }
        if (align === "center") {
          doc.text(line, pageWidth / 2, yPos, { align: "center" });
        } else {
          doc.text(line, margin, yPos);
        }
        yPos += fontSize * 0.5;
      });
    };

    const addLine = () => {
      yPos += 2;
      doc.setDrawColor(0, 0, 0);
      doc.line(margin, yPos, pageWidth - margin, yPos);
      yPos += 5;
    };

    // Header - Plain black and white
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(18);
    doc.setFont("helvetica", "bold");
    doc.text("FIRST INFORMATION REPORT (FIR)", pageWidth / 2, 15, { align: "center" });
    doc.setDrawColor(0, 0, 0);
    doc.line(margin, 20, pageWidth - margin, 20);
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.text(`FIR ID: ${result.fir_id}`, pageWidth / 2, 28, { align: "center" });
    doc.text(`Generated: ${new Date().toLocaleString()}`, pageWidth / 2, 34, { align: "center" });
    doc.line(margin, 38, pageWidth - margin, 38);

    yPos = 48;

    // Section A: Complainant Details
    addText("SECTION A: COMPLAINANT DETAILS", 11, true);
    addLine();
    addText(`Name: ${result.name}`, 10);
    addText(`Contact: ${result.contact}`, 10);
    if (result.witness_name) {
      addText(`Witness: ${result.witness_name} (${result.witness_contact || "N/A"})`, 10);
    }
    yPos += 5;

    // Section B: Incident Details
    addText("SECTION B: INCIDENT DETAILS", 11, true);
    addLine();
    addText(`Date: ${result.date}`, 10);
    addText(`Time: ${result.time}`, 10);
    addText(`Location: ${result.location}`, 10);
    yPos += 5;

    // Section C: Classification
    addText("SECTION C: OFFENCE CLASSIFICATION", 11, true);
    addLine();
    addText(`Type: ${result.offence_type}`, 10);
    addText(`Confidence: ${(result.confidence * 100).toFixed(1)}% (${result.confidence_level})`, 10);
    addText(`Severity: ${result.severity_level} (Score: ${result.severity_score}/100)`, 10);
    yPos += 5;

    // Section D: Extracted Information
    addText("SECTION D: EXTRACTED INFORMATION", 11, true);
    addLine();
    if (result.extracted_persons?.length > 0) {
      addText(`Persons Mentioned: ${result.extracted_persons.join(", ")}`, 10);
    }
    if (result.extracted_entities?.locations?.length > 0) {
      addText(`Locations: ${result.extracted_entities.locations.join(", ")}`, 10);
    }
    if (result.extracted_phone_numbers?.length > 0) {
      addText(`Phone Numbers: ${result.extracted_phone_numbers.join(", ")}`, 10);
    }
    if (result.extracted_emails?.length > 0) {
      addText(`Emails: ${result.extracted_emails.join(", ")}`, 10);
    }
    if (result.extracted_aadhar?.length > 0) {
      addText(`Aadhaar Numbers: ${result.extracted_aadhar.join(", ")}`, 10);
    }
    if (result.extracted_vehicle_numbers?.length > 0) {
      addText(`Vehicle Numbers: ${result.extracted_vehicle_numbers.join(", ")}`, 10);
    }
    if (result.extracted_pan_numbers?.length > 0) {
      addText(`PAN Numbers: ${result.extracted_pan_numbers.join(", ")}`, 10);
    }
    yPos += 5;

    // Section E: Legal Sections
    if (result.ipc_sections?.length > 0) {
      addText("SECTION E: APPLICABLE LEGAL SECTIONS", 11, true);
      addLine();
      result.ipc_sections.forEach((section) => {
        addText(`Section ${section.section}: ${section.description}`, 10);
      });
      yPos += 5;
    }

    // Section F: Severity Factors
    if (result.severity_factors?.length > 0) {
      addText("SECTION F: SEVERITY FACTORS", 11, true);
      addLine();
      result.severity_factors.forEach((factor, idx) => {
        addText(`${idx + 1}. ${factor}`, 10);
      });
      yPos += 5;
    }

    // Section G: Full FIR Document
    addText("SECTION G: FIR DOCUMENT", 11, true);
    addLine();
    yPos += 5;

    doc.setFontSize(9);
    doc.setFont("courier", "normal");
    const firLines = doc.splitTextToSize(result.fir_text, contentWidth);
    firLines.forEach((line: string) => {
      if (yPos > pageHeight - margin - 15) {
        doc.addPage();
        yPos = margin;
      }
      doc.text(line, margin, yPos);
      yPos += 4;
    });

    // Footer
    yPos = pageHeight - 25;
    addLine();
    doc.setFontSize(8);
    doc.setFont("helvetica", "italic");
    doc.setTextColor(0, 0, 0);
    doc.text(
      "This document was generated by the Intelligent FIR Auto Writing System.",
      pageWidth / 2,
      yPos,
      { align: "center" }
    );
    doc.text(
      "AI-generated content should be verified by legal authorities.",
      pageWidth / 2,
      yPos + 4,
      { align: "center" }
    );
    doc.text(
      `Processing Time: ${result.processing_time_seconds?.toFixed(3)}s`,
      pageWidth / 2,
      yPos + 8,
      { align: "center" }
    );

    const fileName = `FIR_${result.fir_id}_${result.name.replace(/\s+/g, "_")}.pdf`;
    doc.save(fileName);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 bg-primary/10 text-primary text-xs font-mono rounded-md border border-primary/20">
            {result.fir_id}
          </span>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onCopy}
            className={`text-xs transition-all ${
              copied
                ? "bg-chart-2/10 text-chart-2 border-chart-2/20"
                : "hover:bg-chart-1/5 hover:text-chart-1 hover:border-chart-1/20"
            }`}
          >
            {copied ? "✓ Copied!" : "📋 Copy"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadPDF}
            className="text-xs hover:bg-destructive/5 hover:text-destructive hover:border-destructive/20"
          >
            📄 PDF
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onPrint}
            className="text-xs hover:bg-chart-3/5 hover:text-chart-3 hover:border-chart-3/20"
          >
            🖨 Print
          </Button>
        </div>
      </div>
      <div className="border border-border rounded-xl overflow-hidden">
        <div className="bg-muted/50 px-4 py-2 border-b border-border flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-destructive"></span>
          <span className="w-2 h-2 rounded-full bg-chart-4"></span>
          <span className="w-2 h-2 rounded-full bg-chart-2"></span>
          <span className="ml-2 text-xs text-muted-foreground">FIR Document</span>
        </div>
        <pre className="p-4 text-xs text-foreground font-mono whitespace-pre-wrap overflow-x-auto max-h-[500px] overflow-y-auto bg-card">
          {result.fir_text}
        </pre>
      </div>
    </div>
  );
}
