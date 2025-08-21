# EduVis Site

An educational visualization platform with integrated v0 AI project generation.

## Features

- 🎓 Interactive educational content
- 🤖 AI-powered project generation using v0 API
- 📊 Dynamic visualizations and simulations
- 🎨 Modern UI with shadcn/ui components

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set environment variables:**
   Create `.env.local` with:
   ```
   V0_API_KEY=your_v0_api_key_here
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

## Deployment

### Vercel Deployment

1. Connect your GitHub repository to Vercel
2. Set the `V0_API_KEY` environment variable in Vercel project settings
3. Deploy

The project is configured for Vercel with:
- Next.js 15.2.4 App Router
- API routes with 30s timeout for v0 generation
- Optimized for serverless functions

## Architecture

- **Frontend:** Next.js with React 19, Tailwind CSS, shadcn/ui
- **API:** Next.js API routes for v0 integration
- **Deployment:** Vercel serverless functions

## Environment Variables

- `V0_API_KEY` - Required for v0 API access
