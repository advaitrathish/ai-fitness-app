import { useState } from "react";

export default function MealPlanner() {
  const [goal, setGoal] = useState("bulking");

  const meals =
    goal === "bulking"
      ? ["Chicken Rice Bowl", "Peanut Butter Oats", "Egg & Avocado Toast"]
      : ["Grilled Chicken Salad", "Oats with Fruits", "Boiled Eggs & Veggies"];

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-3xl font-bold">Meal Planner</h1>

      <select
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        className="p-2 rounded-xl border"
      >
        <option value="bulking">Bulking</option>
        <option value="cutting">Cutting</option>
      </select>

      <div className="grid md:grid-cols-3 gap-6">
        {meals.map((meal, i) => (
          <div
            key={i}
            className="bg-white/30 backdrop-blur-xl p-6 rounded-2xl shadow-lg"
          >
            <h2 className="font-semibold">{meal}</h2>
            <p className="text-sm text-gray-600">
              Healthy balanced macro meal.
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}