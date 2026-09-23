import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { updateProfile, generateDietPlan } from '../api'
import toast from 'react-hot-toast'
import { LoadingSpinner } from '../components/LoadingState'
import { ChevronRight, ChevronLeft, Leaf } from 'lucide-react'

const HEALTH_CONDITIONS = [
  'Diabetes', 'Hypertension', 'Heart Disease', 'Kidney Disease',
  'Obesity', 'High Cholesterol', 'Thyroid', 'PCOS', 'Arthritis', 'Anemia'
]

const DIETARY_PREFS = [
  { value: 'none', label: 'No Restriction' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'vegan', label: 'Vegan' },
  { value: 'halal', label: 'Halal' },
  { value: 'kosher', label: 'Kosher' },
  { value: 'pescatarian', label: 'Pescatarian' },
  { value: 'gluten_free', label: 'Gluten-Free' },
]

const FITNESS_GOALS = [
  { value: 'lose', label: '🔥 Lose Weight' },
  { value: 'maintain', label: '⚖️ Maintain Weight' },
  { value: 'gain', label: '📈 Gain Weight' },
  { value: 'muscle', label: '💪 Build Muscle' },
  { value: 'disease_management', label: '🏥 Disease Management' },
]

const ACTIVITY_LEVELS = [
  { value: 'sedentary', label: 'Sedentary', desc: 'Little to no exercise' },
  { value: 'light', label: 'Light', desc: '1-3 days/week' },
  { value: 'moderate', label: 'Moderate', desc: '3-5 days/week' },
  { value: 'active', label: 'Active', desc: '6-7 days/week' },
  { value: 'very_active', label: 'Very Active', desc: 'Physical job + training' },
]

const STEPS = ['Basic Info', 'Health', 'Preferences', 'Goals']

