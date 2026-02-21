import { ThemeToggle } from "@/components/ThemeToggle";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6">
      <h1 className="text-4xl font-bold">
        Theme Test
      </h1>

      <div className="w-40 h-40 bg-blue-500 dark:bg-yellow-400 rounded-lg transition-colors duration-300" />

      <ThemeToggle />
    </div>
  );
}