import { useEffect, useState } from 'react'
import {
  ArrowRight,
  BookOpen,
  BrainCircuit,
  BriefcaseBusiness,
  CalendarCheck2,
  CheckCircle2,
  Clock3,
  Dna,
  Download,
  FlaskConical,
  FileText,
  GraduationCap,
  LogOut,
  Sigma,
  ShieldCheck,
  Sparkles,
  Star,
  Target,
  X,
} from 'lucide-react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  fetchDashboard,
  fetchEnrollments,
  fetchSubjects,
  getCurrentStudent,
  enrollInSubject,
  loginStudent,
  logoutStudent,
  registerStudent,
} from './lib/api.js'
import { demoDashboard } from './lib/demoDashboard.js'
import './App.css'

const statIcons = {
  calendar: CalendarCheck2,
  target: Target,
  file: FileText,
  briefcase: BriefcaseBusiness,
}

const subjectIcons = {
  mathematics: Sigma,
  chemistry: FlaskConical,
  biology: Dna,
}

const features = [
  {
    icon: BrainCircuit,
    title: 'AI tutor',
    text: 'Get guided explanations for tough topics, step-by-step study prompts, and quick review recaps.',
  },
  {
    icon: BookOpen,
    title: 'Smart resources',
    text: 'Build a focused learning path with curated notes, exam guides, and subject-specific recommendations.',
  },
  {
    icon: ShieldCheck,
    title: 'Opportunity discovery',
    text: 'Review scholarships, internships, and programs with source status and application deadlines.',
  },
]

