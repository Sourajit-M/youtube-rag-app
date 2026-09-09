import React from 'react'
import { Play, ExternalLink } from 'lucide-react'

export default function CitationBadge({ citation, onPlayCitation }) {
  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-color)',
        borderRadius: '6px',
        overflow: 'hidden',
        fontSize: '0.75rem',
        boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
      }}
    >
      <button
        onClick={() => onPlayCitation(citation)}
        style={{
          background: 'none',
          border: 'none',
          color: 'var(--text-primary)',
          padding: '0.3rem 0.55rem',
          cursor: 'pointer',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
          fontWeight: 600,
          transition: 'background-color 0.15s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-subtle)')}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        title={`Jump to ${citation.timestamp_formatted} in video`}
      >
        <Play size={10} fill="#e11d48" style={{ color: '#e11d48' }} />
        <span>{citation.timestamp_formatted}</span>
      </button>

      <a
        href={citation.youtube_url}
        target="_blank"
        rel="noreferrer"
        style={{
          padding: '0.3rem 0.45rem',
          color: 'var(--text-muted)',
          borderLeft: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          transition: 'color 0.15s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
        onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
        title="Open on YouTube"
      >
        <ExternalLink size={11} />
      </a>
    </div>
  )
}
