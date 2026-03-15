function GeneratePodcastAudio(script: string, persona: string) -> string {
  client GeminiTTS
  prompt #"
    {{ persona }}:

    {{ script }}
  "#
}