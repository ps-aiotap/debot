import AuthWrapper from './components/AuthWrapper'
import Dashboard from './components/Dashboard'

function App() {
  return (
    <AuthWrapper>
      <Dashboard />
    </AuthWrapper>
  )
}

export default App