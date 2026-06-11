import { X } from 'lucide-react'
import { cn } from '../../lib/utils'

export function Dialog({ open, onClose, children }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative z-50 w-full max-w-lg rounded-xl bg-white p-6 shadow-xl mx-4">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 transition-opacity"
        >
          <X className="h-4 w-4" />
        </button>
        {children}
      </div>
    </div>
  )
}

export function DialogTitle({ className, children }) {
  return <h2 className={cn('text-lg font-semibold text-gray-900', className)}>{children}</h2>
}
