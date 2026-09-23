import { useState, useRef } from 'react'
import { logMeal, type MealLog } from '../api'
import toast from 'react-hot-toast'
import { LoadingSpinner, EmptyState } from '../components/LoadingState'
import { Type, Camera, Mic, Check, Upload } from 'lucide-react'
import clsx from 'clsx'

type Tab = 'text' | 'photo' | 'voice'

const MEAL_TYPES = ['breakfast', 'lunch', 'dinner', 'snack', 'meal']

export default function LogMeal() {
  const [tab, setTab] = useState<Tab>('text')
  const [mealType, setMealType] = useState('meal')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<MealLog | null>(null)

  // Text tab
  const [textInput, setTextInput] = useState('')

  // Photo tab
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Voice tab
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const recognitionRef = useRef<any>(null)

  function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setImageFile(file)
    setImagePreview(URL.createObjectURL(file))
  }

  function startVoice() {
    const SpeechRecognitionAPI =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognitionAPI) {
      toast.error('Speech recognition is not supported in this browser')
      return
    }
    const rec = new SpeechRecognitionAPI()
    rec.continuous = false
    rec.interimResults = true
    rec.lang = 'en-US'

    rec.onresult = (e: any) => {
      const text = Array.from(e.results as any[])
        .map((r: any) => r[0].transcript)
        .join('')
      setTranscript(text)
    }
    rec.onend = () => setIsListening(false)
    rec.onerror = () => {
      setIsListening(false)
      toast.error('Voice recognition error')
    }

    rec.start()
    recognitionRef.current = rec
    setIsListening(true)
  }

  function stopVoice() {
    recognitionRef.current?.stop()
    setIsListening(false)
  }

  async function handleSubmit() {
    const fd = new FormData()
    fd.append('meal_type', mealType)

    if (tab === 'text') {
      if (!textInput.trim()) { toast.error('Please describe your meal'); return }
      fd.append('input_text', textInput)
    } else if (tab === 'photo') {
      if (!imageFile) { toast.error('Please select an image'); return }
      fd.append('image', imageFile)
      if (textInput.trim()) fd.append('input_text', textInput)
    } else {
      if (!transcript.trim()) { toast.error('Please record your meal description'); return }
      fd.append('input_text', transcript)
    }

    setLoading(true)
    try {
      const log = await logMeal(fd)
      setResult(log)
      toast.success('Meal logged!')
      setTextInput('')
      setTranscript('')
      setImageFile(null)
      setImagePreview(null)
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to log meal')
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'text' as Tab, icon: Type, label: 'Text' },
    { id: 'photo' as Tab, icon: Camera, label: 'Photo' },
    { id: 'voice' as Tab, icon: Mic, label: 'Voice' },
  ]

  return (
    <div className="space-y-4 max-w-xl">
      <h1 className="text-xl font-bold text-gray-800">Log a Meal</h1>

      {/* Meal type */}
      <div>
        <label className="label">Meal Type</label>
        <div className="flex gap-2 flex-wrap">
          {MEAL_TYPES.map(t => (
            <button
              key={t}
              onClick={() => setMealType(t)}
              className={`px-3 py-1.5 rounded-lg text-sm capitalize transition-colors ${
                mealType === t
                  ? 'bg-primary-100 text-primary-700 font-medium'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="flex border-b border-gray-100 mb-4">
          {tabs.map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              onClick={() => { setTab(id); setResult(null) }}
              className={clsx(
                'flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px',
                tab === id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              )}
            >
              <Icon size={15} />
              {label}
            </button>
          ))}
        </div>

        {/* Text tab */}
        {tab === 'text' && (
          <div className="space-y-3">
            <label className="label">Describe your meal</label>
            <textarea
              className="input min-h-[120px] resize-none"
              placeholder="e.g. I had a bowl of dal tadka with 2 rotis and some raita for lunch"
              value={textInput}
              onChange={e => setTextInput(e.target.value)}
            />
          </div>
        )}

        {/* Photo tab */}
        {tab === 'photo' && (
          <div className="space-y-3">
            <div
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                imagePreview ? 'border-primary-300' : 'border-gray-200 hover:border-primary-300'
              }`}
            >
              {imagePreview ? (
                <img src={imagePreview} alt="Food preview" className="max-h-48 mx-auto rounded-xl object-cover" />
              ) : (
                <div className="text-gray-400">
                  <Upload size={32} className="mx-auto mb-2" />
                  <p className="text-sm">Click to upload a food photo</p>
                  <p className="text-xs mt-1">JPG, PNG up to 10MB</p>
                </div>
              )}
              <input
                type="file" ref={fileInputRef} className="hidden"
                accept="image/*" onChange={handleImageChange}
              />
            </div>
            {imagePreview && (
              <div>
                <label className="label">Add description (optional)</label>
                <input
                  type="text" className="input"
                  placeholder="e.g. Chicken biryani with raita"
                  value={textInput} onChange={e => setTextInput(e.target.value)}
                />
              </div>
            )}
          </div>
        )}

        {/* Voice tab */}
        {tab === 'voice' && (
          <div className="space-y-4 text-center">
            <div
              className={`w-24 h-24 rounded-full mx-auto flex items-center justify-center cursor-pointer transition-all ${
                isListening
                  ? 'bg-red-100 ring-4 ring-red-200 animate-pulse'
                  : 'bg-primary-100 hover:bg-primary-200'
              }`}
              onClick={isListening ? stopVoice : startVoice}
            >
              <Mic size={36} className={isListening ? 'text-red-500' : 'text-primary-600'} />
            </div>
            <p className="text-sm text-gray-500">
              {isListening ? 'Listening... tap to stop' : 'Tap mic to start speaking'}
            </p>
            {transcript && (
              <div className="text-left">
                <label className="label">Transcript</label>
                <div className="input min-h-[80px] bg-gray-50 text-gray-700 whitespace-pre-wrap">
                  {transcript}
                </div>
                <button
                  onClick={() => setTranscript('')}
                  className="text-xs text-gray-400 hover:text-gray-600 mt-1"
                >
                  Clear
                </button>
              </div>
            )}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn-primary w-full mt-4 flex items-center justify-center gap-2"
        >
          {loading ? <LoadingSpinner size={16} /> : <Check size={16} />}
          {loading ? 'Analyzing...' : 'Log This Meal'}
        </button>
      </div>

      {/* Result */}
      {result && (
        <div className="card border-primary-200 bg-primary-50">
          <div className="flex items-center gap-2 mb-3">
            <Check size={16} className="text-primary-600" />
            <h3 className="font-semibold text-primary-800">Meal Logged!</h3>
          </div>

          {/* Totals */}
          <div className="grid grid-cols-4 gap-2 mb-3">
            {[
              { label: 'Calories', value: Math.round(result.calories), unit: 'kcal' },
              { label: 'Protein', value: Math.round(result.protein_g), unit: 'g' },
              { label: 'Carbs', value: Math.round(result.carbs_g), unit: 'g' },
              { label: 'Fat', value: Math.round(result.fat_g), unit: 'g' },
            ].map(m => (
              <div key={m.label} className="bg-white rounded-xl p-2 text-center">
                <p className="text-xs text-gray-500">{m.label}</p>
                <p className="font-bold text-gray-800 text-sm">{m.value}<span className="text-xs font-normal">{m.unit}</span></p>
              </div>
            ))}
          </div>

          {/* Recognized foods */}
          {result.recognized_foods.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-medium text-gray-600 mb-1">Identified Items:</p>
              <div className="space-y-1">
                {result.recognized_foods.map((f, i) => (
                  <div key={i} className="flex justify-between text-xs bg-white rounded-lg px-3 py-1.5">
                    <span className="text-gray-700">{f.name} ({f.quantity_g}g)</span>
                    <span className="text-gray-500">{Math.round(f.calories)} kcal</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.feedback && (
            <p className="text-xs text-primary-800 whitespace-pre-line">{result.feedback}</p>
          )}
        </div>
      )}
    </div>
  )
}
