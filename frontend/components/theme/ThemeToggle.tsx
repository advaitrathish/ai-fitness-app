"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) return null;

  return (
    <div className="flex flex-col gap-4">
      <p>Current theme: {theme}</p>
      <button
        onClick={() => {
          const newTheme = theme === "dark" ? "light" : "dark";
          console.log("Switching to:", newTheme);
          setTheme(newTheme);
        }}
        className="px-4 py-2 rounded-lg border border-white"
      >
        Toggle Theme
      </button>
    </div>
  );
}