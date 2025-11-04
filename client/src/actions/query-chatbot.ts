"use server";

export async function queryChatbot(sessionId: string, query: string) {
  try {
    if (!query) {
      return {
        success: false,
        error: "No query provided",
      };
    }

    const body = {
      session_id: sessionId,
      prompt: query,
    };

    const response = await fetch(`${process.env.API_URL}/api/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json", // ✅ Must be present
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      return {
        success: false,
        error: error.detail || "Query Request Failed",
      };
    }

    const result = await response.json();

    return {
      success: true,
      status: result.status,
      description: result.description,
      sessionId: result.session_id,
      answer: result.response,
    };
  } catch (error) {
    console.error("Upload error:", error);
    return {
      success: false,
      error: "Failed to upload file to server",
    };
  }
}
