import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react'
import ChatInterface from './components/ChatInterface'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">🤖 DeBot</h1>
              <span className="ml-2 text-sm text-gray-500">AI Domain Expert</span>
            </div>
            <div className="flex items-center space-x-4">
              <SignedOut>
                <SignInButton className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                  Sign In
                </SignInButton>
              </SignedOut>
              <SignedIn>
                <UserButton />
              </SignedIn>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <SignedOut>
          <div className="text-center py-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Welcome to DeBot
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Your AI-powered domain expert chatbot for intelligent document interaction
            </p>
            <SignInButton className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md text-lg font-medium">
              Get Started
            </SignInButton>
          </div>
        </SignedOut>
        
        <SignedIn>
          <ChatInterface />
        </SignedIn>
      </main>
    </div>
  )
}

export default App