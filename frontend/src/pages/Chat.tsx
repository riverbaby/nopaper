import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import api from '../api/client'

interface Message {
  role: 'user' | 'assistant'
  content: string
  citations?: any[]
}

function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await api.post('/search/chat', {
        message,
        k: 5,
        with_citations: true,
      })
      return response.data
    },
    onSuccess: (data) => {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: data.message, citations: data.citations }
      ])
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      setMessages(prev => [...prev, { role: 'user', content: input }])
      chatMutation.mutate(input)
      setInput('')
    }
  }

  return (
    <div>
      <h2>RAG Chat</h2>

      <div className="chat-container" style={{ marginTop: '1rem' }}>
        <div className="chat-messages">
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', color: '#666', marginTop: '2rem' }}>
              <p>Ask me anything about your documents!</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx}>
              <div className={`chat-message ${msg.role}`}>
                <div style={{ fontWeight: '500', marginBottom: '0.5rem' }}>
                  {msg.role === 'user' ? 'You' : 'Assistant'}
                </div>
                <div>{msg.content}</div>
              </div>

              {msg.citations && msg.citations.length > 0 && (
                <div style={{ marginTop: '0.5rem', marginBottom: '1rem', fontSize: '0.875rem', color: '#666' }}>
                  <details>
                    <summary style={{ cursor: 'pointer' }}>Sources ({msg.citations.length})</summary>
                    <div style={{ marginTop: '0.5rem', paddingLeft: '1rem' }}>
                      {msg.citations.map((citation: any, cidx: number) => (
                        <div key={cidx} style={{ marginBottom: '0.5rem' }}>
                          • {citation.title} (Page {citation.page_index + 1})
                        </div>
                      ))}
                    </div>
                  </details>
                </div>
              )}
            </div>
          ))}

          {chatMutation.isPending && (
            <div className="chat-message assistant">
              <div>Thinking...</div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="chat-input">
          <input
            type="text"
            placeholder="Ask a question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={chatMutation.isPending}
          />
          <button type="submit" disabled={chatMutation.isPending || !input.trim()}>
            Send
          </button>
        </form>
      </div>

      {chatMutation.isError && (
        <div style={{ marginTop: '1rem', padding: '1rem', background: '#f8d7da', color: '#721c24', borderRadius: '4px' }}>
          Error sending message. Please try again.
        </div>
      )}
    </div>
  )
}

export default Chat
