import React from 'react'
import { Tv, ExternalLink } from 'lucide-react'

export default function VideoPlayer({ activePlayer }) {
  if (!activePlayer) return null

  return (
    <aside
      style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-color)',
        borderRadius: '12px',
        padding: '1.15rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.85rem',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '0.65rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <Tv size={15} style={{ color: 'var(--accent-brand)' }} />
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Video Preview
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span
            style={{
              fontSize: '0.725rem',
              color: 'var(--text-secondary)',
              backgroundColor: 'var(--bg-subtle)',
              border: '1px solid var(--border-color)',
              padding: '0.2rem 0.5rem',
              borderRadius: '4px',
              fontFamily: 'monospace',
              fontWeight: 600,
            }}
          >
            t={activePlayer.startTime}s
          </span>
          <a
            href={`https://youtube.com/watch?v=${activePlayer.videoId}&t=${activePlayer.startTime}s`}
            target="_blank"
            rel="noreferrer"
            style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}
            title="Open on YouTube"
          >
            <ExternalLink size={14} />
          </a>
        </div>
      </div>

      {/* YouTube IFrame Embed */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          paddingTop: '56.25%', // 16:9 ratio
          backgroundColor: '#000000',
          borderRadius: '8px',
          overflow: 'hidden',
          border: '1px solid var(--border-color)',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <iframe
          key={`${activePlayer.videoId}-${activePlayer.startTime}`}
          src={`https://www.youtube-nocookie.com/embed/${activePlayer.videoId}?start=${activePlayer.startTime}&autoplay=1`}
          title={activePlayer.title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            border: 'none',
          }}
        />
      </div>

      {/* Video Title & Timestamp Context */}
      <div>
        <h3
          style={{
            fontSize: '0.875rem',
            fontWeight: 600,
            color: 'var(--text-primary)',
            lineHeight: 1.4,
          }}
        >
          {activePlayer.title}
        </h3>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Clicking any citation in the chat seeks the video directly to that second.
        </p>
      </div>
    </aside>
  )
}
