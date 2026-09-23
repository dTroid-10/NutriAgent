import api from './client'

// --- Auth ---

export interface AuthResponse {
  access_token: string
  token_type: string
  user_id: number
  name: string
}

export async function register(email: string, password: string, name: string): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>('/auth/register', { email, password, name })
  return data
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const params = new URLSearchParams()
  params.append('username', email)
  params.append('password', password)
  const { data } = await api.post<AuthResponse>('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

// --- Profile ---

export interface Profile {
  id: number
  user_id: number
  age: number | null
  sex: string | null
  weight_kg: number | null
  height_cm: number | null
  health_conditions: string[]
  allergies: string[]
  dietary_preference: string
  fitness_goal: string
  activity_level: string
}

export async function getProfile(): Promise<Profile> {
  const { data } = await api.get<Profile>('/profile')
  return data
}

export async function updateProfile(profile: Partial<Profile>): Promise<Profile> {
  const { data } = await api.put<Profile>('/profile', profile)
  return data
}

// --- Diet Plan ---

export interface MealItem {
  food: string
  quantity_g: number
  calories: number
}

export interface DayPlan {
  day: string
  breakfast: MealItem[]
  lunch: MealItem[]
  dinner: MealItem[]
  snacks: MealItem[]
}

export interface DietPlan {
  id: number
  plan_data: {
    days: DayPlan[]
    calorie_target?: number
    protein_target_g?: number
    carbs_target_g?: number
    fat_target_g?: number
  }
  calorie_target: number
  protein_target_g: number
  carbs_target_g: number
  fat_target_g: number
  created_at: string
}

export async function generateDietPlan(): Promise<DietPlan> {
  const { data } = await api.post<DietPlan>('/diet-plan/generate')
  return data
}

export async function getCurrentDietPlan(): Promise<DietPlan> {
  const { data } = await api.get<DietPlan>('/diet-plan/current')
  return data
}

// --- Meal Log ---

export interface RecognizedFood {
  name: string
  quantity_g: number
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g: number
}

export interface MealLog {
  id: number
  meal_type: string
  input_text: string | null
  recognized_foods: RecognizedFood[]
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g: number
  feedback: string | null
  logged_at: string
}

export async function logMeal(formData: FormData): Promise<MealLog> {
  const { data } = await api.post<MealLog>('/meal-log', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function getMealHistory(limit = 30): Promise<MealLog[]> {
  const { data } = await api.get<MealLog[]>(`/meal-log/history?limit=${limit}`)
  return data
}

// --- Dashboard ---

export interface WeeklyTrend {
  date: string
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

export interface DashboardSummary {
  today_calories: number
  today_protein_g: number
  today_carbs_g: number
  today_fat_g: number
  calorie_target: number
  protein_target_g: number
  carbs_target_g: number
  fat_target_g: number
  weekly_trend: WeeklyTrend[]
  deficiency_alerts: string[]
  streak_days: number
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await api.get<DashboardSummary>('/dashboard/summary')
  return data
}

// --- Chat ---

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  citations?: string[]
  agent_used?: string
}

export interface ChatResponse {
  response: string
  citations: string[]
  agent_used: string
}

export async function sendChat(message: string, intent = 'general'): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>('/chat', { message, intent })
  return data
}

// --- Food Search ---

export interface FoodSearchResult {
  name: string
  calories_per_100g: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g: number
  cuisine: string
}

export async function searchFood(q: string): Promise<FoodSearchResult[]> {
  const { data } = await api.get<FoodSearchResult[]>(`/food/search?q=${encodeURIComponent(q)}`)
  return data
}
