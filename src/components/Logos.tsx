const logos = [
  { name: "Hunter", letter: "H" },
  { name: "Claude", letter: "C" },
  { name: "Gmail", letter: "G" },
  { name: "Zapier", letter: "Z" },
  { name: "Streamlit", letter: "S" },
];

export default function Logos() {
  return (
    <section className="logos">
      <div className="container">
        <p className="logos-label">Powered by tools you already trust</p>
        <div className="logos-row">
          {logos.map((l) => (
            <div className="logo-item" key={l.name}>
              <span
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 7,
                  background: "currentColor",
                  color: "#fff",
                  display: "grid",
                  placeItems: "center",
                  fontSize: 14,
                  fontWeight: 800,
                }}
              >
                {l.letter}
              </span>
              {l.name}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
