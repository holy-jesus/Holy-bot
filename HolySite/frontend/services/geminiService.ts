import { GoogleGenAI, SchemaType, Type } from "@google/genai";

let ai: GoogleGenAI | null = null;

try {
  // Assuming process.env.API_KEY is available as per instructions
  if (process.env.API_KEY) {
    ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  }
} catch (error) {
  console.warn("Gemini API Key missing or invalid initialization", error);
}

export const generateBotResponse = async (userMessage: string): Promise<string> => {
  if (!ai) {
    return "I'm currently disconnected from my AI brain (API Key missing). I can still help you with dashboard tasks though!";
  }

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: userMessage,
      config: {
        systemInstruction: "You are Holy-bot, a helpful, witty, and slightly divine Twitch bot assistant. You help streamers manage their dashboard. Keep responses concise and gamer-friendly.",
      }
    });
    return response.text || "I received your message but couldn't think of a response.";
  } catch (error) {
    console.error("Error generating bot response:", error);
    return "My connection to the celestial network is interrupted. Please try again later.";
  }
};

export const generateCommandConfig = async (description: string): Promise<any> => {
  if (!ai) {
    return null;
  }

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: `Create a Twitch bot command configuration based on this description: "${description}".
      
      If the description implies a simple static text response (e.g. "link to discord"), use mode "basic".
      If the description implies a dynamic personality, roleplay, or complex variable text generation (e.g. "roast the user", "tell a joke"), use mode "ai".
      
      Return JSON only.`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            name: { type: Type.STRING, description: "Short descriptive name for the command" },
            trigger: { type: Type.STRING, description: "Trigger keyword starting with !" },
            mode: { type: Type.STRING, enum: ["basic", "ai"] },
            response: { type: Type.STRING, description: "The static response text (if basic mode)" },
            aiPrompt: { type: Type.STRING, description: "The system instruction for the AI (if ai mode)" },
            cooldown: { type: Type.INTEGER, description: "Recommended cooldown in seconds" }
          },
          required: ["name", "trigger", "mode", "cooldown"]
        }
      }
    });

    if (response.text) {
        return JSON.parse(response.text);
    }
    return null;

  } catch (error) {
    console.error("Error generating command config:", error);
    return null;
  }
}