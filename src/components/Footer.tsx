import { BoltIcon } from "./Icons";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-top">
          <div className="footer-brand">
            <a href="#top" className="logo">
              <span className="logo-mark">
                <BoltIcon />
              </span>
              Recruiter Outreach AI
            </a>
            <p>
              Find verified recruiter emails, write personalized outreach with
              Claude, and send with confidence.
            </p>
          </div>
          <div className="footer-col">
            <h4>Product</h4>
            <ul>
              <li><a href="#how-it-works">How it works</a></li>
              <li><a href="#features">Features</a></li>
              <li><a href="#safety">Safety</a></li>
              <li><a href="#faq">FAQ</a></li>
            </ul>
          </div>
          <div className="footer-col">
            <h4>Setup</h4>
            <ul>
              <li><a href="#get-started">Get started</a></li>
              <li><a href="https://hunter.io" target="_blank" rel="noreferrer">Hunter</a></li>
              <li><a href="https://console.anthropic.com" target="_blank" rel="noreferrer">Anthropic API</a></li>
              <li><a href="https://developers.google.com/gmail/api" target="_blank" rel="noreferrer">Gmail API</a></li>
            </ul>
          </div>
          <div className="footer-col">
            <h4>Integrations</h4>
            <ul>
              <li><a href="https://hunter.io" target="_blank" rel="noreferrer">Hunter.io</a></li>
              <li><a href="https://zapier.com/apps/mcp" target="_blank" rel="noreferrer">Zapier MCP</a></li>
              <li><a href="https://www.anthropic.com/claude" target="_blank" rel="noreferrer">Claude</a></li>
              <li><a href="https://streamlit.io" target="_blank" rel="noreferrer">Streamlit</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <span>(c) 2026 Recruiter Outreach AI. A local-first MVP.</span>
          <span>Built with Claude, Hunter, and Gmail.</span>
        </div>
      </div>
    </footer>
  );
}
