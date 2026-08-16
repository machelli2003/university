import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios"
import { useAuthStore } from "@/store/authStore"

// Use relative URL so requests go through the Vite dev proxy (no CORS)
// In production, VITE_API_BASE_URL should be set to the absolute backend URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1"

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let refreshQueue: Array<() => void> = []

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshQueue.push(() => resolve(apiClient(originalRequest)))
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = useAuthStore.getState().refreshToken

      if (!refreshToken) {
        useAuthStore.getState().logout()
        return Promise.reject(error)
      }

      try {
        const response = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })
        const { access_token, refresh_token } = response.data
        useAuthStore.getState().setTokens(access_token, refresh_token)

        refreshQueue.forEach((cb) => cb())
        refreshQueue = []

        return apiClient(originalRequest)
      } catch (refreshError) {
        useAuthStore.getState().logout()
        window.location.href = "/login"
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

function extractValidationMessage(value: unknown): string {
  if (typeof value === "string") return value
  if (Array.isArray(value)) {
    return value.map(extractValidationMessage).filter(Boolean).join(" • ")
  }
  if (value && typeof value === "object") {
    const obj = value as Record<string, unknown>
    if (typeof obj.msg === "string") return obj.msg
    if (typeof obj.message === "string") return obj.message
    if (typeof obj.error === "string") return obj.error
    if (Array.isArray(obj.errors)) {
      return obj.errors.map(extractValidationMessage).filter(Boolean).join(" • ")
    }
  }
  return ""
}

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as any

    if (typeof data === "string") return data
    if (data && typeof data === "object") {
      if (typeof data.detail === "string") return data.detail
      if (Array.isArray(data.detail)) {
        const msg = data.detail.map(extractValidationMessage).filter(Boolean).join(" • ")
        if (msg) return msg
      }
      if (typeof data.message === "string") return data.message
      if (Array.isArray(data)) {
        const msg = data.map(extractValidationMessage).filter(Boolean).join(" • ")
        if (msg) return msg
      }
    }

    return error.message || "Something went wrong"
  }

  if (error && typeof error === "object") {
    const e = error as Record<string, unknown>
    if (typeof e.message === "string") return e.message
    if (typeof e.detail === "string") return e.detail
  }

  return "Something went wrong"
}
