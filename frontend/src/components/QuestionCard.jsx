function QuestionCard({ question }) {
  if (!question) return null

  return (
    <section className="question-card">
      <div className="question-header">
        <span className="pill pill-primary">Question</span>
        {question.topic && <span className="pill pill-subtle">{question.topic}</span>}
        {typeof question.difficulty === 'number' && (
          <span className="pill pill-subtle">Difficulty: {question.difficulty.toFixed(1)}</span>
        )}
      </div>
      <h2 className="question-text">{question.question}</h2>
      {question.options && Array.isArray(question.options) && question.options.length > 0 && (
        <ul className="options-list">
          {question.options.map((opt, idx) => (
            <li key={idx} className="option-item">
              {opt}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default QuestionCard

