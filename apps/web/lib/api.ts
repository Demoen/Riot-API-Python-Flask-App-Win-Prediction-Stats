const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function analyzeStats(riotId: string, region: string) {
    console.log("Analyzing with API_URL:", API_URL);
    console.log("Full Request URL:", `${API_URL}/analyze`);

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

    return response.json();
}
