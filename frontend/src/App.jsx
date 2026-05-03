import { useState, useEffect } from 'react'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// ── Design tokens ──────────────────────────────────────────
const C = {
  bg       : '#0a0e1a',
  surface  : '#111827',
  card     : '#1a2235',
  border   : '#2a3a5c',
  accent   : '#3b82f6',
  accentLo : '#1d4ed8',
  green    : '#10b981',
  red      : '#ef4444',
  amber    : '#f59e0b',
  text     : '#f1f5f9',
  muted    : '#94a3b8',
  faint    : '#4a5568',
}

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    background: ${C.bg};
    color: ${C.text};
    font-family: 'Space Grotesk', sans-serif;
    min-height: 100vh;
  }

  .mono { font-family: 'JetBrains Mono', monospace; }

  @keyframes fadeUp {
    from { opacity:0; transform:translateY(16px); }
    to   { opacity:1; transform:translateY(0); }
  }
  @keyframes pulse {
    0%,100% { opacity:1; }
    50%      { opacity:.5; }
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  @keyframes scanline {
    0%   { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
  }
  @keyframes glow {
    0%,100% { box-shadow: 0 0 20px rgba(59,130,246,0.3); }
    50%      { box-shadow: 0 0 40px rgba(59,130,246,0.6); }
  }
  @keyframes barFill {
    from { width: 0; }
  }

  .fade-up { animation: fadeUp 0.4s ease both; }

  .grid-bg {
    background-image:
      linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  .card {
    background: ${C.card};
    border: 1px solid ${C.border};
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 12px;
  }

  .input-field {
    width: 100%;
    padding: 12px 16px;
    background: ${C.surface};
    border: 1px solid ${C.border};
    border-radius: 10px;
    color: ${C.text};
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .input-field:focus {
    border-color: ${C.accent};
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
  }
  .input-field::placeholder { color: ${C.faint}; }

  .btn-primary {
    width: 100%;
    padding: 13px;
    background: linear-gradient(135deg, ${C.accent}, ${C.accentLo});
    color: #fff;
    border: none;
    border-radius: 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    letter-spacing: 0.3px;
    transition: opacity 0.2s, transform 0.1s;
    margin-top: 14px;
  }
  .btn-primary:hover:not(:disabled) { opacity: 0.9; }
  .btn-primary:active:not(:disabled) { transform: scale(0.99); }
  .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

  .btn-secondary {
    width: 100%;
    padding: 11px;
    background: transparent;
    color: ${C.muted};
    border: 1px solid ${C.border};
    border-radius: 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
    margin-top: 8px;
  }
  .btn-secondary:hover { background: ${C.surface}; color: ${C.text}; }

  .btn-green {
    background: linear-gradient(135deg, ${C.green}, #059669);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 13px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    margin-top: 14px;
    transition: opacity 0.2s;
  }
  .btn-green:hover:not(:disabled) { opacity: 0.9; }
  .btn-green:disabled { opacity: 0.5; cursor: not-allowed; }

  .tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.3px;
  }

  .stat-box {
    background: ${C.surface};
    border: 1px solid ${C.border};
    border-radius: 10px;
    padding: 10px 8px;
    text-align: center;
  }

  .spinner {
    width: 18px; height: 18px;
    border: 2px solid rgba(255,255,255,0.2);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    display: inline-block;
    margin-right: 8px;
    vertical-align: middle;
  }

  .risk-bar-track {
    position: relative;
    height: 8px;
    border-radius: 4px;
    background: linear-gradient(to right, ${C.green}, #65a30d, ${C.amber}, #ea580c, ${C.red});
    margin: 8px 0 4px;
    overflow: visible;
  }
  .risk-indicator {
    position: absolute;
    top: -4px;
    width: 16px; height: 16px;
    border-radius: 50%;
    background: #fff;
    border: 2.5px solid #fff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5);
    transform: translateX(-50%);
    transition: left 0.8s cubic-bezier(0.34,1.56,0.64,1);
  }

  .hash-box {
    background: ${C.surface};
    border: 1px solid ${C.border};
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 11px;
    color: ${C.muted};
    word-break: break-all;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.6;
  }

  .scam-alert {
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 10px;
  }

  .verify-box {
    border-radius: 12px;
    padding: 16px;
    margin-top: 10px;
  }

  .caption-item {
    background: ${C.surface};
    border-left: 2px solid ${C.border};
    border-radius: 0 6px 6px 0;
    padding: 6px 10px;
    font-size: 12px;
    color: ${C.muted};
    margin-bottom: 4px;
    line-height: 1.5;
  }

  .toggle-wrap {
    display: flex;
    background: ${C.surface};
    border: 1px solid ${C.border};
    border-radius: 10px;
    padding: 4px;
    margin-bottom: 14px;
  }
  .toggle-btn {
    flex: 1;
    padding: 9px 0;
    border: none;
    border-radius: 7px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .toggle-btn.active {
    background: ${C.accent};
    color: #fff;
    font-weight: 600;
  }
  .toggle-btn.inactive {
    background: transparent;
    color: ${C.muted};
    font-weight: 400;
  }

  .existing-banner {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 12px;
  }

  label { font-size: 12px; color: ${C.muted}; display: block; margin-bottom: 5px; font-weight: 500; }
  textarea.input-field { resize: vertical; height: 70px; }

  .linkedin-info {
    background: rgba(59,130,246,0.07);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: ${C.muted};
    margin-bottom: 12px;
  }
`

// ── Scam Warning ────────────────────────────────────────────
const ScamWarning = ({ categories, bioKeywords, postKeywords, postsAnalyzed, webSignals, websiteUrl, websiteSsl }) => {
  if ((!categories || categories.length === 0) && (!webSignals || webSignals.length === 0)) return null

  const catLabels = {
    trading_scam        : '📈 Trading Scam',
    job_scam            : '💼 Job Scam',
    ecommerce_scam      : '🛒 E-commerce Scam',
    adult_spam          : '🔞 Adult Spam',
    giveaway_scam       : '🎁 Giveaway Scam',
    suspicious_domain   : '🌐 Suspicious Domain',
    suspicious_redirect : '🔀 Suspicious Redirect',
    unreachable_website : '❌ Unreachable Website'
  }

  const catDesc = {
    trading_scam        : 'Suspicious trading/investment language detected',
    job_scam            : 'Suspicious job offer or work-from-home scheme',
    ecommerce_scam      : 'Suspicious selling activity or fake product offers',
    adult_spam          : 'Adult content or follow-spam patterns',
    giveaway_scam       : 'Fake giveaway or prize scheme',
    suspicious_domain   : 'Domain commonly associated with scams',
    suspicious_redirect : 'Website redirects to a different domain',
    unreachable_website : 'Website cannot be reached'
  }

  return (
    <div className="scam-alert">
      <div style={{ fontWeight:600, fontSize:13, color:C.amber, marginBottom:10, display:'flex', alignItems:'center', gap:6 }}>
        <span>⚠</span> Suspicious Content Detected
      </div>
      {categories && categories.map(c => (
        <div key={c} style={{ marginBottom:8 }}>
          <span className="tag" style={{ background:'rgba(245,158,11,0.15)', color:C.amber, marginBottom:3 }}>
            {catLabels[c] || c}
          </span>
          <div style={{ fontSize:11, color:C.muted, marginTop:3, marginLeft:2 }}>{catDesc[c]}</div>
        </div>
      ))}
      <div style={{ display:'flex', gap:14, flexWrap:'wrap', marginTop:6, fontSize:11, color:C.faint }}>
        {bioKeywords && bioKeywords.length > 0 && (
          <span>📝 Bio: {bioKeywords.length} signal{bioKeywords.length > 1 ? 's' : ''}</span>
        )}
        {postKeywords && postKeywords.length > 0 && (
          <span>📸 Posts: {postKeywords.length} signal{postKeywords.length > 1 ? 's' : ''} across {postsAnalyzed} post{postsAnalyzed > 1 ? 's' : ''}</span>
        )}
      </div>
      {webSignals && webSignals.length > 0 && (
        <div style={{ marginTop:8, borderTop:`1px solid rgba(245,158,11,0.2)`, paddingTop:8 }}>
          <div style={{ fontSize:11, color:C.amber, fontWeight:600, marginBottom:4 }}>
            🌐 {websiteUrl?.replace('https://','').replace('http://','').slice(0,35)}
            {websiteSsl === false && <span style={{ color:C.red, marginLeft:6 }}>⚠ No SSL</span>}
            {websiteSsl === true  && <span style={{ color:C.green, marginLeft:6 }}>✓ SSL</span>}
          </div>
          {webSignals.map((s,i) => (
            <div key={i} style={{ fontSize:11, color:C.muted, marginBottom:2 }}>• {s}</div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Main App ────────────────────────────────────────────────
export default function App() {
  const [mode, setMode]                     = useState('url')
  const [url, setUrl]                       = useState('')
  const [profile, setProfile]               = useState(null)
  const [result, setResult]                 = useState(null)
  const [step, setStep]                     = useState('input')
  const [loading, setLoading]               = useState(false)
  const [verifyResult, setVerifyResult]     = useState(null)
  const [verifying, setVerifying]           = useState(false)
  const [existingRecord, setExistingRecord] = useState(null)
  const [platform, setPlatform]             = useState('instagram')
  const [forceAnalyze, setForceAnalyze]     = useState(false)

  const [manual, setManual] = useState({
    username:'', profile_pic:0, nums_length_username:0,
    fullname_words:0, nums_length_fullname:0, name_equals_username:0,
    description_length:0, external_url:0, private:0,
    posts:'', followers:'', following:'', bio_text:'',
    connections:'', experience_count:'', education_count:'',
    skills_count:'', recommendations:'', projects:'',
    publications:'', courses:'', honors:'', languages:'',
    organizations:'', interests:'', activities:'', linkedin_bio:''
  })

  const reset = () => {
    setUrl(''); setProfile(null); setResult(null)
    setVerifyResult(null); setExistingRecord(null); setStep('input')
    setManual({
      username:'', profile_pic:0, nums_length_username:0,
      fullname_words:0, nums_length_fullname:0, name_equals_username:0,
      description_length:0, external_url:0, private:0,
      posts:'', followers:'', following:'', bio_text:'',
      connections:'', experience_count:'', education_count:'',
      skills_count:'', recommendations:'', projects:'',
      publications:'', courses:'', honors:'', languages:'',
      organizations:'', interests:'', activities:'', linkedin_bio:''
    })
  }

  const fetchProfile = async () => {
    if (!url.trim()) return
    setLoading(true)
    let username = url.replace('https://','').replace('http://','')
    if (platform === 'instagram') {
      username = username.replace('www.instagram.com/','').replace('instagram.com/','')
    } else {
      username = username.replace('www.linkedin.com/in/','').replace('linkedin.com/in/','')
    }
    username = username.replace('@','').split('?')[0].replace(/\/$/,'')

    try {
      if (!forceAnalyze) {
        const check = await axios.post(`${API}/check-existing`, { username })
        if (check.data.exists) { setExistingRecord(check.data); setLoading(false); return }
      }
    } catch {}

    try {
      const res = await axios.post(
        platform === 'linkedin' ? `${API}/fetch-linkedin` : `${API}/fetch-profile`,
        platform === 'linkedin' ? { url } : { username: url }
      )
      setProfile(res.data)
      setStep('fetched')
      setForceAnalyze(false)
    } catch { alert('Could not fetch profile. Check the username.') }
    setLoading(false)
  }

  const submitManual = () => {
    const f = manual
    if (platform === 'linkedin') {
      const skills = parseFloat(f.skills_count)||0
      const exp    = parseFloat(f.experience_count)||0
      const edu    = parseFloat(f.education_count)||0
      const fol    = parseFloat(f.followers)||0
      const recs   = parseFloat(f.recommendations)||0
      setProfile({
        username:f.username, connections:parseFloat(f.connections)||0,
        followers:fol, experience_count:exp, education_count:edu,
        skills_count:skills, recommendations:recs,
        projects:parseFloat(f.projects)||0, publications:parseFloat(f.publications)||0,
        courses:parseFloat(f.courses)||0, honors:parseFloat(f.honors)||0,
        languages:parseFloat(f.languages)||0, organizations:parseFloat(f.organizations)||0,
        interests:parseFloat(f.interests)||0, activities:parseFloat(f.activities)||0,
        profile_strength:skills+exp+edu, engagement:fol+recs,
        bio_text:f.linkedin_bio||'',
        display:{full_name:f.username, bio:f.linkedin_bio||'', profile_pic_url:'', is_verified:false}
      })
    } else {
      setProfile({
        username:f.username, profile_pic:f.profile_pic,
        nums_length_username:parseFloat(f.nums_length_username)||0,
        fullname_words:parseFloat(f.fullname_words)||0,
        nums_length_fullname:parseFloat(f.nums_length_fullname)||0,
        name_equals_username:f.name_equals_username,
        description_length:parseFloat(f.description_length)||0,
        external_url:f.external_url, private:f.private,
        posts:parseFloat(f.posts)||0,
        followers:parseFloat(f.followers)||0,
        following:parseFloat(f.following)||0,
        bio_scan:null,
        display:{full_name:f.username, bio:f.bio_text||'', profile_pic_url:'', is_verified:false}
      })
    }
    setStep('fetched')
  }

  const analyze = async () => {
    setLoading(true)
    try {
      const res = await axios.post(
        platform === 'linkedin' ? `${API}/analyze-linkedin` : `${API}/analyze-profile`,
        profile
      )
      setResult(res.data)
      setStep('result')
    } catch { alert('Analysis failed. Make sure Flask is running.') }
    setLoading(false)
  }

  const verifyOnBlockchain = async () => {
    setVerifying(true)
    try {
      const res = await axios.post(`${API}/verify-result`, { username: profile?.username })
      setVerifyResult(res.data)
    } catch { alert('Verification failed.') }
    setVerifying(false)
  }

  const handleManual = (e) => {
    const val = e.target.type === 'checkbox' ? (e.target.checked ? 1 : 0) : e.target.value
    setManual({ ...manual, [e.target.name]: val })
  }

  const riskColor = (score) => score > 60 ? C.red : score > 40 ? C.amber : C.green

  return (
    <>
      <style>{styles}</style>
      <div className="grid-bg" style={{ minHeight:'100vh', padding:'0 0 3rem' }}>

        {/* ── Header ── */}
        <div style={{ textAlign:'center', padding:'3rem 1rem 1.5rem', borderBottom:`1px solid ${C.border}`, marginBottom:'2rem', background:`linear-gradient(180deg, rgba(59,130,246,0.06) 0%, transparent 100%)` }}>
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:10, marginBottom:8 }}>
            <div style={{ width:36, height:36, borderRadius:10, background:'linear-gradient(135deg, #3b82f6, #1d4ed8)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:18 }}>🛡</div>
            <h1 style={{ fontSize:24, fontWeight:700, letterSpacing:'-0.5px', color:C.text }}>
              Fake Profile Identification
            </h1>
          </div>
          <p style={{ fontSize:13, color:'grey', letterSpacing:'0.5px' }}>
            ML + Blockchain Verification · Multi-Platform Detection
          </p>
        </div>

        <div style={{ maxWidth:560, margin:'0 auto', padding:'0 1rem' }}>

          {/* ── INPUT STEP ── */}
          {step === 'input' && (
            <div className="fade-up">

              {/* Platform toggle */}
              <div className="toggle-wrap">
                {[['instagram','📷  Instagram'],['linkedin','💼  LinkedIn']].map(([p,l]) => (
                  <button key={p}
                    onClick={() => { setPlatform(p); setMode(p==='linkedin'?'manual':'url') }}
                    className={`toggle-btn ${platform===p?'active':'inactive'}`}>{l}
                  </button>
                ))}
              </div>

              {/* Existing record banner */}
              {existingRecord && (
                <div className="existing-banner fade-up">
                  <div style={{ fontSize:13, fontWeight:600, color:C.green, marginBottom:6 }}>
                    ✓ Previously analyzed
                  </div>
                  <div style={{ fontSize:13, color:C.muted, marginBottom:10 }}>
                    <span style={{ color:C.text, fontWeight:500 }}>@{existingRecord.username}</span>
                    {' '}· {existingRecord.hours_old}h ago ·{' '}
                    <span style={{ color: existingRecord.result==='Fake' ? C.red : C.green, fontWeight:600 }}>
                      {existingRecord.result}
                    </span>
                    {' '}({existingRecord.risk_score}% risk)
                  </div>
                  <div style={{ display:'flex', gap:8 }}>
                    <button onClick={() => { setResult(existingRecord); setProfile({username:existingRecord.username}); setStep('result'); setExistingRecord(null) }}
                      style={{ flex:1, padding:'9px', background:'rgba(16,185,129,0.15)', color:C.green, border:`1px solid rgba(16,185,129,0.3)`, borderRadius:8, fontSize:13, fontWeight:600, cursor:'pointer' }}>
                      View Result
                    </button>
                    <button onClick={async () => {
                                      setExistingRecord(null)
                                      setLoading(true)
                                      try {
                                        // Reuse stored profile data — no Instagram API call
                                        const res = await axios.post(`${API}/get-stored-profile`, {
                                          username: existingRecord.username
                                        })
                                        if (res.data.found) {
                                          setProfile(res.data.profile_data)
                                          setStep('fetched')
                                          console.log('Reusing stored profile — saved Instagram API quota')
                                        } else {
                                          // No stored data, must fetch fresh
                                          setForceAnalyze(true)
                                          setUrl(existingRecord.username)
                                        }
                                      } catch {
                                        setForceAnalyze(true)
                                      }
                                      setLoading(false)
                                    }}
                      style={{ flex:1, padding:'9px', background:'transparent', color:C.muted, border:`1px solid ${C.border}`, borderRadius:8, fontSize:13, cursor:'pointer' }}>
                      Re-analyze
                    </button>
                  </div>
                </div>
              )}

              {/* Mode toggle — Instagram only */}
              {platform === 'instagram' && (
                <div className="toggle-wrap">
                  {[['url','🔗  URL / Username'],['manual','✏️  Manual Input']].map(([m,l]) => (
                    <button key={m} onClick={() => setMode(m)} className={`toggle-btn ${mode===m?'active':'inactive'}`}>{l}</button>
                  ))}
                </div>
              )}

              {platform === 'linkedin' && (
                <div className="linkedin-info">
                  💼 Enter LinkedIn profile details manually for ML analysis
                </div>
              )}

              {/* URL mode */}
              {mode === 'url' && platform === 'instagram' && (
                <div className="card fade-up">
                  <div style={{ fontSize:13, fontWeight:600, color:C.muted, marginBottom:12, textTransform:'uppercase', letterSpacing:'0.8px', color:'white'}}>
                    Instagram Profile
                  </div>
                  <input className="input-field" value={url} onChange={e=>setUrl(e.target.value)}
                    placeholder="instagram.com/username  or  @username"
                    onKeyDown={e=>e.key==='Enter'&&fetchProfile()} />
                  <p style={{ fontSize:11, color:C.faint, marginTop:6 }}>
                    Auto-fetches followers, posts, bio + scans for scam content
                  </p>
                  <button className="btn-primary" onClick={fetchProfile} disabled={loading}>
                    {loading ? <><span className="spinner"/>Fetching profile...</> : 'Fetch & Analyze →'}
                  </button>
                </div>
              )}

              {/* Manual mode */}
              {(mode === 'manual' || platform === 'linkedin') && (
                <div className="card fade-up">
                  <div style={{ fontSize:11, fontWeight:600, color:C.muted, marginBottom:14, textTransform:'uppercase', letterSpacing:'0.8px', color:'white' }}>
                    {platform === 'linkedin' ? 'LinkedIn Profile' : 'Manual Instagram Input'}
                  </div>

                  {platform === 'instagram' ? (
                    <div style={{ display:'grid', gap:12 }}>
                      <div>
                        <label>Username</label>
                        <input className="input-field" name="username" value={manual.username} onChange={handleManual} placeholder="john_doe" />
                      </div>
                      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:10 }}>
                        {[['Followers','followers'],['Following','following'],['Posts','posts']].map(([l,n])=>(
                          <div key={n}><label>{l}</label><input type="number" className="input-field" name={n} value={manual[n]} onChange={handleManual} placeholder="0" /></div>
                        ))}
                      </div>
                      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
                        <div><label>Bio length (chars)</label><input type="number" className="input-field" name="description_length" value={manual.description_length} onChange={handleManual} placeholder="0" /></div>
                        <div><label>Full name words</label><input type="number" className="input-field" name="fullname_words" value={manual.fullname_words} onChange={handleManual} placeholder="0" /></div>
                      </div>
                      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
                        <div><label>Nums ratio username (0–1)</label><input type="number" step="0.01" className="input-field" name="nums_length_username" value={manual.nums_length_username} onChange={handleManual} placeholder="0.0" /></div>
                        <div><label>Nums ratio fullname (0–1)</label><input type="number" step="0.01" className="input-field" name="nums_length_fullname" value={manual.nums_length_fullname} onChange={handleManual} placeholder="0.0" /></div>
                      </div>
                      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8 }}>
                        {[['Has profile picture','profile_pic'],['Has external URL','external_url'],['Private account','private'],['Username = full name','name_equals_username']].map(([l,n])=>(
                          <label key={n} style={{ display:'flex', alignItems:'center', gap:8, fontSize:13, color:C.muted, cursor:'pointer', fontWeight:400, letterSpacing:0 }}>
                            <input type="checkbox" name={n} checked={manual[n]===1} onChange={handleManual} style={{ accentColor:C.accent }} />{l}
                          </label>
                        ))}
                      </div>
                      <div>
                        <label>Bio / Caption text <span style={{color:C.faint}}>(scanned for scam)</span></label>
                        <textarea className="input-field" name="bio_text" value={manual.bio_text} onChange={handleManual} placeholder="Paste bio or post caption..." />
                      </div>
                    </div>
                  ) : (
                    <div style={{ display:'grid', gap:12 }}>
                      <div><label>LinkedIn Username</label><input className="input-field" name="username" value={manual.username} onChange={handleManual} placeholder="john-smith" /></div>
                      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
                        <div><label>Connections</label><input type="number" className="input-field" name="connections" value={manual.connections} onChange={handleManual} placeholder="500" /></div>
                        <div><label>Followers</label><input type="number" className="input-field" name="followers" value={manual.followers} onChange={handleManual} placeholder="300" /></div>
                      </div>
                      <div style={{ fontSize:11, color:C.faint, fontWeight:600, textTransform:'uppercase', letterSpacing:'0.5px' }}>Profile Activity</div>
                      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:10 }}>
                        {[['Experiences','experience_count'],['Educations','education_count'],['Skills','skills_count']].map(([l,n])=>(
                          <div key={n}><label>{l}</label><input type="number" className="input-field" name={n} value={manual[n]} onChange={handleManual} placeholder="0" /></div>
                        ))}
                      </div>
                      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:10 }}>
                        {[['Recommendations','recommendations'],['Projects','projects'],['Publications','publications']].map(([l,n])=>(
                          <div key={n}><label>{l}</label><input type="number" className="input-field" name={n} value={manual[n]} onChange={handleManual} placeholder="0" /></div>
                        ))}
                      </div>
                      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:10 }}>
                        {[['Courses','courses'],['Honors','honors'],['Languages','languages']].map(([l,n])=>(
                          <div key={n}><label>{l}</label><input type="number" className="input-field" name={n} value={manual[n]} onChange={handleManual} placeholder="0" /></div>
                        ))}
                      </div>
                      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
                        {[['Organizations','organizations'],['Activities','activities']].map(([l,n])=>(
                          <div key={n}><label>{l}</label><input type="number" className="input-field" name={n} value={manual[n]} onChange={handleManual} placeholder="0" /></div>
                        ))}
                      </div>
                      <div>
                        <label>About / Bio <span style={{color:C.faint}}>(scanned for scam)</span></label>
                        <textarea className="input-field" name="linkedin_bio" value={manual.linkedin_bio} onChange={handleManual} placeholder="Paste LinkedIn about section..." />
                      </div>
                      <div style={{ background:`rgba(59,130,246,0.05)`, border:`1px solid rgba(59,130,246,0.15)`, borderRadius:8, padding:'8px 12px', fontSize:11, color:C.faint }}>
                        Profile Strength = Skills + Experiences + Educations · Engagement = Followers + Recommendations
                      </div>
                    </div>
                  )}
                  <button className="btn-primary" onClick={submitManual}>Analyze Profile →</button>
                </div>
              )}
            </div>
          )}

          {/* ── FETCHED PREVIEW ── */}
          {step === 'fetched' && profile && (
            <div className="fade-up">
              <div className="card">
                {/* Profile header */}
                <div style={{ display:'flex', gap:14, alignItems:'center', marginBottom:16 }}>
                  {profile.display?.profile_pic_url ? (
                    <img src={profile.display.profile_pic_url} alt="pic"
                      style={{ width:60, height:60, borderRadius:'50%', objectFit:'cover', border:`2px solid ${C.border}` }}
                      onError={e => { e.target.style.display='none'; e.target.nextSibling.style.display='flex' }}
                    />
                  ) : null}
                  <div style={{ width:60, height:60, borderRadius:'50%', background:`linear-gradient(135deg, ${C.accent}33, ${C.accentLo}33)`, border:`2px solid ${C.border}`, display: profile.display?.profile_pic_url ? 'none' : 'flex', alignItems:'center', justifyContent:'center', fontSize:24, flexShrink:0 }}>
                    {platform==='linkedin'?'💼':'👤'}
                  </div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontWeight:700, fontSize:16, color:C.text }}>
                      {platform==='linkedin'?'':('@')}{profile.username}
                    </div>
                    {profile.display?.full_name && profile.display.full_name !== profile.username && (
                      <div style={{ fontSize:13, color:C.muted, marginTop:2 }}>{profile.display.full_name}</div>
                    )}
                    <div style={{ display:'flex', gap:6, marginTop:6, flexWrap:'wrap' }}>
                      {profile.display?.is_verified && (
                        <span className="tag" style={{ background:'rgba(59,130,246,0.15)', color:C.accent }}>✓ Verified</span>
                      )}
                      <span className="tag" style={{ background:`rgba(148,163,184,0.1)`, color:C.faint }}>
                        {mode==='url' ? '✅ Fetched' : '✏️ Manual'}
                      </span>
                      {platform==='instagram' && (
                        <span className="tag" style={{ background:`rgba(148,163,184,0.1)`, color:C.faint }}>
                          {profile.private ? '🔒 Private' : '🌐 Public'}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Stats */}
                {platform === 'linkedin' ? (
                  <>
                    <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:8, marginBottom:8 }}>
                      {[['Connections',profile.connections],['Skills',profile.skills_count],['Experience',profile.experience_count]].map(([l,v])=>(
                        <div key={l} className="stat-box">
                          <div style={{ fontWeight:700, fontSize:18, color:C.text }}>{Number(v||0).toLocaleString()}</div>
                          <div style={{ fontSize:11, color:C.faint, marginTop:2 }}>{l}</div>
                        </div>
                      ))}
                    </div>
                    <div style={{ fontSize:12, color:C.faint }}>
                      Strength: {profile.profile_strength} · Engagement: {profile.engagement}
                    </div>
                  </>
                ) : (
                  <>
                    <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:8, marginBottom:8 }}>
                      {[['Posts',profile.posts],['Followers',profile.followers],['Following',profile.following]].map(([l,v])=>(
                        <div key={l} className="stat-box">
                          <div style={{ fontWeight:700, fontSize:18, color:C.text }}>{Number(v||0).toLocaleString()}</div>
                          <div style={{ fontSize:11, color:C.faint, marginTop:2 }}>{l}</div>
                        </div>
                      ))}
                    </div>
                    <div style={{ fontSize:12, color:C.faint }}>
                      {profile.profile_pic ? '📷 Has photo' : '👤 No photo'} &nbsp;·&nbsp;
                      {profile.external_url ? '🔗 Has URL' : 'No external URL'}
                    </div>
                  </>
                )}

                {/* Bio */}
                {(profile.display?.bio || profile.bio_text) && (
                  <div style={{ marginTop:12, padding:'10px 12px', background:C.surface, borderRadius:8, fontSize:13, color:C.muted, lineHeight:1.6, borderLeft:`2px solid ${C.border}` }}>
                    {profile.display?.bio || profile.bio_text}
                  </div>
                )}

                {/* Post captions preview */}
                {profile.bio_scan?.captions && profile.bio_scan.captions.length > 0 && (
                  <div style={{ marginTop:12 }}>
                    <div style={{ fontSize:11, color:C.faint, fontWeight:600, textTransform:'uppercase', letterSpacing:'0.5px', marginBottom:6 }}>
                      📸 Recent Captions ({profile.bio_scan.captions.length})
                    </div>
                    {profile.bio_scan.captions.slice(0,3).map((cap,i) => (
                      <div key={i} className="caption-item">
                        {cap.slice(0,120)}{cap.length>120?'…':''}
                      </div>
                    ))}
                  </div>
                )}

                {/* Scam warning in preview */}
                {profile.bio_scan?.found && (
                  <ScamWarning
                    categories={profile.bio_scan.categories}
                    bioKeywords={profile.bio_scan.bio_keywords}
                    postKeywords={profile.bio_scan.post_keywords}
                    postsAnalyzed={profile.bio_scan.posts_analyzed}
                  />
                )}

                <button className="btn-green" onClick={analyze} disabled={loading}>
                  {loading ? <><span className="spinner"/>Analyzing...</> : 'Run ML Analysis →'}
                </button>
                <button className="btn-secondary" onClick={reset}>← Start over</button>
              </div>
            </div>
          )}

          {/* ── RESULT ── */}
          {step === 'result' && result && (
            <div className="fade-up">
              <div className="card" style={{
                borderColor: result.result==='Fake' ? 'rgba(239,68,68,0.4)' : 'rgba(16,185,129,0.4)',
                background: result.result==='Fake'
                  ? 'linear-gradient(180deg, rgba(239,68,68,0.06) 0%, rgba(26,34,53,1) 60%)'
                  : 'linear-gradient(180deg, rgba(16,185,129,0.06) 0%, rgba(26,34,53,1) 60%)'
              }}>
                {/* Platform badge */}
                <div style={{ fontSize:11, color:C.faint, marginBottom:10, textTransform:'uppercase', letterSpacing:'0.8px' }}>
                  {platform==='linkedin' ? '💼 LinkedIn' : '📷 Instagram'} · ML Analysis
                </div>

                {/* Main verdict */}
                <div style={{ display:'flex', alignItems:'center', gap:12, marginBottom:4 }}>
                  <div style={{ fontSize:28, fontWeight:800, color: result.result==='Fake' ? C.red : C.green, letterSpacing:'-0.5px' }}>
                    {result.result==='Fake' ? '⚠ FAKE ACCOUNT' : '✓ GENUINE ACCOUNT'}
                  </div>
                </div>

                {result.scam_detected && (
                  <div style={{ fontSize:12, color:C.amber, marginBottom:4, fontWeight:500 }}>
                    ⚠ Result overridden by scam content analysis
                  </div>
                )}

                {/* Risk level */}
                <div style={{ fontSize:13, color:C.muted, marginBottom:12 }}>
                  Risk Level:{' '}
                  <strong style={{ color: riskColor(result.risk_score) }}>
                    {result.risk_level}
                  </strong>
                  {' '}— {result.risk_label}
                  {result.ml_score !== undefined && (
                    <span style={{ color:C.faint, fontSize:11, marginLeft:8 }}>
                      (ML: {result.ml_score}%)
                    </span>
                  )}
                </div>

                {/* Risk score */}
                <div style={{ fontSize:32, fontWeight:800, color: riskColor(result.risk_score), marginBottom:4, letterSpacing:'-1px' }}>
                  {result.risk_score}<span style={{ fontSize:18, fontWeight:400 }}>%</span>
                </div>
                <div style={{ fontSize:11, color:C.faint, marginBottom:6 }}>Risk Score</div>

                {/* Risk bar */}
                <div className="risk-bar-track">
                  <div className="risk-indicator" style={{ left:`${Math.min(result.risk_score, 99)}%` }} />
                </div>
                <div style={{ display:'flex', justifyContent:'space-between', fontSize:10, color:C.faint, marginBottom:14 }}>
                  <span>Safe 0%</span><span>Suspicious 50%</span><span>100% Fake</span>
                </div>

                {/* Profile summary */}
                <div style={{ fontSize:13, color:C.muted, marginBottom:14, padding:'8px 12px', background:C.surface, borderRadius:8, display:'flex', alignItems:'center', gap:8, flexWrap:'wrap' }}>
                  {platform==='linkedin'
                    ? <><strong style={{color:C.text}}>{profile?.username}</strong> · {profile?.connections||0} connections · {profile?.skills_count||0} skills</>
                    : <><strong style={{color:C.text}}>@{profile?.username}</strong> · {Number(profile?.followers||0).toLocaleString()} followers · {profile?.posts||0} posts</>
                  }
                </div>

                {/* Scam warning in result */}
                {(result.scam_detected || (result.web_signals && result.web_signals.length > 0)) && (
                  <ScamWarning
                    categories={result.scam_categories}
                    bioKeywords={result.bio_keywords}
                    postKeywords={result.post_keywords}
                    postsAnalyzed={result.posts_analyzed}
                    webSignals={result.web_signals}
                    websiteUrl={result.website_url}
                    websiteSsl={result.website_ssl}
                  />
                )}
                {/* LLM Analysis */}
                {result.llm_verdict && (
                  <div style={{
                    background: result.llm_verdict === 'SCAM'
                      ? 'rgba(239,68,68,0.07)'
                      : result.llm_verdict === 'SUSPICIOUS'
                      ? 'rgba(245,158,11,0.07)'
                      : 'rgba(16,185,129,0.07)',
                    border: `1px solid ${
                      result.llm_verdict === 'SCAM' ? 'rgba(239,68,68,0.25)'
                      : result.llm_verdict === 'SUSPICIOUS' ? 'rgba(245,158,11,0.25)'
                      : 'rgba(16,185,129,0.25)'
                    }`,
                    borderRadius: 10,
                    padding: '12px 14px',
                    marginTop: 10
                  }}>
                    <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}>
                      <span style={{ fontSize:11, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.8px',
                        color: result.llm_verdict==='SCAM' ? C.red : result.llm_verdict==='SUSPICIOUS' ? C.amber : C.green
                      }}>
                        🤖 AI Analysis · {result.llm_verdict}
                      </span>
                      {result.llm_confidence && (
                        <span style={{ fontSize:11, color:C.faint }}>
                          {result.llm_confidence}% confidence
                        </span>
                      )}
                    </div>
                    {result.llm_reason && (
                      <div style={{ fontSize:12, color:C.muted, lineHeight:1.6 }}>
                        {result.llm_reason}
                      </div>
                    )}
                  </div>
                )}

                {/* Hashes */}
                <div className="hash-box" style={{ marginTop:14 }}>
                  <div style={{ fontWeight:600, color:C.muted, marginBottom:6, fontFamily:'Space Grotesk', fontSize:11, textTransform:'uppercase', letterSpacing:'0.5px' }}>
                    Verification Data
                  </div>
                  <div style={{ marginBottom:4 }}>
                    <span style={{ color:C.faint }}>SHA-256 · </span>{result.hash}
                  </div>
                  {result.tx_hash && (
                    <div>
                      <span style={{ color:C.faint }}>Blockchain · </span>
                      <a href={`https://sepolia.etherscan.io/tx/${result.tx_hash}`}
                        target="_blank" rel="noreferrer"
                        style={{ color:C.accent, textDecoration:'none' }}>
                        {result.tx_hash.slice(0,22)}... ↗ Etherscan
                      </a>
                    </div>
                  )}
                </div>
              </div>

              {/* Verify button */}
              <button
                onClick={verifyOnBlockchain} disabled={verifying}
                style={{ width:'100%', padding:'13px', background:'transparent', color:C.accent, border:`1px solid ${C.accent}`, borderRadius:10, fontSize:14, fontWeight:600, cursor:'pointer', marginBottom:8, fontFamily:'Space Grotesk', transition:'background 0.2s' }}
                onMouseOver={e=>e.target.style.background='rgba(59,130,246,0.1)'}
                onMouseOut={e=>e.target.style.background='transparent'}
              >
                {verifying ? <><span className="spinner"/>Verifying...</> : '⛓ Verify on Blockchain'}
              </button>

              {/* Verify result */}
              {verifyResult && (
                <div className="verify-box fade-up" style={{
                  background: verifyResult.verified ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)',
                  border: `1px solid ${verifyResult.verified ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`
                }}>
                  <div style={{ fontSize:15, fontWeight:700, color: verifyResult.verified ? C.green : C.red, marginBottom:6 }}>
                    {verifyResult.verified ? '✅ AUTHENTIC — Not Tampered' : '❌ TAMPERED — Data Modified'}
                  </div>
                  <div style={{ fontSize:12, color:C.muted, marginBottom:10 }}>{verifyResult.message}</div>
                  <div className="hash-box">
                    <div style={{ marginBottom:4 }}>
                      <span style={{ color:C.faint }}>Recalculated · </span>
                      <span style={{ color: verifyResult.recalculated_hash===verifyResult.stored_db_hash ? C.green : C.red }}>
                        {verifyResult.recalculated_hash}
                      </span>
                    </div>
                    <div style={{ marginBottom:4 }}>
                      <span style={{ color:C.faint }}>MongoDB · </span>
                      <span style={{ color: verifyResult.recalculated_hash===verifyResult.stored_db_hash ? C.green : C.red }}>
                        {verifyResult.stored_db_hash}
                      </span>
                    </div>
                    <div>
                      <span style={{ color:C.faint }}>Blockchain · </span>
                      <span style={{ color: verifyResult.stored_db_hash===verifyResult.blockchain_hash ? C.green : C.red }}>
                        {verifyResult.blockchain_hash || 'Not confirmed'}
                      </span>
                    </div>
                  </div>
                  <div style={{ fontSize:11, color:C.faint, marginTop:8 }}>
                    Originally analyzed: {verifyResult.timestamp?.split('T')[0]} at {verifyResult.timestamp?.split('T')[1]?.slice(0,8)} UTC
                  </div>
                </div>
              )}

              <button className="btn-secondary" onClick={reset} style={{ marginTop:8 }}>
                Analyze Another Profile
              </button>
            </div>
          )}

        </div>
      </div>
    </>
  )
}
