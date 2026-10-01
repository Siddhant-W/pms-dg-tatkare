export type Weekday = 'MONDAY' | 'TUESDAY' | 'WEDNESDAY' | 'THURSDAY' | 'FRIDAY' | 'SATURDAY';
export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'NOT_MARKED';
export type ProxyStatus = 'PENDING' | 'ASSIGNED' | 'UNRESOLVED';
export type Role = 'ADMIN' | 'SUPERVISOR';

export interface Teacher { id: string; name: string; class_name: string | null; active: boolean; }
export interface TeacherWithAttendance extends Teacher { attendance_status: AttendanceStatus; }
export interface TimetableEntry { id: string; teacher_id: string; weekday: Weekday; period_number: number; subject: string | null; class_name: string | null; is_recess: boolean; is_free: boolean; time_start: string | null; time_end: string | null; }
export interface Attendance { id: string; teacher_id: string; date: string; status: AttendanceStatus; marked_at: string; }
export interface ProxyRequirement { id: string; date: string; period_number: number; absent_teacher_id: string; absent_teacher_name: string; class_name: string; subject: string | null; status: ProxyStatus; assigned_proxy_teacher_id: string | null; assigned_proxy_teacher_name: string | null; }
export interface ProxyAssignment { id: string; requirement_id: string; proxy_teacher_id: string; proxy_teacher_name: string; assigned_at: string; }
export interface ProxyCandidate {
  teacher_id: string;
  teacher_name: string;
  is_recommended: boolean;
  rank: number;
  class_match: 'exact' | 'same_standard' | null;
  subject_match: boolean;
  proxy_count_today: number;
  reasons: string[];
}
export interface ProxyAssignmentDetail {
  id: string;
  requirement_id: string;
  date: string;
  weekday: Weekday;
  period_number: number;
  class_name: string | null;
  subject: string | null;
  absent_teacher_id: string;
  absent_teacher_name: string | null;
  proxy_teacher_id: string;
  proxy_teacher_name: string | null;
  status: 'ASSIGNED' | 'CANCELLED';
  assigned_at: string;
  assigned_by_name: string | null;
  cancelled_at: string | null;
}
export interface ResetAllResult { date: string; cleared_absences: number; removed_requirements: number; cancelled_assignments: number; }
export interface AttendanceSummary { date: string; total: number; present: number; absent: number; not_marked: number; }
export interface TeacherCount { teacher_id: string; teacher_name: string; count: number; }
export interface DailyStats {
  date: string;
  absent_count: number;
  requirements_count: number;
  assigned_count: number;
  unresolved_count: number;
  avg_assignment_time_seconds: number | null;
  collision_attempts: number;
  most_frequently_absent_teachers: TeacherCount[];
  most_frequently_assigned_teachers: TeacherCount[];
  proxy_load_distribution: TeacherCount[];
}
export interface AuditEvent { id: string; event_type: string; entity_type: string; entity_id: string; metadata: Record<string, unknown>; created_at: string; actor_name: string | null; summary: string; }
