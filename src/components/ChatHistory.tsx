import React, { useState, useEffect } from 'react'
import { History, Plus, MoreVertical, Edit3, Trash2, MessageSquare } from 'lucide-react'
import { User } from '@supabase/supabase-js'
import { 
  ChatSession, 
  getChatSessions, 
  createChatSession,
  updateChatSession,
  deleteChatSession 
} from '../services/supabaseService'

interface ChatHistoryProps {
  user: User | null
  currentSessionId: string | null
  onSessionSelect: (sessionId: string) => void
  onNewChat: () => void
  isVisible: boolean
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ 
  user, 
  currentSessionId, 
  onSessionSelect, 
  onNewChat,
  isVisible 
}) => {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [loading, setLoading] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [menuOpen, setMenuOpen] = useState<string | null>(null)

  useEffect(() => {
    if (user) {
      loadSessions()
    } else {
      setSessions([])
    }
  }, [user])

  const loadSessions = async () => {
    if (!user) return
    setLoading(true)
    try {
      const data = await getChatSessions()
      setSessions(data)
    } catch (error) {
      console.error('Error loading sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNewChat = async () => {
    if (!user) {
      onNewChat()
      return
    }

    try {
      const newSession = await createChatSession('New Chat')
      if (newSession) {
        setSessions([newSession, ...sessions])
        onSessionSelect(newSession.id)
      }
    } catch (error) {
      console.error('Error creating new chat:', error)
    }
  }

  const handleEditTitle = async (sessionId: string) => {
    if (!editTitle.trim()) return

    try {
      const success = await updateChatSession(sessionId, editTitle.trim())
      if (success) {
        setSessions(sessions.map(session => 
          session.id === sessionId 
            ? { ...session, title: editTitle.trim() }
            : session
        ))
      }
    } catch (error) {
      console.error('Error updating session title:', error)
    } finally {
      setEditingId(null)
      setEditTitle('')
    }
  }

  const handleDeleteSession = async (sessionId: string) => {
    if (!window.confirm('Are you sure you want to delete this chat?')) return

    try {
      const success = await deleteChatSession(sessionId)
      if (success) {
        setSessions(sessions.filter(session => session.id !== sessionId))
        if (currentSessionId === sessionId) {
          onNewChat()
        }
      }
    } catch (error) {
      console.error('Error deleting session:', error)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 1) return 'Today'
    if (diffDays === 2) return 'Yesterday'
    if (diffDays <= 7) return `${diffDays - 1} days ago`
    
    return date.toLocaleDateString()
  }

  if (!isVisible) return null

  return (
    <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <History size={20} className="text-gray-600 mr-2" />
            <h2 className="font-semibold text-gray-900">Chat History</h2>
          </div>
          <button
            onClick={handleNewChat}
            className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            title="New Chat"
          >
            <Plus size={16} />
          </button>
        </div>

        {!user && (
          <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
            <p className="font-medium mb-1">Sign in to save chats</p>
            <p>Your conversations will be saved automatically when you log in.</p>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-center text-gray-500">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
            Loading...
          </div>
        ) : user && sessions.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <MessageSquare size={32} className="mx-auto mb-2 text-gray-400" />
            <p className="text-sm">No chat history yet</p>
            <p className="text-xs text-gray-400 mt-1">Start a conversation to see it here</p>
          </div>
        ) : user ? (
          <div className="space-y-1 p-2">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
                  currentSessionId === session.id
                    ? 'bg-blue-50 border border-blue-200'
                    : 'hover:bg-white hover:shadow-sm'
                }`}
                onClick={() => !editingId && onSessionSelect(session.id)}
              >
                {editingId === session.id ? (
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onBlur={() => handleEditTitle(session.id)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleEditTitle(session.id)
                      if (e.key === 'Escape') {
                        setEditingId(null)
                        setEditTitle('')
                      }
                    }}
                    className="w-full px-2 py-1 text-sm border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                ) : (
                  <>
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium text-gray-900 text-sm truncate pr-2">
                        {session.title}
                      </h3>
                      <div className="relative">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setMenuOpen(menuOpen === session.id ? null : session.id)
                          }}
                          className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition-all"
                        >
                          <MoreVertical size={14} />
                        </button>

                        {menuOpen === session.id && (
                          <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[120px]">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                setEditingId(session.id)
                                setEditTitle(session.title)
                                setMenuOpen(null)
                              }}
                              className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center"
                            >
                              <Edit3 size={12} className="mr-2" />
                              Rename
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleDeleteSession(session.id)
                                setMenuOpen(null)
                              }}
                              className="w-full text-left px-3 py-2 text-sm hover:bg-red-50 text-red-600 flex items-center"
                            >
                              <Trash2 size={12} className="mr-2" />
                              Delete
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(session.updated_at)}
                    </p>
                  </>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 text-center text-gray-500">
            <MessageSquare size={32} className="mx-auto mb-2 text-gray-400" />
            <p className="text-sm">Sign in to view chat history</p>
          </div>
        )}
      </div>

      {/* Click outside to close menu */}
      {menuOpen && (
        <div 
          className="fixed inset-0 z-0" 
          onClick={() => setMenuOpen(null)}
        />
      )}
    </div>
  )
}

export default ChatHistory 