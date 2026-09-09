import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import IngestBar from './components/IngestBar'
import VideoLibrary from './components/VideoLibrary'
import ChatArea from './components/ChatArea'
import VideoPlayer from './components/VideoPlayer'

export default function App() {
  const [url, setUrl] = useState('')
  const [isIngesting, setIsIngesting] = useState(false)
  const [ingestStatus, setIngestStatus] = useState(null)
  const [videos, setVideos] = useState([])
  const [query, setQuery] = useState('')
  const [isQuerying, setIsQuerying] = useState(false)
  const [isLibraryOpen, setIsLibraryOpen] = useState(false)
  const [activePlayer, setActivePlayer] = useState(null)
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      text: 'Welcome to **YouTube RAG**! Paste any YouTube video or playlist URL above to index it, then ask any question. Answers are strictly grounded with exact clickable timestamps.',
      citations: [],
    },
  ])

  // Fetch indexed videos on mount
  const loadVideos = async () => {
    try {
      const res = await fetch('/api/videos')
      if (res.ok) {
        const data = await res.json()
        const fetchedVideos = data.videos || []
        setVideos(fetchedVideos)
        if (fetchedVideos.length > 0 && !activePlayer) {
          setActivePlayer({
            videoId: fetchedVideos[0].video_id,
            startTime: 0,
            title: fetchedVideos[0].video_title,
          })
        }
      }
    } catch (err) {
      console.error('Failed to load indexed videos:', err)
    }
  }

  useEffect(() => {
    loadVideos()
  }, [])

  // Handle URL Ingestion
  const handleIngest = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setIsIngesting(true)
    setIngestStatus(null)

    try {
      const res = await fetch('/api/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim(), force: false }),
      })

      const data = await res.json()
      if (res.ok) {
        setIngestStatus({
          type: 'success',
          text: `Processed ${data.total_processed} video(s) successfully.`,
        })
        setUrl('')
        await loadVideos()
      } else {
        setIngestStatus({
          type: 'error',
          text: data.detail || 'Failed to ingest URL.',
        })
      }
    } catch (err) {
      setIngestStatus({
        type: 'error',
        text: 'Server connection error. Ensure backend is running.',
      })
    } finally {
      setIsIngesting(false)
    }
  }

  // Handle Question Asking
  const handleQuery = async (questionText) => {
    const q = (questionText || query).trim()
    if (!q || isQuerying) return

    const newMessages = [...messages, { id: Date.now().toString(), role: 'user', text: q }]
    setMessages(newMessages)
    setQuery('')
    setIsQuerying(true)

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q }),
      })

      const data = await res.json()
      if (res.ok) {
        setMessages([
          ...newMessages,
          {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            text: data.answer,
            citations: data.citations || [],
          },
        ])
      } else {
        setMessages([
          ...newMessages,
          {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            text: `⚠️ **Error**: ${data.detail || 'Unable to generate response.'}`,
            citations: [],
          },
        ])
      }
    } catch (err) {
      setMessages([
        ...newMessages,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          text: '⚠️ **Connection Error**: Could not reach the backend server.',
          citations: [],
        },
      ])
    } finally {
      setIsQuerying(false)
    }
  }

  const handlePlayCitation = (citation) => {
    setActivePlayer({
      videoId: citation.video_id,
      startTime: citation.start_time,
      title: citation.video_title,
    })
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Header */}
      <Header
        videoCount={videos.length}
        onOpenLibrary={() => setIsLibraryOpen(true)}
      />

      {/* Main Workspace */}
      <main
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          width: '100%',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          padding: '1.25rem 1.5rem',
          gap: '1.25rem',
        }}
      >
        {/* Ingest Section with Compact Summary */}
        <IngestBar
          url={url}
          setUrl={setUrl}
          isIngesting={isIngesting}
          onIngest={handleIngest}
          ingestStatus={ingestStatus}
          videos={videos}
          onOpenLibrary={() => setIsLibraryOpen(true)}
        />

        {/* Content Split: Chat + Video Preview */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: activePlayer ? '1.15fr 0.85fr' : '1fr',
            gap: '1.25rem',
            flex: 1,
            minHeight: 0,
          }}
        >
          {/* Q&A Chat */}
          <ChatArea
            messages={messages}
            query={query}
            setQuery={setQuery}
            isQuerying={isQuerying}
            onSendQuery={handleQuery}
            onPlayCitation={handlePlayCitation}
          />

          {/* Interactive Player */}
          <VideoPlayer activePlayer={activePlayer} />
        </div>
      </main>

      {/* Slide-over Library Drawer for Many Videos */}
      <VideoLibrary
        isOpen={isLibraryOpen}
        onClose={() => setIsLibraryOpen(false)}
        videos={videos}
        activePlayer={activePlayer}
        onSelectVideo={(video) => setActivePlayer(video)}
      />
    </div>
  )
}
