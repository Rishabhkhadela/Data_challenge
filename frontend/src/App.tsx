import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  FileText,
  Search,
  Trophy,
  User,
  ArrowLeftRight,
  BarChart3,
  Brain,
  Settings,
  Download,
  Loader2,
  Sparkles,
  Filter,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  Briefcase,
  GraduationCap,
  Award
} from 'lucide-react';

const getRecommendationColor = (rating: string) => {
  if (rating.includes("STRONG")) return '#22c55e';
  if (rating.includes("INTERVIEW")) return '#3b82f6';
  return '#eab308';
};
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

const API_URL = 'http://localhost:8000/api';

// Types
interface Weights {
  skill: number;
  behavior: number;
  career: number;
  experience: number;
}

interface SettingsState {
  weights: Weights;
  dataset_mode: string;
  jd_text: string;
}

interface Requirements {
  skills: string[];
  experience: string[];
  behavior_traits: string[];
  leadership_requirements: string[];
}

interface CandidateBrief {
  candidate_id: string;
  anonymized_name: string;
  headline: string;
  summary: string;
  years_of_experience: number;
  location: string;
  country: string;
  notice_period_days: number;
  preferred_work_mode: string;
  match_score: number;
  skill_score: number;
  behavior_score: number;
  career_score: number;
  experience_score: number;
}

interface CandidateDetails {
  candidate_id: string;
  anonymized_name: string;
  headline: string;
  summary: string;
  years_of_experience: number;
  location: string;
  country: string;
  notice_period_days: number;
  preferred_work_mode: string;
  expected_salary_min: number | null;
  expected_salary_max: number | null;
  github_activity_score: number | null;
  profile_completeness_score: number | null;
  match_score: number;
  skill_score: number;
  behavior_score: number;
  career_score: number;
  experience_score: number;
  key_strengths: string[];
  risks_gaps: string[];
  recommendation: string;
  career_history: any[];
  education: any[];
  skills: any[];
  certifications: any[];
  languages: any[];
  assessments: Record<string, number>;
}

