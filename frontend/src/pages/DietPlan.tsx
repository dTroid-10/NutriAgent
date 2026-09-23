import { useEffect, useState } from 'react'
import { getCurrentDietPlan, generateDietPlan, type DietPlan, type DayPlan } from '../api'
import toast from 'react-hot-toast'
import { SkeletonCard, EmptyState } from '../components/LoadingState'
import { LoadingSpinner } from '../components/LoadingState'
import { RefreshCw, Calendar, Utensils } from 'lucide-react'

const MEAL_LABELS: Record<string, string> = {
  breakfast: '🌅 Breakfast',
  lunch: '☀️ Lunch',
  dinner: '🌙 Dinner',
  snacks: '🍎 Snacks',
}

const MEAL_COLORS: Record<string, string> = {
  breakfast: 'bg-amber-50 border-amber-100',
  lunch: 'bg-blue-50 border-blue-100',
  dinner: 'bg-purple-50 border-purple-100',
  snacks: 'bg-green-50 border-green-100',
}

function DayCard({ day }: { day: DayPlan }) {
  const [expanded, setExpanded] = useState(false)
  const totalCal = ['breakfast', 'lunch', 'dinner', 'snacks'].reduce((sum, mt) => {
    const items = (day as any)[mt] || []
    return sum + items.reduce((s: number, f: any) => s + (f.calories || 0), 0)
  }, 0)

  return (
    <div className="card">
      <button
        className="w-full flex items-center justify-between"
        onClick={() => setExpanded(e => !e)}
      >
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
            <Calendar size={15} className="text-primary-600" />
          </div>
          <div className="text-left">
            <p className="font-semibold text-gray-800">{day.day}</p>
            <p className="text-xs text-gray-400">~{Math.round(totalCal)} kcal</p>
          </div>
        </div>
        <span className="text-gray-400 text-sm">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="mt-4 space-y-3">
          {(['breakfast', 'lunch', 'dinner', 'snacks'] as const).map(mealType => {
            const items = (day as any)[mealType] || []
            if (items.length === 0) return null
            return (
              <div
                key={mealType}
                className={`rounded-xl border p-3 ${MEAL_COLORS[mealType]}`}
              >
                <p className="text-sm font-semibold text-gray-700 mb-2">
                  {MEAL_LABELS[mealType]}
                </p>
                <div className="space-y-1">
                  {items.map((item: any, i: number) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-1.5">
                        <Utensils size={11} className="text-gray-400" />
                        <span className="text-gray-700">{item.food}</span>
                        <span className="text-gray-400 text-xs">({item.quantity_g}g)</span>
                      </div>
                      <span className="text-gray-500 text-xs font-medium">{Math.round(item.calories)} kcal</span>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default function DietPlanPage() {
  const [plan, setPlan] = useState<DietPlan | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    load()
  }, [])

  async function load() {
    setLoading(true)
    try {
      const p = await getCurrentDietPlan()
      setPlan(p)
    } catch (e: any) {
      if (e?.response?.status !== 404) {
        toast.error('Failed to load diet plan')
      }
    } finally {
      setLoading(false)
    }
  }

  async function handleGenerate() {
    setGenerating(true)
    try {
      const p = await generateDietPlan()
      setPlan(p)
      toast.success('Diet plan generated!')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to generate plan. Complete your profile first.')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map(i => <SkeletonCard key={i} />)}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">Weekly Diet Plan</h1>
          {plan && (
            <p className="text-sm text-gray-500">
              Target: {Math.round(plan.calorie_target)} kcal/day
            </p>
          )}
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="btn-primary flex items-center gap-2 text-sm"
        >
          {generating ? <LoadingSpinner size={14} /> : <RefreshCw size={14} />}
          {plan ? 'Regenerate' : 'Generate Plan'}
        </button>
      </div>

      {/* Macro targets */}
      {plan && (
        <div className="card">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Daily Targets</p>
          <div className="grid grid-cols-4 gap-3">
            {[
              { label: 'Calories', value: Math.round(plan.calorie_target), unit: 'kcal', color: 'text-primary-600' },
              { label: 'Protein', value: Math.round(plan.protein_target_g), unit: 'g', color: 'text-blue-600' },
              { label: 'Carbs', value: Math.round(plan.carbs_target_g), unit: 'g', color: 'text-amber-600' },
              { label: 'Fat', value: Math.round(plan.fat_target_g), unit: 'g', color: 'text-pink-600' },
            ].map(m => (
              <div key={m.label} className="text-center">
                <p className={`text-lg font-bold ${m.color}`}>{m.value}<span className="text-xs text-gray-400">{m.unit}</span></p>
                <p className="text-xs text-gray-500">{m.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Days */}
      {plan?.plan_data?.days && plan.plan_data.days.length > 0 ? (
        <div className="space-y-3">
          {plan.plan_data.days.map((day, i) => (
            <DayCard key={i} day={day} />
          ))}
        </div>
      ) : (
        <div className="card">
          <EmptyState
            message="No diet plan yet. Generate one based on your profile!"
            icon={<Calendar size={36} />}
          />
          <div className="text-center mt-4">
            <button onClick={handleGenerate} disabled={generating} className="btn-primary">
              {generating ? 'Generating...' : 'Generate My Plan'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
