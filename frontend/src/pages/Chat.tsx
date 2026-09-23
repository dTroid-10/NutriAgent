import { useState, useRef, useEffect } from 'react'
import { sendChat, type ChatMessage } from '../api'
import { ChatBubble } from '../components/ChatBubble'
import { LoadingSpinner } from '../components/LoadingState'
import { Send, MessageCircle, Sparkles } from 'lucide-react'

const SUGGESTED_QUESTIONS = [
  'What are the nutrition facts for lentil soup?',
  'Is quinoa good for diabetes?',
  'How can I increase my protein intake as a vegetarian?',
  'What foods are high in iron?',
  'Is avocado toast a healthy breakfast?',
  'What should I eat to reduce blood pressure?',
]

const INTENT_HINTS: Record<string, string> = {
  'nutrition': 'knowledge',
  'calories': 'knowledge',
  'protein': 'knowledge',
  'carbs': 'knowledge',
  'fat': 'knowledge',
  'fiber': 'knowledge',
  'vitamin': 'knowledge',
  'health': 'advisory',
  'diabetes': 'advisory',
  'blood pressure': 'advisory',
  'heart': 'advisory',
  'deficiency': 'advisory',
}

function detectIntent(message: string): string {
  const lower = message.toLowerCase()
  for (const [keyword, intent] of Object.entries(INTENT_HINTS)) {
    if (lower.includes(keyword)) return intent
  }
  return 'general'
}

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: "Hi! I'm your NutriAgent AI assistant. Ask me anything about nutrition, food, your health goals, or meal planning. I'll give you evidence-based answers from our nutrition knowledge base.",
      citations: [],
      agent_used: 'orchestrator',
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend(messageText?: string) {
    const text = messageText || input.trim()
    if (!text || loading) return

    const userMessage: ChatMessage = { role: 'user', content: text }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const intent = detectIntent(text)
      const res = await sendChat(text, intent)
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: res.response,
          citations: res.citations,
          agent_used: res.agent_used,
        }
      ])
    } catch (e: any) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          citations: [],
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] md:h-[calc(100vh-2rem)] max-w-2xl">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 bg-primary-500 rounded-xl flex items-center justify-center">
          <Sparkles size={16} className="text-white" />
        </div>
        <div>
          <h1 className="font-bold text-gray-800">Nutrition AI</h1>
          <p className="text-xs text-gray-400">Powered by RAG + IBM Granite</p>
        </div>
      </div>

      {/* Suggested questions (only when no user messages yet) */}
      {messages.length === 1 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
          {SUGGESTED_QUESTIONS.map((q, i) => (
            <button
              key={i}
              onClick={() => handleSend(q)}
              className="text-left px-3 py-2.5 bg-white border border-gray-100 rounded-xl text-sm text-gray-600 hover:border-primary-300 hover:text-primary-700 hover:bg-primary-50 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.map((msg, i) => (
          <ChatBubble
            key={i}
            role={msg.role}
            content={msg.content}
            citations={msg.citations}
            agentUsed={msg.agent_used}
          />
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-2">
              <LoadingSpinner size={16} />
              <span className="text-sm text-gray-500">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2 pt-4 border-t border-gray-100 mt-4">
        <input
          className="input flex-1"
          placeholder="Ask about nutrition, foods, or your health..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
          disabled={loading}
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || loading}
          className="btn-primary px-4"
        >
          {loading ? <LoadingSpinner size={16} /> : <Send size={16} />}
        </button>
      </div>
    </div>
  )
}
