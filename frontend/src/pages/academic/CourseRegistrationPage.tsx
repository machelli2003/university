import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { useAuthStore } from "@/store/authStore"
import { useCourses, useRegisterCourses } from "@/hooks/useAcademic"
import { getErrorMessage } from "@/services/api/client"

export default function CourseRegistrationPage() {
  const studentId = useAuthStore((s) => s.studentId)
  const { data: courses, isLoading } = useCourses()
  const registerMutation = useRegisterCourses()

  const [selected, setSelected] = useState<string[]>([])
  const [academicYear, setAcademicYear] = useState(String(new Date().getFullYear()))
  const [semester, setSemester] = useState("1")

  const totalCredits = (courses ?? [])
    .filter((c) => selected.includes(c.id))
    .reduce((sum, c) => sum + c.credit_hours, 0)

  const toggleCourse = (id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]))
  }

  if (!studentId) {
    return (
      <AppShell>
        <Card className="max-w-xl mx-auto">
          <CardHeader><CardTitle>Course Registration</CardTitle></CardHeader>
          <CardContent>
            <p className="text-cocoa-500">
              You need to accept your admission offer and create your student record before registering for courses.
            </p>
          </CardContent>
        </Card>
      </AppShell>
    )
  }

  const onSubmit = () => {
    registerMutation.mutate({
      student_id: studentId,
      course_ids: selected,
      academic_year: academicYear,
      semester,
    })
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Course Registration</h1>
      <p className="text-cocoa-400 mb-6">Select courses for the semester. Total credits must be 12–24.</p>

      <Card>
        <CardHeader><CardTitle>Select Courses</CardTitle></CardHeader>
        <CardContent>
          {registerMutation.isError && <ErrorAlert message={getErrorMessage(registerMutation.error)} />}
          {registerMutation.isSuccess && (
            <SuccessAlert
              message={`Registered ${registerMutation.data.registered_courses.length} courses (${registerMutation.data.total_credits} credits).`}
            />
          )}

          <div className="grid grid-cols-2 gap-3 mb-4">
            <Input label="Academic Year" value={academicYear} onChange={(e) => setAcademicYear(e.target.value)} />
            <Input label="Semester" value={semester} onChange={(e) => setSemester(e.target.value)} />
          </div>

          {isLoading && <Spinner />}

          <div className="space-y-2 mb-4 max-h-96 overflow-y-auto scrollbar-thin">
            {courses?.map((course) => (
              <label
                key={course.id}
                className="flex items-center justify-between border border-cocoa-100 rounded-md px-4 py-3 cursor-pointer hover:bg-cocoa-50"
              >
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={selected.includes(course.id)}
                    onChange={() => toggleCourse(course.id)}
                    className="h-4 w-4 accent-cocoa-600"
                  />
                  <div>
                    <p className="font-medium text-sm">{course.code} — {course.name}</p>
                    <p className="text-xs text-cocoa-400 capitalize">{course.course_type}</p>
                  </div>
                </div>
                <span className="font-mono text-sm text-cocoa-500">{course.credit_hours} cr</span>
              </label>
            ))}
          </div>

          <div className="flex items-center justify-between border-t border-cocoa-100 pt-4">
            <p className="text-sm">
              <span className="text-cocoa-400">Total credits: </span>
              <span className={`font-mono font-semibold ${totalCredits < 12 || totalCredits > 24 ? "text-red-600" : "text-green-600"}`}>
                {totalCredits}
              </span>
              <span className="text-cocoa-400"> / 12–24 required</span>
            </p>
            <Button
              onClick={onSubmit}
              isLoading={registerMutation.isPending}
              disabled={selected.length === 0}
            >
              Register Courses
            </Button>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  )
}
