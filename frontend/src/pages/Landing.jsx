import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import Features from "../components/Landing/Features";
import Hero from "../components/Landing/Hero";
import { AuroraBackground } from "../components/ui/aurorobackground";
import useFetchHook from "../hooks/useFetch.hook";
import { BASE_URL } from "../utils/constants";
import Footer from "../components/Landing/Footer";

function Landing() {
  const navigate = useNavigate();
  const { data, error, loading } = useFetchHook(`${BASE_URL}/auth/current-user`);

  useEffect(() => {
    if (data) {
      navigate("/home");
    }
  }, [data, navigate]);

  return (
    <div>
      <AuroraBackground>
        <Header />
        <Hero />
      </AuroraBackground>
      <Features />
      <Footer />
    </div>
  );
}

export default Landing;
