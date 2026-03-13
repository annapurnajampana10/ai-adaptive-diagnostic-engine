function AnswerBox({ value, onChange, disabled }) {
  return (
    <section className="answer-box">
      <label className="answer-label" htmlFor="answer-textarea">
        Your answer
      </label>
      <textarea
        id="answer-textarea"
        className="answer-textarea"
        rows={6}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Type your answer here. Explain your reasoning in your own words."
        disabled={disabled}
      />
    </section>
  )
}

export default AnswerBox

