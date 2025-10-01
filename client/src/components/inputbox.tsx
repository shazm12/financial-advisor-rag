"use client";

import { useState } from "react";
import { Send } from "lucide-react";

export default function InputBox() {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Submitted:", value);
    setValue("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full mt-10 max-w-3xl mx-auto px-4"
    >
      <div className="relative rounded-2xl bg-white shadow-lg ring-1 ring-gray-200 focus-within:ring-blue-500 transition-shadow">
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Ask anything..."
          className="w-full px-5 py-4 pr-12 text-gray-800 placeholder-gray-400 bg-transparent rounded-2xl outline-none"
        />
        <button
          type="submit"
          aria-label="Send"
          className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
          disabled={!value.trim()}
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </form>
  );
}