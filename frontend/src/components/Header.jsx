import React from 'react'
import { Layers } from 'lucide-react'

export default function Header({ videoCount, onOpenLibrary }) {
  return (
    <header
      style={{
        borderBottom: '1px solid var(--border-color)',
        backgroundColor: 'rgba(255, 255, 255, 0.85)',
        backdropFilter: 'blur(10px)',
        position: 'sticky',
        top: 0,
        zIndex: 30,
      }}
    >
      <div
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          padding: '0.85rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              backgroundColor: '#e11d48',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 5px rgba(225, 29, 72, 0.25)',
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
            </svg>
          </div>
          <div>
            <h1 style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              YouTube RAG
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Timestamp-Grounded Video Knowledge Base
            </p>
          </div>
        </div>

        <button
          onClick={onOpenLibrary}
          className="btn-secondary"
          style={{ padding: '0.4rem 0.85rem', fontSize: '0.775rem' }}
          title="Browse all indexed videos"
        >
          <Layers size={13} style={{ color: 'var(--text-secondary)' }} />
          <span>
            Library <strong>({videoCount})</strong>
          </span>
        </button>
      </div>
    </header>
  )
}
