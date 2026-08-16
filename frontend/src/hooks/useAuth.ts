import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import { authApi } from "@/services/api/auth"
import { useAuthStore } from "@/store/authStore"
import type { LoginRequest, RegisterRequest } from "@/types/auth"
import { ROUTES } from "@/constants/routes"

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth)
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token)
      navigate(ROUTES.DASHBOARD)
    },
    onError: (error: any) => {
      const data = error?.response?.data
      const user = data?.user
      if (error?.response?.status === 403 && (user || data?.detail?.includes("Password reset required"))) {
        sessionStorage.setItem("pendingPasswordResetUser", JSON.stringify(user || { email: "" }))
        navigate(ROUTES.RESET_PASSWORD)
      }
    },
  })
}

export function useRegister() {
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: () => {
      navigate(ROUTES.LOGIN)
    },
  })
}

export function useLogout() {
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return () => {
    logout()
    queryClient.clear()
    navigate(ROUTES.LOGIN)
  }
}

export function useCurrentUser() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const setUser = useAuthStore((s) => s.setUser)

  return useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const user = await authApi.getMe()
      setUser(user)
      return user
    },
    enabled: isAuthenticated,
    retry: false,
  })
}
