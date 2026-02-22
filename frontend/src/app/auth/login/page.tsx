"use client";

import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import { useState } from "react";

type Role = "user" | "trainer" | "admin";

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<Role>("user");

  const handleLogin = () => {
    Cookies.set("role", role);

    if (role === "user") router.push("/user/dashboard");
    else if (role === "trainer") router.push("/trainer/dashboard");
    else if (role === "admin") router.push("/admin/dashboard");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0F0F14] text-white">
      <div className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
        <h1 className="mb-6 text-2xl font-semibold text-center">
          Login to Fit<span className="text-purple-500">AI</span>
        </h1>

        <div className="space-y-4">
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as Role)}
            className="w-full rounded-xl bg-white/10 p-3 text-white outline-none"
          >
            <option value="user">User</option>
            <option value="trainer">Trainer</option>
            <option value="admin">Admin</option>
          </select>

          <button
            onClick={handleLogin}
            className="w-full rounded-xl bg-purple-600 py-3 font-medium transition hover:bg-purple-500"
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
}