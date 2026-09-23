import { useEffect, useState } from 'react'
import { getProfile, updateProfile, type Profile } from '../api'
import toast from 'react-hot-toast'
import { SkeletonCard } from '../components/LoadingState'
import { LoadingSpinner } from '../components/LoadingState'
import { Save, User } from 'lucide-react'

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
  { value: 'lose', label: 'Lose Weight' },
  { value: 'maintain', label: 'Maintain Weight' },
  { value: 'gain', label: 'Gain Weight' },
  { value: 'muscle', label: 'Build Muscle' },
  { value: 'disease_management', label: 'Disease Management' },
]

export default function ProfilePage() {
  const [profile, setProfile] = useState<Partial<Profile> | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [allergyInput, setAllergyInput] = useState('')
  const user = JSON.parse(localStorage.getItem('nutriagent_user') || '{}')

  useEffect(() => {
    getProfile()
      .then(p => setProfile(p))
      .catch(() => setProfile({}))
      .finally(() => setLoading(false))
  }, [])

  function toggleCondition(c: string) {
    setProfile(p => ({
      ...p,
      health_conditions: (p?.health_conditions || []).includes(c)
        ? (p?.health_conditions || []).filter(x => x !== c)
        : [...(p?.health_conditions || []), c],
    }))
  }

  function addAllergen() {
    const val = allergyInput.trim()
    if (val && !(profile?.allergies || []).includes(val)) {
      setProfile(p => ({ ...p, allergies: [...(p?.allergies || []), val] }))
      setAllergyInput('')
    }
  }

  function removeAllergen(a: string) {
    setProfile(p => ({ ...p, allergies: (p?.allergies || []).filter(x => x !== a) }))
  }

  async function handleSave() {
    if (!profile) return
    setSaving(true)
    try {
      const updated = await updateProfile(profile)
      setProfile(updated)
      toast.success('Profile updated!')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="space-y-4">{[1,2,3].map(i => <SkeletonCard key={i} />)}</div>

  return (
    <div className="space-y-5 max-w-xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-800">My Profile</h1>
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary flex items-center gap-2 text-sm"
        >
          {saving ? <LoadingSpinner size={14} /> : <Save size={14} />}
          Save Changes
        </button>
      </div>

      {/* Account info */}
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-primary-100 rounded-2xl flex items-center justify-center">
            <User size={22} className="text-primary-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-800">{user.name}</p>
            <p className="text-sm text-gray-400">Account ID: {user.id}</p>
          </div>
        </div>
      </div>

      {/* Body stats */}
      <div className="card space-y-4">
        <h2 className="font-semibold text-gray-700">Body Stats</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Age</label>
            <input
              type="number" className="input" placeholder="e.g. 28"
              value={profile?.age || ''}
              onChange={e => setProfile(p => ({ ...p, age: Number(e.target.value) }))}
            />
          </div>
          <div>
            <label className="label">Sex</label>
            <select
              className="input"
              value={profile?.sex || 'male'}
              onChange={e => setProfile(p => ({ ...p, sex: e.target.value }))}
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="label">Weight (kg)</label>
            <input
              type="number" className="input" placeholder="e.g. 70" step="0.1"
              value={profile?.weight_kg || ''}
              onChange={e => setProfile(p => ({ ...p, weight_kg: Number(e.target.value) }))}
            />
          </div>
          <div>
            <label className="label">Height (cm)</label>
            <input
              type="number" className="input" placeholder="e.g. 170"
              value={profile?.height_cm || ''}
              onChange={e => setProfile(p => ({ ...p, height_cm: Number(e.target.value) }))}
            />
          </div>
        </div>
      </div>

      {/* Health conditions */}
      <div className="card space-y-3">
        <h2 className="font-semibold text-gray-700">Health Conditions</h2>
        <div className="flex flex-wrap gap-2">
          {HEALTH_CONDITIONS.map(c => (
            <button
              key={c} type="button"
              onClick={() => toggleCondition(c)}
              className={`badge cursor-pointer transition-colors ${
                (profile?.health_conditions || []).includes(c)
                  ? 'bg-primary-100 text-primary-700 ring-1 ring-primary-400'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Allergies */}
      <div className="card space-y-3">
        <h2 className="font-semibold text-gray-700">Allergies</h2>
        <div className="flex gap-2">
          <input
            className="input flex-1"
            placeholder="Add allergen"
            value={allergyInput}
            onChange={e => setAllergyInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addAllergen()}
          />
          <button onClick={addAllergen} className="btn-primary">Add</button>
        </div>
        <div className="flex flex-wrap gap-2">
          {(profile?.allergies || []).map(a => (
            <span key={a} className="badge bg-red-50 text-red-700">
              {a}
              <button onClick={() => removeAllergen(a)} className="ml-1.5">×</button>
            </span>
          ))}
        </div>
      </div>

      {/* Dietary preference */}
      <div className="card space-y-3">
        <h2 className="font-semibold text-gray-700">Dietary Preference</h2>
        <div className="grid grid-cols-2 gap-2">
          {DIETARY_PREFS.map(p => (
            <button
              key={p.value} type="button"
              onClick={() => setProfile(pr => ({ ...pr, dietary_preference: p.value }))}
              className={`px-3 py-2 rounded-xl text-sm font-medium border text-left transition-colors ${
                profile?.dietary_preference === p.value
                  ? 'border-primary-400 bg-primary-50 text-primary-700'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Fitness goal */}
      <div className="card space-y-3">
        <h2 className="font-semibold text-gray-700">Fitness Goal</h2>
        <div className="space-y-2">
          {FITNESS_GOALS.map(g => (
            <button
              key={g.value} type="button"
              onClick={() => setProfile(p => ({ ...p, fitness_goal: g.value }))}
              className={`w-full px-4 py-2.5 rounded-xl text-sm border text-left transition-colors ${
                profile?.fitness_goal === g.value
                  ? 'border-primary-400 bg-primary-50 text-primary-700 font-medium'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300'
              }`}
            >
              {g.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
