import Header from "./components/Header";
import Hero from "./components/Hero";
import Logos from "./components/Logos";
import Steps from "./components/Steps";
import Features from "./components/Features";
import Safety from "./components/Safety";
import Faq from "./components/Faq";
import Cta from "./components/Cta";
import Footer from "./components/Footer";

import "./styles/header.css";
import "./styles/hero.css";
import "./styles/logos.css";
import "./styles/steps.css";
import "./styles/features.css";
import "./styles/safety.css";
import "./styles/faq.css";
import "./styles/cta.css";
import "./styles/footer.css";

export default function App() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <Logos />
        <Steps />
        <Features />
        <Safety />
        <Faq />
        <Cta />
      </main>
      <Footer />
    </>
  );
}
