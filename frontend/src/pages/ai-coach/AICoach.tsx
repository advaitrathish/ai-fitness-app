import { useState } from "react";

export default function AICoach() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! Ask me about workouts or diet." }
  ]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input) return;

    setMessages([...messages, { sender: "user", text: input }]);
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Focus on proper form and rest 60s." }
      ]);
    }, 1000);
    setInput("");
  };

  return (
    <div className="p-8 flex flex-col h-[80vh]">
      <h1 className="text-3xl font-bold mb-4">AI Coach</h1>

      <div className="flex-1 overflow-y-auto space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded-xl w-fit ${
              msg.sender === "bot"
                ? "bg-purple-200"
                : "bg-blue-200 ml-auto"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="flex mt-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 p-2 rounded-l-xl border"
        />
        <button
          onClick={sendMessage}
          className="bg-purple-500 text-white px-4 rounded-r-xl"
        >
          Send
        </button>
      </div>
    </div>
  );
}