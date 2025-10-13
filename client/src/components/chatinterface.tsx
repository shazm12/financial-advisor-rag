"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Bot } from "lucide-react";

export default function ChatInterface({ fileName }: { fileName: string }) {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userQuestion = input;
    setInput("");
    setIsLoading(true);
    setResponse("");

    try {
      // Replace with your actual API call
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userQuestion, fileName })
      });

      const data = await res.json();
      setResponse(data.answer);
    } catch (error) {
      setResponse("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-2">Analyzing: {fileName}</h2>
      </div>
      {/* Input Form */}
      <form onSubmit={handleSubmit}>
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your file..."
            className="flex-1"
            disabled={isLoading}
          />
          <Button type="submit" size="icon" disabled={isLoading}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </form>
      {/* Response Display Area */}
      {(response || isLoading) && (
        <div className="mt-4 p-4 bg-slate-50 rounded-lg border min-h-[120px]">
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              {isLoading ? (
                <div className="space-y-2">
                  <div className="h-4 bg-slate-200 rounded animate-pulse w-3/4"></div>
                  <div className="h-4 bg-slate-200 rounded animate-pulse w-1/2"></div>
                  <div className="h-4 bg-slate-200 rounded animate-pulse w-5/6"></div>
                </div>
              ) : (
                <p className="text-slate-900">{response}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
