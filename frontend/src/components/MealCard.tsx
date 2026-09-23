import type { RecognizedFood } from '../api'
import { Utensils } from 'lucide-react'

interface MealCardProps {
  mealType: string
  inputText: string | null
  foods: RecognizedFood[]
  calories: number
  loggedAt: string
  feedback?: string | null
}

export function MealCard({ mealType, inputText, foods, calories, loggedAt, feedback }: MealCardProps) {
  const time = new Date(loggedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-50 rounded-lg flex items-center justify-center">
            <Utensils size={15} className="text-primary-600" />
          </div>
          <div>
            <p className="font-semibold text-sm capitalize text-gray-800">{mealType}</p>
            <p className="text-xs text-gray-400">{time}</p>
          </div>
        </div>
        <span className="text-primary-600 font-bold text-sm">{Math.round(calories)} kcal</span>
      </div>

      {inputText && (
        <p className="text-sm text-gray-500 mt-2 italic line-clamp-2">"{inputText}"</p>
      )}

      {foods.length > 0 && (
        <div className="mt-3 space-y-1">
          {foods.map((f, i) => (
            <div key={i} className="flex items-center justify-between text-xs">
              <span className="text-gray-700">{f.name} <span className="text-gray-400">({f.quantity_g}g)</span></span>
              <span className="text-gray-500">{Math.round(f.calories)} kcal</span>
            </div>
          ))}
        </div>
      )}

      {feedback && (
        <p className="text-xs text-primary-700 bg-primary-50 rounded-lg px-3 py-2 mt-3">{feedback}</p>
      )}
    </div>
  )
}
