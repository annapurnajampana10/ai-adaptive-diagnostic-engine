function FeedbackPanel({ feedback, score }) {
  if (feedback == null && score == null) return null

  const scorePercent =
    typeof score === 'number' && !Number.isNaN(score)
      ? `${Math.round(score * 100)}%`
      : 'N/A'

  return (
    <section className="feedback-panel">
      <h3>AI Feedback</h3>
      <div className="feedback-score">
        <span className="feedback-score-label">Score:</span>
        <span className="feedback-score-value">{scorePercent}</span>
      </div>
      {feedback && <p className="feedback-text">{feedback}</p>}
    </section>
  )
}

export default FeedbackPanel