function App() {
  const [dashboard, setDashboard] = useState(null)
  const [dashboardError, setDashboardError] = useState('')
  const [isUsingDemoData, setIsUsingDemoData] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [refreshKey, setRefreshKey] = useState(0)
  const [authenticatedUser, setAuthenticatedUser] = useState(null)
  const [authMode, setAuthMode] = useState(null)
  const [authError, setAuthError] = useState('')
  const [isSubmittingAuth, setIsSubmittingAuth] = useState(false)
  const [sessionError, setSessionError] = useState('')
  const [subjects, setSubjects] = useState([])
  const [isLoadingSubjects, setIsLoadingSubjects] = useState(true)
  const [catalogError, setCatalogError] = useState('')
  const [catalogRefreshKey, setCatalogRefreshKey] = useState(0)
  const [enrolledSubjectIds, setEnrolledSubjectIds] = useState([])
  const [enrollingSubjectId, setEnrollingSubjectId] = useState(null)
  const [enrollmentError, setEnrollmentError] = useState('')
  const [expandedSubjectIds, setExpandedSubjectIds] = useState([])

  useEffect(() => {
    const controller = new AbortController()

    async function loadDashboard() {
      setIsLoading(true)
      setDashboardError('')
      try {
        const data = await fetchDashboard(controller.signal)
        setDashboard(data)
        setIsUsingDemoData(false)
      } catch (error) {
        if (controller.signal.aborted) return
        setDashboard(demoDashboard)
        setIsUsingDemoData(true)
        setDashboardError(error instanceof Error ? error.message : 'Unable to load dashboard data.')
      } finally {
        if (!controller.signal.aborted) setIsLoading(false)
      }
    }

    loadDashboard()
    return () => controller.abort()
  }, [refreshKey])

  useEffect(() => {
    const controller = new AbortController()

    async function loadSubjects() {
      setIsLoadingSubjects(true)
      setCatalogError('')
      try {
        const data = await fetchSubjects(controller.signal)
        setSubjects(data)
      } catch (error) {
        if (controller.signal.aborted) return
        setCatalogError(error instanceof Error ? error.message : 'Unable to load subjects.')
      } finally {
        if (!controller.signal.aborted) setIsLoadingSubjects(false)
      }
    }

    loadSubjects()
    return () => controller.abort()
  }, [catalogRefreshKey])

  useEffect(() => {
    const controller = new AbortController()

    async function restoreSession() {
      try {
        const user = await getCurrentStudent(controller.signal)
        if (!controller.signal.aborted) {
          setAuthenticatedUser(user)
          setSessionError('')
        }
      } catch {
        if (!controller.signal.aborted) {
          setAuthenticatedUser(null)
          setSessionError('Your saved sign-in could not be verified. Try again when the API is available.')
        }
      }
    }

    restoreSession()
    return () => controller.abort()
  }, [refreshKey])

  useEffect(() => {
    if (!authenticatedUser) return undefined

    const controller = new AbortController()
    async function loadEnrollments() {
      try {
        const result = await fetchEnrollments(controller.signal)
        if (!controller.signal.aborted) {
          setEnrolledSubjectIds(result.enrollments.map(({ subject_id }) => subject_id))
          setEnrollmentError('')
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          setEnrollmentError(error instanceof Error ? error.message : 'Unable to load enrollments.')
        }
      }
    }

    loadEnrollments()
    return () => controller.abort()
  }, [authenticatedUser, refreshKey])

  function openAuth(mode) {
    setAuthError('')
    setAuthMode(mode)
  }

  async function handleAuthSubmit(event) {
    event.preventDefault()
    if (!authMode) return

    const formData = new FormData(event.currentTarget)
    const email = String(formData.get('email') || '').trim()
    const password = String(formData.get('password') || '')
    setAuthError('')
    setIsSubmittingAuth(true)

    try {
      const result = authMode === 'register'
        ? await registerStudent({
            display_name: String(formData.get('display_name') || '').trim(),
            email,
            password,
          })
        : await loginStudent({ email, password })

      setAuthenticatedUser(result.user)
      setSessionError('')
      setAuthMode(null)
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Unable to authenticate. Please try again.')
    } finally {
      setIsSubmittingAuth(false)
    }
  }

  function handleLogout() {
    logoutStudent()
    setAuthenticatedUser(null)
    setEnrolledSubjectIds([])
    setSessionError('')
  }

  async function handleEnroll(subjectId) {
    if (!authenticatedUser) {
      openAuth('login')
      return
    }

    setEnrollingSubjectId(subjectId)
    setEnrollmentError('')
    try {
      const enrollment = await enrollInSubject(subjectId)
      setEnrolledSubjectIds((currentIds) => (
        currentIds.includes(enrollment.subject_id)
          ? currentIds
          : [...currentIds, enrollment.subject_id]
      ))
    } catch (error) {
      setEnrollmentError(error instanceof Error ? error.message : 'Unable to enroll in this subject.')
    } finally {
      setEnrollingSubjectId(null)
    }
  }

  function toggleCurriculum(subjectId) {
    setExpandedSubjectIds((currentIds) => (
      currentIds.includes(subjectId)
        ? currentIds.filter((id) => id !== subjectId)
        : [...currentIds, subjectId]
    ))
  }

  function startSubject(subjectId) {
    setExpandedSubjectIds((currentIds) => (
      currentIds.includes(subjectId) ? currentIds : [...currentIds, subjectId]
    ))
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-wrap">
          <div className="brand-mark">
            <GraduationCap size={20} />
          </div>
          <div>
            <p className="brand-name">EduBridge AI</p>
            <span className="brand-tag">Student success platform</span>
          </div>
        </div>

        <nav className="nav" aria-label="Main navigation">
          <a href="#features">Features</a>
          <a href="#progress">Progress</a>
          <a href="#learning-paths">Subjects</a>
          <a href="#opportunities">Opportunities</a>
        </nav>

        <div className="topbar-actions">
          {authenticatedUser ? (
            <>
              <span className="welcome-name">Hi, {authenticatedUser.display_name}</span>
              <button type="button" className="nav-button subtle" onClick={handleLogout}>
                <LogOut size={16} /> Log out
              </button>
            </>
          ) : (
            <>
              <button type="button" className="nav-button subtle" onClick={() => openAuth('login')}>Log in</button>
              <button type="button" className="nav-button primary" onClick={() => openAuth('register')}>
                Get started <ArrowRight size={16} />
              </button>
            </>
          )}
        </div>
      </header>

      <main className="main-content">
        <div className={`connection-banner ${dashboardError ? 'error' : ''}`} role="status" aria-live="polite">
          {isLoading ? (
            <span>Connecting to EduBridge dashboard…</span>
          ) : isUsingDemoData ? (
            <>
              <span>Backend unavailable — showing local demo data. {dashboardError}</span>
              <button type="button" onClick={() => setRefreshKey((key) => key + 1)}>Retry</button>
            </>
          ) : (
            <>
              <span><CheckCircle2 size={16} /> Dashboard loaded from the database · Demo data</span>
              <button type="button" onClick={() => setRefreshKey((key) => key + 1)}>Refresh</button>
            </>
          )}
        </div>

        <section className="hero-panel">
          <div className="hero-copy">
            <span className="eyebrow">
              <Sparkles size={14} />
              Guided study, clarity, and opportunity
            </span>
            <h1>Turn learning goals into measurable momentum.</h1>
            <p>
              EduBridge AI helps students plan smarter, stay consistent, and discover opportunities with clear source information.
            </p>

            <div className="cta-row">
              <button type="button" className="nav-button primary large" onClick={() => openAuth('register')}>
                Start learning <ArrowRight size={18} />
              </button>
              <button
                type="button"
                className="nav-button subtle large"
                onClick={() => document.getElementById('progress')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Explore dashboard
              </button>
            </div>

            <div className="trust-row" aria-label="Key data points">
              <div>
                <strong>AI-guided</strong>
                <span>learning support</span>
              </div>
              <div>
                <strong>Student-first</strong>
                <span>study experience</span>
              </div>
              <div>
                <strong>Clear sources</strong>
                <span>for opportunities</span>
              </div>
            </div>
          </div>

          <div className="hero-visual" aria-label="Overview dashboard preview">
            <div className="mini-card accent-card">
              <div className="mini-header">
                <span className="dot" />
                <span>Latest progress</span>
              </div>
              <strong>
                {dashboard ? `${dashboard.weekly_progress.at(-1)?.score ?? '—'}%` : '—'}
              </strong>
              <small>From the most recent saved progress point</small>
            </div>

            <div className="mini-card overview-card">
              <div className="mini-row">
                <span>AI tutor</span>
                <CheckCircle2 size={16} />
              </div>
              <p>
                {dashboard
                  ? `${dashboard.study_plan.length} study sessions in your plan`
                  : 'Study plan loads from your dashboard'}
              </p>
            </div>

            <div className="mini-card floating-card">
              <div className="mini-row">
                <span>Next opportunity</span>
                <Star size={14} />
              </div>
              <strong>{dashboard?.opportunities[0]?.priority ?? 'Loading'}</strong>
            </div>
          </div>
        </section>

        <section className="stats-grid" aria-label="Student statistics">
          {dashboard ? dashboard.stats.map(({ label, value, icon }) => {
            const Icon = statIcons[icon]
            return (
              <article className="stat-card" key={label}>
                <div className="stat-icon"><Icon size={18} /></div>
                <div>
                  <strong>{value}</strong>
                  <span>{label}</span>
                </div>
              </article>
            )
          }) : <p className="data-message">{isLoading ? 'Loading your dashboard…' : 'Dashboard data is unavailable.'}</p>}
        </section>

        <section id="features" className="content-section">
          <div className="section-heading">
            <span className="eyebrow muted">
              <Target size={14} />
              Built for momentum
            </span>
            <h2>Everything students need to stay focused.</h2>
          </div>

          <div className="feature-grid">
            {features.map(({ icon: Icon, title, text }) => (
              <article className="feature-card" key={title}>
                <div className="feature-icon">
                  <Icon size={20} />
                </div>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="progress" className="dashboard-panel">
          <div className="panel-column">
            <div className="section-heading compact">
              <span className="eyebrow muted">
                <Clock3 size={14} />
                This week
              </span>
              <h2>Study plan</h2>
            </div>

            <div className="study-list">
              {dashboard ? dashboard.study_plan.map(({ title, time, status, accent }) => (
                <div className={`study-item ${accent}`} key={title}>
                  <div className="study-bullet" />
                  <div className="study-copy">
                    <strong>{title}</strong>
                    <span>{time}</span>
                  </div>
                  <span className="status-pill">{status}</span>
                </div>
              )) : <p className="data-message">{isLoading ? 'Loading study plan…' : 'Study plan is unavailable.'}</p>}
            </div>
          </div>

          <div className="panel-column chart-box">
            <div className="section-heading compact">
              <span className="eyebrow muted">
                <BookOpen size={14} />
                Progress
              </span>
              <h2>Performance trend</h2>
            </div>

            <div className="chart-wrap">
              {dashboard ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={dashboard.weekly_progress} margin={{ top: 18, right: 12, left: -18, bottom: 0 }}>
                    <defs>
                      <linearGradient id="scoreFill" x1="0" x2="0" y1="0" y2="1">
                        <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.7} />
                        <stop offset="95%" stopColor="#7c3aed" stopOpacity={0.08} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke="rgba(148,163,184,0.18)" vertical={false} />
                    <XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} domain={[50, 100]} />
                    <Tooltip
                      contentStyle={{
                        background: '#0f172a',
                        border: '1px solid rgba(148,163,184,0.3)',
                        borderRadius: 12,
                        color: '#e2e8f0',
                      }}
                    />
                    <Area type="monotone" dataKey="score" stroke="#8b5cf6" strokeWidth={3} fill="url(#scoreFill)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : <p className="data-message">{isLoading ? 'Loading performance…' : 'Performance data is unavailable.'}</p>}
            </div>
          </div>
        </section>

        <section id="learning-paths" className="catalog-section">
          <div className="section-heading">
            <span className="eyebrow muted">
              <BookOpen size={14} />
              Learning paths
            </span>
            <h2>Choose a subject to study.</h2>
            <p className="catalog-intro">
              Enroll in a subject to access its topics and learning units.
            </p>
          </div>

          {enrollmentError && <p className="auth-error catalog-error" role="alert">{enrollmentError}</p>}

          {isLoadingSubjects ? (
            <p className="data-message">Loading subjects…</p>
          ) : catalogError ? (
            <div className="catalog-load-error" role="alert">
              <p>{catalogError}</p>
              <button
                type="button"
                className="nav-button subtle"
                onClick={() => setCatalogRefreshKey((key) => key + 1)}
              >
                Retry
              </button>
            </div>
          ) : (
            <div className="subject-grid">
              {subjects.map((subject) => {
                const SubjectIcon = subjectIcons[subject.slug] || BookOpen
                const unitCount = subject.topics.reduce((count, topic) => count + topic.units.length, 0)
                const isEnrolled = enrolledSubjectIds.includes(subject.id)
                const isEnrolling = enrollingSubjectId === subject.id
                const isCurriculumOpen = expandedSubjectIds.includes(subject.id)

                return (
                  <article className="subject-card" key={subject.id}>
                    <div className="subject-card-header">
                      <div className="subject-icon"><SubjectIcon size={22} /></div>
                      <span className="subject-level">{subject.level}</span>
                    </div>
                    <h3>{subject.title}</h3>
                    <p className="subject-description">{subject.description}</p>
                    <div className="subject-counts">
                      <span>{subject.topics.length} topics</span>
                      <span>{unitCount} units</span>
                    </div>

                    {subject.pdf_url && (
                      <div className="subject-resource">
                        <a
                          className="nav-button subtle download-button"
                          href={subject.pdf_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          aria-label={`Download ${subject.pdf_title || subject.title} PDF`}
                        >
                          <Download size={16} />
                          Download PDF
                        </a>
                        <p className="resource-attribution">
                          {subject.pdf_title || subject.title}
                          {subject.pdf_source && <> by {subject.pdf_source}</>}
                          {subject.pdf_source_url && (
                            <>
                              {' · '}
                              <a href={subject.pdf_source_url} target="_blank" rel="noopener noreferrer">
                                Source
                              </a>
                            </>
                          )}
                          {subject.pdf_license_url && (
                            <>
                              {' · '}
                              <a href={subject.pdf_license_url} target="_blank" rel="noopener noreferrer">
                                {subject.pdf_license}
                              </a>
                            </>
                          )}
                        </p>
                      </div>
                    )}

                    <details className="curriculum-details" open={isCurriculumOpen}>
                      <summary onClick={(event) => {
                        event.preventDefault()
                        toggleCurriculum(subject.id)
                      }}>
                        {isCurriculumOpen ? 'Hide topics and units' : 'View topics and units'}
                      </summary>
                      <div className="topic-list">
                        {subject.topics.map((topic) => (
                          <article className="topic-item" key={topic.id}>
                            <div className="topic-heading">
                              <h4>{topic.title}</h4>
                              {topic.video_url && (
                                <a
                                  className="video-link"
                                  href={topic.video_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  aria-label={`Watch ${topic.video_title || topic.title} on ${topic.video_source || 'YouTube'}`}
                                >
                                  Watch topic video
                                </a>
                              )}
                            </div>
                            <p>{topic.description}</p>
                            <ul>
                              {topic.units.map((unit) => (
                                <li key={unit.id}>
                                  <span className="unit-title">{unit.title}</span>
                                  <span className="unit-meta">
                                    <span className="unit-duration">{unit.duration_minutes} min</span>
                                    {unit.video_url && (
                                      <a
                                        className="video-link"
                                        href={unit.video_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        aria-label={`Watch ${unit.video_title || unit.title} on ${unit.video_source || 'YouTube'}`}
                                      >
                                        Watch video
                                      </a>
                                    )}
                                  </span>
                                </li>
                              ))}
                            </ul>
                          </article>
                        ))}
                      </div>
                    </details>

                    <div className="subject-actions">
                      {isEnrolled ? (
                        <>
                          <span className="enrollment-status">
                            <CheckCircle2 size={16} /> Enrolled
                          </span>
                          <button
                            type="button"
                            className="nav-button primary start-button"
                            onClick={() => startSubject(subject.id)}
                          >
                            <BookOpen size={16} />
                            Start learning
                          </button>
                        </>
                      ) : (
                        <button
                          type="button"
                          className="nav-button primary enroll-button"
                          disabled={enrollingSubjectId !== null}
                          onClick={() => handleEnroll(subject.id)}
                        >
                          {isEnrolling
                            ? 'Enrolling…'
                            : authenticatedUser
                              ? 'Enroll in subject'
                              : 'Log in to enroll'}
                        </button>
                      )}
                    </div>
                  </article>
                )
              })}
            </div>
          )}
        </section>

        <section id="opportunities" className="bottom-grid">
          <div className="opportunity-panel">
            <div className="section-heading compact">
              <span className="eyebrow muted">
                <BriefcaseBusiness size={14} />
                Opportunities
              </span>
              <h2>Recommended next moves</h2>
            </div>

            <div className="opportunity-list">
              {dashboard ? dashboard.opportunities.map(({ title, detail, priority }) => (
                <div className="opportunity-item" key={title}>
                  <div>
                    <strong>{title}</strong>
                    <p>{detail}</p>
                  </div>
                  <span className="priority-tag">{priority}</span>
                </div>
              )) : <p className="data-message">{isLoading ? 'Loading opportunities…' : 'Opportunities are unavailable.'}</p>}
            </div>
          </div>

          <aside className="checklist-panel">
            <div className="section-heading compact">
              <span className="eyebrow muted">
                <CheckCircle2 size={14} />
                Today
              </span>
              <h2>Focus checklist</h2>
            </div>

            <ul className="checklist">
              {dashboard ? dashboard.today_checklist.map((item) => (
                <li key={item}>
                  <span className="checkmark">
                    <CheckCircle2 size={16} />
                  </span>
                  <span>{item}</span>
                </li>
              )) : <li className="data-message">{isLoading ? 'Loading checklist…' : 'Checklist is unavailable.'}</li>}
            </ul>
          </aside>
        </section>
      </main>

      {sessionError && (
        <p className="session-notice" role="status">{sessionError}</p>
      )}

      {authMode && (
        <div
          className="auth-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setAuthMode(null)
          }}
        >
          <section className="auth-dialog" role="dialog" aria-modal="true" aria-labelledby="auth-title">
            <button
              type="button"
              className="auth-close"
              aria-label="Close dialog"
              onClick={() => setAuthMode(null)}
            >
              <X size={20} />
            </button>
            <div className="brand-mark auth-brand"><GraduationCap size={20} /></div>
            <p className="auth-kicker">EduBridge AI student account</p>
            <h2 id="auth-title">{authMode === 'register' ? 'Create your account' : 'Welcome back'}</h2>
            <p className="auth-description">
              {authMode === 'register'
                ? 'Sign up to start your learning journey.'
                : 'Log in to continue to your learning dashboard.'}
            </p>

            <form className="auth-form" onSubmit={handleAuthSubmit}>
              {authMode === 'register' && (
                <label>
                  Full name
                  <input
                    name="display_name"
                    type="text"
                    autoComplete="name"
                    minLength="1"
                    maxLength="100"
                    required
                    autoFocus
                  />
                </label>
              )}
              <label>
                Email address
                <input
                  name="email"
                  type="email"
                  autoComplete="email"
                  maxLength="320"
                  required
                  autoFocus={authMode === 'login'}
                />
              </label>
              <label>
                Password
                <input
                  name="password"
                  type="password"
                  autoComplete={authMode === 'register' ? 'new-password' : 'current-password'}
                  minLength={authMode === 'register' ? 8 : 1}
                  maxLength="128"
                  required
                />
              </label>

              {authError && <p className="auth-error" role="alert">{authError}</p>}

              <button type="submit" className="nav-button primary auth-submit" disabled={isSubmittingAuth}>
                {isSubmittingAuth
                  ? 'Please wait…'
                  : authMode === 'register'
                    ? 'Create account'
                    : 'Log in'}
              </button>
            </form>

            <p className="auth-switch">
              {authMode === 'register' ? 'Already have an account?' : 'New to EduBridge AI?'}
              {' '}
              <button
                type="button"
                onClick={() => openAuth(authMode === 'register' ? 'login' : 'register')}
              >
                {authMode === 'register' ? 'Log in' : 'Get started'}
              </button>
            </p>
          </section>
        </div>
      )}
    </div>
  )
}

export default App
