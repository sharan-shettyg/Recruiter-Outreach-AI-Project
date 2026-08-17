export default function Hero() {
  return (
    <section className="hero" id="top">
      <div className="hero-bg" />
      <div className="container hero-inner">
        <div className="hero-content">
          <span className="eyebrow">Find recruiters faster</span>
          <h1>
            Find the right recruiters and write outreach that <span className="accent">actually gets replies</span>.
          </h1>
          <p className="hero-lead">
            Recruiter Outreach AI locates verified recruiter emails at any
            company, then uses Claude to write a personalized cold email from
            your resume — ready to review and send as a Gmail draft.
          </p>
          <div className="hero-actions">
            <a href="#get-started" className="btn btn-primary btn-lg">
              Get started free
            </a>
            <a href="#how-it-works" className="btn btn-secondary btn-lg">
              See how it works
            </a>
          </div>
          <div className="hero-stats">
            <div>
              <div className="stat-value">5 min</div>
              <div className="stat-label">From resume to draft</div>
            </div>
            <div>
              <div className="stat-value">10+</div>
              <div className="stat-label">Recruiters per search</div>
            </div>
            <div>
              <div className="stat-value">100%</div>
              <div className="stat-label">Human-reviewed sends</div>
            </div>
          </div>
        </div>

        <div className="hero-visual">
          <div className="preview-card">
            <div className="preview-top">
              <span className="preview-dot" />
              <span className="preview-dot" />
              <span className="preview-dot" />
              <span className="preview-title">Recruiter Outreach AI</span>
            </div>
            <div className="preview-body">
              <div className="preview-step">
                <span className="preview-step-num">1</span>
                <div className="preview-step-text">
                  <b>Upload your resume</b> and enter a target company.
                  <br />
                  <span className="tag tag-done">Done</span>
                </div>
              </div>
              <div className="preview-step">
                <span className="preview-step-num">2</span>
                <div className="preview-step-text">
                  <b>Hunter finds recruiters</b> at deloitte.com — names,
                  titles, and verified emails.
                  <br />
                  <span className="tag tag-done">3 contacts</span>
                </div>
              </div>
              <div className="preview-step">
                <span className="preview-step-num">3</span>
                <div className="preview-step-text">
                  <b>Claude writes each email</b> from your resume, tailored to
                  the role and recruiter.
                  <br />
                  <span className="tag tag-ai">AI personalized</span>
                </div>
              </div>
              <div className="preview-step">
                <span className="preview-step-num">4</span>
                <div className="preview-step-text">
                  <b>Review, edit, and create a Gmail draft</b> — you stay in
                  control of every send.
                  <br />
                  <span className="tag tag-done">Ready</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
