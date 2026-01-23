import React, { useState } from 'react'
import { User, LogOut, Settings, UserCircle } from 'lucide-react'
import { User as SupabaseUser } from '@supabase/supabase-js'
import { signOut } from '../services/supabaseService'

interface UserProfileProps {
  user: SupabaseUser | null
  onLoginClick: () => void
  onLogoutSuccess: () => void
  onShowSettings: () => void
}

const UserProfile: React.FC<UserProfileProps> = ({ user, onLoginClick, onLogoutSuccess, onShowSettings }) => {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleLogout = async () => {
    setLoading(true)
    try {
      const { error } = await signOut()
      if (!error) {
        onLogoutSuccess()
        setDropdownOpen(false)
      } else {
        console.error('Logout error:', error)
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <button
        onClick={onLoginClick}
        className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        <UserCircle size={16} className="mr-2" />
        Sign In
      </button>
    )
  }

  return (
    <div className="relative">
      <button
        onClick={() => setDropdownOpen(!dropdownOpen)}
        className="flex items-center px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
      >
        <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center mr-3">
          {user.email?.charAt(0).toUpperCase() || 'U'}
        </div>
        <div className="text-left hidden sm:block">
          <p className="text-sm font-medium text-gray-900 truncate max-w-32">
            {user.email}
          </p>
          <p className="text-xs text-gray-500">
            Signed in
          </p>
        </div>
      </button>

      {dropdownOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setDropdownOpen(false)}
          />
          <div className="absolute right-0 top-full mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-20">
            <div className="p-4 border-b border-gray-100">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center mr-3">
                  {user.email?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {user.email}
                  </p>
                  <p className="text-xs text-gray-500">
                    Premium User
                  </p>
                </div>
              </div>
            </div>
            
            <div className="py-2">
              <button
                onClick={() => {
                  setDropdownOpen(false)
                  onShowSettings()
                }}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <Settings size={16} className="mr-3 text-gray-400" />
                Settings
              </button>
              
              <button
                onClick={handleLogout}
                disabled={loading}
                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center disabled:opacity-50"
              >
                <LogOut size={16} className="mr-3" />
                {loading ? 'Signing out...' : 'Sign out'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default UserProfile 