import React, { useState } from 'react'
import { X, Search, Play, ExternalLink, Layers, Check } from 'lucide-react'

export default function VideoLibrary({
  isOpen,
  onClose,
  videos,
  activePlayer,
  onSelectVideo,
}) {
  const [searchFilter, setSearchFilter] = useState('')

  if (!isOpen) return null

  const filteredVideos = videos.filter((v) =>
    (v.video_title || v.video_id).toLowerCase().includes(searchFilter.toLowerCase())
  )

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.45)',
        backdropFilter: 'blur(4px)',
        zIndex: 50,
        display: 'flex',
        justifyContent: 'flex-end',
      }}
      onClick={onClose}
    >
      <div
        className="animate-fade-in"
        style={{
          width: '100%',
          maxWidth: '460px',
          height: '100%',
          backgroundColor: '#ffffff',
          boxShadow: 'var(--shadow-lg)',
          display: 'flex',
          flexDirection: 'column',
          borderLeft: '1px solid var(--border-color)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div
          style={{
            padding: '1.25rem 1.5rem',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={18} style={{ color: 'var(--accent-brand)' }} />
            <h2 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
              Video Library ({videos.length})
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: '0.25rem',
              borderRadius: '6px',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Search Bar */}
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-color)' }}>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search indexed videos..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="input-field"
              style={{ width: '100%', paddingLeft: '2.2rem', fontSize: '0.825rem' }}
            />
            <Search
              size={14}
              style={{
                position: 'absolute',
                left: '0.75rem',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)',
              }}
            />
          </div>
        </div>

        {/* Videos List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {filteredVideos.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem 1rem', fontSize: '0.875rem' }}>
              No videos matching "{searchFilter}"
            </div>
          ) : (
            filteredVideos.map((v) => {
              const isPlaying = activePlayer?.videoId === v.video_id
              return (
                <div
                  key={v.video_id}
                  style={{
                    backgroundColor: isPlaying ? '#f8fafc' : 'var(--bg-primary)',
                    border: '1px solid',
                    borderColor: isPlaying ? '#0f172a' : 'var(--border-color)',
                    borderRadius: '10px',
                    padding: '0.85rem 1rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
                    <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.4 }}>
                      {v.video_title}
                    </h4>
                    {isPlaying && (
                      <span
                        style={{
                          fontSize: '0.7rem',
                          backgroundColor: '#0f172a',
                          color: '#ffffff',
                          padding: '0.15rem 0.4rem',
                          borderRadius: '4px',
                          fontWeight: 600,
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.2rem',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        <Check size={10} /> Active
                      </span>
                    )}
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '0.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>{v.chunk_count} chunks</span>
                      <span>•</span>
                      <span style={{ textTransform: 'uppercase' }}>{v.lang_original || 'en'}</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <button
                        onClick={() => {
                          onSelectVideo({
                            videoId: v.video_id,
                            startTime: 0,
                            title: v.video_title,
                          })
                          onClose()
                        }}
                        className="btn-secondary"
                        style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
                      >
                        <Play size={11} fill="currentColor" />
                        <span>Play</span>
                      </button>

                      <a
                        href={`https://youtube.com/watch?v=${v.video_id}`}
                        target="_blank"
                        rel="noreferrer"
                        className="btn-secondary"
                        style={{ padding: '0.25rem 0.45rem', color: 'var(--text-muted)' }}
                        title="Open on YouTube"
                      >
                        <ExternalLink size={12} />
                      </a>
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}
