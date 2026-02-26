import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { User, Mail, Lock, Eye, EyeOff } from "lucide-react";
import GlassBackground from "@/components/GlassBackground";
import ThemeToggle from "@/components/ThemeToggle";
import API from "../lib/apis";

const Register = () => {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    age: "",
    height: "",
    weight: "",
    goal: "maintain",
    consent: false,
  });

  const [error, setError] = useState("");

  const handleChange = (e: any) => {
    const { name, value, type, checked } = e.target;
    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!form.consent) {
      setError("You must agree to data policy");
      return;
    }

    try {
      await API.post("register/", {
        username: form.username,
        email: form.email,
        password: form.password,
        confirm_password: form.confirmPassword,
        age: parseInt(form.age),
        height: parseFloat(form.height),
        weight: parseFloat(form.weight),
        goal: form.goal,
        consent: form.consent,
      });

      navigate("/login");
    } catch (err: any) {
      setError("Registration failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative">
      <GlassBackground />

      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        className="w-full max-w-lg bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 shadow-xl"
      >
        <h2 className="text-3xl font-bold text-center mb-2">
          Create Account
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">

          {/* Username */}
          <div className="relative">
            <User className="absolute left-3 top-3 text-gray-400" size={18} />
            <input
              name="username"
              placeholder="Username"
              className="w-full pl-10 pr-3 py-2 rounded-lg bg-white/20 border border-white/30 focus:outline-none"
              onChange={handleChange}
              required
            />
          </div>

          {/* Email */}
          <div className="relative">
            <Mail className="absolute left-3 top-3 text-gray-400" size={18} />
            <input
              name="email"
              placeholder="Email (optional)"
              className="w-full pl-10 pr-3 py-2 rounded-lg bg-white/20 border border-white/30 focus:outline-none"
              onChange={handleChange}
            />
          </div>

          {/* Password */}
          <div className="relative">
            <Lock className="absolute left-3 top-3 text-gray-400" size={18} />
            <input
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Password"
              className="w-full pl-10 pr-10 py-2 rounded-lg bg-white/20 border border-white/30 focus:outline-none"
              onChange={handleChange}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-2 text-gray-400"
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {/* Confirm Password */}
          <div className="relative">
            <Lock className="absolute left-3 top-3 text-gray-400" size={18} />
            <input
              type={showConfirm ? "text" : "password"}
              name="confirmPassword"
              placeholder="Confirm Password"
              className="w-full pl-10 pr-10 py-2 rounded-lg bg-white/20 border border-white/30 focus:outline-none"
              onChange={handleChange}
              required
            />
            <button
              type="button"
              onClick={() => setShowConfirm(!showConfirm)}
              className="absolute right-3 top-2 text-gray-400"
            >
              {showConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {/* Age / Height / Weight */}
          <div className="grid grid-cols-3 gap-3">
            <input name="age" placeholder="Age" className="inputGlass" onChange={handleChange} required />
            <input name="height" placeholder="Height (cm)" className="inputGlass" onChange={handleChange} required />
            <input name="weight" placeholder="Weight (kg)" className="inputGlass" onChange={handleChange} required />
          </div>

          {/* Goal */}
          <select
            name="goal"
            onChange={handleChange}
            className="w-full py-2 px-3 rounded-lg bg-white/20 border border-white/30"
          >
            <option value="cut">Cut</option>
            <option value="bulk">Bulk</option>
            <option value="maintain">Maintain</option>
          </select>

          {/* Consent */}
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" name="consent" onChange={handleChange} />
            I agree to data usage policy
          </label>

          {error && (
            <p className="text-red-400 text-sm text-center">{error}</p>
          )}

          <button
            type="submit"
            className="w-full py-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold"
          >
            Sign Up
          </button>
        </form>

        <p className="text-center text-sm mt-4">
          Already have an account?{" "}
          <Link to="/login" className="text-purple-400">
            Sign In
          </Link>
        </p>
      </motion.div>
    </div>
  );
};

export default Register;