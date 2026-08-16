import { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { academicApi } from "@/services/api/academic"
import { getErrorMessage } from "@/services/api/client"

export default function AcademicSetupPage() {
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [facultyForm, setFacultyForm] = useState({ name: "Faculty of Computing", code: "FOC", description: "Computing and digital systems" })
  const [departmentForm, setDepartmentForm] = useState({ faculty_id: "", name: "Computer Science", code: "CS" })
  const [programmeForm, setProgrammeForm] = useState({
    faculty_id: "",
    department_id: "",
    name: "BSc Computer Science",
    code: "BSC-CS",
    duration_years: 4,
    capacity_planned: 200,
  })
  const [courseForm, setCourseForm] = useState({
    code: "CSC101",
    name: "Introduction to Computing",
    description: "Foundations of computing",
    credit_hours: 3,
    course_type: "core",
  })
  const [calendarForm, setCalendarForm] = useState({
    academic_year: "2026/2027",
    semester: "Semester 1",
    registration_open: "2026-08-15T00:00:00",
    registration_close: "2026-09-30T00:00:00",
    exam_period_start: "2026-12-01T00:00:00",
    exam_period_end: "2026-12-20T00:00:00",
  })

  const [faculties, setFaculties] = useState<any[]>([])
  const [departments, setDepartments] = useState<any[]>([])
  const [programmes, setProgrammes] = useState<any[]>([])
  const [courses, setCourses] = useState<any[]>([])

  async function refreshLists() {
    try {
      const [facultyRes, programmeRes, courseRes] = await Promise.all([
        academicApi.listFaculties(),
        academicApi.listProgrammes(),
        academicApi.listCourses(),
      ])
      setFaculties(facultyRes)
      setProgrammes(programmeRes)
      setCourses(courseRes)

      if (facultyRes[0]?.id) {
        const deptRes = await academicApi.listDepartments(facultyRes[0].id)
        setDepartments(deptRes)
      } else {
        setDepartments([])
      }
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  useEffect(() => {
    void refreshLists()
  }, [])

  async function handleCreateFaculty(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    try {
      const res = await academicApi.createFaculty(facultyForm)
      setMessage(`Faculty created: ${res.name}`)
      await refreshLists()
      setFacultyForm({ ...facultyForm, name: "", code: "", description: "" })
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function handleCreateDepartment(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    try {
      if (!departmentForm.faculty_id) {
        throw new Error("Select a faculty before creating a department.")
      }
      const res = await academicApi.createDepartment(departmentForm)
      setMessage(`Department created: ${res.name}`)
      await refreshLists()
      setDepartmentForm({ faculty_id: departmentForm.faculty_id, name: "", code: "" })
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function handleCreateProgramme(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    try {
      if (!programmeForm.faculty_id || !programmeForm.department_id) {
        throw new Error("Select a faculty and department before creating a programme.")
      }
      const res = await academicApi.createProgramme({ ...programmeForm, duration_years: Number(programmeForm.duration_years), capacity_planned: Number(programmeForm.capacity_planned) })
      setMessage(`Programme created: ${res.name}`)
      await refreshLists()
      setProgrammeForm({ faculty_id: programmeForm.faculty_id, department_id: programmeForm.department_id, name: "", code: "", duration_years: 4, capacity_planned: 200 })
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function handleCreateCourse(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    try {
      const res = await academicApi.createCourse({ ...courseForm, credit_hours: Number(courseForm.credit_hours) })
      setMessage(`Course created: ${res.name}`)
      await refreshLists()
      setCourseForm({ code: "", name: "", description: "", credit_hours: 3, course_type: "core" })
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function handleCreateCalendar(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    try {
      const res = await academicApi.createAcademicCalendar(calendarForm)
      setMessage(`Academic calendar created for ${res.academic_year}`)
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">University Academic Setup</h1>
          <p className="text-cocoa-400 mb-6">Create the foundation for a university: faculties, departments, programmes, courses, and academic calendar.</p>
        </div>

        {message && <div className="rounded border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-700">{message}</div>}
        {error && <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

        <div className="grid gap-6 lg:grid-cols-2">
          <form onSubmit={handleCreateFaculty} className="space-y-3 rounded-lg border border-cocoa-100 p-4 bg-white">
            <h2 className="text-lg font-medium text-ink">Create Faculty</h2>
            <input className="w-full input" value={facultyForm.name} onChange={(e) => setFacultyForm({ ...facultyForm, name: e.target.value })} placeholder="Faculty name" />
            <input className="w-full input" value={facultyForm.code} onChange={(e) => setFacultyForm({ ...facultyForm, code: e.target.value })} placeholder="Faculty code" />
            <textarea className="w-full input min-h-[100px]" value={facultyForm.description} onChange={(e) => setFacultyForm({ ...facultyForm, description: e.target.value })} placeholder="Description" />
            <button type="submit" className="btn btn-primary">Save faculty</button>
          </form>

          <form onSubmit={handleCreateDepartment} className="space-y-3 rounded-lg border border-cocoa-100 p-4 bg-white">
            <h2 className="text-lg font-medium text-ink">Create Department</h2>
            <select className="w-full input" value={departmentForm.faculty_id} onChange={(e) => setDepartmentForm({ ...departmentForm, faculty_id: e.target.value })}>
              <option value="">Select faculty</option>
              {faculties.map((faculty) => (
                <option key={faculty.id} value={faculty.id}>{faculty.name}</option>
              ))}
            </select>
            <input className="w-full input" value={departmentForm.name} onChange={(e) => setDepartmentForm({ ...departmentForm, name: e.target.value })} placeholder="Department name" />
            <input className="w-full input" value={departmentForm.code} onChange={(e) => setDepartmentForm({ ...departmentForm, code: e.target.value })} placeholder="Department code" />
            <button type="submit" className="btn btn-primary">Save department</button>
          </form>

          <form onSubmit={handleCreateProgramme} className="space-y-3 rounded-lg border border-cocoa-100 p-4 bg-white">
            <h2 className="text-lg font-medium text-ink">Create Programme</h2>
            <select className="w-full input" value={programmeForm.faculty_id} onChange={(e) => setProgrammeForm({ ...programmeForm, faculty_id: e.target.value })}>
              <option value="">Select faculty</option>
              {faculties.map((faculty) => (
                <option key={faculty.id} value={faculty.id}>{faculty.name}</option>
              ))}
            </select>
            <select className="w-full input" value={programmeForm.department_id} onChange={(e) => setProgrammeForm({ ...programmeForm, department_id: e.target.value })}>
              <option value="">Select department</option>
              {departments.map((department) => (
                <option key={department.id} value={department.id}>{department.name}</option>
              ))}
            </select>
            <input className="w-full input" value={programmeForm.name} onChange={(e) => setProgrammeForm({ ...programmeForm, name: e.target.value })} placeholder="Programme name" />
            <input className="w-full input" value={programmeForm.code} onChange={(e) => setProgrammeForm({ ...programmeForm, code: e.target.value })} placeholder="Programme code" />
            <input type="number" className="w-full input" value={programmeForm.duration_years} onChange={(e) => setProgrammeForm({ ...programmeForm, duration_years: Number(e.target.value) })} placeholder="Duration years" />
            <input type="number" className="w-full input" value={programmeForm.capacity_planned} onChange={(e) => setProgrammeForm({ ...programmeForm, capacity_planned: Number(e.target.value) })} placeholder="Capacity" />
            <button type="submit" className="btn btn-primary">Save programme</button>
          </form>

          <form onSubmit={handleCreateCourse} className="space-y-3 rounded-lg border border-cocoa-100 p-4 bg-white">
            <h2 className="text-lg font-medium text-ink">Create Course</h2>
            <input className="w-full input" value={courseForm.code} onChange={(e) => setCourseForm({ ...courseForm, code: e.target.value })} placeholder="Course code" />
            <input className="w-full input" value={courseForm.name} onChange={(e) => setCourseForm({ ...courseForm, name: e.target.value })} placeholder="Course name" />
            <textarea className="w-full input min-h-[100px]" value={courseForm.description} onChange={(e) => setCourseForm({ ...courseForm, description: e.target.value })} placeholder="Description" />
            <input type="number" className="w-full input" value={courseForm.credit_hours} onChange={(e) => setCourseForm({ ...courseForm, credit_hours: Number(e.target.value) })} placeholder="Credit hours" />
            <select className="w-full input" value={courseForm.course_type} onChange={(e) => setCourseForm({ ...courseForm, course_type: e.target.value })}>
              <option value="core">Core</option>
              <option value="elective">Elective</option>
              <option value="general">General</option>
            </select>
            <button type="submit" className="btn btn-primary">Save course</button>
          </form>

          <form onSubmit={handleCreateCalendar} className="space-y-3 rounded-lg border border-cocoa-100 p-4 bg-white lg:col-span-2">
            <h2 className="text-lg font-medium text-ink">Create Academic Calendar</h2>
            <div className="grid gap-3 md:grid-cols-2">
              <input className="w-full input" value={calendarForm.academic_year} onChange={(e) => setCalendarForm({ ...calendarForm, academic_year: e.target.value })} placeholder="Academic year" />
              <input className="w-full input" value={calendarForm.semester} onChange={(e) => setCalendarForm({ ...calendarForm, semester: e.target.value })} placeholder="Semester" />
              <input type="datetime-local" className="w-full input" value={calendarForm.registration_open} onChange={(e) => setCalendarForm({ ...calendarForm, registration_open: e.target.value })} />
              <input type="datetime-local" className="w-full input" value={calendarForm.registration_close} onChange={(e) => setCalendarForm({ ...calendarForm, registration_close: e.target.value })} />
              <input type="datetime-local" className="w-full input" value={calendarForm.exam_period_start} onChange={(e) => setCalendarForm({ ...calendarForm, exam_period_start: e.target.value })} />
              <input type="datetime-local" className="w-full input" value={calendarForm.exam_period_end} onChange={(e) => setCalendarForm({ ...calendarForm, exam_period_end: e.target.value })} />
            </div>
            <button type="submit" className="btn btn-primary">Save academic calendar</button>
          </form>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          <div className="rounded-lg border border-cocoa-100 bg-white p-4">
            <h3 className="font-medium text-ink mb-2">Faculties</h3>
            <ul className="space-y-2 text-sm text-cocoa-600">
              {faculties.length ? faculties.map((faculty) => <li key={faculty.id}>{faculty.name} ({faculty.code})</li>) : <li>No faculties yet.</li>}
            </ul>
          </div>

          <div className="rounded-lg border border-cocoa-100 bg-white p-4">
            <h3 className="font-medium text-ink mb-2">Departments</h3>
            <ul className="space-y-2 text-sm text-cocoa-600">
              {departments.length ? departments.map((department) => <li key={department.id}>{department.name} ({department.code})</li>) : <li>No departments yet.</li>}
            </ul>
          </div>

          <div className="rounded-lg border border-cocoa-100 bg-white p-4">
            <h3 className="font-medium text-ink mb-2">Programmes</h3>
            <ul className="space-y-2 text-sm text-cocoa-600">
              {programmes.length ? programmes.map((programme) => <li key={programme.id}>{programme.name} ({programme.code})</li>) : <li>No programmes yet.</li>}
            </ul>
          </div>
        </div>
      </div>
    </AppShell>
  )
}
