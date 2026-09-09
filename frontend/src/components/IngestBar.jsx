import React from 'react'
import { RotateCw, CheckCircle2, AlertCircle, Plus, BookOpen } from 'lucide-react'

export default function IngestBar({
  url,
  setUrl,
  isIngesting,
  onIngest,
  ingestStatus,
  videos,
  onOpenLibrary,
}) {
  const totalChunks = videos.reduce((acc, v) => acc + (v.chunk_count || 0), 0)

  return (
    <section
      style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-color)',
        borderRadius: '12px',
        padding: '1.1rem 1.25rem',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <form onSubmit={onIngest} style={{ display: 'flex', gap: '0.75rem' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <input
            type="text"
            placeholder="Paste any YouTube video or playlist URL (e.g. https://www.youtube.com/watch?v=... or playlist?list=...)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="input-field"
            style={{ width: '100%', paddingLeft: '2.5rem' }}
            disabled={isIngesting}
          />
          <svg
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="#e11d48"
            style={{
              position: 'absolute',
              left: '0.85rem',
              top: '50%',
              transform: 'translateY(-50%)',
            }}
          >
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
          </svg>
        </div>

        <button
          type="submit"
          disabled={isIngesting || !url.trim()}
          className="btn-primary"
        >
          {isIngesting ? (
            <>
              <RotateCw size={14} className="animate-spin" />
              <span>Ingesting...</span>
            </>
          ) : (
            <>
              <Plus size={15} />
              <span>Ingest</span>
            </>
          )}
        </button>
      </form>

      {/* Status Feedback Message */}
      {ingestStatus && (
        <div
          className="animate-fade-in"
          style={{
            marginTop: '0.75rem',
            fontSize: '0.825rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.45rem',
            color: ingestStatus.type === 'success' ? '#16a34a' : '#dc2626',
            backgroundColor: ingestStatus.type === 'success' ? '#f0fdf4' : '#fef2f2',
            padding: '0.45rem 0.75rem',
            borderRadius: '6px',
            border: `1px solid ${ingestStatus.type === 'success' ? '#bbf7d0' : '#fecaca'}`,
          }}
        >
          {ingestStatus.type === 'success' ? (
            <CheckCircle2 size={15} />
          ) : (
            <AlertCircle size={15} />
          )}
          <span>{ingestStatus.text}</span>
        </div>
      )}

      {/* Compact Summary Bar (Prevents clutter when indexing many videos) */}
      <div
        style={{
          marginTop: '0.85rem',
          paddingTop: '0.75rem',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.8rem',
          color: 'var(--text-secondary)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Knowledge Base:</span>
          <span>
            {videos.length} {videos.length === 1 ? 'video' : 'videos'} indexed ({totalChunks.toLocaleString()} chunks)
          </span>
        </div>

        {videos.length > 0 && (
          <button
            type="button"
            onClick={onOpenLibrary}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--accent-brand)',
              fontWeight: 600,
              fontSize: '0.8rem',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.2rem 0.4rem',
              borderRadius: '4px',
            }}
          >
            <BookOpen size={13} />
            <span>Browse Library &rarr;</span>
          </button>
        )}
      </div>
    </section>
  )
}
