import { UserButton, useUser } from '@clerk/clerk-react'
import ChatInterface from './ChatInterface'

const Dashboard = () => {
  const { user, isLoaded } = useUser()

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header with user info */}
      <div className="bg-white shadow-sm border-b p-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">🤖 DeBot - AI Domain Expert</h1>
          <p className="text-gray-600">Welcome, {user?.firstName || user?.emailAddresses[0]?.emailAddress}</p>
        </div>
        <UserButton afterSignOutUrl="/" />
      </div>

      {/* Chat Interface */}
      <div className="flex-1">
        <ChatInterface />
      </div>
    </div>
  )
}

export default Dashboard