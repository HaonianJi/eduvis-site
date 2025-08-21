"use client"

import SiteHeader from "@/components/site-header"
import Footer from "@/components/footer"
import V0Generator from "@/components/v0-generator"
import { ErrorBoundary } from "@/components/error-boundary"

export default function V0PlaygroundPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      <main className="flex-1 mx-auto max-w-6xl w-full px-4 sm:px-6 lg:px-8 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">V0 Playground</h1>
          <p className="mt-2 text-muted-foreground">
            Generate interactive educational visualizations using V0 API. Create step-by-step problem solvers,
            interactive diagrams, and pedagogical tools.
          </p>
        </div>
        <ErrorBoundary>
          <V0Generator />
        </ErrorBoundary>
      </main>
      <Footer />
    </div>
  )
}
