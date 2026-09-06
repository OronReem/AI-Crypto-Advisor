import { useState } from 'react'

// tries a real coin logo first; falls back to our own initials badge if
// that ticker isn't available at this free icon service
function CoinIcon({ coin }) {
  const [imageFailed, setImageFailed] = useState(false)

  if (imageFailed) {
    return (
      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gold/15 text-xs font-semibold text-gold">
        {coin.slice(0, 3)}
      </span>
    )
  }

  return (
    <img
      src={`https://assets.coincap.io/assets/icons/${coin.toLowerCase()}@2x.png`}
      alt={coin}
      className="h-8 w-8 rounded-full"
      onError={() => setImageFailed(true)}
    />
  )
}

export default CoinIcon
