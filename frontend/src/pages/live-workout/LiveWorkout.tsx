import { useEffect, useState } from "react";
import { useFitnessStore } from "@/store/useFitnessStore";

export default function LiveWorkout() {
  const {
    addGoodRep,
    addBadRep,
    completeWorkout,
    totalXP,
    level,
  } = useFitnessStore();

  const [currentTime, setCurrentTime] = useState(0);
  const [totalReps, setTotalReps] = useState(0);
  const [grade, setGrade] = useState("Good Rep");

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime((prev) => prev + 1);

      // Simulate rep every 3 seconds
      if (currentTime % 3 === 0 && currentTime !== 0) {
        const isGood = Math.random() > 0.3;

        if (isGood) {
          addGoodRep();
          setGrade("Good Rep");
        } else {
          addBadRep();
          setGrade("Bad Rep");
        }

        setTotalReps((prev) => prev + 1);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [currentTime]);

  const handleEndWorkout = () => {
    completeWorkout();
    alert("Workout Completed! XP Added 🎉");
  };

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-3xl font-bold">Live Workout</h1>

      <div className="bg-white/30 backdrop-blur-xl rounded-2xl p-6 shadow-lg space-y-4">
        <p>Total Reps: {totalReps}</p>
        <p>Time: {currentTime}s</p>
        <p>
          Rep Quality:
          <span
            className={`ml-2 font-bold ${
              grade === "Good Rep" ? "text-green-500" : "text-red-500"
            }`}
          >
            {grade}
          </span>
        </p>

        <p>Total XP: {totalXP}</p>
        <p>Level: {level}</p>

        <button
          onClick={handleEndWorkout}
          className="mt-4 bg-purple-500 text-white px-4 py-2 rounded-xl"
        >
          End Workout
        </button>
      </div>
    </div>
  );
}