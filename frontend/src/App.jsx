import { useState } from 'react'
import './App.css'

function App() {
  const [words, setWords] = useState([])
  const [history, setHistory] = useState([])
  const [session, setSession] = useState(null)
  const [message, setMessage] = useState('')

  const token = localStorage.getItem('hksd_token')

  const request = async (url, options = {}) => {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Token ${token}` } : {}),
        ...(options.headers || {}),
      },
      ...options,
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) {
      throw new Error(data.detail || `Request failed with status ${response.status}`)
    }
    return data
  }

  const fetchWords = async () => {
    try {
      const data = await request('/api/words/')
      setWords(data)
      setMessage('Loaded words successfully.')
    } catch (error) {
      setMessage(`Words request failed: ${error.message}`)
    }
  }

  const fetchPracticeHistory = async () => {
    try {
      const data = await request('/api/practice/history/')
      setHistory(data)
      console.log('Practice history:', data)
      setMessage('Loaded practice history successfully.')
    } catch (error) {
      setMessage(`History request failed: ${error.message}`)
    }
  }

  const createAndFetchPracticeSession = async () => {
    try {
      const created = await request('/api/practice/sessions/', {
        method: 'POST',
        body: JSON.stringify({ planned_item_count: 10 }),
      })
      const detail = await request(`/api/practice/sessions/${created.id}/`)
      setSession(detail)
      setMessage(`Created and loaded practice session ${created.id}.`)
    } catch (error) {
      setMessage(`Practice session flow failed: ${error.message}`)
    }
  }

  return (
    <main style={{ padding: '2rem', fontFamily: 'Verdana, sans-serif' }}>
      <h1>HKSD Speech Platform API Smoke Test</h1>
      <p>Set API token in localStorage key <code>hksd_token</code> before testing protected routes.</p>
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
        <button onClick={fetchWords}>Fetch /api/words/</button>
        <button onClick={fetchPracticeHistory}>Fetch /api/practice/history/</button>
        <button onClick={createAndFetchPracticeSession}>POST+GET practice session</button>
      </div>
      {message && <p>{message}</p>}

      <h2>Words</h2>
      <pre>{JSON.stringify(words, null, 2)}</pre>

      <h2>Practice History</h2>
      <pre>{JSON.stringify(history, null, 2)}</pre>

      <h2>Latest Practice Session</h2>
      <pre>{JSON.stringify(session, null, 2)}</pre>
    </main>
  )
}

export default App
