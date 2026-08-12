import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { User } from "@/types/auth"

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  applicantId: string | null
  studentId: string | null
  selectedTenantId: string | null
  setAuth: (user: User, accessToken: string, refreshToken: string) => void
  setTokens: (accessToken: string, refreshToken: string) => void
  setUser: (user: User) => void
  setApplicantId: (id: string) => void
  setStudentId: (id: string | null) => void
  setSelectedTenantId: (tenantId: string | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      applicantId: null,
      studentId: null,

      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken, isAuthenticated: true }),

      setTokens: (accessToken, refreshToken) =>
        set({ accessToken, refreshToken }),

      setUser: (user) => set({ user }),

      setApplicantId: (id) => set({ applicantId: id }),
      setStudentId: (id) => set({ studentId: id }),
      selectedTenantId: null,
      setSelectedTenantId: (tenantId) => set({ selectedTenantId: tenantId }),

      logout: () =>
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false, applicantId: null, studentId: null, selectedTenantId: null }),
    }),
    {
      name: "eump-auth-storage",
    }
  )
)
