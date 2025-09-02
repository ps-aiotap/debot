import { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, AlertCircle, FileText } from 'lucide-react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

export default function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [personas, setPersonas] = useState(null)
  const [selectedPersona, setSelectedPersona] = useState('')
  const [showExplanations, setShowExplanations] = useState(true)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    fetchPersonas()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchPersonas = async () => {
    try {
      const response = await axios.get(`${API_BASE}/personas`)
      setPersonas(response.data)
      setSelectedPersona(response.data.current)
    } catch (error) {
      console.error('Failed to fetch personas:', error)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message: input,
        persona: selectedPersona,
        explain: showExplanations
      })

      const botMessage = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        explanation: response.data.explanation
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message}`,
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex h-[calc(100vh-200px)]">
      {/* Sidebar */}
      <div className="w-80 bg-white rounded-lg shadow-sm border p-6 mr-6">
        <h3 className="text-lg font-semibold mb-4">Settings</h3>
        
        {personas && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Persona
            </label>
            <select
              value={selectedPersona}
              onChange={(e) => setSelectedPersona(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              {personas.available.map(persona => (
                <option key={persona} value={persona}>{persona}</option>
              ))}
            </select>
            
            <div className="mt-3 text-sm text-gray-600">
              <p><strong>Collections:</strong></p>
              <ul className="list-disc list-inside">
                {personas.collections.map(collection => (
                  <li key={collection}>{collection}</li>
                ))}
              </ul>
              <p className="mt-2"><strong>Style:</strong> {personas.prompt_style}</p>
            </div>
          </div>
        )}

        <div className="mb-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={showExplanations}
              onChange={(e) => setShowExplanations(e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm">Show explanations</span>
          </label>
        </div>

        <button
          onClick={() => setMessages([])}
          className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm"
        >
          Clear Chat
        </button>
      </div>

      {/* Chat Area */}
      <div className="flex-1 bg-white rounded-lg shadow-sm border flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-12">
              <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p>Start a conversation with your AI domain expert</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-3xl ${message.role === 'user' ? 'bg-blue-600 text-white' : message.error ? 'bg-red-50 border border-red-200' : 'bg-gray-50'} rounded-lg p-4`}>
                <div className="flex items-start space-x-3">
                  {message.role === 'user' ? (
                    <User className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  ) : message.error ? (
                    <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0 text-red-500" />
                  ) : (
                    <Bot className="w-5 h-5 mt-0.5 flex-shrink-0 text-gray-600" />
                  )}
                  <div className="flex-1">
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    
                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-gray-200">
                        <p className="font-medium text-sm text-gray-700 mb-2">Sources:</p>
                        <div className="space-y-1">
                          {message.sources.filter(s => s.type !== 'hash').map((source, idx) => (
                            <div key={idx} className="flex items-center text-sm text-gray-600">
                              <FileText className="w-4 h-4 mr-2" />
                              {source.filename} ({source.type})
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Explanation */}
                    {message.explanation && (
                      <details className="mt-4 pt-3 border-t border-gray-200">
                        <summary className="cursor-pointer font-medium text-sm text-gray-700">
                          🔍 Why these documents were selected
                        </summary>
                        <div className="mt-2 text-sm text-gray-600 space-y-2">
                          <p><strong>Query:</strong> {message.explanation.query}</p>
                          <p><strong>Documents Retrieved:</strong> {message.explanation.total_docs_retrieved}</p>
                          
                          {message.explanation.potential_issues && message.explanation.potential_issues.length > 0 && (
                            <div className="bg-yellow-50 border border-yellow-200 rounded p-2">
                              <p className="font-medium text-yellow-800">Potential Issues:</p>
                              {message.explanation.potential_issues.map((issue, idx) => (
                                <p key={idx} className="text-yellow-700">⚠️ {issue}</p>
                              ))}
                            </div>
                          )}

                          <div>
                            <p className="font-medium">Document Analysis:</p>
                            {message.explanation.explanations.map((exp, idx) => (
                              <div key={idx} className="ml-4 mt-2 p-2 bg-gray-50 rounded">
                                <p className="font-medium">📄 {exp.document}</p>
                                <p>Similarity: {exp.similarity_score}</p>
                                <p>Reason: {exp.relevance_reason}</p>
                                {exp.location_mismatch && (
                                  <p className="text-red-600">⚠️ Location mismatch detected</p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center space-x-3">
                  <Bot className="w-5 h-5 text-gray-600" />
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t p-4">
          <div className="flex space-x-4">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your documents..."
              className="flex-1 p-3 border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="2"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white p-3 rounded-md"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}