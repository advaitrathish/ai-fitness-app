import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Tooltip,
  CartesianGrid,
  XAxis,
  YAxis
} from "recharts";

const data = [
  { name: "Mon", workouts: 2 },
  { name: "Tue", workouts: 3 },
  { name: "Wed", workouts: 1 },
  { name: "Thu", workouts: 4 },
  { name: "Fri", workouts: 2 }
];

const pieData = [
  { name: "Strength", value: 60 },
  { name: "Cardio", value: 40 }
];

export default function Progress() {
  return (
    <div className="p-8 space-y-6">
      <h1 className="text-3xl font-bold">Progress</h1>

      <div className="bg-white/30 backdrop-blur-xl rounded-2xl p-6 shadow-lg">
        <LineChart width={500} height={300} data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="workouts" stroke="#8884d8" />
        </LineChart>
      </div>

      <div className="bg-white/30 backdrop-blur-xl rounded-2xl p-6 shadow-lg">
        <PieChart width={400} height={300}>
          <Pie data={pieData} dataKey="value" outerRadius={100} fill="#82ca9d" />
          <Tooltip />
        </PieChart>
      </div>
    </div>
  );
}