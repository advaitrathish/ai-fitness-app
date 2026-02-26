import { motion } from "framer-motion";
import {
  Flame,
  Dumbbell,
  Clock,
  Zap,
  TrendingUp,
  Trophy,
  Target,
  ArrowRight,
} from "lucide-react";
import XPBar from "@/components/XPBar";
import { useFitnessStore } from "@/store/useFitnessStore";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

const Dashboard = () => {
  const { totalXP, level, streak, sessionsCompleted } =
    useFitnessStore();

  const stats = [
    {
      label: "Total XP",
      value: totalXP,
      icon: Flame,
      color:
        "from-[hsl(25,100%,65%)] to-[hsl(340,90%,60%)]",
    },
    {
      label: "Workouts Done",
      value: sessionsCompleted,
      icon: Dumbbell,
      color:
        "from-[hsl(265,85%,60%)] to-[hsl(330,85%,60%)]",
    },
    {
      label: "Current Level",
      value: level,
      icon: TrendingUp,
      color:
        "from-[hsl(200,90%,55%)] to-[hsl(265,85%,60%)]",
    },
    {
      label: "Current Streak",
      value: `${streak} days`,
      icon: Zap,
      color:
        "from-[hsl(160,85%,50%)] to-[hsl(200,90%,55%)]",
    },
  ];

  const achievements = [
    {
      name: "First Workout",
      icon: "🏋️",
      unlocked: sessionsCompleted >= 1,
    },
    {
      name: "100 XP Earned",
      icon: "🔥",
      unlocked: totalXP >= 100,
    },
    {
      name: "Level 5",
      icon: "⭐",
      unlocked: level >= 5,
    },
    {
      name: "7 Day Streak",
      icon: "🏆",
      unlocked: streak >= 7,
    },
  ];

  const recentWorkouts = [
    {
      name: "Live Session",
      duration: "Simulated",
      xp: `+${totalXP > 0 ? 50 : 0} XP`,
      date: "Today",
    },
  ];

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-6 max-w-6xl"
    >
      {/* Header */}
      <motion.div
        variants={item}
        className="flex flex-col md:flex-row md:items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl md:text-3xl font-display font-bold text-foreground">
            Welcome back,{" "}
            <span className="gradient-text">Athlete</span> 👋
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Keep pushing your limits today.
          </p>
        </div>
        <div className="w-full md:w-72">
          <XPBar current={totalXP} max={level * 1000} level={level} />
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        variants={item}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {stats.map((s) => (
          <motion.div
            key={s.label}
            variants={item}
            className="stat-card"
          >
            <div
              className={`w-10 h-10 rounded-xl bg-gradient-to-br ${s.color} flex items-center justify-center`}
            >
              <s.icon className="w-5 h-5 text-white" />
            </div>
            <p className="text-2xl font-display font-bold text-foreground">
              {s.value}
            </p>
            <p className="text-xs text-muted-foreground">
              {s.label}
            </p>
          </motion.div>
        ))}
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Workouts */}
        <motion.div
          variants={item}
          className="lg:col-span-2 glass-card-strong p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-semibold text-foreground flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-primary" />{" "}
              Recent Workouts
            </h2>
            <button className="text-xs text-primary font-medium flex items-center gap-1 hover:underline">
              View All{" "}
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {recentWorkouts.map((w) => (
              <div
                key={w.name}
                className="flex items-center justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary/15 flex items-center justify-center">
                    <Dumbbell className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {w.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {w.duration} • {w.date}
                    </p>
                  </div>
                </div>
                <span className="text-xs font-semibold text-secondary">
                  {w.xp}
                </span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Achievements */}
        <motion.div
          variants={item}
          className="glass-card-strong p-5"
        >
          <h2 className="font-display font-semibold text-foreground flex items-center gap-2 mb-4">
            <Trophy className="w-4 h-4 text-accent" /> Achievements
          </h2>

          <div className="grid grid-cols-2 gap-3">
            {achievements.map((a) => (
              <div
                key={a.name}
                className={`flex flex-col items-center p-3 rounded-lg text-center transition-all ${
                  a.unlocked
                    ? "bg-primary/10"
                    : "bg-muted/30 opacity-50"
                }`}
              >
                <span className="text-2xl mb-1">
                  {a.icon}
                </span>
                <span className="text-xs font-medium text-foreground">
                  {a.name}
                </span>
                {!a.unlocked && (
                  <span className="text-[10px] text-muted-foreground">
                    Locked
                  </span>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Daily Goals */}
      <motion.div
        variants={item}
        className="glass-card-strong p-5"
      >
        <h2 className="font-display font-semibold text-foreground flex items-center gap-2 mb-4">
          <Target className="w-4 h-4 text-secondary" /> Daily Goals
        </h2>

        <div className="grid sm:grid-cols-3 gap-4">
          {[
            { label: "Steps", current: 7200, target: 10000 },
            { label: "Water", current: 5, target: 8 },
            { label: "Protein", current: 95, target: 140 },
          ].map((g) => (
            <div key={g.label} className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-foreground font-medium">
                  {g.label}
                </span>
                <span className="text-muted-foreground">
                  {g.current}/{g.target}
                </span>
              </div>

              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <motion.div
                  className="xp-bar h-full"
                  initial={{ width: 0 }}
                  animate={{
                    width: `${
                      (g.current / g.target) * 100
                    }%`,
                  }}
                  transition={{
                    duration: 1,
                    delay: 0.3,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;