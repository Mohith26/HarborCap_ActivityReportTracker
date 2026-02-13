"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { reportsAPI } from "@/lib/api";
import { formatFileSize } from "@/lib/utils";
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface FileUploadDropzoneProps {
  propertyId: string;
  onUploadComplete: () => void;
}

export default function FileUploadDropzone({ propertyId, onUploadComplete }: FileUploadDropzoneProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<{ success: boolean; message: string } | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      setUploading(true);
      setUploadResult(null);

      try {
        for (const file of acceptedFiles) {
          await reportsAPI.upload(propertyId, file);
        }
        setUploadResult({
          success: true,
          message: `Successfully uploaded ${acceptedFiles.length} file(s). Extraction in progress...`,
        });
        onUploadComplete();
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Upload failed";
        setUploadResult({ success: false, message });
      } finally {
        setUploading(false);
      }
    },
    [propertyId, onUploadComplete]
  );

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel.sheet.macroEnabled.12": [".xlsm"],
      "application/pdf": [".pdf"],
    },
    disabled: uploading,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-blue-500 bg-blue-50"
            : uploading
              ? "border-gray-300 bg-gray-50 cursor-not-allowed"
              : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
        }`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
            <p className="text-gray-600">Uploading and extracting data...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="w-10 h-10 text-gray-400" />
            <p className="text-gray-600">
              {isDragActive
                ? "Drop your activity report here..."
                : "Drag & drop activity reports here, or click to browse"}
            </p>
            <p className="text-xs text-gray-400">Accepts .xlsx, .xlsm, and .pdf files</p>
          </div>
        )}
      </div>

      {acceptedFiles.length > 0 && !uploading && (
        <div className="mt-4 space-y-2">
          {acceptedFiles.map((file) => (
            <div key={file.name} className="flex items-center gap-2 text-sm text-gray-600">
              <FileText size={16} />
              <span>{file.name}</span>
              <span className="text-gray-400">({formatFileSize(file.size)})</span>
            </div>
          ))}
        </div>
      )}

      {uploadResult && (
        <div
          className={`mt-4 p-3 rounded-lg flex items-center gap-2 text-sm ${
            uploadResult.success ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
          }`}
        >
          {uploadResult.success ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          {uploadResult.message}
        </div>
      )}
    </div>
  );
}
