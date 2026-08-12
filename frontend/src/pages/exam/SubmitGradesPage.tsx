import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { ErrorAlert, SuccessAlert } from "@/components/ui/Feedback"
import { useSubmitGrade } from "@/hooks/useExam"
import { lecturerApi } from "@/services/api/lecturer"
import { getErrorMessage } from "@/services/api/client"
import type { SubmitGradeRequest } from "@/types/exam"

export default function SubmitGradesPage() {
  const [courses, setCourses] = useState<any[]>([])
  const submitMutation = useSubmitGrade()
  const { register, handleSubmit, reset } = useForm<SubmitGradeRequest>({
    defaultValues: {
      student_id: "",
      course_id: "",
      academic_year: String(new Date().getFullYear()),
      semester: "1",
      continuous_assessment: 0,
      final_exam_score: 0,
    },
  })

  useEffect(() => {
    async function loadCourses() {
      try {
        const res = await lecturerApi.myCourses()
        setCourses(res.data)
      } catch (err) {
        console.error(err)
      }
    }
    loadCourses()
  }, [])

  const onSubmit = (data: SubmitGradeRequest) => {
    submitMutation.mutate(
      {
        ...data,
        continuous_assessment: Number(data.continuous_assessment),
        final_exam_score: Number(data.final_exam_score),
        practical_score: data.practical_score ? Number(data.practical_score) : undefined,
        mid_semester_score: data.mid_semester_score ? Number(data.mid_semester_score) : undefined,
      },
      { onSuccess: () => reset() }
    )
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Submit Grades</h1>
      <p className="text-cocoa-400 mb-6">
        CA (30%) + Final Exam (70%) — or CA (20%) + Practical (20%) + Final (60%) if practical score is given.
      </p>

      <Card className="max-w-xl">
        <CardHeader><CardTitle>Grade Entry</CardTitle></CardHeader>
        <CardContent>
          {submitMutation.isError && <ErrorAlert message={getErrorMessage(submitMutation.error)} />}
          {submitMutation.isSuccess && (
            <SuccessAlert
              message={`Grade submitted: ${submitMutation.data.letter_grade} (${submitMutation.data.total_score.toFixed(1)}%)`}
            />
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input label="Student ID" {...register("student_id", { required: true })} />
            {courses.length > 0 ? (
              <label className="block">
                <span className="text-sm font-medium text-cocoa-600">Course</span>
                <select
                  {...register("course_id", { required: true })}
                  className="input w-full mt-1"
                >
                  <option value="">Select course</option>
                  {courses.map((course) => (
                    <option key={course.id} value={course.id}>
                      {course.code} — {course.title}
                    </option>
                  ))}
                </select>
              </label>
            ) : (
              <Input label="Course ID" {...register("course_id", { required: true })} />
            )}

            <div className="grid grid-cols-2 gap-3">
              <Input label="Academic Year" {...register("academic_year", { required: true })} />
              <Input label="Semester" {...register("semester", { required: true })} />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Continuous Assessment (0-100)"
                type="number"
                {...register("continuous_assessment", { required: true })}
              />
              <Input
                label="Final Exam Score (0-100)"
                type="number"
                {...register("final_exam_score", { required: true })}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input label="Practical Score (optional)" type="number" {...register("practical_score")} />
              <Input label="Mid-Semester Score (optional)" type="number" {...register("mid_semester_score")} />
            </div>

            <Button type="submit" isLoading={submitMutation.isPending} className="w-full">
              Submit Grade
            </Button>
          </form>
        </CardContent>
      </Card>
    </AppShell>
  )
}
