import { apiClient } from "./client"
import type { AuthResponse, LoginRequest, RegisterRequest, User } from "@/types/auth"

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const res = await apiClient.post("/auth/login", data)
    return res.data
  },

  register: async (data: RegisterRequest): Promise<{ id: string; email: string; message: string }> => {
    const res = await apiClient.post("/auth/register", data)
    return res.data
  },

  changePassword: async (payload: {
    current_password: string
    new_password: string
    confirm_password: string
    email?: string
  }): Promise<{ message: string }> => {
    const endpoint = payload.email ? "/auth/reset-password" : "/auth/change-password"
    const res = await apiClient.post(endpoint, payload)
    return res.data
  },

  getMe: async (): Promise<User> => {
    const res = await apiClient.get("/auth/me")
    return res.data
  },

  refreshToken: async (refresh_token: string): Promise<{ access_token: string; refresh_token: string }> => {
    const res = await apiClient.post("/auth/refresh", { refresh_token })
    return res.data
  },
}
