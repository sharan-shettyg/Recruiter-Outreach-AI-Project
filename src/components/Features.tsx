import { TargetIcon, SparkleIcon, ShieldIcon, EyeIcon, LockIcon, MailIcon } from "./Icons";

const features = [
  {
    icon: <TargetIcon />,
    cls: "fi-blue",
    title: "Verified recruiter emails",
    text: "Hunter's domain search returns real, verified email addresses for recruiters and talent acquisition professionals — not guesses.",
  },
  {
    icon: <SparkleIcon />,
    cls: "fi-amber",
    title: "Resume-aware personalization",
    text: "Claude reads your actual resume and highlights 2–3 strengths that fit each role. Every email is written for a specific recruiter.",
  },
  {
    icon: <EyeIcon />,
    cls: "fi-green",
    title: "Full review before sending",
    text: "Every subject and body is editable. You approve recipients, copy, and timing. No email leaves without your say-so.",
  },
  {
    icon: <MailIcon />,
    cls: "fi-blue",
    title: "Gmail drafts, not auto-sends",
    text: "Creates Gmail drafts you can open, tweak, and send manually. The app never calls send on your behalf unless you choose to.",
  },
  {
    icon: <LockIcon />,
    cls: "fi-amber",
    title: "Your data stays local",
    text: "Your resume is used only for personalization and is never attached to an email. Credentials and tokens stay on your machine.",
  },
  {
    icon: <ShieldIcon />,
    cls: "fi-green",
    title: "Honest, grounded copy",
    text: "Claude is instructed to use only facts from your resume — no invented skills, employers, or credentials. No desperate sales tone.",
  },
];

export default function Features() {
  return (
    <section className="section features" id="features">
      <div className="container">
        <div className="features-header">
          <span className="eyebrow">Why it's different</span>
          <h2 className="section-title">Outreach that's personal, not spammy</h2>
          <p className="section-subtitle">
            Most cold outreach tools blast generic templates. Recruiter Outreach
            AI writes a grounded, specific email for each recruiter — and keeps
            you in control of every send.
          </p>
        </div>
        <div className="features-grid">
          {features.map((f) => (
            <div className="feature-card" key={f.title}>
              <div className={`feature-icon ${f.cls}`}>{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
