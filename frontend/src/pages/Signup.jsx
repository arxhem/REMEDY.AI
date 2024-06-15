import { Suspense, useState, useEffect } from "react";
import Button from "../components/ui/button";
import Authanimation from "../components/ui/authanimation";
import { Link, useNavigate } from "react-router-dom";
import HashLoader from "react-spinners/HashLoader";
import { toast } from "react-toastify";
import { BASE_URL } from "../utils/constants";

// Define a module-scoped variable to store the array values
let exportedArr = [];

function SignUp() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
    gender: "",
    occupation: "",
    age: "",
    height: "",
    weight: "",
  });

  const [arr, setArr] = useState([]);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  useEffect(() => {
    // Update arr whenever formData changes
    const valuesArray = Object.values(formData);
    setArr(valuesArray);

    // Update the module-scoped exportedArr
    exportedArr = valuesArray;
  }, [formData]);

  const submitHandler = async (event) => {
    event.preventDefault();
    setLoading(true);

    try {
      const res = await fetch(`${BASE_URL}/auth/register`, {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
        credentials: "include",
      });
      if (res.status === 409) {
        throw new Error("Something went wrong");
      }
      const { message } = await res.json();
      setLoading(false);
      toast.success(message);
      navigate("/login");
    } catch (err) {
      toast.error("User already exists");
      setLoading(false);
    }
  };

  return (
    <>
      <main className="flex flex-col sm:flex-row items-center justify-center sm:items-start mt-24 gap-12 sm:gap-6">
        <Suspense>
          <div className="w-[40%] sm:p-0 lg:p-24 lg:pt-0 -z-10">
            <Authanimation />
          </div>
        </Suspense>
        <div className="w-[40%] rounded-lg shadow-md md:p-10">
          <h3 className="text-center text-[22px] leading-9 font-bold mb-10">
            Create an <span className="text-primary"> account</span>
          </h3>
          <form className="space-y-6" onSubmit={submitHandler}>
            <div className="">
              <input
                type="text"
                placeholder="Enter Your Full Name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                className="input"
              />
            </div>
            <div className="">
              <input
                type="email"
                placeholder="Enter Your Email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                className="input"
              />
            </div>

            <div className="">
              <input
                type="password"
                placeholder="Enter Your Password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="input"
              />
            </div>
            <div className="flex gap-6">
              <select
                id="gender"
                name="gender"
                className="input"
                value={formData.gender}
                onChange={handleInputChange}
              >
                <option value="" disabled>
                  Gender
                </option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
              <input
                type="number"
                placeholder="Age"
                name="age"
                min={0}
                value={formData.age}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    age: e.target.value === "" ? "" : Number(e.target.value),
                  })
                }
                required
                className="input"
              />
              <input
                type="number"
                placeholder="Height"
                name="height"
                min={0}
                value={formData.height}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    height: e.target.value === "" ? "" : Number(e.target.value),
                  })
                }
                required
                className="input"
              />
              <input
                type="number"
                placeholder="Weight"
                name="weight"
                min={0}
                value={formData.weight}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    weight: e.target.value === "" ? "" : Number(e.target.value),
                  })
                }
                required
                className="input"
              />
            </div>
            <div className="mb-[3.5rem] flex items-center justify-between"></div>

            <div className="mt-10">
              <Button
                disabled={loading}
                type="submit"
                className={`w-full rounded-lg py-3 px-4`}
              >
                {loading ? (
                  <HashLoader
                    cssOverride={{ padding: ".75rem 0" }}
                    size={25}
                    color="#ffffff"
                  />
                ) : (
                  "Sign Up"
                )}
              </Button>
            </div>
            <p className="mt-5 text-head text-center cursor-pointer">
              Already have an account?
              <Link to="/login" className="text-primary font-medium ml-1">
                Login
              </Link>
            </p>
          </form>
        </div>
      </main>
    </>
  );
}

// Export the updated array
export { SignUp, exportedArr };
