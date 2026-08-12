import { apiClient } from "./client"
import type { AxiosResponse } from "axios"

interface AdminApi {
  listUsers(tenantId?: string, includeInactive?: boolean): Promise<AxiosResponse<any>>
  createUser(data: any): Promise<AxiosResponse<any>>
  updateUser(id: string, data: any): Promise<AxiosResponse<any>>
  unlockUser(id: string): Promise<AxiosResponse<any>>
  deleteUser(id: string): Promise<AxiosResponse<any>>
}

export const adminApi: AdminApi = {
  listUsers: (tenantId?: string, includeInactive?: boolean) =>
    apiClient.get("/admin/users", { params: { tenant_id: tenantId, include_inactive: includeInactive } }),
  createUser: (data: any) => apiClient.post("/admin/users", data),
  updateUser: (id: string, data: any) => apiClient.put(`/admin/users/${id}`, data),
  unlockUser: (id: string) => apiClient.patch(`/admin/users/${id}/unlock`),
  deleteUser: (id: string) => apiClient.delete(`/admin/users/${id}`),
}
