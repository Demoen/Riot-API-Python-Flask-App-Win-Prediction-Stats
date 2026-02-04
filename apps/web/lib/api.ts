const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function analyzeStats(
    riotId: string,
    region: string,
    onProgress?: (progress: { message: string, percent: number }) => void
) {
    console.log("Analyzing with API_URL:", API_URL);

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ riot_id: riotId, region }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Failed to analyze stats");
        }

        if (!response.body) throw new Error("No response body");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");

            // Process all complete lines
            buffer = lines.pop() || ""; // Keep the last incomplete line in buffer

            for (const line of lines) {
                if (!line.trim()) continue;

                try {
                    const event = JSON.parse(line);

                    if (event.type === "progress" && onProgress) {
                        onProgress({ message: event.message, percent: event.percent });
                    } else if (event.type === "result") {
                        return event.data;
                    } else if (event.type === "error") {
                        throw new Error(event.message);
                    }
                } catch (e) {
                    console.error("Error parsing stream line:", line, e);
                }
            }
        }

    } catch (error: any) {
        console.error("Analysis error:", error);
        throw error;
    }
}
