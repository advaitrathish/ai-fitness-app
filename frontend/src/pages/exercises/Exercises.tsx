const exercises = [
  { name: "Squats", desc: "Lower body strength exercise.", difficulty: "Medium" },
  { name: "Pushups", desc: "Upper body bodyweight exercise.", difficulty: "Medium" },
  { name: "Bicep Curls", desc: "Targets biceps muscles.", difficulty: "Easy" },
  { name: "Tricep Dips", desc: "Builds triceps and shoulders.", difficulty: "Medium" },
  { name: "Lateral Raises", desc: "Shoulder isolation movement.", difficulty: "Easy" },
  { name: "Lunges", desc: "Leg balance and strength exercise.", difficulty: "Medium" },
  { name: "Pullups", desc: "Upper body pulling movement.", difficulty: "Hard" },
  { name: "Planks", desc: "Core stability exercise.", difficulty: "Medium" },
  { name: "Crunches", desc: "Abdominal muscle workout.", difficulty: "Easy" }
];

export default function Exercises() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Exercises</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {exercises.map((ex, index) => (
          <div
            key={index}
            className="bg-white/30 backdrop-blur-xl rounded-2xl p-6 shadow-lg hover:scale-105 transition"
          >
            <h2 className="text-xl font-semibold">{ex.name}</h2>
            <p className="text-sm text-gray-600 my-2">{ex.desc}</p>

            <span
              className={`text-xs px-3 py-1 rounded-full ${
                ex.difficulty === "Easy"
                  ? "bg-green-200 text-green-700"
                  : ex.difficulty === "Medium"
                  ? "bg-yellow-200 text-yellow-700"
                  : "bg-red-200 text-red-700"
              }`}
            >
              {ex.difficulty}
            </span>

            <img
              src="https://media.giphy.com/media/3o7btPCcdNniyf0ArS/giphy.gif"
              alt="exercise"
              className="mt-4 rounded-lg"
            />
          </div>
        ))}
      </div>
    </div>
  );
}