import { useEffect, useState } from 'react'
import { getDashboardSummary, getMealHistory, type DashboardSummary as Summary, type MealLog } from '../api'
import { MacroRing } from '../components/MacroRing'
import { NutrientCard } from '../components/NutrientCard'
import { MealCard } from '../components/MealCard'
import { SkeletonCard, EmptyState } from '../components/LoadingState'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'
import { Flame, TrendingUp, AlertTriangle, Zap } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Dashboard() {
  const navigate = useNavigate()
  const [summary, setSummary] = useState<Summary | null>(null)
  const [logs, setLogs] = useState<MealLog[]>([])
  const [loading, setLoading] = useState(true)
  const user = JSON.parse(localStorage.getItem('nutriagent_user') || '{}')

  useEffect(() => {
    async function load() {
      try {
        const [s, l] = await Promise.all([getDashboardSummary(), getMealHistory(5)])
        setSummary(s)
        setLogs(l)
      } catch (e: any) {
        if (e?.response?.status === 404) {
          // No plan yet, that's OK
        }
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const todayLogs = logs.filter(l => {
    const logDate = new Date(l.logged_at).toDateString()
    return logDate === new Date().toDateString()
  })

  if (loading) {
    return (
      <div className="space-y-4">
        {[1,2,3,4].map(i => <SkeletonCard key={i} />)}
      </div>
    )
  }

  const calorieTarget = summary?.calorie_target || 2000
  const proteinTarget = summary?.protein_target_g || 100
  const carbsTarget = summary?.carbs_target_g || 225
  const fatTarget = summary?.fat_target_g || 55

  return (
    <div className="space-y-5">
      {/* Greeting */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">
            Good {getGreeting()}, {user.name?.split(' ')[0] || 'there'}! 👋
          </h1>
          <p className="text-sm text-gray-500">Here's your nutrition overview</p>
        </div>
        <div className="flex items-center gap-1 bg-amber-50 text-amber-700 px-3 py-1.5 rounded-xl text-sm font-medium">
          <Zap size={14} />
          {summary?.streak_days || 0} day streak
        </div>
      </div>

      {/* Calorie ring + macros */}
      <div className="card">
        <h2 className="font-semibold text-gray-700 mb-4">Today's Progress</h2>
        <div className="flex items-center justify-around flex-wrap gap-4">
          {/* Main calorie ring */}
          <div className="flex flex-col items-center">
            <div className="relative w-32 h-32">
              <svg className="w-32 h-32 -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="52" fill="none" stroke="#f3f4f6" strokeWidth="12" />
                <circle
                  cx="60" cy="60" r="52" fill="none"
                  stroke="#10b981"
                  strokeWidth="12"
                  strokeDasharray={`${Math.PI * 2 * 52}`}
                  strokeDashoffset={`${Math.PI * 2 * 52 * (1 - Math.min((summary?.today_calories || 0) / calorieTarget, 1))}`}
                  strokeLinecap="round"
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <Flame size={16} className="text-primary-500 mb-0.5" />
                <span className="text-xl font-bold text-gray-800">{Math.round(summary?.today_calories || 0)}</span>
                <span className="text-xs text-gray-400">/ {Math.round(calorieTarget)} kcal</span>
              </div>
            </div>
            <p className="text-sm font-medium text-gray-600 mt-1">Calories</p>
          </div>

          <MacroRing label="Protein" value={summary?.today_protein_g || 0} target={proteinTarget} color="#3b82f6" />
          <MacroRing label="Carbs" value={summary?.today_carbs_g || 0} target={carbsTarget} color="#f59e0b" />
          <MacroRing label="Fat" value={summary?.today_fat_g || 0} target={fatTarget} color="#ec4899" />
        </div>
      </div>

      {/* Weekly trend chart */}
      <div className="card">
        <h2 className="font-semibold text-gray-700 mb-3">Weekly Calories Trend</h2>
        {summary?.weekly_trend && summary.weekly_trend.some(d => d.calories > 0) ? (
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={summary.weekly_trend} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis
                dataKey="date"
                tickFormatter={d => new Date(d).toLocaleDateString([], { weekday: 'short' })}
                tick={{ fontSize: 11, fill: '#9ca3af' }}
              />
              <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} width={40} />
              <Tooltip
                formatter={(v: number) => [`${Math.round(v)} kcal`, 'Calories']}
                labelFormatter={d => new Date(d).toLocaleDateString([], { weekday: 'long', month: 'short', day: 'numeric' })}
                contentStyle={{ borderRadius: '12px', border: '1px solid #e5e7eb', fontSize: 12 }}
              />
              <Line
                type="monotone" dataKey="calories" stroke="#10b981"
                strokeWidth={2.5} dot={{ r: 3, fill: '#10b981' }} activeDot={{ r: 5 }}
              />
              {/* Target reference */}
              <Line
                type="monotone" dataKey={() => calorieTarget}
                stroke="#d1fae5" strokeWidth={1.5} strokeDasharray="4 4" dot={false}
                name="Target"
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <EmptyState
            message="Log meals to see your weekly trend"
            icon={<TrendingUp size={32} />}
          />
        )}
      </div>

      {/* Deficiency alerts */}
      {summary?.deficiency_alerts && summary.deficiency_alerts.length > 0 && (
        <div className="space-y-2">
          <h2 className="font-semibold text-gray-700">Nutrient Alerts</h2>
          {summary.deficiency_alerts.map((alert, i) => (
            <div key={i} className="flex items-start gap-2 bg-amber-50 border border-amber-100 rounded-xl p-3">
              <AlertTriangle size={16} className="text-amber-500 shrink-0 mt-0.5" />
              <p className="text-sm text-amber-800">{alert.replace(/^[⚠️\s]+/, '')}</p>
            </div>
          ))}
        </div>
      )}

      {/* Today's meals */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-gray-700">Today's Meals</h2>
          <button
            onClick={() => navigate('/log')}
            className="text-sm text-primary-600 font-medium hover:underline"
          >
            + Log meal
          </button>
        </div>
        {todayLogs.length > 0 ? (
          <div className="space-y-3">
            {todayLogs.map(log => (
              <MealCard
                key={log.id}
                mealType={log.meal_type}
                inputText={log.input_text}
                foods={log.recognized_foods}
                calories={log.calories}
                loggedAt={log.logged_at}
                feedback={log.feedback}
              />
            ))}
          </div>
        ) : (
          <div className="card">
            <EmptyState
              message="No meals logged today. Start tracking to see your nutrition data!"
              icon={<Flame size={32} />}
            />
            <div className="text-center mt-3">
              <button onClick={() => navigate('/log')} className="btn-primary text-sm">
                Log your first meal
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
}
