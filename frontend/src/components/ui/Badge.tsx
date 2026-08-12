import { type HTMLAttributes } from "react"
import { cn } from "@/lib/utils"

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "info"
}

const variants = {
  default: "bg-cocoa-100 text-cocoa-700",
  success: "bg-green-100 text-green-700",
  warning: "bg-brass-100 text-brass-600",
  danger: "bg-red-100 text-red-700",
  info: "bg-blue-100 text-blue-700",
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium font-mono",
        variants[variant],
        className
      )}
      {...props}
    />
  )
}

export function statusToVariant(status: string): BadgeProps["variant"] {
  const successStates = ["accepted", "results_approved", "eligible", "allocated", "offered"]
  const warningStates = ["submitted", "results_uploaded", "awaiting_results", "waitlisted", "pending", "ranked"]
  const dangerStates = ["rejected", "ineligible", "failed"]

  if (successStates.includes(status)) return "success"
  if (warningStates.includes(status)) return "warning"
  if (dangerStates.includes(status)) return "danger"
  return "default"
}
