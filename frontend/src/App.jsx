import { useState } from 'react'
import axios from 'axios'
import './App.css'
import QuestionCard from './components/QuestionCard.jsx'
import AnswerBox from './components/AnswerBox.jsx'
import FeedbackPanel from './components/FeedbackPanel.jsx'

const api = axios.create({
  baseURL: 'http://localhost:8080',
})

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [sessionInfo, setSessionInfo] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [pendingNextQuestion, setPendingNextQuestion] = useState(null)
  const [answer, setAnswer] = useState('')
  const [feedback, setFeedback] = useState(null)
  const [score, setScore] = useState(null)
  const [studyPlan, setStudyPlan] = useState(null)   // ⭐ NEW STATE
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [hasSubmitted, setHasSubmitted] = useState(false)

  const handleStart = async () => {
    try {
      setLoading(true)
      setError(null)
      setFeedback(null)
      setScore(null)
      setStudyPlan(null)  // ⭐ reset study plan
      setHasSubmitted(false)
      setAnswer('')

      const res = await api.get('/next-question')
      const { session, question } = res.data
      setSessionId(session.id)
      setSessionInfo(session)
      setCurrentQuestion(question)
      setPendingNextQuestion(null)
    } catch (err) {
      console.error(err)
      setError('Failed to start diagnostic. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!sessionId || !currentQuestion) return
    if (!answer.trim()) {
      setError('Please enter an answer before submitting.')
      return
    }

    try {
      setLoading(true)
      setError(null)

      const res = await api.post('/submit-answer', {
        session_id: sessionId,
        question_id: currentQuestion.id,
        selected_answer: answer,
      })

      const {
        feedback: fb,
        score: sc,
        next_question: nextQ,
        session: sessionRes,
        study_plan
      } = res.data

      setFeedback(fb)
      setScore(sc)
      setPendingNextQuestion(nextQ)

      if (sessionRes) {
        setSessionInfo(sessionRes)
      }

      // ⭐ CAPTURE STUDY PLAN FROM BACKEND
      if (study_plan) {
        setStudyPlan(study_plan)
      }

      setHasSubmitted(true)

    } catch (err) {
      console.error(err)
      setError('Failed to submit answer. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleNextQuestion = () => {
    if (!pendingNextQuestion) {
      setCurrentQuestion(null)
      setAnswer('')
      setFeedback(null)
      setScore(null)
      setHasSubmitted(false)
      return
    }

    setCurrentQuestion(pendingNextQuestion)
    setPendingNextQuestion(null)
    setAnswer('')
    setFeedback(null)
    setScore(null)
    setHasSubmitted(false)
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <h1>AI-Driven Adaptive Diagnostic Engine</h1>
        <p className="subtitle">
          Start a diagnostic session, answer questions in your own words, and get instant AI feedback.
        </p>
      </header>

      <main className="app-main">
        <div className="controls">
          <button onClick={handleStart} disabled={loading}>
            {sessionId ? 'Restart Test' : 'Start Test'}
          </button>
        </div>

        {error && <div className="error-banner">{error}</div>}

        {sessionId && sessionInfo && (
          <div className="session-meta">
            <span className="pill pill-subtle">
              Difficulty: {sessionInfo.difficulty_level ?? 'medium'}
            </span>
            <span className="pill pill-subtle">
              Ability: {sessionInfo.ability.toFixed(1)}
            </span>
            <span className="pill pill-subtle">
              Answered: {sessionInfo.answered_count}
            </span>
          </div>
        )}

        {sessionId && currentQuestion && (
          <div className="diagnostic-layout">
            <QuestionCard question={currentQuestion} />

            <AnswerBox
              value={answer}
              onChange={setAnswer}
              disabled={loading}
            />

            <div className="actions-row">
              <button onClick={handleSubmit} disabled={loading || !answer.trim()}>
                {loading ? 'Submitting...' : 'Submit Answer'}
              </button>

              {hasSubmitted && (
                <button onClick={handleNextQuestion} disabled={loading}>
                  Next Question
                </button>
              )}
            </div>

            {hasSubmitted && (
              <FeedbackPanel
                feedback={feedback}
                score={score}
              />
            )}
          </div>
        )}

{sessionId && !currentQuestion && !loading && (
  <div className="completion">
    <h2>Diagnostic Complete ✅</h2>

    <p>Your diagnostic test is finished.</p>

    {score !== null && (
      <p>Score: {(score * 100).toFixed(0)}%</p>
    )}

    {studyPlan && (
      <>
        <p>Based on your answers, here is your study plan:</p>
        <ul>
          {studyPlan.map((step, index) => (
            <li key={index}>{step}</li>
          ))}
        </ul>
      </>
    )}
  </div>
)}


      </main>
    </div>
  )
}

export default App