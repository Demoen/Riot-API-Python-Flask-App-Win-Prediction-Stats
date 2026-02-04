const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function analyzeStats(
    riotId: string,
    region: string,
    onProgress?: (progress: { message: string, percent: number }) => void
) {

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
            
            if (value) {
                buffer += decoder.decode(value, { stream: !done });
            }
            
            // Process complete lines (newline-delimited JSON)
            let newlineIndex;
            while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
                const line = buffer.slice(0, newlineIndex).trim();
                buffer = buffer.slice(newlineIndex + 1);
                
                if (!line) continue;

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
                    // JSON parse error - ignore partial chunks
                    // If parse fails, the line might be incomplete - it will be handled
                    // when more data arrives, but since we only process on newlines,
                    // this shouldn't happen for complete lines
                }
            }
            
            if (done) break;
        }
        
        // Handle any remaining buffer content after stream ends
        if (buffer.trim()) {
            try {
                const event = JSON.parse(buffer.trim());
                if (event.type === "result") {
                    return event.data;
                } else if (event.type === "error") {
                    throw new Error(event.message);
                }
            } catch (e) {
                // Ignore parse errors on final buffer
            }
        }
        
        // If we reach here without returning, the stream ended without a result
        throw new Error("Stream ended without receiving analysis result");

    } catch (error: unknown) {
        console.error("Analysis error:", error);
        throw error;
    }
}
