import { ShieldIcon, CheckIcon, EyeIcon, LockIcon } from "./Icons";

const points = [
  {
    icon: <EyeIcon />,
    title: "You review every message",
    text: "Subjects and bodies are fully editable. Nothing is sent or drafted until you click the button.",
  },
  {
    icon: <CheckIcon />,
    title: "Drafts, not auto-sends",
    text: "The app uses Gmail's drafts.create. It never calls messages.send behind your back. You send manually from Gmail.",
  },
  {
    icon: <LockIcon />,
    title: "Credentials stay on your device",
    text: "Your Google OAuth token and API keys live in local files. They're never uploaded or shared.",
  },
];

export default function Safety() {
  return (
    <section className="section safety" id="safety">
      <div className="container safety-inner">
        <div className="safety-visual">
          <div className="safety-shield">
            <ShieldIcon />
          </div>
          <h3>Safety is built in, not bolted on</h3>
          <p>
            Recruiter Outreach AI is designed so that a human is always in the
            loop. The app creates drafts and writes copy — it never sends
            anything without your explicit approval.
          </p>
        </div>
        <ul className="safety-points">
          {points.map((p) => (
            <li className="safety-point" key={p.title}>
              <span className="safety-check">{p.icon}</span>
              <div>
                <h4>{p.title}</h4>
                <p>{p.text}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
