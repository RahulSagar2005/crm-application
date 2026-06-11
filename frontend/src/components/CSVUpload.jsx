import { useCallback, useState } from 'react'
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { uploadCustomersCSV } from '../api/customers'
import { Button } from './ui/button'
import { cn } from '../lib/utils'

export default function CSVUpload({ onSuccess }) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleUpload = useCallback(async (file) => {
    if (!file || !file.name.endsWith('.csv')) {
      setError('Please upload a CSV file')
      return
    }
    setUploading(true)
    setError(null)
    setResult(null)
    setProgress(0)
    try {
      const data = await uploadCustomersCSV(file, setProgress)
      setResult(data)
      onSuccess?.()
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }, [onSuccess])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    handleUpload(file)
  }, [handleUpload])

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={cn(
          'relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition-colors',
          dragging ? 'border-primary bg-primary/5' : 'border-gray-300 hover:border-primary/50',
          uploading && 'pointer-events-none opacity-60'
        )}
      >
        <Upload className="h-10 w-10 text-gray-400 mb-3" />
        <p className="text-sm font-medium text-gray-700">Drag & drop CSV file here</p>
        <p className="text-xs text-gray-400 mt-1">or click to browse</p>
        <input
          type="file"
          accept=".csv"
          className="absolute inset-0 cursor-pointer opacity-0"
          onChange={(e) => handleUpload(e.target.files[0])}
          disabled={uploading}
        />
        {uploading && (
          <div className="mt-4 w-full max-w-xs">
            <div className="h-2 rounded-full bg-gray-200">
              <div
                className="h-2 rounded-full bg-primary transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1 text-center">{progress}%</p>
          </div>
        )}
      </div>

      {result && (
        <div className="flex items-start gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-700">
          <CheckCircle className="h-4 w-4 mt-0.5 shrink-0" />
          <div>
            <p>Upload complete: {result.created} created, {result.skipped} skipped</p>
            {result.errors?.length > 0 && (
              <p className="text-xs mt-1">{result.errors.length} errors</p>
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      <div className="flex items-center gap-2 text-xs text-gray-400">
        <FileText className="h-3 w-3" />
        Expected columns: name, email, phone, city, product_name, amount, channel
      </div>
    </div>
  )
}
