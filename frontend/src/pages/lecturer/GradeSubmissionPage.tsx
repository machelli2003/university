/**
 * Lecturer Grade Submission Page
 * 
 * Allows lecturers to submit grades for their assigned courses.
 * Includes validation, error handling, and a comprehensive form interface.
 */

import React, { useState, useEffect } from "react"
import { useForm, useFieldArray } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import axios from "axios"
import { AlertCircle, CheckCircle, Loader, Plus, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/Button"

// Validation schema using Zod
const gradeEntrySchema = z.object({
  student_id: z.string().min(1, "Student ID is required"),
  score: z.number().min(0, "Score cannot be negative").max(100, "Score cannot exceed 100"),
  remarks: z.string().optional(),
})

const gradeSubmissionSchema = z.object({
  course_id: z.string().min(1, "Course is required"),
  grades: z.array(gradeEntrySchema).min(1, "At least one grade is required"),
  submission_notes: z.string().optional(),
})

type GradeSubmissionForm = z.infer<typeof gradeSubmissionSchema>

interface Course {
  id: string
  code: string
  title: string
}

interface GradeEntry {
  student_id: string
  score: number
  remarks?: string
}

interface SubmissionResult {
  success: boolean
  message: string
  submittedCount?: number
  errors?: string[]
}

export default function GradeSubmissionPage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<SubmissionResult | null>(null)
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)
  const [courseStudents, setCourseStudents] = useState<Array<{ id: string; name: string }>>([])

  const {
    control,
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<GradeSubmissionForm>({
    resolver: zodResolver(gradeSubmissionSchema),
    defaultValues: {
      course_id: "",
      grades: [{ student_id: "", score: 0, remarks: "" }],
      submission_notes: "",
    },
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: "grades",
  })

  const courseId = watch("course_id")

  // Fetch lecturer's courses on mount
  useEffect(() => {
    fetchMyCourses()
  }, [])

  // Fetch course roster when course changes
  useEffect(() => {
    if (courseId) {
      const selected = courses.find((c) => c.id === courseId)
      setSelectedCourse(selected || null)
      fetchCourseRoster(courseId)
    }
  }, [courseId, courses])

  const fetchMyCourses = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem("access_token")
      const response = await axios.get("/api/v1/lecturer/courses", {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      })
      setCourses(response.data)
    } catch (err) {
      setResult({
        success: false,
        message: "Failed to load your courses",
      })
    } finally {
      setLoading(false)
    }
  }

  const fetchCourseRoster = async (courseId: string) => {
    try {
      const token = localStorage.getItem("access_token")
      const response = await axios.get(`/api/v1/lecturer/courses/${courseId}/roster`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      })
      setCourseStudents(response.data)
    } catch (err) {
      console.error("Failed to fetch course roster:", err)
    }
  }

  const onSubmit = async (data: GradeSubmissionForm) => {
    try {
      setSubmitting(true)
      const token = localStorage.getItem("access_token")

      const payload = {
        course_id: data.course_id,
        grades: data.grades.map((g) => ({
          student_id: g.student_id,
          score: parseFloat(g.score.toString()),
          remarks: g.remarks || undefined,
        })),
        submission_notes: data.submission_notes,
      }

      const response = await axios.post("/api/v1/lecturer/courses/grades", payload, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      })

      setResult({
        success: true,
        message: response.data.message,
        submittedCount: response.data.submitted_count,
      })

      // Reset form after successful submission
      setTimeout(() => {
        reset()
        setResult(null)
      }, 3000)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Failed to submit grades"
      setResult({
        success: false,
        message: errorMessage,
        errors: err.response?.data?.errors || [],
      })
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin text-blue-600 mx-auto" />
          <p className="mt-4 text-gray-600">Loading your courses...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Submit Course Grades</h1>
          <p className="text-gray-600 mt-1">Submit grades for students in your courses</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Result Message */}
        {result && (
          <div
            className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
              result.success
                ? "bg-green-50 border border-green-200"
                : "bg-red-50 border border-red-200"
            }`}
          >
            {result.success ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            <div>
              <p
                className={`font-medium ${
                  result.success ? "text-green-900" : "text-red-900"
                }`}
              >
                {result.message}
              </p>
              {result.submittedCount && (
                <p
                  className={`text-sm ${
                    result.success ? "text-green-800" : "text-red-800"
                  }`}
                >
                  {result.submittedCount} grades submitted successfully
                </p>
              )}
            </div>
          </div>
        )}

        {/* Main Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-lg shadow-md p-6">
          {/* Course Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Select Course<span className="text-red-500">*</span>
            </label>
            <select
              {...register("course_id")}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            >
              <option value="">Choose a course...</option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.code} - {course.title}
                </option>
              ))}
            </select>
            {errors.course_id && (
              <p className="text-sm text-red-600 mt-1">{errors.course_id.message}</p>
            )}
          </div>

          {/* Course Information */}
          {selectedCourse && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-gray-600">
                <strong>Course:</strong> {selectedCourse.code} - {selectedCourse.title}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                <strong>Enrolled Students:</strong> {courseStudents.length}
              </p>
            </div>
          )}

          {/* Grades Table */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Student Grades</h2>
              <Button
                type="button"
                onClick={() => append({ student_id: "", score: 0, remarks: "" })}
                className="bg-blue-600 hover:bg-blue-700 flex items-center gap-2"
                size="sm"
              >
                <Plus className="w-4 h-4" />
                Add Student Grade
              </Button>
            </div>

            <div className="overflow-x-auto border border-gray-200 rounded-lg">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Student</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Score (0-100)</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Remarks</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {fields.map((field, index) => (
                    <tr key={field.id} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <select
                          {...register(`grades.${index}.student_id`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                        >
                          <option value="">Select student...</option>
                          {courseStudents.map((student) => (
                            <option key={student.id} value={student.id}>
                              {student.name}
                            </option>
                          ))}
                        </select>
                        {errors.grades?.[index]?.student_id && (
                          <p className="text-xs text-red-600 mt-1">
                            {errors.grades[index]?.student_id?.message}
                          </p>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <input
                          type="number"
                          min="0"
                          max="100"
                          step="0.5"
                          {...register(`grades.${index}.score`, {
                            valueAsNumber: true,
                          })}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                          placeholder="0"
                        />
                        {errors.grades?.[index]?.score && (
                          <p className="text-xs text-red-600 mt-1">
                            {errors.grades[index]?.score?.message}
                          </p>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <input
                          type="text"
                          {...register(`grades.${index}.remarks`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                          placeholder="Optional remarks..."
                        />
                      </td>
                      <td className="px-4 py-3">
                        <button
                          type="button"
                          onClick={() => remove(index)}
                          className="text-red-600 hover:text-red-900 p-2"
                          title="Remove grade entry"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {errors.grades && typeof errors.grades === "object" && "message" in errors.grades && (
              <p className="text-sm text-red-600 mt-2">{errors.grades.message}</p>
            )}
          </div>

          {/* Submission Notes */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Submission Notes (Optional)
            </label>
            <textarea
              {...register("submission_notes")}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              placeholder="Any additional notes about the grade submission..."
            />
          </div>

          {/* Submission Info */}
          <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-sm text-gray-700">
              <strong>Important:</strong> Once submitted, grades will be recorded in the system and will be
              visible to students. Please verify all entries before submitting.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              type="submit"
              disabled={submitting}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2"
            >
              {submitting ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Submit Grades
                </>
              )}
            </Button>
            <Button
              type="button"
              onClick={() => reset()}
              className="bg-gray-300 hover:bg-gray-400 text-gray-900"
            >
              Clear Form
            </Button>
          </div>
        </form>

        {/* Help Section */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">📋 How to Submit Grades</h2>
          <ol className="space-y-3 text-gray-700">
            <li className="flex gap-3">
              <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white text-sm font-medium flex-shrink-0">
                1
              </span>
              <span>Select the course you want to submit grades for</span>
            </li>
            <li className="flex gap-3">
              <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white text-sm font-medium flex-shrink-0">
                2
              </span>
              <span>Select each student from the dropdown and enter their score (0-100)</span>
            </li>
            <li className="flex gap-3">
              <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white text-sm font-medium flex-shrink-0">
                3
              </span>
              <span>Optionally add remarks for any student (e.g., "Excellent performance")</span>
            </li>
            <li className="flex gap-3">
              <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white text-sm font-medium flex-shrink-0">
                4
              </span>
              <span>Review all grades carefully and click "Submit Grades"</span>
            </li>
            <li className="flex gap-3">
              <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white text-sm font-medium flex-shrink-0">
                5
              </span>
              <span>Grades will be recorded immediately and visible to students</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  )
}
