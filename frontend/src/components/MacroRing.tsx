import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

interface MacroRingProps {
  label: string
  value: number
  target: number
  color: string
  unit?: string
}

export function MacroRing({ label, value, target, color, unit = 'g' }: MacroRingProps) {
  const pct = target > 0 ? Math.min((value / target) * 100, 100) : 0
  const remaining = 100 - pct
  const data = [
    { value: pct },
    { value: remaining },
  ]

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-24 h-24">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={32}
              outerRadius={44}
              startAngle={90}
              endAngle={-270}
              dataKey="value"
              strokeWidth={0}
            >
              <Cell fill={color} />
              <Cell fill="#f3f4f6" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-base font-bold text-gray-800">{Math.round(value)}</span>
          <span className="text-xs text-gray-400">{unit}</span>
        </div>
      </div>
      <p className="text-sm font-medium text-gray-600 mt-1">{label}</p>
      <p className="text-xs text-gray-400">/ {Math.round(target)}{unit}</p>
    </div>
  )
}
