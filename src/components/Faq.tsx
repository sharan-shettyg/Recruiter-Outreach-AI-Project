const faqs = [
  {
    q: "Do I need a job description?",
    a: "No. The app is built for general recruiter outreach — you enter a target company and role, and Claude writes a cold email that fits. You can still paste a job description if you have one.",
  },
  {
    q: "Where do the recruiter emails come from?",
    a: "Recruiter contacts are found via Hunter's domain search, which returns verified professional email addresses for people at the company you specify. The app filters for recruiter, talent acquisition, and HR titles.",
  },
  {
    q: "Does the app send emails automatically?",
    a: "No. By default it creates a Gmail draft that you open, review, and send yourself. There is an optional send button, but it only fires after you explicitly approve and click it.",
  },
  {
    q: "Is my resume attached to the email?",
    a: "No. Your resume is used only by Claude to personalize the email body. It is never attached to or included in the message that gets sent.",
  },
  {
    q: "What do I need to set up?",
    a: "An Anthropic API key, a Zapier MCP connection for Hunter, and a Google OAuth credentials file for Gmail drafts. The README walks you through each step.",
  },
  {
    q: "Is this a hosted service?",
    a: "This is a local tool you run with Streamlit. A hosted web version is on the roadmap — for now, everything runs on your machine so your credentials never leave your device.",
  },
];

function FaqItem({ q, a }: { q: string; a: string }) {
  return (
    <details className="faq-item">
      <summary>
        <span>{q}</span>
        <svg className="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="m6 9 6 6 6-6" />
        </svg>
      </summary>
      <div className="faq-answer">{a}</div>
    </details>
  );
}

export default function Faq() {
  return (
    <section className="section faq" id="faq">
      <div className="container">
        <div className="faq-header">
          <span className="eyebrow">FAQ</span>
          <h2 className="section-title">Questions, answered</h2>
        </div>
        <div className="faq-list">
          {faqs.map((f) => (
            <FaqItem key={f.q} q={f.q} a={f.a} />
          ))}
        </div>
      </div>
    </section>
  );
}
