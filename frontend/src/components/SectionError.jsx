// shown by all four dashboard sections when their fetch throws, so the
// wording lives in one place instead of being repeated four times
function SectionError() {
  return (
    <p className="text-sm text-ink-muted">
      Couldn't load this section. Try refreshing the page.
    </p>
  )
}

export default SectionError
