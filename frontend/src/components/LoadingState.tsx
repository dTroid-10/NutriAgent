export function LoadingSpinner({ size = 20 }: { size?: number }) {
  return (
    <svg
      className="animate-spin text-primary-500"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        className="opacity-25"
        cx="12" cy="12" r="10"
        stroke="currentColor" strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  )
}

export function SkeletonCard() {
  return (
    <div className="card">
      <div className="shimmer h-4 rounded-lg w-1/3 mb-3" />
      <div className="shimmer h-8 rounded-lg w-1/2 mb-2" />
      <div className="shimmer h-3 rounded-lg w-2/3" />
    </div>
  )
}

export function EmptyState({ message, icon }: { message: string; icon?: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {icon && <div className="text-gray-300 mb-3">{icon}</div>}
      <p className="text-gray-500 text-sm">{message}</p>
    </div>
  )
}
