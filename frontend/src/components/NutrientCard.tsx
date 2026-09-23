interface NutrientCardProps {
  label: string
  value: string | number
  unit?: string
  color?: string
  icon?: React.ReactNode
  subtitle?: string
}

export function NutrientCard({ label, value, unit = '', color = 'text-primary-600', icon, subtitle }: NutrientCardProps) {
  return (
    <div className="card flex items-center gap-4">
      {icon && (
        <div className="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center shrink-0">
          {icon}
        </div>
      )}
      <div className="min-w-0">
        <p className="text-xs text-gray-500 font-medium truncate">{label}</p>
        <p className={`text-2xl font-bold ${color}`}>
          {typeof value === 'number' ? Math.round(value) : value}
          <span className="text-sm font-normal text-gray-500 ml-1">{unit}</span>
        </p>
        {subtitle && <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>}
      </div>
    </div>
  )
}
