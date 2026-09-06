// Pure rules about a user's three preference fields, read from GET /me.
// Kept out of the components so each rule is defined exactly once.

// the order sections appear in before any personalisation
const DEFAULT_ORDER = ['prices', 'insight', 'news', 'meme']

// Has this user finished the onboarding quiz?
// The three preference columns are always saved together in one transaction,
// so checking one of them is enough to know about all three.
export function isOnboarded(user) {
  return Boolean(user.investor_type)
}

// picked sections first, the rest after — default order kept inside each group
export function orderSections(contentTypes) {
  const chosen = contentTypes || []
  const picked = DEFAULT_ORDER.filter((section) => chosen.includes(section))
  const rest = DEFAULT_ORDER.filter((section) => !chosen.includes(section))
  return [...picked, ...rest]
}
