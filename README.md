# Labil

AI-powered diagram generation tool. Create flowcharts, process diagrams, and swimlanes with natural language.

## Stack

- **Framework**: Next.js 14 (App Router)
- **UI**: React Flow, Tailwind CSS, Framer Motion
- **AI**: OpenAI / Anthropic
- **Database**: Supabase (coming soon)
- **Hosting**: Vercel

## Getting Started

```bash
# Install dependencies
npm install

# Copy env file and add your keys
cp .env.example .env.local

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Features

- 🎨 Visual diagram editor with drag & drop
- 🤖 AI agent that generates diagrams from text
- 📐 Multiple shapes: rectangles, diamonds, circles, hexagons, chevrons
- 🏊 Swimlanes for process flows
- ↩️ Undo/Redo with full history
- 💾 Export/Import projects as JSON
- ⌨️ Keyboard shortcuts

## Environment Variables

```env
OPENAI_API_KEY=         # Required for AI features
ANTHROPIC_API_KEY=      # Optional, for Claude
```

## License

MIT
