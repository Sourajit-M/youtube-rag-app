import React, { useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { Search, RotateCw, ChevronRight } from 'lucide-react'
import CitationBadge from './CitationBadge'

export default function ChatArea({
  messages,
  query,
  setQuery,
  isQuerying,
  onSendQuery,
  onPlayCitation,
}) {
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isQuerying])

  const sampleQuestions = [
    'What is runtime polymorphism and how is it achieved?',
    'What is method overriding and how it is performed with an example.',
  ]

  const handleSubmit = (e) => {
    e.preventDefault()
    onSendQuery()
  }

  return (
    <section
      style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-color)',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        minHeight: '520px',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      {/* Messages Stream */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1.25rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
        }}
      >
        {messages.map((m) => (
          <div
            key={m.id}
            className="animate-fade-in"
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: m.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            {/* Sender Label */}
            <div
              style={{
                fontSize: '0.725rem',
                color: 'var(--text-muted)',
                marginBottom: '0.25rem',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
              }}
            >
              {m.role === 'user' ? 'You' : 'Assistant (Groq gpt-oss-120b)'}
            </div>

            {/* Message Bubble */}
            <div
              style={{
                maxWidth: '90%',
                backgroundColor: m.role === 'user' ? '#0f172a' : 'var(--bg-primary)',
                color: m.role === 'user' ? '#ffffff' : 'var(--text-primary)',
                padding: '0.85rem 1.1rem',
                borderRadius:
                  m.role === 'user'
                    ? '14px 14px 2px 14px'
                    : '14px 14px 14px 2px',
                border: m.role === 'user' ? 'none' : '1px solid var(--border-color)',
                boxShadow: m.role === 'user' ? 'var(--shadow-sm)' : 'none',
              }}
            >
              <div className={m.role === 'assistant' ? 'markdown-content' : ''}>
                <ReactMarkdown>{m.text}</ReactMarkdown>
              </div>

              {/* Citations Badges */}
              {m.citations && m.citations.length > 0 && (
                <div
                  style={{
                    marginTop: '0.85rem',
                    paddingTop: '0.75rem',
                    borderTop: '1px solid var(--border-color)',
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.725rem',
                      color: 'var(--text-muted)',
                      fontWeight: 600,
                      marginBottom: '0.4rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    Timestamp Citations (Click to Play):
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem' }}>
                    {m.citations.map((c, i) => (
                      <CitationBadge
                        key={i}
                        citation={c}
                        onPlayCitation={onPlayCitation}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isQuerying && (
          <div
            className="animate-fade-in"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              color: 'var(--text-secondary)',
              fontSize: '0.85rem',
              padding: '0.5rem 0',
            }}
          >
            <RotateCw size={15} className="animate-spin" style={{ color: 'var(--accent-brand)' }} />
            <span>Searching Qdrant Cloud & generating grounded answer...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Quick Question Suggestions */}
      {messages.length <= 2 && (
        <div
          style={{
            padding: '0.6rem 1.25rem',
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: '0.45rem',
            borderTop: '1px solid var(--border-color)',
            backgroundColor: 'var(--bg-primary)',
          }}
        >
          <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            Suggestions:
          </span>
          {sampleQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => onSendQuery(q)}
              className="btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}
            >
              <span>{q}</span>
              <ChevronRight size={12} style={{ color: 'var(--text-muted)' }} />
            </button>
          ))}
        </div>
      )}

      {/* Question Input Box */}
      <form
        onSubmit={handleSubmit}
        style={{
          padding: '0.85rem 1.25rem',
          borderTop: '1px solid var(--border-color)',
          backgroundColor: 'var(--bg-surface)',
          display: 'flex',
          gap: '0.6rem',
        }}
      >
        <input
          type="text"
          placeholder="Ask anything about the ingested video(s)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="input-field"
          style={{ flex: 1 }}
          disabled={isQuerying}
        />
        <button
          type="submit"
          disabled={isQuerying || !query.trim()}
          className="btn-primary"
          style={{ padding: '0.6rem 1.15rem' }}
        >
          <Search size={15} />
          <span>Ask</span>
        </button>
      </form>
    </section>
  )
}
