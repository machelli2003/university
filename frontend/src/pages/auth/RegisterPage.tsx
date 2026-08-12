import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Link } from "react-router-dom"
import { GraduationCap } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { ErrorAlert, SuccessAlert } from "@/components/ui/Feedback"
import { useRegister } from "@/hooks/useAuth"
import { getErrorMessage } from "@/services/api/client"
import { ROUTES } from "@/constants/routes"

const schema = z
  .object({
    first_name: z.string().min(1, "First name is required"),
    last_name: z.string().min(1, "Last name is required"),
    email: z.string().email("Enter a valid email"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  })

type FormData = z.infer<typeof schema>

export default function RegisterPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })
  const registerMutation = useRegister()

  const onSubmit = (data: FormData) => {
    const { confirmPassword, ...payload } = data
    registerMutation.mutate(payload)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper px-4">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <GraduationCap className="h-10 w-10 text-cocoa-600 mb-2" />
          <h1 className="font-display text-2xl font-semibold text-ink">Create Account</h1>
          <p className="text-sm text-cocoa-400 mt-1">Start your application</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 bg-white p-6 rounded-lg border border-cocoa-100 shadow-sm">
          {registerMutation.isError && (
            <ErrorAlert message={getErrorMessage(registerMutation.error)} />
          )}
          {registerMutation.isSuccess && (
            <SuccessAlert message="Registration successful! Redirecting to login..." />
          )}

          <div className="grid grid-cols-2 gap-3">
            <Input label="First name" error={errors.first_name?.message} {...register("first_name")} />
            <Input label="Last name" error={errors.last_name?.message} {...register("last_name")} />
          </div>

          <Input label="Email" type="email" placeholder="you@example.com" error={errors.email?.message} {...register("email")} />
          <Input label="Password" type="password" error={errors.password?.message} {...register("password")} />
          <Input label="Confirm password" type="password" error={errors.confirmPassword?.message} {...register("confirmPassword")} />

          <Button type="submit" className="w-full" isLoading={registerMutation.isPending}>
            Create account
          </Button>

          <p className="text-center text-sm text-cocoa-400">
            Already have an account?{" "}
            <Link to={ROUTES.LOGIN} className="text-cocoa-700 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
