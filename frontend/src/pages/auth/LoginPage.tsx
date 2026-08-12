import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Link } from "react-router-dom"
import { GraduationCap } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { ErrorAlert } from "@/components/ui/Feedback"
import { useLogin } from "@/hooks/useAuth"
import { getErrorMessage } from "@/services/api/client"
import { ROUTES } from "@/constants/routes"

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
})

type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })
  const loginMutation = useLogin()

  const onSubmit = (data: FormData) => {
    loginMutation.mutate(data)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper px-4">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <GraduationCap className="h-10 w-10 text-cocoa-600 mb-2" />
          <h1 className="font-display text-2xl font-semibold text-ink">EUMP</h1>
          <p className="text-sm text-cocoa-400 mt-1">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 bg-white p-6 rounded-lg border border-cocoa-100 shadow-sm">
          {loginMutation.isError && (
            <ErrorAlert message={getErrorMessage(loginMutation.error)} />
          )}

          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            error={errors.email?.message}
            {...register("email")}
          />

          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register("password")}
          />

          <Button type="submit" className="w-full" isLoading={loginMutation.isPending}>
            Sign in
          </Button>

          <p className="text-center text-sm text-cocoa-400">
            Don't have an account?{" "}
            <Link to={ROUTES.REGISTER} className="text-cocoa-700 font-medium hover:underline">
              Register
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
