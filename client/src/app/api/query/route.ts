export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const { session_id, prompt } = await req.json();
  const response = await fetch(`${process.env.API_URL}/api/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ session_id, prompt }),
  });

  return new Response(response.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-store, must-revalidate",
      Connection: "keep-alive",
    },
  });
}
