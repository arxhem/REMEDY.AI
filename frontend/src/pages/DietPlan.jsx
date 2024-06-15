import { useEffect, useState } from "react";
import AuthNavbar from "../components/AuthNavbar";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import { Groq } from "groq-sdk";
import { BASE_URL, RAG_BACKEND_URL } from "../utils/constants";

const groq = new Groq({
  apiKey: import.meta.env.VITE_GROQ_API_KEY,
  dangerouslyAllowBrowser: true,
});

function DietPlan() {
  const [dietPlan, setDietPlan] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  useEffect(() => {
    const fetchDiseasesAndGeneratePlan = async () => {
      setLoading(true);

      try {
        const response = await fetch(`${RAG_BACKEND_URL}/get_disease`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error("Error fetching diseases");
        }

        const data = await response.json();
        const parsedDiseases = data.answer;

        if (parsedDiseases && parsedDiseases.length > 0) {
          localStorage.setItem("disease", JSON.stringify(parsedDiseases));
          fetchDietPlanHandler(parsedDiseases);
        } else {
          setStatus("No relevant details as of now from user to suggest a diet plan!!!");
          setLoading(false);
        }
      } catch (error) {
        setStatus("Error fetching diseases");
        setLoading(false);
      }
    };

    fetchDiseasesAndGeneratePlan();
  }, []);

  const fetchDietPlanHandler = async (parsedDiseases) => {
    try {
      const chatCompletion = await groq.chat.completions.create({
        messages: [
          {
            role: "user",
            content: `Give me a diet plan and my disease if I am having the following diseases and medical problems: ${parsedDiseases}. Just give me at least 5 points in numbers and a max of 8 points, no other response, not in the beginning and not in the end, just the 5 points`,
          },
        ],
        model: "mixtral-8x7b-32768",
      });

      const response = chatCompletion.choices[0]?.message?.content;
      const result = parseNumberedPoints(response);

      setDietPlan(result);
      setLoading(false);
    } catch (error) {
      setStatus("Error generating diet plan");
      setLoading(false);
    }
  };

  function parseNumberedPoints(inputString) {
    // Split the input string by the numbered points using a regular expression
    const points = inputString.split(/\d+\.\s*/).filter(Boolean);

    // Trim any extra whitespace from each point
    return points.map((point) => point.trim());
  }

  return (
    <div className="">
      <AuthNavbar />
      <h2 className="text-3xl mt-4 text-center font-medium">Your customized diet plan</h2>
      <div className="mt-14">
        {loading ? (
          <div className="w-3/5 mx-auto">
            <Skeleton count={3} />
          </div>
        ) : (
          <div className="w-4/5 flex gap-6 flex-wrap mx-auto mt-8">
            {dietPlan.length > 0 ? (
              dietPlan.map((e, index) => (
                <div
                  key={index}
                  className="mx-auto max-w-[500px] bg-zinc-700 text-white shadow-lg rounded-lg transform hover:scale-105 transition-transform duration-300 ease-in-out border border-gray-300 p-6"
                >
                  <li className="list-none">{e}</li>
                </div>
              ))
            ) : (
              <h2 className="text-center">{status}</h2>
            )}
          </div>
        )}
      </div>
      <h2 className="text-center">{status}</h2>
    </div>
  );
}

export default DietPlan;
