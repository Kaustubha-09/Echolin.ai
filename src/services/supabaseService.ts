import { createClient } from '@supabase/supabase-js'
import { User } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL!
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export interface ChatSession {
  id: string
  user_id: string
  title: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  session_id: string
  type: 'user' | 'agent'
  content: string
  metadata?: any
  created_at: string
}

export interface DatabaseChatMessage {
  id: string
  session_id: string
  type: 'user' | 'agent'
  content: string
  metadata: any
  created_at: string
}

// Authentication functions
export const signUp = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  })
  return { data, error }
}

export const signIn = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  return { data, error }
}

export const signOut = async () => {
  const { error } = await supabase.auth.signOut()
  return { error }
}

export const getCurrentUser = async (): Promise<User | null> => {
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

// Chat history functions
export const createChatSession = async (title: string): Promise<ChatSession | null> => {
  const user = await getCurrentUser()
  if (!user) return null

  const { data, error } = await supabase
    .from('chat_sessions')
    .insert([
      {
        user_id: user.id,
        title,
      }
    ])
    .select()
    .single()

  if (error) {
    console.error('Error creating chat session:', error)
    return null
  }

  return data
}

export const getChatSessions = async (): Promise<ChatSession[]> => {
  const user = await getCurrentUser()
  if (!user) return []

  const { data, error } = await supabase
    .from('chat_sessions')
    .select('*')
    .eq('user_id', user.id)
    .order('updated_at', { ascending: false })

  if (error) {
    console.error('Error fetching chat sessions:', error)
    return []
  }

  return data || []
}

export const updateChatSession = async (sessionId: string, title: string): Promise<boolean> => {
  const { error } = await supabase
    .from('chat_sessions')
    .update({ title })
    .eq('id', sessionId)

  if (error) {
    console.error('Error updating chat session:', error)
    return false
  }

  return true
}

export const deleteChatSession = async (sessionId: string): Promise<boolean> => {
  const { error } = await supabase
    .from('chat_sessions')
    .delete()
    .eq('id', sessionId)

  if (error) {
    console.error('Error deleting chat session:', error)
    return false
  }

  return true
}

export const saveChatMessage = async (
  sessionId: string,
  type: 'user' | 'agent',
  content: string,
  metadata?: any
): Promise<ChatMessage | null> => {
  const { data, error } = await supabase
    .from('chat_messages')
    .insert([
      {
        session_id: sessionId,
        type,
        content,
        metadata: metadata || {},
      }
    ])
    .select()
    .single()

  if (error) {
    console.error('Error saving chat message:', error)
    return null
  }

  return data
}

export const getChatMessages = async (sessionId: string): Promise<DatabaseChatMessage[]> => {
  const { data, error } = await supabase
    .from('chat_messages')
    .select('*')
    .eq('session_id', sessionId)
    .order('created_at', { ascending: true })

  if (error) {
    console.error('Error fetching chat messages:', error)
    return []
  }

  return data || []
}

export const getLatestChatSession = async (): Promise<ChatSession | null> => {
  const user = await getCurrentUser()
  if (!user) return null

  const { data, error } = await supabase
    .from('chat_sessions')
    .select('*')
    .eq('user_id', user.id)
    .order('updated_at', { ascending: false })
    .limit(1)
    .single()

  if (error) {
    console.error('Error fetching latest chat session:', error)
    return null
  }

  return data
}

// Auth state change listener
export const onAuthStateChange = (callback: (user: User | null) => void) => {
  return supabase.auth.onAuthStateChange((event, session) => {
    callback(session?.user ?? null)
  })
} 