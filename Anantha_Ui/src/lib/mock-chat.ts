import { ALL_VERSES, type Verse } from "./verses";

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  citations?: Verse[];
  createdAt: number;
};

const REPLIES = [
  "The Gita reminds us that peace is found not in changing the world, but in steadying the mind. Act with devotion, release the fruits, and let stillness become your foundation.",
  "Krishna teaches Arjuna that the self is eternal — untouched by sorrow, fire, or time. When you remember this, fear softens and clarity returns.",
  "Equanimity in success and failure is the heart of yoga. Begin small: notice when you grasp at outcomes, and gently return to the present action.",
  "Desire becomes suffering only when we mistake it for the self. Witness it arise, witness it pass — and the mind grows quiet on its own.",
  "Devotion is not separate from duty. Offer your work as worship, and even ordinary moments become sacred ground.",
];

function pickCitations(seedTokens: string[]): Verse[] {
  const scored = ALL_VERSES.map((v) => {
    const text = (v.translation + " " + v.sanskrit).toLowerCase();
    const score = seedTokens.reduce((acc, t) => (text.includes(t) ? acc + 1 : acc), 0);
    return { v, score };
  });
  scored.sort((a, b) => b.score - a.score);
  const top = scored.slice(0, 3).filter((s) => s.score > 0).map((s) => s.v);
  if (top.length >= 2) return top;
  const pool = [...ALL_VERSES];
  const out: Verse[] = [];
  for (let i = 0; i < 3 && pool.length; i++) {
    out.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
  }
  return out;
}

export async function generateMockReply(
  userText: string,
): Promise<{ content: string; citations: Verse[] }> {
  await new Promise((r) => setTimeout(r, 900 + Math.random() * 800));
  const tokens = userText.toLowerCase().split(/\W+/).filter((w) => w.length > 3);
  const citations = pickCitations(tokens);
  const content = REPLIES[Math.floor(Math.random() * REPLIES.length)];
  return { content, citations };
}

export function makeId() {
  return Math.random().toString(36).slice(2, 10);
}