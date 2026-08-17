import { FileIcon, UsersIcon, SparkleIcon, SendIcon } from "./Icons";

const steps = [
  {
    icon: <FileIcon />,
    num: "01",
    title: "Upload your resume",
    text: "Add your resume PDF and enter the company and role you're targeting. No job description required.",
  },
  {
    icon: <UsersIcon />,
    num: "02",
    title: "Find recruiters",
    text: "Hunter searches the company domain for verified recruiter, talent acquisition, and HR contacts.",
  },
  {
    icon: <SparkleIcon />,
    num: "03",
    title: "Claude writes outreach",
    text: "Claude reads your resume and writes a unique, professional email for each selected recruiter.",
  },
  {
    icon: <SendIcon />,
    num: "04",
    title: "Review and send",
    text: "Edit any email, then create a Gmail draft or send directly. You approve every message before it goes.",
  },
];

export default function Steps() {
  return (
    <section className="section steps" id="how-it-works">
      <div className="container">
        <div className="steps-header">
          <span className="eyebrow">How it works</span>
          <h2 className="section-title">From resume to outreach in four steps</h2>
          <p className="section-subtitle">
            The whole flow takes about five minutes. You stay in control at
            every stage — nothing is sent without your review.
          </p>
        </div>
        <div className="steps-grid">
          {steps.map((s) => (
            <div className="step-card" key={s.num}>
              <span className="step-num">{s.num}</span>
              <div className="step-icon">{s.icon}</div>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
