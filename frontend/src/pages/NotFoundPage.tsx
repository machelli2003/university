import { Link } from "react-router-dom"
import { Compass } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { ROUTES } from "@/constants/routes"

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-paper px-4 text-center">
      <Compass className="h-12 w-12 text-cocoa-400 mb-4" />
      <h1 className="font-display text-2xl font-semibold text-ink mb-2">Page Not Found</h1>
      <p className="text-cocoa-400 mb-6">The page you're looking for doesn't exist.</p>
      <Link to={ROUTES.DASHBOARD}>
        <Button>Back to Dashboard</Button>
      </Link>
    </div>
  )
}