export default function App() {
  const [currentView, setCurrentView] = useState<string>('Dashboard');
  const [settings, setSettings] = useState<SettingsState | null>(null);
  const [requirements, setRequirements] = useState<Requirements | null>(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Global settings fetching
  const fetchSettings = async () => {
    try {
      const res = await fetch(`${API_URL}/settings`);
      const data = await res.json();
      setSettings(data);
    } catch (e) {
      console.error("Failed to fetch settings", e);
    }
  };

  const fetchRequirements = async () => {
    try {
      const res = await fetch(`${API_URL}/job/requirements`);
      const data = await res.json();
      setRequirements(data);
    } catch (e) {
      console.error("Failed to fetch requirements", e);
    }
  };

  useEffect(() => {
    fetchSettings();
    fetchRequirements();
  }, []);

  const triggerToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3000);
  };

  // Views Router
  const renderView = () => {
    switch (currentView) {
      case 'Dashboard':
        return <DashboardView />;
      case 'Job Description':
        return <JobParserView requirements={requirements} setRequirements={setRequirements} triggerToast={triggerToast} />;
      case 'Candidate Search':
        return (
          <CandidateSearchView
            setSelectedCandidateId={setSelectedCandidateId}
            setCurrentView={setCurrentView}
            compareIds={compareIds}
            setCompareIds={setCompareIds}
            triggerToast={triggerToast}
          />
        );
      case 'Candidate Rankings':
        return (
          <CandidateRankingsView
            setSelectedCandidateId={setSelectedCandidateId}
            setCurrentView={setCurrentView}
            triggerToast={triggerToast}
          />
        );
      case 'Candidate Details':
        return (
          <CandidateDetailsView
            selectedCandidateId={selectedCandidateId}
            setSelectedCandidateId={setSelectedCandidateId}
          />
        );
      case 'Candidate Comparison':
        return (
          <CandidateComparisonView
            compareIds={compareIds}
            setCompareIds={setCompareIds}
          />
        );
      case 'Analytics':
        return <AnalyticsView />;
      case 'AI Insights':
        return (
          <AIInsightsView
            setSelectedCandidateId={setSelectedCandidateId}
            setCurrentView={setCurrentView}
          />
        );
      case 'Settings':
        return (
          <SettingsView
            settings={settings}
            fetchSettings={fetchSettings}
            triggerToast={triggerToast}
          />
        );
      default:
        return <DashboardView />;
    }
  };

  return (
    <div className="app-container">
      {/* Toast Alert */}
      {toastMessage && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          backgroundColor: 'rgba(30, 41, 59, 0.95)',
          border: '1px solid #38bdf8',
          boxShadow: '0 0 15px rgba(56, 189, 248, 0.4)',
          borderRadius: '8px',
          padding: '1rem 1.5rem',
          color: '#fff',
          zIndex: 9999,
          fontWeight: 600,
          animation: 'fadeIn 0.2s ease-out'
        }}>
          {toastMessage}
        </div>
      )}

      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Redrob AI</h2>
          <p>Hiring Intelligence</p>
        </div>

        <ul className="nav-menu">
          <li
            className={`nav-item ${currentView === 'Dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('Dashboard')}
          >
            <LayoutDashboard size={20} />
            Dashboard
          </li>
          <li
            className={`nav-item ${currentView === 'Job Description' ? 'active' : ''}`}
            onClick={() => setCurrentView('Job Description')}
          >
            <FileText size={20} />
            Job Description
          </li>
          <li
            className={`nav-item ${currentView === 'Candidate Search' ? 'active' : ''}`}
            onClick={() => setCurrentView('Candidate Search')}
          >
            <Search size={20} />
            Candidate Search
          </li>
          <li
            className={`nav-item ${currentView === 'Candidate Rankings' ? 'active' : ''}`}
            onClick={() => setCurrentView('Candidate Rankings')}
          >
            <Trophy size={20} />
            Candidate Rankings
          </li>
          <li
            className={`nav-item ${currentView === 'Candidate Details' ? 'active' : ''}`}
            onClick={() => setCurrentView('Candidate Details')}
          >
            <User size={20} />
            Candidate Details
          </li>
          <li
            className={`nav-item ${currentView === 'Candidate Comparison' ? 'active' : ''}`}
            onClick={() => setCurrentView('Candidate Comparison')}
          >
            <ArrowLeftRight size={20} />
            Comparison
          </li>
          <li
            className={`nav-item ${currentView === 'Analytics' ? 'active' : ''}`}
            onClick={() => setCurrentView('Analytics')}
          >
            <BarChart3 size={20} />
            Analytics
          </li>
          <li
            className={`nav-item ${currentView === 'AI Insights' ? 'active' : ''}`}
            onClick={() => setCurrentView('AI Insights')}
          >
            <Brain size={20} />
            AI Insights
          </li>
          <li
            className={`nav-item ${currentView === 'Settings' ? 'active' : ''}`}
            onClick={() => setCurrentView('Settings')}
          >
            <Settings size={20} />
            Settings
          </li>
        </ul>

        <div className="sidebar-footer">
          Version 0.1.0 | Env: {settings?.dataset_mode.toUpperCase() || 'LOCAL'}<br />
          India Runs Challenge 2026
        </div>
      </aside>

      {/* Main Panel Content */}
      <main className="main-content">
        {renderView()}
      </main>
    </div>
  );
}

// ----------------------------------------------------
// 1. Dashboard View
// ----------------------------------------------------
function DashboardView() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/analytics`)
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => console.error(e));
  }, []);

  if (loading || !data) {
    return (
      <div className="w-full flex align-center justify-center flex-col animate-fade" style={{ height: '70vh' }}>
        <Loader2 className="animate-spin text-accent" size={48} style={{ color: '#38bdf8' }} />
        <p className="mt-4 text-secondary">Loading dashboard distribution profiles...</p>
      </div>
    );
  }

  const COLORS = ['#2dd4bf', '#38bdf8', '#818cf8', '#a78bfa', '#f472b6'];

  return (
    <div className="animate-fade">
      <header className="view-header">
        <h1>Executive Dashboard</h1>
        <p>High-level candidate metrics and distribution profiles</p>
      </header>

      {/* KPIs Row */}
      <div className="grid-cols-4">
        <div className="glass-panel metric-card">
          <span className="metric-label">Total Candidates</span>
          <span className="metric-value">{data.kpis.total_candidates.toLocaleString()}</span>
          <span className="metric-change positive">Active pool</span>
        </div>
        <div className="glass-panel metric-card">
          <span className="metric-label">Average Experience</span>
          <span className="metric-value">{data.kpis.avg_experience} Yrs</span>
          <span className="metric-change positive">Aligned tenure</span>
        </div>
        <div className="glass-panel metric-card">
          <span className="metric-label">Avg Profile Completeness</span>
          <span className="metric-value">{data.kpis.avg_profile_match}%</span>
          <span className="metric-change positive">Reliable signal</span>
        </div>
        <div className="glass-panel metric-card">
          <span className="metric-label">Highly Onboarding ready</span>
          <span className="metric-value">{data.kpis.highly_responsive}%</span>
          <span className="metric-change positive">Notice period ≤ 30 days</span>
        </div>
      </div>

      {/* Charts Grid Row 1 */}
      <div className="grid-cols-2">
        <div className="glass-panel">
          <h3 className="mb-4">Experience Distribution</h3>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={data.experience_distribution}>
                <XAxis dataKey="label" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
                <Bar dataKey="count" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel">
          <h3 className="mb-4">Preferred Work Mode</h3>
          <div style={{ width: '100%', height: 260 }} className="flex align-center justify-center">
            <ResponsiveContainer width="60%" height="100%">
              <PieChart>
                <Pie
                  data={data.work_mode_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="label"
                >
                  {data.work_mode_distribution.map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-col gap-2 justify-center" style={{ minWidth: '120px' }}>
              {data.work_mode_distribution.map((entry: any, index: number) => (
                <div key={entry.label} className="flex align-center gap-2 text-secondary" style={{ fontSize: '0.85rem' }}>
                  <span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', backgroundColor: COLORS[index % COLORS.length] }}></span>
                  <span style={{ textTransform: 'capitalize' }}>{entry.label} ({entry.count})</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid Row 2 */}
      <div className="grid-cols-2">
        <div className="glass-panel">
          <h3 className="mb-4">Top Geographic Distribution</h3>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={data.country_distribution} layout="vertical">
                <XAxis type="number" stroke="#64748b" />
                <YAxis dataKey="label" type="category" stroke="#64748b" width={80} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
                <Bar dataKey="count" fill="#2dd4bf" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel">
          <h3 className="mb-4">Notice Period Breakdown</h3>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={data.notice_period_distribution.slice(0, 10)}>
                <XAxis dataKey="label" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
                <Bar dataKey="count" fill="#818cf8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// 2. Job Description Parser View
// ----------------------------------------------------
const DEFAULT_JD_TEXT = `Role: Senior AI Engineer (Founding Team)
Company: Redrob AI
Location: Bangalore / Hybrid

We are looking for a Senior AI Engineer to join our founding team. You will lead the development of our candidate search, dense vector retrieval, and LLM-based ranking engines.

Requirements:
- 5-9 years of production software engineering experience, specifically building AI/ML systems.
- Strong proficiency in Python, PyTorch, HuggingFace transformers, and vector databases (FAISS, Milvus, or Qdrant).
- Experience with RAG (Retrieval-Augmented Generation), fine-tuning LLMs, and prompt engineering.
- Excellent behavior traits: absolute ownership, comfort with ambiguity, and product-mindedness.
- Leadership: mentoring junior engineers, driving strategy, and influencing cross-functional decisions.`;

function JobParserView({
  requirements,
  setRequirements,
  triggerToast
}: {
  requirements: Requirements | null;
  setRequirements: (r: Requirements) => void;
  triggerToast: (m: string) => void;
}) {
  const [jdText, setJdText] = useState(DEFAULT_JD_TEXT);
  const [parsing, setParsing] = useState(false);

  const handleParse = async () => {
    if (!jdText.trim()) return;
    setParsing(true);
    try {
      const res = await fetch(`${API_URL}/job/parse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jd_text: jdText })
      });
      const data = await res.json();
      setRequirements(data);
      triggerToast("Job description parsed successfully!");
    } catch (e) {
      console.error(e);
      triggerToast("Failed to parse job description.");
    } finally {
      setParsing(false);
    }
  };

  return (
    <div className="animate-fade">
      <header className="view-header">
        <h1>Job Description Parsing</h1>
        <p>Extract structured requirements using our LLM engine</p>
      </header>

      <div className="glass-panel mb-6">
        <h3 className="mb-4">Analyze Job Requirements</h3>
        <p className="text-secondary mb-4">
          Paste your unstructured job description text below. Our parser will extract the key dimensions
          (Skills, Experience, Behavior Traits, and Leadership) to build the active scoring filter.
        </p>

        <div className="form-group">
          <textarea
            className="form-control"
            rows={10}
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          ></textarea>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleParse}
          disabled={parsing}
        >
          {parsing ? (
            <>
              <Loader2 className="animate-spin" size={16} />
              Parsing with LLM Parser...
            </>
          ) : (
            <>
              <Sparkles size={16} />
              Parse Job Description
            </>
          )}
        </button>
      </div>

      {requirements && (
        <div className="glass-panel animate-fade">
          <h3 className="mb-4 text-accent" style={{ color: '#38bdf8' }}>🎯 Extracted Requirements Profile</h3>

          <div className="grid-cols-2">
            <div>
              <h4 className="mb-4" style={{ color: '#a78bfa' }}>🛠️ Technical Skills</h4>
              <div className="flex flex-wrap gap-2 mb-6">
                {requirements.skills.map((skill) => (
                  <span key={skill} className="tag tag-blue">{skill}</span>
                ))}
                {requirements.skills.length === 0 && <p className="text-secondary" style={{ fontSize: '0.9rem' }}>No skills extracted.</p>}
              </div>

              <h4 className="mb-4" style={{ color: '#2dd4bf' }}>💼 Experience Profile</h4>
              <ul className="text-secondary lh-tall" style={{ paddingLeft: '1.25rem' }}>
                {requirements.experience.map((exp) => (
                  <li key={exp} className="mb-2">{exp}</li>
                ))}
                {requirements.experience.length === 0 && <li>No experience specifications.</li>}
              </ul>
            </div>

            <div>
              <h4 className="mb-4" style={{ color: '#f472b6' }}>🧠 Behavioral Traits</h4>
              <ul className="text-secondary lh-tall" style={{ paddingLeft: '1.25rem' }}>
                {requirements.behavior_traits.map((trait) => (
                  <li key={trait} className="mb-2">{trait}</li>
                ))}
                {requirements.behavior_traits.length === 0 && <li>No behavioral traits extracted.</li>}
              </ul>

              <h4 className="mb-4" style={{ color: '#eab308' }}>👑 Leadership Expectations</h4>
              <ul className="text-secondary lh-tall" style={{ paddingLeft: '1.25rem' }}>
                {requirements.leadership_requirements.map((req) => (
                  <li key={req} className="mb-2">{req}</li>
                ))}
                {requirements.leadership_requirements.length === 0 && <li>No leadership expectations extracted.</li>}
              </ul>
            </div>
          </div>

          <div style={{
            backgroundColor: 'rgba(56, 189, 248, 0.1)',
            border: '1px solid rgba(56, 189, 248, 0.2)',
            padding: '1rem',
            borderRadius: '10px',
            color: '#38bdf8',
            fontSize: '0.9rem',
            fontWeight: 500
          }}>
            💡 These requirements are now active across the Candidate Search, Rankings, and Insights views.
          </div>
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------
// 3. Candidate Search View
// ----------------------------------------------------
function CandidateSearchView({
  setSelectedCandidateId,
  setCurrentView,
  compareIds,
  setCompareIds,
  triggerToast
}: {
  setSelectedCandidateId: (id: string) => void;
  setCurrentView: (v: string) => void;
  compareIds: string[];
  setCompareIds: (ids: string[]) => void;
  triggerToast: (m: string) => void;
}) {
  const [candidates, setCandidates] = useState<CandidateBrief[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filter States
  const [query, setQuery] = useState('');
  const [minExp, setMinExp] = useState(0);
  const [maxExp, setMaxExp] = useState(20);
  const [maxNotice, setMaxNotice] = useState(180);
  const [showFilters, setShowFilters] = useState(false);
  const [countriesList, setCountriesList] = useState<string[]>([]);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [selectedModes, setSelectedModes] = useState<string[]>([]);

  // Fetch unique metadata for dropdowns
  useEffect(() => {
    fetch(`${API_URL}/analytics`)
      .then(res => res.json())
      .then(d => {
        if (d.country_distribution) {
          setCountriesList(d.country_distribution.map((c: any) => c.label));
        }
      })
      .catch(e => console.error(e));
  }, []);

  const fetchCandidatesList = () => {
    setLoading(true);
    const params = new URLSearchParams({
      min_exp: minExp.toString(),
      max_exp: maxExp.toString(),
      max_notice: maxNotice.toString(),
      page: page.toString(),
      limit: '5'
    });

    if (query.trim()) {
      params.append('q', query);
    }
    selectedCountries.forEach(c => params.append('countries', c));
    selectedModes.forEach(m => params.append('work_modes', m));

    fetch(`${API_URL}/candidates?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setCandidates(data.candidates);
        setTotalCount(data.total_count);
        setTotalPages(data.pages);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchCandidatesList();
  }, [page, minExp, maxExp, maxNotice, selectedCountries, selectedModes]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchCandidatesList();
  };

  const handleResetFilters = () => {
    setMinExp(0);
    setMaxExp(20);
    setMaxNotice(180);
    setSelectedCountries([]);
    setSelectedModes([]);
    setQuery('');
    setPage(1);
  };

  const toggleCompare = (cid: string) => {
    if (compareIds.includes(cid)) {
      setCompareIds(compareIds.filter(id => id !== cid));
      triggerToast(`Removed ${cid} from comparison.`);
    } else {
      let newList = [...compareIds];
      if (newList.length >= 2) {
        newList.shift();
      }
      newList.push(cid);
      setCompareIds(newList);
      triggerToast(`Added ${cid} to comparison.`);
    }
  };

  return (
    <div className="animate-fade">
      <header className="view-header">
        <h1>Semantic Candidate Search</h1>
        <p>Query your talent pool using natural language and filters</p>
      </header>

      {/* Search Input Bar */}
      <div className="glass-panel mb-4">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="form-group mb-0 w-full" style={{ position: 'relative' }}>
            <input
              type="text"
              className="form-control"
              placeholder="🔍 e.g. Python backend developer with experience in Kubernetes and RAG"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ paddingLeft: '2.5rem' }}
            />
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '13px', color: '#64748b' }} />
          </div>
          <button type="submit" className="btn btn-primary">Search</button>
          <button
            type="button"
            className="btn"
            onClick={() => setShowFilters(!showFilters)}
            style={{ borderColor: showFilters ? '#38bdf8' : 'rgba(51, 65, 85, 0.5)' }}
          >
            <Filter size={18} />
            Filters
          </button>
        </form>

        {/* Expandable filters */}
        {showFilters && (
          <div className="filters-drawer mt-4 animate-fade">
            <div className="filters-grid">
              <div>
                <label className="form-label">Years of Experience: {minExp} - {maxExp} Yrs</label>
                <div className="flex gap-2 align-center">
                  <input
                    type="range"
                    min="0"
                    max="20"
                    value={minExp}
                    onChange={(e) => setMinExp(parseInt(e.target.value))}
                    style={{ accentColor: '#38bdf8', width: '100%' }}
                  />
                  <input
                    type="range"
                    min="0"
                    max="20"
                    value={maxExp}
                    onChange={(e) => setMaxExp(parseInt(e.target.value))}
                    style={{ accentColor: '#38bdf8', width: '100%' }}
                  />
                </div>
              </div>

              <div>
                <label className="form-label">Max Notice Period: {maxNotice} Days</label>
                <input
                  type="range"
                  min="0"
                  max="180"
                  step="10"
                  value={maxNotice}
                  onChange={(e) => setMaxNotice(parseInt(e.target.value))}
                  style={{ accentColor: '#38bdf8', width: '100%' }}
                />
              </div>

              <div>
                <label className="form-label">Countries</label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                  {countriesList.map(country => {
                    const isSelected = selectedCountries.includes(country);
                    return (
                      <span
                        key={country}
                        onClick={() => {
                          if (isSelected) setSelectedCountries(selectedCountries.filter(c => c !== country));
                          else setSelectedCountries([...selectedCountries, country]);
                        }}
                        style={{
                          fontSize: '0.75rem',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '12px',
                          border: `1px solid ${isSelected ? '#38bdf8' : '#334155'}`,
                          backgroundColor: isSelected ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                          color: isSelected ? '#38bdf8' : '#94a3b8',
                          cursor: 'pointer'
                        }}
                      >
                        {country}
                      </span>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="form-label">Work Mode</label>
                <div className="flex gap-2">
                  {['remote', 'hybrid', 'onsite'].map(mode => {
                    const isSelected = selectedModes.includes(mode);
                    return (
                      <button
                        key={mode}
                        type="button"
                        onClick={() => {
                          if (isSelected) setSelectedModes(selectedModes.filter(m => m !== mode));
                          else setSelectedModes([...selectedModes, mode]);
                        }}
                        className="btn"
                        style={{
                          padding: '0.4rem 0.8rem',
                          fontSize: '0.8rem',
                          textTransform: 'capitalize',
                          backgroundColor: isSelected ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                          color: isSelected ? '#38bdf8' : '#94a3b8',
                          borderColor: isSelected ? '#38bdf8' : '#334155'
                        }}
                      >
                        {mode}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
            <button className="btn mt-4" style={{ fontSize: '0.8rem' }} onClick={handleResetFilters}>
              Reset Filters
            </button>
          </div>
        )}
      </div>

      <p className="text-secondary mb-4" style={{ fontSize: '0.9rem' }}>
        Showing <strong>{totalCount}</strong> candidates matching criteria
      </p>

      {/* Candidates List cards */}
      {loading ? (
        <div className="w-full flex align-center justify-center flex-col" style={{ height: '40vh' }}>
          <Loader2 className="animate-spin text-accent" size={40} style={{ color: '#38bdf8' }} />
          <p className="mt-4 text-secondary">Searching talent pool...</p>
        </div>
      ) : (
        <div>
          {candidates.map((c) => (
            <div key={c.candidate_id} className="candidate-card-item">
              <div className="candidate-info">
                <div className="candidate-name-row">
                  <span className="candidate-name">{c.anonymized_name}</span>
                  <span className="candidate-id">({c.candidate_id})</span>
                </div>
                <div className="candidate-headline">{c.headline}</div>
                <p className="candidate-summary">{c.summary}</p>
                <div className="candidate-meta">
                  <span className="tag tag-blue">💼 {c.years_of_experience} yrs exp</span>
                  <span className="tag tag-teal">📍 {c.location}, {c.country}</span>
                  <span className="tag tag-purple">⏱️ {c.notice_period_days}d notice</span>
                  <span className="tag tag-green">🏢 {c.preferred_work_mode.toUpperCase()}</span>
                </div>

                <div className="candidate-actions">
                  <button
                    className="btn"
                    onClick={() => {
                      setSelectedCandidateId(c.candidate_id);
                      setCurrentView('Candidate Details');
                    }}
                  >
                    View Details
                  </button>
                  <button
                    className="btn"
                    onClick={() => toggleCompare(c.candidate_id)}
                    style={{ borderColor: compareIds.includes(c.candidate_id) ? '#22c55e' : 'rgba(51, 65, 85, 0.5)' }}
                  >
                    {compareIds.includes(c.candidate_id) ? 'Remove Compare' : 'Add Compare'}
                  </button>
                </div>
              </div>

              <div className="candidate-score-block">
                <span className="score-badge">Match: {(c.match_score * 100).toFixed(1)}%</span>
                <div className="score-breakdown">
                  <div>Skill Score: {(c.skill_score * 100).toFixed(0)}%</div>
                  <div>Behavior Score: {(c.behavior_score * 100).toFixed(0)}%</div>
                  <div>Career Score: {(c.career_score * 100).toFixed(0)}%</div>
                  <div>Exp Score: {(c.experience_score * 100).toFixed(0)}%</div>
                </div>
              </div>
            </div>
          ))}

          {candidates.length === 0 && (
            <div className="glass-panel text-center text-secondary" style={{ padding: '3rem' }}>
              No candidates match your current search and filter settings.
            </div>
          )}

          {/* Pagination bar */}
          {totalPages > 1 && (
            <div className="flex align-center justify-between mt-4">
              <span className="text-secondary" style={{ fontSize: '0.85rem' }}>
                Page {page} of {totalPages}
              </span>
              <div className="flex gap-2">
                <button
                  className="btn"
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft size={16} />
                </button>
                <button
                  className="btn"
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------
// 4. Candidate Rankings View
// ----------------------------------------------------
function CandidateRankingsView({
  setSelectedCandidateId,
  setCurrentView,
  triggerToast
}: {
  setSelectedCandidateId: (id: string) => void;
  setCurrentView: (v: string) => void;
  triggerToast: (m: string) => void;
}) {
  const [rankings, setRankings] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortBy, setSortBy] = useState('score');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/rankings?sort_by=${sortBy}&page=${page}&limit=15`)
      .then(res => res.json())
      .then(data => {
        setRankings(data.rankings);
        setTotalPages(data.pages);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  }, [page, sortBy]);

  const handleExport = () => {
    triggerToast("Generating challenge-compliant CSV file...");
    window.open(`${API_URL}/export`, '_blank');
  };

  return (
    <div className="animate-fade">
      <header className="view-header">
        <h1>Overall Candidate Rankings</h1>
        <p>Global ranked talent pool matched against active requirements</p>
      </header>

      <div className="glass-panel">
        <div className="flex justify-between align-center mb-6">
          <h3>Ranking Directory</h3>

          <div className="flex gap-4 align-center">
            <div className="form-group mb-0 flex align-center gap-2">
              <label className="form-label mb-0" style={{ whiteSpace: 'nowrap' }}>Sort table by</label>
              <select
                className="form-control"
                value={sortBy}
                onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
                style={{ padding: '0.4rem 2rem 0.4rem 0.75rem', fontSize: '0.85rem' }}
              >
                <option value="score">Score</option>
                <option value="rank">Rank</option>
                <option value="skill">Skill</option>
                <option value="behavior">Behavior</option>
                <option value="career">Career</option>
                <option value="experience">Experience</option>
              </select>
            </div>

            <button className="btn btn-success" onClick={handleExport}>
              <Download size={16} />
              Export Top 100 CSV
            </button>
          </div>
        </div>

        {loading ? (
          <div className="w-full flex align-center justify-center flex-col" style={{ height: '30vh' }}>
            <Loader2 className="animate-spin text-accent" size={32} style={{ color: '#38bdf8' }} />
            <p className="mt-4 text-secondary" style={{ fontSize: '0.9rem' }}>Compiling rankings directory...</p>
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Candidate ID</th>
                  <th>Name</th>
                  <th>Headline</th>
                  <th>Overall Score</th>
                  <th>Skill</th>
                  <th>Behavior</th>
                  <th>Career</th>
                  <th>Experience</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {rankings.map((r) => (
                  <tr key={r.candidate_id}>
                    <td><strong>#{r.display_rank}</strong></td>
                    <td style={{ fontFamily: 'monospace', color: '#38bdf8' }}>{r.candidate_id}</td>
                    <td><strong>{r.anonymized_name}</strong></td>
                    <td style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{r.headline}</td>
                    <td><span style={{ color: '#22c55e', fontWeight: 'bold' }}>{(r.score * 100).toFixed(1)}%</span></td>
                    <td>{(r.skill_score * 100).toFixed(0)}%</td>
                    <td>{(r.behavior_score * 100).toFixed(0)}%</td>
                    <td>{(r.career_score * 100).toFixed(0)}%</td>
                    <td>{(r.experience_score * 100).toFixed(0)}%</td>
                    <td>
                      <button
                        className="btn"
                        style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                        onClick={() => {
                          setSelectedCandidateId(r.candidate_id);
                          setCurrentView('Candidate Details');
                        }}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {totalPages > 1 && (
          <div className="flex align-center justify-between mt-6">
            <span className="text-secondary" style={{ fontSize: '0.85rem' }}>
              Page {page} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button
                className="btn"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft size={16} />
              </button>
              <button
                className="btn"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ----------------------------------------------------
// 5. Candidate Details View
// ----------------------------------------------------
function CandidateDetailsView({
  selectedCandidateId,
  setSelectedCandidateId
}: {
  selectedCandidateId: string | null;
  setSelectedCandidateId: (id: string) => void;
}) {
  const [candidatesList, setCandidatesList] = useState<string[]>([]);
  const [details, setDetails] = useState<CandidateDetails | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch candidate list for selector
  useEffect(() => {
    fetch(`${API_URL}/candidates?limit=1000`)
      .then(res => res.json())
      .then(data => {
        const ids = data.candidates.map((c: any) => c.candidate_id);
        setCandidatesList(ids);
        if (!selectedCandidateId && ids.length > 0) {
          setSelectedCandidateId(ids[0]);
        }
      })
      .catch(e => console.error(e));
  }, []);

  // Fetch full details when selectedCandidateId changes
  useEffect(() => {
    if (!selectedCandidateId) return;
    setLoading(true);
    fetch(`${API_URL}/candidates/${selectedCandidateId}`)
      .then(res => res.json())
      .then(data => {
        setDetails(data);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  }, [selectedCandidateId]);

  if (!selectedCandidateId) {
    return (
      <div className="glass-panel text-center text-secondary" style={{ padding: '3rem' }}>
        No candidate selected. Go to Candidate Search or Rankings to select one.
      </div>
    );
  }

  if (loading || !details) {
    return (
      <div className="w-full flex align-center justify-center flex-col animate-fade" style={{ height: '50vh' }}>
        <Loader2 className="animate-spin text-accent" size={40} style={{ color: '#38bdf8' }} />
        <p className="mt-4 text-secondary">Retrieving AI candidate insights...</p>
      </div>
    );
  }

  // Polar/Radar Data mapping
  const radarData = [
    { subject: 'Skills', value: Math.round(details.skill_score * 100) },
    { subject: 'Behavior', value: Math.round(details.behavior_score * 100) },
    { subject: 'Career', value: Math.round(details.career_score * 100) },
    { subject: 'Experience', value: Math.round(details.experience_score * 100) }
  ];



  return (
    <div className="animate-fade">
      <header className="view-header">
        <h1>Candidate Profile & Insights</h1>
      </header>

      {/* Candidate Profile Selector */}
      <div className="glass-panel mb-6 flex align-center justify-between" style={{ padding: '1rem 1.5rem' }}>
        <span className="font-bold">Active Candidate Inspect</span>
        <div className="form-group mb-0 flex align-center gap-2">
          <label className="form-label mb-0">Select Profile:</label>
          <select
            className="form-control"
            value={selectedCandidateId}
            onChange={(e) => setSelectedCandidateId(e.target.value)}
            style={{ width: '180px', padding: '0.4rem 2rem 0.4rem 0.75rem', fontSize: '0.85rem' }}
          >
            {candidatesList.map(id => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Banner */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        padding: '2rem',
        borderRadius: '16px',
        borderLeft: '6px solid #38bdf8',
        border: '1px solid rgba(255,255,255,0.05)',
        borderLeftColor: '#38bdf8',
        marginBottom: '2rem',
        boxShadow: 'var(--glass-shadow)'
      }}>
        <h2 style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>
          {details.anonymized_name} <span style={{ fontSize: '1rem', color: '#64748b' }}>({details.candidate_id})</span>
        </h2>
        <h4 style={{ color: '#38bdf8', fontWeight: 600, fontSize: '1.1rem', marginBottom: '1rem' }}>{details.headline}</h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', fontSize: '0.9rem', color: '#94a3b8' }}>
          <span>📍 {details.location}, {details.country}</span>
          <span>💼 {details.years_of_experience} Years of Experience</span>
          <span>🏢 Preferred Work Mode: <span style={{ textTransform: 'capitalize' }}>{details.preferred_work_mode}</span></span>
        </div>
      </div>

      {/* Metric Breakdown and Radar chart */}
      <div className="grid-cols-2">
        <div className="glass-panel flex flex-col justify-between">
          <div>
            <h3 className="mb-4">Profile Score Breakdown</h3>
            <div className="flex align-center justify-between mb-6">
              <span className="text-secondary">Overall Suitability Match</span>
              <span style={{ fontSize: '2.5rem', fontWeight: 800, color: '#38bdf8' }}>
                {(details.match_score * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="glass-panel" style={{ padding: '1rem', backgroundColor: 'rgba(15,23,42,0.4)' }}>
              <span className="text-muted" style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 700 }}>Skills</span>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#a78bfa' }}>{(details.skill_score * 100).toFixed(0)}%</div>
            </div>
            <div className="glass-panel" style={{ padding: '1rem', backgroundColor: 'rgba(15,23,42,0.4)' }}>
              <span className="text-muted" style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 700 }}>Behavior</span>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f472b6' }}>{(details.behavior_score * 100).toFixed(0)}%</div>
            </div>
            <div className="glass-panel" style={{ padding: '1rem', backgroundColor: 'rgba(15,23,42,0.4)' }}>
              <span className="text-muted" style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 700 }}>Career Alignment</span>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#2dd4bf' }}>{(details.career_score * 100).toFixed(0)}%</div>
            </div>
            <div className="glass-panel" style={{ padding: '1rem', backgroundColor: 'rgba(15,23,42,0.4)' }}>
              <span className="text-muted" style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 700 }}>Experience Fit</span>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#818cf8' }}>{(details.experience_score * 100).toFixed(0)}%</div>
            </div>
          </div>
        </div>

        <div className="glass-panel flex align-center justify-center">
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="subject" stroke="#94a3b8" />
              <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" />
              <Radar name="Candidate" dataKey="value" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AI Insights & Recommendation */}
      <div className="glass-panel mb-6">
        <h3 className="mb-4">🧠 Explainable AI Insights</h3>

        <div className="grid-cols-2 mb-4">
          <div>
            <h4 style={{ color: '#22c55e', display: 'flex', gap: '0.5rem', alignItems: 'center' }} className="mb-2">
              <Sparkles size={16} /> Key Strengths
            </h4>
            <ul className="text-secondary lh-tall" style={{ paddingLeft: '1.25rem' }}>
              {details.key_strengths.map((str, idx) => (
                <li key={idx} className="mb-2">{str}</li>
              ))}
            </ul>
          </div>

          <div>
            <h4 style={{ color: '#eab308', display: 'flex', gap: '0.5rem', alignItems: 'center' }} className="mb-2">
              <AlertTriangle size={16} /> Risks & Skill Gaps
            </h4>
            <ul className="text-secondary lh-tall" style={{ paddingLeft: '1.25rem' }}>
              {details.risks_gaps.map((r, idx) => (
                <li key={idx} className="mb-2">{r}</li>
              ))}
            </ul>
          </div>
        </div>

        <div style={{
          backgroundColor: 'rgba(30, 41, 59, 0.4)',
          border: '1px solid',
          borderColor: getRecommendationColor(details.recommendation),
          borderRadius: '12px',
          padding: '1.25rem',
          textAlign: 'center',
          marginTop: '1.5rem'
        }}>
          <h4 style={{
            margin: 0,
            color: getRecommendationColor(details.recommendation),
            fontSize: '1.2rem',
            fontWeight: 800
          }}>
            Hiring Recommendation: {details.recommendation}
          </h4>
        </div>
      </div>

      {/* Timeline Section */}
      <div className="grid-cols-2">
        <div className="glass-panel">
          <h3 className="mb-6" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <Briefcase size={20} style={{ color: '#38bdf8' }} /> Experience Timeline
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {details.career_history.map((role, idx) => (
              <div key={idx} style={{ position: 'relative', paddingLeft: '1.5rem', borderLeft: '2px solid #334155' }}>
                <span style={{
                  position: 'absolute',
                  left: '-6px',
                  top: '4px',
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  backgroundColor: role.is_current ? '#22c55e' : '#38bdf8'
                }}></span>
                <h4 style={{ fontSize: '1rem', margin: '0 0 0.25rem 0' }}>{role.title}</h4>
                <div style={{ fontSize: '0.85rem', color: '#38bdf8', fontWeight: 600, marginBottom: '0.25rem' }}>
                  {role.company}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', fontStyle: 'italic', marginBottom: '0.5rem' }}>
                  {role.start_date} to {role.end_date || 'Present'} ({role.duration_months} Months)
                </div>
                <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5 }}>
                  {role.description}
                </p>
              </div>
            ))}
            {details.career_history.length === 0 && <p className="text-secondary">No experience timeline available.</p>}
          </div>
        </div>

        <div className="glass-panel flex flex-col gap-6">
          <div>
            <h3 className="mb-6" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <GraduationCap size={20} style={{ color: '#2dd4bf' }} /> Education
            </h3>
            {details.education.map((edu, idx) => (
              <div key={idx} className="mb-4">
                <h4 style={{ fontSize: '0.95rem', margin: '0 0 0.25rem 0' }}>{edu.degree} in {edu.field_of_study}</h4>
                <div style={{ fontSize: '0.85rem', color: '#2dd4bf', fontWeight: 600, marginBottom: '0.25rem' }}>{edu.institution}</div>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  {edu.start_year} - {edu.end_year} | Grade: {edu.grade} | Tier: {edu.tier}
                </div>
              </div>
            ))}
            {details.education.length === 0 && <p className="text-secondary">No education details available.</p>}
          </div>

          <div>
            <h3 className="mb-4" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <Award size={20} style={{ color: '#a78bfa' }} /> Skills & Certifications
            </h3>
            <h5 className="text-secondary mb-2" style={{ fontSize: '0.85rem' }}>Endorsed Skills</h5>
            <div className="flex flex-wrap gap-2 mb-4">
              {details.skills.map((s, idx) => (
                <span key={idx} className="tag tag-blue" style={{ fontSize: '0.7rem' }}>
                  {s.name} ({s.proficiency})
                </span>
              ))}
            </div>

            {Object.keys(details.assessments).length > 0 && (
              <>
                <h5 className="text-secondary mb-2" style={{ fontSize: '0.85rem' }}>Platform Assessments</h5>
                <div className="flex flex-wrap gap-2 mb-4">
                  {Object.entries(details.assessments).map(([sname, sscore]) => (
                    <span key={sname} className="tag tag-teal" style={{ fontSize: '0.7rem' }}>
                      {sname}: {sscore}/100
                    </span>
                  ))}
                </div>
              </>
            )}

            {details.certifications.length > 0 && (
              <>
                <h5 className="text-secondary mb-2" style={{ fontSize: '0.85rem' }}>Certifications</h5>
                <ul className="text-secondary lh-tall" style={{ paddingLeft: '1rem', fontSize: '0.85rem' }}>
                  {details.certifications.map((c, idx) => (
                    <li key={idx} className="mb-1"><strong>{c.name}</strong> - {c.issuer} ({c.year})</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// 6. Side-by-Side Candidate Comparison View
// ----------------------------------------------------
function CandidateComparisonView({
  compareIds,
  setCompareIds
}: {
  compareIds: string[];
  setCompareIds: (ids: string[]) => void;
}) {
  const [candidatesList, setCandidatesList] = useState<string[]>([]);
  const [c1Id, setC1Id] = useState<string>('');
  const [c2Id, setC2Id] = useState<string>('');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/candidates?limit=1000`)
      .then(res => res.json())
      .then(d => {
        const ids = d.candidates.map((c: any) => c.candidate_id);
        setCandidatesList(ids);

        const defaultC1 = compareIds[0] && ids.includes(compareIds[0]) ? compareIds[0] : ids[0] || '';
        const defaultC2 = compareIds[1] && ids.includes(compareIds[1]) ? compareIds[1] : ids[1] || ids[0] || '';
        setC1Id(defaultC1);
        setC2Id(defaultC2);
        setCompareIds([defaultC1, defaultC2]);
      })
      .catch(e => console.error(e));
  }, []);

  useEffect(() => {
    if (!c1Id || !c2Id || c1Id === c2Id) {
      setData(null);
      return;
    }
    setLoading(true);
    fetch(`${API_URL}/compare?c1_id=${c1Id}&c2_id=${c2Id}`)
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  }, [c1Id, c2Id]);

  const handleC1Change = (val: string) => {
    setC1Id(val);
    setCompareIds([val, c2Id]);
  };

  const handleC2Change = (val: string) => {
    setC2Id(val);
    setCompareIds([c1Id, val]);
  };

  const renderProgressBar = (label: string, v1: number, v2: number, fillClass = "bg-fill-blue") => {
    const winner1 = v1 > v2;
    const winner2 = v2 > v1;
    return (
      <div className="mb-4">
        <div className="flex justify-between align-center mb-1" style={{ fontSize: '0.9rem' }}>
          <strong>{label}</strong>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          <div>
            <div className="flex justify-between mb-1" style={{ fontSize: '0.8rem', color: winner1 ? '#22c55e' : '#94a3b8' }}>
              <span>{(v1 * 100).toFixed(1)}% {winner1 && '🏆'}</span>
            </div>
            <div className="progress-bar-container">
              <div className={`progress-bar-fill ${fillClass}`} style={{ width: `${v1 * 100}%` }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-1" style={{ fontSize: '0.8rem', color: winner2 ? '#22c55e' : '#94a3b8' }}>
              <span>{(v2 * 100).toFixed(1)}% {winner2 && '🏆'}</span>
            </div>
            <div className="progress-bar-container">
              <div className={`progress-bar-fill ${fillClass}`} style={{ width: `${v2 * 100}%` }}></div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="animate-fade">
      <header className="view-header">
        <h1>Candidate Comparison</h1>
        <p>Side-by-side evaluations to select the top profile</p>
      </header>

      {/* Selectors Panel */}
      <div className="glass-panel mb-6">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          <div className="form-group mb-0">
            <label className="form-label">Candidate 1 ID</label>
            <select
              className="form-control"
              value={c1Id}
              onChange={(e) => handleC1Change(e.target.value)}
            >
              {candidatesList.map(id => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-group mb-0">
            <label className="form-label">Candidate 2 ID</label>
            <select
              className="form-control"
              value={c2Id}
              onChange={(e) => handleC2Change(e.target.value)}
            >
              {candidatesList.map(id => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {c1Id === c2Id && (
        <div className="glass-panel text-center text-secondary">
          Select two different candidates to compare.
        </div>
      )}

      {loading && (
        <div className="w-full flex align-center justify-center flex-col animate-fade" style={{ height: '30vh' }}>
          <Loader2 className="animate-spin text-accent" size={32} style={{ color: '#38bdf8' }} />
          <p className="mt-4 text-secondary">Calculating comparison side-by-sides...</p>
        </div>
      )}

      {!loading && data && c1Id !== c2Id && (
        <div className="animate-fade">
          {/* Suitability Bars */}
          <div className="glass-panel mb-6">
            <h3 className="mb-6">Match Suitability Profile</h3>
            {renderProgressBar("Overall Suitability Score", data.c1.match_score, data.c2.match_score, "bg-fill-blue")}
            {renderProgressBar("Skills Score", data.c1.skill_score, data.c2.skill_score, "bg-fill-purple")}
            {renderProgressBar("Behavior Score", data.c1.behavior_score, data.c2.behavior_score, "bg-fill-green")}
            {renderProgressBar("Career Score", data.c1.career_score, data.c2.career_score, "bg-fill-teal")}
            {renderProgressBar("Experience Score", data.c1.experience_score, data.c2.experience_score, "bg-fill-blue")}
          </div>

          {/* Demographics table */}
          <div className="glass-panel">
            <h3 className="mb-4">Profile Comparison Table</h3>
            <div className="data-table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Attribute</th>
                    <th>{c1Id}</th>
                    <th>{c2Id}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Anonymized Name</strong></td>
                    <td>{data.c1.anonymized_name}</td>
                    <td>{data.c2.anonymized_name}</td>
                  </tr>
                  <tr>
                    <td><strong>Headline</strong></td>
                    <td><span style={{ color: '#38bdf8' }}>{data.c1.headline}</span></td>
                    <td><span style={{ color: '#38bdf8' }}>{data.c2.headline}</span></td>
                  </tr>
                  <tr>
                    <td><strong>Location</strong></td>
                    <td>{data.c1.location}, {data.c1.country}</td>
                    <td>{data.c2.location}, {data.c2.country}</td>
                  </tr>
                  <tr>
                    <td><strong>Years of Experience</strong></td>
                    <td>{data.c1.years_of_experience} yrs</td>
                    <td>{data.c2.years_of_experience} yrs</td>
                  </tr>
                  <tr>
                    <td><strong>Notice Period</strong></td>
                    <td>{data.c1.notice_period_days} days</td>
                    <td>{data.c2.notice_period_days} days</td>
                  </tr>
                  <tr>
                    <td><strong>Preferred Work Mode</strong></td>
                    <td style={{ textTransform: 'capitalize' }}>{data.c1.preferred_work_mode}</td>
                    <td style={{ textTransform: 'capitalize' }}>{data.c2.preferred_work_mode}</td>
                  </tr>
                  <tr>
                    <td><strong>Expected Salary Min (LPA)</strong></td>
                    <td>{data.c1.expected_salary_min ? `${data.c1.expected_salary_min} LPA` : 'N/A'}</td>
                    <td>{data.c2.expected_salary_min ? `${data.c2.expected_salary_min} LPA` : 'N/A'}</td>
                  </tr>
                  <tr>
                    <td><strong>Expected Salary Max (LPA)</strong></td>
                    <td>{data.c1.expected_salary_max ? `${data.c1.expected_salary_max} LPA` : 'N/A'}</td>
                    <td>{data.c2.expected_salary_max ? `${data.c2.expected_salary_max} LPA` : 'N/A'}</td>
                  </tr>
                  <tr>
                    <td><strong>GitHub Activity Score</strong></td>
                    <td>{data.c1.github_activity_score !== null ? `${data.c1.github_activity_score}/100` : 'N/A'}</td>
                    <td>{data.c2.github_activity_score !== null ? `${data.c2.github_activity_score}/100` : 'N/A'}</td>
                  </tr>
                  <tr>
                    <td><strong>Profile Completeness</strong></td>
                    <td>{data.c1.profile_completeness_score}%</td>
                    <td>{data.c2.profile_completeness_score}%</td>
                  </tr>
                  <tr>
                    <td><strong>Recommendation</strong></td>
                    <td><span style={{ color: getRecommendationColor(data.c1.recommendation), fontWeight: 'bold' }}>{data.c1.recommendation}</span></td>
                    <td><span style={{ color: getRecommendationColor(data.c2.recommendation), fontWeight: 'bold' }}>{data.c2.recommendation}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------
// 7. Advanced Analytics View
// ----------------------------------------------------
function AnalyticsView() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/analytics`)
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => console.error(e));
  }, []);

  if (loading || !data) {
    return (
      <div className="w-full flex align-center justify-center flex-col animate-fade" style={{ height: '60vh' }}>
        <Loader2 className="animate-spin text-accent" size={40} style={{ color: '#38bdf8' }} />
        <p className="mt-4 text-secondary">Loading multi-dimensional analytics...</p>
      </div>
    );
  }

  // salary spreads bar chart mapping
  const salaryData = data.salary_spread.map((item: any) => ({
    name: item.candidate_id,
    range: [item.salary_min, item.salary_max],
    min: item.salary_min,
    max: item.salary_max
  })).slice(0, 15);

  return (
    <div className="animate-fade">
      <header className="view-header">
        <h1>Advanced Analytics</h1>
        <p>Deep dive candidate pool analysis and scatter profiles</p>
      </header>

      {/* Row 1 */}
      <div className="grid-cols-2">
        <div className="glass-panel">
          <h3 className="mb-4">Match Score vs. Experience</h3>
          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                <XAxis type="number" dataKey="years_of_experience" name="Experience" unit=" yrs" stroke="#64748b" />
                <YAxis type="number" dataKey="score" name="Match Score" unit="%" stroke="#64748b" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
                <Scatter name="Candidates" data={data.scatter_exp_score} fill="#38bdf8" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel">
          <h3 className="mb-4">Expected Salary Spread (INR LPA)</h3>
          {salaryData.length > 0 ? (
            <div style={{ width: '100%', height: 280 }}>
              <ResponsiveContainer>
                <BarChart data={salaryData} margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                  <XAxis dataKey="name" stroke="#64748b" style={{ fontSize: '0.75rem' }} />
                  <YAxis stroke="#64748b" />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
                  <Bar dataKey="range" fill="#2dd4bf" radius={[4, 4, 4, 4]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ height: 280 }} className="flex align-center justify-center text-secondary">
              No salary expectations available.
            </div>
          )}
        </div>
      </div>

      {/* Row 2 */}
      <div className="grid-cols-2">
        <div className="glass-panel">
          <h3 className="mb-4">GitHub Score vs. Profile Completeness</h3>
          {data.git_completeness.length > 0 ? (
            <div style={{ width: '100%', height: 280 }}>
              <ResponsiveContainer>
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                  <XAxis type="number" dataKey="completeness" name="Completeness" unit="%" stroke="#64748b" />
                  <YAxis type="number" dataKey="github_score" name="GitHub Score" stroke="#64748b" />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
                  <Scatter name="Developers" data={data.git_completeness} fill="#a78bfa" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ height: 280 }} className="flex align-center justify-center text-secondary">
              No GitHub linking signals recorded.
            </div>
          )}
        </div>

        <div className="glass-panel">
          <h3 className="mb-4">Component Scores Correlation Matrix</h3>
          <div className="data-table-container" style={{ border: 'none' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center', fontSize: '0.85rem' }}>
              <thead>
                <tr>
                  <th style={{ backgroundColor: '#0f172a', padding: '0.75rem', border: '1px solid #334155' }}>Variable</th>
                  {data.correlation_matrix.columns.map((c: string) => (
                    <th key={c} style={{ backgroundColor: '#0f172a', padding: '0.75rem', border: '1px solid #334155', textTransform: 'capitalize' }}>
                      {c.replace('_score', '')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.correlation_matrix.index.map((idxVal: string, rIdx: number) => (
                  <tr key={idxVal}>
                    <td style={{ backgroundColor: '#0f172a', fontWeight: 'bold', padding: '0.75rem', border: '1px solid #334155', textAlign: 'left', textTransform: 'capitalize' }}>
                      {idxVal.replace('_score', '')}
                    </td>
                    {data.correlation_matrix.values[rIdx].map((coef: number, cIdx: number) => {
                      // Calculate correlation intensity color
                      const intensity = Math.abs(coef);
                      const isPositive = coef >= 0;
                      const cellColor = isPositive 
                        ? `rgba(56, 189, 248, ${intensity * 0.4})` 
                        : `rgba(239, 68, 68, ${intensity * 0.4})`;
                      return (
                        <td
                          key={cIdx}
                          style={{
                            padding: '0.75rem',
                            border: '1px solid #334155',
                            backgroundColor: cellColor,
                            color: '#fff',
                            fontWeight: intensity > 0.6 ? 'bold' : 'normal'
                          }}
                        >
                          {coef}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// 8. AI Insights View
// ----------------------------------------------------
function AIInsightsView({
  setSelectedCandidateId,
  setCurrentView
}: {
  setSelectedCandidateId: (id: string) => void;
  setCurrentView: (v: string) => void;
}) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/insights`)
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => console.error(e));
  }, []);

  if (loading || !data) {
    return (
      <div className="w-full flex align-center justify-center flex-col animate-fade" style={{ height: '50vh' }}>
        <Loader2 className="animate-spin text-accent" size={40} style={{ color: '#38bdf8' }} />
        <p className="mt-4 text-secondary">Assembling talent insights pipeline...</p>
      </div>
    );
  }

  return (
    <div className="animate-fade">
      <header className="view-header">
        <h1>AI Talent Insights</h1>
        <p>Automated recruiter feedback and hiring suggestions</p>
      </header>

      {/* Recommended Interview Order */}
      <div className="glass-panel mb-6">
        <h3 className="mb-4" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Brain size={20} style={{ color: '#38bdf8' }} /> Proposed Interview Scheduling Order
        </h3>
        <p className="text-secondary mb-4" style={{ fontSize: '0.9rem' }}>
          Recommended candidates sorted by suitability match. Click on a candidate to view their details.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {data.interview_order.map((item: any) => (
            <div
              key={item.candidate_id}
              onClick={() => {
                setSelectedCandidateId(item.candidate_id);
                setCurrentView('Candidate Details');
              }}
              style={{
                backgroundColor: 'rgba(30, 41, 59, 0.6)',
                border: '1px solid rgba(51, 65, 85, 0.5)',
                borderLeft: '4px solid #22c55e',
                borderRadius: '8px',
                padding: '1rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: 'all 0.2s ease-out'
              }}
              className="glass-panel-hover"
            >
              <div className="flex align-center gap-4">
                <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#22c55e', minWidth: '30px', textAlign: 'center' }}>
                  #{item.rank}
                </span>
                <div>
                  <h4 style={{ margin: 0, fontSize: '0.95rem' }}>
                    {item.anonymized_name} <span style={{ color: '#64748b', fontSize: '0.75rem', fontFamily: 'monospace' }}>({item.candidate_id})</span>
                  </h4>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{item.headline}</span>
                </div>
              </div>

              <span style={{ color: '#22c55e', fontWeight: 800, fontSize: '1.1rem' }}>
                {(item.score * 100).toFixed(1)}% Match
              </span>
            </div>
          ))}

          {data.interview_order.length === 0 && (
            <p className="text-secondary text-center">Talent pool is empty.</p>
          )}
        </div>
      </div>

      <div className="grid-cols-2">
        {/* Talent Gaps */}
        <div className="glass-panel">
          <h3 className="mb-4">🔍 Talent Pool Skill Gap Analysis</h3>
          <p className="text-secondary mb-4" style={{ fontSize: '0.85rem' }}>
            Aggregated required skills that are most commonly <strong>missing</strong> across your candidate pool:
          </p>

          <div className="data-table-container">
            <table className="data-table" style={{ fontSize: '0.85rem' }}>
              <thead>
                <tr>
                  <th>Skill Requirement</th>
                  <th>Gaps Count</th>
                  <th>Missing Ratio</th>
                </tr>
              </thead>
              <tbody>
                {data.skill_gaps.map((gap: any) => (
                  <tr key={gap.skill}>
                    <td><strong>{gap.skill}</strong></td>
                    <td>{gap.gap_count} profiles</td>
                    <td>
                      <div className="flex align-center gap-2">
                        <div className="progress-bar-container" style={{ width: '80px', height: '6px' }}>
                          <div className="progress-bar-fill bg-fill-purple" style={{ width: `${gap.missing_ratio}%` }}></div>
                        </div>
                        <span style={{ fontWeight: 'bold', color: gap.missing_ratio > 50 ? '#ef4444' : '#94a3b8' }}>
                          {gap.missing_ratio.toFixed(0)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
                {data.skill_gaps.length === 0 && (
                  <tr>
                    <td colSpan={3} className="text-center text-secondary">No active skill requirements.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <span style={{ display: 'block', fontSize: '0.75rem', color: '#64748b', marginTop: '0.75rem' }}>
            💡 High missing ratio indicates a restrictive skill requirement that limits your talent pool.
          </span>
        </div>

        {/* Fast Track */}
        <div className="glass-panel">
          <h3 className="mb-4" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={20} style={{ color: '#2dd4bf' }} /> Fast-Track Candidates (Low Notice & High Responsiveness)
          </h3>
          <p className="text-secondary mb-4" style={{ fontSize: '0.85rem' }}>
            These candidates have a notice period of ≤ 30 days and response rate of ≥ 70%. Excellent for urgent hiring needs.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {data.fast_track.map((ft: any) => (
              <div
                key={ft.candidate_id}
                style={{
                  backgroundColor: 'rgba(30, 41, 59, 0.4)',
                  padding: '1rem',
                  borderRadius: '10px',
                  border: '1px solid rgba(51, 65, 85, 0.5)'
                }}
              >
                <h4 style={{ fontSize: '0.9rem', margin: '0 0 0.5rem 0' }}>
                  {ft.anonymized_name} <span style={{ color: '#64748b', fontSize: '0.75rem', fontFamily: 'monospace' }}>({ft.candidate_id})</span>
                </h4>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#94a3b8' }}>
                  <span>Match: <strong style={{ color: '#22c55e' }}>{(ft.score * 100).toFixed(1)}%</strong></span>
                  <span>Notice: <strong>{ft.notice_period_days} Days</strong></span>
                  <span>Resp Rate: <strong>{(ft.response_rate * 100).toFixed(0)}%</strong></span>
                </div>
              </div>
            ))}

            {data.fast_track.length === 0 && (
              <div style={{ padding: '2rem', textAlign: 'center' }} className="text-secondary">
                No candidates fit the urgent notice and response criteria in the loaded slice.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// 9. Settings View
// ----------------------------------------------------
function SettingsView({
  settings,
  fetchSettings,
  triggerToast
}: {
  settings: SettingsState | null;
  fetchSettings: () => void;
  triggerToast: (m: string) => void;
}) {
  const [skillWeight, setSkillWeight] = useState(0.35);
  const [behaviorWeight, setBehaviorWeight] = useState(0.2);
  const [careerWeight, setCareerWeight] = useState(0.2);
  const [expWeight, setExpWeight] = useState(0.25);
  const [datasetMode, setDatasetMode] = useState('sample');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (settings) {
      setSkillWeight(settings.weights.skill);
      setBehaviorWeight(settings.weights.behavior);
      setCareerWeight(settings.weights.career);
      setExpWeight(settings.weights.experience);
      setDatasetMode(settings.dataset_mode);
    }
  }, [settings]);

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API_URL}/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          weights: {
            skill: skillWeight,
            behavior: behaviorWeight,
            career: careerWeight,
            experience: expWeight
          },
          dataset_mode: datasetMode
        })
      });
      await res.json();
      fetchSettings();
      triggerToast("Settings successfully saved and dataset reloaded.");
    } catch (e) {
      console.error(e);
      triggerToast("Failed to save settings.");
    } finally {
      setSaving(false);
    }
  };

  const totalWeights = skillWeight + behaviorWeight + careerWeight + expWeight;
  const getNormalized = (w: number) => {
    if (totalWeights <= 0) return 0;
    return (w / totalWeights) * 100;
  };

  return (
    <div className="animate-fade">
      <header className="view-header">
        <h1>System Settings</h1>
        <p>Configure scoring weights and dataset profiles</p>
      </header>

      <div className="glass-panel mb-6">
        <h3 className="mb-2">🎚️ Candidate Scoring Weights</h3>
        <p className="text-secondary mb-6" style={{ fontSize: '0.85rem' }}>
          Adjust the weight factors for each scoring component. Component scores are normalized to sum to 100%.
        </p>

        <div className="form-group">
          <label className="form-label">Skills Weight: {getNormalized(skillWeight).toFixed(0)}%</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={skillWeight}
            onChange={(e) => setSkillWeight(parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: '#38bdf8' }}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Behavior Weight: {getNormalized(behaviorWeight).toFixed(0)}%</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={behaviorWeight}
            onChange={(e) => setBehaviorWeight(parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: '#38bdf8' }}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Career Alignment Weight: {getNormalized(careerWeight).toFixed(0)}%</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={careerWeight}
            onChange={(e) => setCareerWeight(parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: '#38bdf8' }}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Experience Fit Weight: {getNormalized(expWeight).toFixed(0)}%</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={expWeight}
            onChange={(e) => setExpWeight(parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: '#38bdf8' }}
          />
        </div>

        <div style={{
          backgroundColor: 'rgba(15, 23, 42, 0.4)',
          border: '1px solid var(--border-color)',
          borderRadius: '10px',
          padding: '1rem',
          fontSize: '0.85rem',
          color: '#94a3b8',
          marginBottom: '1.5rem'
        }}>
          <strong>Active normalized weights distribution:</strong>
          <ul style={{ paddingLeft: '1.25rem', marginTop: '0.25rem' }}>
            <li>Skills: {getNormalized(skillWeight).toFixed(1)}%</li>
            <li>Behavior: {getNormalized(behaviorWeight).toFixed(1)}%</li>
            <li>Career Alignment: {getNormalized(careerWeight).toFixed(1)}%</li>
            <li>Experience Fit: {getNormalized(expWeight).toFixed(1)}%</li>
          </ul>
        </div>
      </div>

      <div className="glass-panel mb-6">
        <h3 className="mb-2">📂 Dataset Profile</h3>
        <p className="text-secondary mb-4" style={{ fontSize: '0.85rem' }}>
          Select which database slice to load into memory.
        </p>

        <div className="form-group">
          <div className="flex flex-col gap-2">
            <label className="flex align-center gap-2 text-secondary" style={{ cursor: 'pointer' }}>
              <input
                type="radio"
                name="datasetMode"
                value="sample"
                checked={datasetMode === 'sample'}
                onChange={() => setDatasetMode('sample')}
                style={{ accentColor: '#38bdf8' }}
              />
              Sample Dataset (50 candidates - instant)
            </label>
            <label className="flex align-center gap-2 text-secondary" style={{ cursor: 'pointer' }}>
              <input
                type="radio"
                name="datasetMode"
                value="full"
                checked={datasetMode === 'full'}
                onChange={() => setDatasetMode('full')}
                style={{ accentColor: '#38bdf8' }}
              />
              Full Dataset (100,000 candidates - heavy processing)
            </label>
          </div>
        </div>

        {datasetMode === 'full' && (
          <div style={{
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            padding: '1rem',
            borderRadius: '10px',
            color: '#f87171',
            fontSize: '0.85rem',
            fontWeight: 500,
            marginBottom: '1rem'
          }}>
            ⚠️ Warning: The full dataset is 487MB (100,000 rows). Loading, embedding, and indexing all candidates will take significant memory and CPU processing time on startup. We recommend using the Sample Dataset for real-time hackathon review.
          </div>
        )}
      </div>

      <button
        className="btn btn-primary"
        onClick={handleSaveSettings}
        disabled={saving}
      >
        {saving ? (
          <>
            <Loader2 className="animate-spin" size={16} />
            Re-initializing Systems...
          </>
        ) : (
          "Save Configuration"
        )}
      </button>
    </div>
  );
}
