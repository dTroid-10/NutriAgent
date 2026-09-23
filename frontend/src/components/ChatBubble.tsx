import clsx from 'clsx'

interface ChatBubbleProps {
  role: 'user' | 'assistant'
  content: string
  citations?: string[]
  agentUsed?: string
}

export function ChatBubble({ role, content, citations, agentUsed }: ChatBubbleProps) {
  const isUser = role === 'user'

  // Simple markdown-ish rendering: bold **text** → <strong>
  function renderContent(text: string) {
    return text
      .split('\n')
      .map((line, i) => {
        const parts = line.split(/(\*\*[^*]+\*\*)/)
        return (
          <p key={i} className={i > 0 ? 'mt-1' : ''}>
            {parts.map((part, j) =>
              part.startsWith('**') && part.endsWith('**') ? (
                <strong key={j}>{part.slice(2, -2)}</strong>
              ) : (
                <span key={j}>{part}</span>
              )
            )}
          </p>
        )
      })
  }

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={clsx(
          'max-w-[80%] rounded-2xl px-4 py-3 text-sm',
          isUser
            ? 'bg-primary-500 text-white rounded-br-sm'
            : 'bg-white border border-gray-100 text-gray-800 shadow-card rounded-bl-sm'
        )}
      >
        {renderContent(content)}

        {!isUser && agentUsed && (
          <p className="text-xs mt-2 text-gray-400">Agent: {agentUsed}</p>
        )}

        {!isUser && citations && citations.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-100">
            <p className="text-xs text-gray-400 font-medium mb-0.5">Sources:</p>
            {citations.slice(0, 4).map((c, i) => (
              <p key={i} className="text-xs text-accent-500">
                [{i + 1}] {c}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
