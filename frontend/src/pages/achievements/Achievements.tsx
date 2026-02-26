import { useFitnessStore } from "@/store/useFitnessStore";

export default function Achievements() {
  const { totalXP, sessionsCompleted, streak, level } =
    useFitnessStore();

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-3xl font-bold">Achievements</h1>

      <div className="grid md:grid-cols-3 gap-6">
        <Badge
          title="First Workout"
          unlocked={sessionsCompleted >= 1}
        />
        <Badge
          title="100 XP Earned"
          unlocked={totalXP >= 100}
        />
        <Badge
          title="7 Day Streak"
          unlocked={streak >= 7}
        />
        <Badge
          title="Level 5 Reached"
          unlocked={level >= 5}
        />
      </div>
    </div>
  );
}

function Badge({
  title,
  unlocked,
}: {
  title: string;
  unlocked: boolean;
}) {
  return (
    <div
      className={`p-6 rounded-2xl shadow-lg backdrop-blur-xl ${
        unlocked
          ? "bg-green-200 text-green-900"
          : "bg-gray-200 text-gray-600"
      }`}
    >
      <p className="font-semibold">{title}</p>
      <p className="text-sm">
        {unlocked ? "Unlocked 🎉" : "Locked 🔒"}
      </p>
    </div>
  );
}