import { type ReactNode } from "react"
import { Navigate, useLocation } from "react-router-dom"
import { useAuthStore } from "@/store/authStore"
import { ROUTES } from "@/constants/routes"

interface PrivateRouteProps {
  children: ReactNode
  allowedRoles?: string[]
  requiredPermissions?: string[]  // Additional permission checks
  requireTenantAdmin?: boolean     // Must be tenant admin
  requireSuperAdmin?: boolean      // Must be super admin
}

/**
 * Section 57-62: Frontend Route Protection
 * 
 * Provides comprehensive route authorization:
 * 1. Authentication check (isAuthenticated)
 * 2. Role-based access (allowedRoles)
 * 3. Permission-based access (requiredPermissions)
 * 4. Admin-level access (requireTenantAdmin, requireSuperAdmin)
 * 
 * Redirects unauthorized users to:
 * - /login if not authenticated
 * - /unauthorized if role/permission denied
 */
export function PrivateRoute({
  children,
  allowedRoles,
  requiredPermissions,
  requireTenantAdmin = false,
  requireSuperAdmin = false,
}: PrivateRouteProps) {
  const location = useLocation()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const user = useAuthStore((s) => s.user)

  // Step 1: Check authentication
  if (!isAuthenticated || !user) {
    // Store redirect location for post-login navigation
    sessionStorage.setItem("redirectAfterLogin", location.pathname)
    return <Navigate to={ROUTES.LOGIN} replace />
  }

  // Step 2: Check super admin requirement (highest privilege)
  if (requireSuperAdmin && user.role !== "super_admin") {
    return <Navigate to={ROUTES.UNAUTHORIZED} replace />
  }

  // Step 3: Check tenant admin requirement
  if (requireTenantAdmin && !["tenant_admin", "super_admin"].includes(user.role)) {
    return <Navigate to={ROUTES.UNAUTHORIZED} replace />
  }

  // Step 4: Check role-based access
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={ROUTES.UNAUTHORIZED} replace />
  }

  // Step 5: Check permission-based access
  if (requiredPermissions && requiredPermissions.length > 0) {
    // Check if user has all required permissions
    const userPermissions = user.permissions || []
    const hasAllPermissions = requiredPermissions.every((perm) =>
      userPermissions.includes(perm)
    )
    
    if (!hasAllPermissions) {
      return <Navigate to={ROUTES.UNAUTHORIZED} replace />
    }
  }

  // All authorization checks passed
  return <>{children}</>
}