export default function Onboarding() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [saving, setSaving] = useState(false)
  const [allergyInput, setAllergyInput] = useState('')

  const [form, setForm] = useState({
    age: '',
    sex: 'male',
    weight_kg: '',
    height_cm: '',
    health_conditions: [] as string[],
    allergies: [] as string[],
    dietary_preference: 'none',
    fitness_goal: 'maintain',
    activity_level: 'moderate',
  })

  function toggleCondition(c: string) {
    setForm(f => ({
      ...f,
      health_conditions: f.health_conditions.includes(c)
        ? f.health_conditions.filter(x => x !== c)
        : [...f.health_conditions, c],
    }))
  }

  function addAllergen() {
    const val = allergyInput.trim()
    if (val && !form.allergies.includes(val)) {
      setForm(f => ({ ...f, allergies: [...f.allergies, val] }))
      setAllergyInput('')
    }
  }

  function removeAllergen(a: string) {
    setForm(f => ({ ...f, allergies: f.allergies.filter(x => x !== a) }))
  }

  async function handleFinish() {
    setSaving(true)
    try {
      await updateProfile({
        age: form.age ? Number(form.age) : undefined,
        sex: form.sex,
        weight_kg: form.weight_kg ? Number(form.weight_kg) : undefined,
        height_cm: form.height_cm ? Number(form.height_cm) : undefined,
        health_conditions: form.health_conditions,
        allergies: form.allergies,
        dietary_preference: form.dietary_preference,
        fitness_goal: form.fitness_goal,
        activity_level: form.activity_level,
      } as any)
      toast.success('Profile saved! Generating your diet plan...')
      // Auto-generate diet plan
      try {
        await generateDietPlan()
      } catch { /* plan gen non-critical */ }
      navigate('/')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  const stepContent = [
    // Step 0: Basic Info
    <div key="basic" className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800">Tell us about yourself</h2>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Age</label>
          <input
            type="number" min="10" max="120"
            className="input" placeholder="e.g. 28"
            value={form.age} onChange={e => setForm(f => ({ ...f, age: e.target.value }))}
          />
        </div>
        <div>
          <label className="label">Sex</label>
          <select className="input" value={form.sex} onChange={e => setForm(f => ({ ...f, sex: e.target.value }))}>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label className="label">Weight (kg)</label>
          <input
            type="number" min="20" max="300" step="0.1"
            className="input" placeholder="e.g. 70"
            value={form.weight_kg} onChange={e => setForm(f => ({ ...f, weight_kg: e.target.value }))}
          />
        </div>
        <div>
          <label className="label">Height (cm)</label>
          <input
            type="number" min="100" max="250"
            className="input" placeholder="e.g. 170"
            value={form.height_cm} onChange={e => setForm(f => ({ ...f, height_cm: e.target.value }))}
          />
        </div>
      </div>
    </div>,

    // Step 1: Health conditions + allergies
    <div key="health" className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-1">Health Conditions</h2>
        <p className="text-sm text-gray-500 mb-3">Select any that apply (optional)</p>
        <div className="flex flex-wrap gap-2">
          {HEALTH_CONDITIONS.map(c => (
            <button
              key={c}
              type="button"
              onClick={() => toggleCondition(c)}
              className={`badge cursor-pointer transition-colors ${
                form.health_conditions.includes(c)
                  ? 'bg-primary-100 text-primary-700 ring-1 ring-primary-400'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>
      <div>
        <h2 className="text-lg font-bold text-gray-800 mb-1">Allergies & Intolerances</h2>
        <p className="text-sm text-gray-500 mb-2">We'll never recommend these foods</p>
        <div className="flex gap-2">
          <input
            className="input flex-1"
            placeholder="Type an allergen (e.g. peanuts)"
            value={allergyInput}
            onChange={e => setAllergyInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addAllergen()}
          />
          <button type="button" onClick={addAllergen} className="btn-primary">Add</button>
        </div>
        {form.allergies.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {form.allergies.map(a => (
              <span key={a} className="badge bg-red-50 text-red-700">
                {a}
                <button onClick={() => removeAllergen(a)} className="ml-1.5 hover:text-red-900">×</button>
              </span>
            ))}
          </div>
        )}
      </div>
    </div>,

    // Step 2: Dietary preferences
    <div key="prefs" className="space-y-3">
      <h2 className="text-xl font-bold text-gray-800">Dietary Preference</h2>
      <div className="grid grid-cols-2 gap-2">
        {DIETARY_PREFS.map(p => (
          <button
            key={p.value}
            type="button"
            onClick={() => setForm(f => ({ ...f, dietary_preference: p.value }))}
            className={`px-4 py-3 rounded-xl text-sm font-medium border transition-colors text-left ${
              form.dietary_preference === p.value
                ? 'border-primary-400 bg-primary-50 text-primary-700'
                : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>
    </div>,

    // Step 3: Goals + activity
    <div key="goals" className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-3">Fitness Goal</h2>
        <div className="space-y-2">
          {FITNESS_GOALS.map(g => (
            <button
              key={g.value}
              type="button"
              onClick={() => setForm(f => ({ ...f, fitness_goal: g.value }))}
              className={`w-full px-4 py-3 rounded-xl text-sm font-medium border transition-colors text-left ${
                form.fitness_goal === g.value
                  ? 'border-primary-400 bg-primary-50 text-primary-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              {g.label}
            </button>
          ))}
        </div>
      </div>
      <div>
        <h2 className="text-lg font-bold text-gray-800 mb-2">Activity Level</h2>
        <div className="space-y-2">
          {ACTIVITY_LEVELS.map(a => (
            <button
              key={a.value}
              type="button"
              onClick={() => setForm(f => ({ ...f, activity_level: a.value }))}
              className={`w-full px-4 py-3 rounded-xl text-sm border transition-colors text-left ${
                form.activity_level === a.value
                  ? 'border-primary-400 bg-primary-50 text-primary-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="font-medium">{a.label}</span>
              <span className="text-gray-400 ml-2 text-xs">{a.desc}</span>
            </button>
          ))}
        </div>
      </div>
    </div>,
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-soft w-full max-w-md">
        {/* Header */}
        <div className="flex items-center gap-2 px-6 pt-6 pb-4 border-b border-gray-100">
          <div className="w-7 h-7 bg-primary-500 rounded-lg flex items-center justify-center">
            <Leaf size={15} className="text-white" />
          </div>
          <span className="font-bold text-gray-800">NutriAgent Setup</span>
        </div>

        {/* Step indicator */}
        <div className="flex gap-1 px-6 py-3">
          {STEPS.map((s, i) => (
            <div key={i} className="flex-1">
              <div className={`h-1 rounded-full transition-colors ${i <= step ? 'bg-primary-500' : 'bg-gray-100'}`} />
              <p className={`text-xs mt-1 text-center ${i === step ? 'text-primary-600 font-medium' : 'text-gray-400'}`}>
                {s}
              </p>
            </div>
          ))}
        </div>

        {/* Content */}
        <div className="px-6 py-4 min-h-[300px]">
          {stepContent[step]}
        </div>

        {/* Navigation */}
        <div className="flex justify-between px-6 pb-6 pt-2">
          {step > 0 ? (
            <button
              type="button"
              onClick={() => setStep(s => s - 1)}
              className="btn-secondary flex items-center gap-1"
            >
              <ChevronLeft size={16} /> Back
            </button>
          ) : <div />}

          {step < STEPS.length - 1 ? (
            <button
              type="button"
              onClick={() => setStep(s => s + 1)}
              className="btn-primary flex items-center gap-1"
            >
              Next <ChevronRight size={16} />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleFinish}
              disabled={saving}
              className="btn-primary flex items-center gap-2"
            >
              {saving ? <LoadingSpinner size={16} /> : null}
              {saving ? 'Saving...' : 'Finish Setup'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
