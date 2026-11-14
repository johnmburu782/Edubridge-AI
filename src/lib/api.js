const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const TOKEN_STORAGE_KEY = 'edubridge_access_token'

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function getStoredToken() {
  return sessionStorage.getItem(TOKEN_STORAGE_KEY)
}

function getDetailMessage(payload, status) {
  if (typeof payload?.detail === 'string') return payload.detail
  if (Array.isArray(payload?.detail)) {
    return payload.detail.map((issue) => issue.msg).join(' ')
  }
  return `Request failed (${status}).`
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers)
  headers.set('Accept', 'application/json')
  if (options.body) headers.set('Content-Type', 'application/json')

  const token = getStoredToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })
  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : null

  if (response.status === 502 && API_BASE_URL === '/api/v1') {
    throw new ApiError(
      'The API is not reachable at localhost:8000. Start FastAPI and make sure PostgreSQL is running at localhost:5432.',
      response.status,
    )
  }
  if (!response.ok) {
    throw new ApiError(getDetailMessage(payload, response.status), response.status)
  }
  if (!payload) {
    throw new ApiError('The API returned an invalid response.', response.status)
  }

  return payload
}

export function fetchDashboard(signal) {
  return request('/dashboard', { signal })
}

export function fetchSubjects(signal) {
  return request('/catalog/subjects', { signal })
}

export function fetchEnrollments(signal) {
  return request('/catalog/enrollments', { signal })
}

export function enrollInSubject(subjectId) {
  return request(`/catalog/subjects/${subjectId}/enroll`, { method: 'POST' })
}

export async function registerStudent(student) {
  const result = await request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(student),
  })
  sessionStorage.setItem(TOKEN_STORAGE_KEY, result.access_token)
  return result
}

export async function loginStudent(credentials) {
  const result = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
  sessionStorage.setItem(TOKEN_STORAGE_KEY, result.access_token)
  return result
}

export async function getCurrentStudent(signal) {
  if (!getStoredToken()) return null

  try {
    const result = await request('/auth/me', { signal })
    return result
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      sessionStorage.removeItem(TOKEN_STORAGE_KEY)
      return null
    }
    throw error
  }
}

export function logoutStudent() {
  sessionStorage.removeItem(TOKEN_STORAGE_KEY)
}
