import { useState, useEffect } from 'react'
import { authFetch } from '../lib/api.js'
import VoteButtons from '../components/VoteButtons.jsx'
import SectionError from '../components/SectionError.jsx'
import SectionLoading from '../components/SectionLoading.jsx'

function MemeSection({ myVotes }) {
  const [meme, setMeme] = useState(null)
  const [failed, setFailed] = useState(false)

  // runs once after the first render — the empty array is what limits it to once
  useEffect(() => {
    async function loadMeme() {
      try {
        const response = await authFetch('/dashboard/meme')
        if (!response.ok) throw new Error(response.status)
        const data = await response.json()
        setMeme(data)
      } catch {
        setFailed(true)
      }
    }
    loadMeme()
  }, [])

  if (failed) {
    return <SectionError />
  }

  if (meme === null) {
    return <SectionLoading />
  }

  return (
    <div className="flex flex-col items-center">
      {/* fixed-height frame, so the card doesn't resize when the template changes */}
      <div className="flex h-72 w-full items-center justify-center overflow-hidden rounded-xl border border-ink-muted/15 bg-parchment p-3">
        <img
          src={meme.imageUrl}
          alt={meme.alt}
          // object-contain fits the whole image inside without cropping it
          className="max-h-full max-w-full object-contain"
        />
      </div>
      <div className="mt-4">
        <VoteButtons
          section="meme"
          topic={meme.topic}
          item={meme.id}
          initialVote={myVotes[meme.id]}
        />
      </div>
    </div>
  )
}

export default MemeSection
