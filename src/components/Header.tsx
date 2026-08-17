import { useEffect, useState } from "react";
import { BoltIcon, MenuIcon } from "./Icons";

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={`header ${scrolled ? "scrolled" : ""}`}>
      <div className="container header-inner">
        <a href="#top" className="logo" aria-label="Recruiter Outreach AI home">
          <span className="logo-mark">
            <BoltIcon />
          </span>
          Recruiter Outreach AI
        </a>

        <nav className={`nav ${menuOpen ? "open" : ""}`} aria-label="Primary">
          <ul className="nav-links">
            <li>
              <a href="#how-it-works" onClick={() => setMenuOpen(false)}>
                How it works
              </a>
            </li>
            <li>
              <a href="#features" onClick={() => setMenuOpen(false)}>
                Features
              </a>
            </li>
            <li>
              <a href="#safety" onClick={() => setMenuOpen(false)}>
                Safety
              </a>
            </li>
            <li>
              <a href="#faq" onClick={() => setMenuOpen(false)}>
                FAQ
              </a>
            </li>
          </ul>
          <a href="#get-started" className="btn btn-ghost">
            Docs
          </a>
          <a href="#get-started" className="btn btn-primary">
            Get started
          </a>
          <button
            className="menu-toggle"
            aria-label="Toggle menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((o) => !o)}
          >
            <MenuIcon />
          </button>
        </nav>
      </div>
    </header>
  );
}
