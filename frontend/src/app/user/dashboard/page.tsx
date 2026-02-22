export default function UserDashboard() {
  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold text-white/90">
          Welcome Back 👋
        </h1>
        <p className="text-white/60 mt-2">
          Here’s your performance overview.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">

        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
          <p className="text-sm text-white/60">Workout Score</p>
          <h3 className="mt-2 text-2xl font-semibold">87</h3>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
          <p className="text-sm text-white/60">Recovery Index</p>
          <h3 className="mt-2 text-2xl font-semibold text-green-400">
            Optimal
          </h3>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
          <p className="text-sm text-white/60">Weekly Progress</p>
          <h3 className="mt-2 text-2xl font-semibold">+12%</h3>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
          <p className="text-sm text-white/60">Streak</p>
          <h3 className="mt-2 text-2xl font-semibold text-purple-400">
            5 Days 🔥
          </h3>
        </div>

      </div>

      {/* Progress Section */}
      <div className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
        <h2 className="text-lg font-semibold mb-4">
          Weekly Workout Progress
        </h2>

        <div className="h-4 w-full rounded-full bg-white/10">
          <div className="h-4 w-[70%] rounded-full bg-gradient-to-r from-purple-400 to-purple-600" />
        </div>

        <p className="text-sm text-white/60 mt-3">
          4 of 6 workouts completed this week.
        </p>
      </div>

    </div>
  );
}