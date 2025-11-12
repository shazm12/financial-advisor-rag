"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Bot } from "lucide-react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { toast } from "sonner";

export default function ChatInterface({ fileName }: { fileName: string }) {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const userQuestion = input;
    setInput("");
    setIsLoading(true);
    setOutput("");

    try {
      const sessionId = localStorage.getItem("sessionId");
      if (!sessionId) {
        toast.error("No Session Id found, Try reconnecting to server", {
          position: "bottom-right",
          duration: 4000,
        });
        return;
      }
      if (!userQuestion.trim()) {
        toast.error("Please provide a prompt", {
          position: "bottom-right",
          duration: 4000,
        });
        return;
      }

      const response = await fetch("/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ session_id: sessionId, prompt: userQuestion }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while(reader) {
        const {done, value} = await reader.read();
        if(done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.startsWith('data: '));
        lines.forEach(line => {
          const content = line.substring(6);
          setOutput(prev => prev + content);
        });
      }

    } catch (error) {
      toast.error("An error occurred. Please try again.", {
        position: "bottom-right",
        duration: 4000,
      });
      setOutput("Error Occurred!");
    } finally {
      setIsLoading(false);
    }
  };

  // if(output) {
  //   console.log(output);
  // }


  return (
    <div className="w-full max-h-1/4 max-w-2xl mx-auto p-6">
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
      {(output || isLoading) && (
        <div className="mt-4 p-4 bg-slate-50 rounded-lg border max-h-[50vh] overflow-y-auto">
          <div className="flex gap-3">
            <div className="flex-1">
              {isLoading ? (
                <div className="space-y-2">
                  <div className="h-4 bg-slate-200 rounded animate-pulse w-3/4"></div>
                  <div className="h-4 bg-slate-200 rounded animate-pulse w-1/2"></div>
                  <div className="h-4 bg-slate-200 rounded animate-pulse w-5/6"></div>
                </div>
              ) : (
                <div>
                  <Markdown 
                    remarkPlugins={[remarkGfm, remarkBreaks]}
                  >
                    {output}
                  </Markdown>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
