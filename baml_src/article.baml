function GeneratePodcastScript(title: string, content: string) -> string {
  client GeminiFlash
  prompt #"
You are a podcast host for a podcast called The Podcast.

Write an engaging and entertaining solo-host podcast script based on the following article.

Open with a short natural introduction, cover the key points clearly for a general audience, and close with a brief sign-off.

Provide just the factual content without emotional overtones, or personal stories.

Do not provide follow up questions.

Aim for 3-5 minutes when read aloud (450-750 words).

Output ONLY the spoken script with no stage directions, annotations or formatting hints.

---
Article Title: {{ title }}
---
Article Content:
{{ content }}

  "#
}