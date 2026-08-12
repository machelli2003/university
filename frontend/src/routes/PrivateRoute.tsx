import { type ReactNode } from "react"
import { Navigate } from "react-router-dom"
import { useAuthStore } from "@/store/authStore"
import { ROUTES } from "@/constants/routes"

interface PrivateRouteProps {
  children: ReactNode
  allowedRoles?: string[]
}

export function PrivateRoute({ children, allowedRoles }: PrivateRouteProps) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const user = useAuthStore((s) => s.user)

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to={ROUTES.UNAUTHORIZED} replace />
  }

  return <>{children}</>
}
