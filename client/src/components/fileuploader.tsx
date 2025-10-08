"use client";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Upload, FileText, X } from "lucide-react";

export default function FileUploader({ onFileUpload }: { onFileUpload: (file: File) => void }) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onloadend = () => setPreview(reader.result as string);
        reader.readAsDataURL(file);
      } else setPreview(null);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setPreview(null);
  };

  const handleSubmit = () => selectedFile && onFileUpload(selectedFile);

  return (
    <div className="w-full max-w-md space-y-5">
      {/* Upload area */}
      <div className="grid gap-2">
        <Label htmlFor="file" className="text-sm font-medium tracking-wide text-black">
          Upload document
        </Label>
        <label
          htmlFor="file"
          className="group relative flex h-32 cursor-pointer items-center justify-center rounded-xl border-2 border-dashed border-neutral-300 bg-white transition hover:border-black"
        >
          <div className="pointer-events-none flex flex-col items-center gap-2">
            <Upload className="h-5 w-5 text-neutral-500 transition group-hover:text-black" />
            <span className="text-xs text-neutral-500 transition group-hover:text-black">PDF, DOC, TXT</span>
          </div>
          <Input
            id="file"
            type="file"
            className="absolute inset-0 h-full w-full opacity-0"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleFileChange}
          />
        </label>
      </div>

      {/* Selected file card */}
      {selectedFile && (
        <div className="rounded-xl border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="h-5 w-5 text-black" />
              <span className="text-sm font-medium text-black">{selectedFile.name}</span>
            </div>
            <Button variant="ghost" size="icon-sm" onClick={handleRemove}>
              <X className="h-4 w-4 text-neutral-500 hover:text-black" />
            </Button>
          </div>

          {preview && (
            <img
              src={preview}
              alt=""
              className="mt-4 max-h-48 w-full rounded-lg object-cover"
            />
          )}

          <Button
            onClick={handleSubmit}
            className="mt-4 w-full rounded-lg bg-black text-white hover:bg-neutral-800"
          >
            Continue
          </Button>
        </div>
      )}
    </div>
  );
}