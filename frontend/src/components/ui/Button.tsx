import { type ButtonHTMLAttributes, forwardRef } from "react"
import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger"
  size?: "xs" | "sm" | "md" | "lg"
  isLoading?: boolean
}

const variants = {
  primary: "bg-cocoa-600 text-white hover:bg-cocoa-700",
  secondary: "bg-brass-400 text-ink hover:bg-brass-500",
  outline: "border border-cocoa-300 text-cocoa-700 hover:bg-cocoa-50",
  ghost: "text-cocoa-700 hover:bg-cocoa-50",
  danger: "bg-red-600 text-white hover:bg-red-700",
}

const sizes = {
  xs: "px-2 py-1 text-xs",
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-sm",
  lg: "px-6 py-3 text-base",
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", isLoading, disabled, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          "focus:outline-none focus:ring-2 focus:ring-cocoa-400 focus:ring-offset-1",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
        {children}
      </button>
    )
  }
)
Button.displayName = "Button"
