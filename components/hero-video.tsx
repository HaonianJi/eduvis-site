"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Play, Pause, ExternalLink } from "lucide-react"

export default function HeroVideo() {
  const [isPlaying, setIsPlaying] = useState(false)

  return (
    <div className="relative">
      <Card className="overflow-hidden">
        <CardContent className="p-0">
          <div className="relative aspect-video bg-gradient-to-br from-blue-50 to-purple-50">
            {/* Video embed */}
            <iframe
              src="https://platform.twitter.com/embed/Tweet.html?id=1938794758258008151"
              className="w-full h-full border-0"
              title="EduVisAgent Demo Video"
              allowFullScreen
            />

            {/* Overlay controls */}
            <div className="absolute inset-0 bg-black/20 opacity-0 hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="bg-white/90 hover:bg-white"
                >
                  {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                </Button>
                <Button size="sm" variant="secondary" asChild className="bg-white/90 hover:bg-white">
                  <a href="https://x.com/i/status/1938794758258008151" target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="mt-4 text-center">
        <h3 className="font-semibold">EduVisAgent Demo Video</h3>
        <p className="text-sm text-muted-foreground">
          Watch our multi-agent system generate interactive educational visualizations in real-time
        </p>
      </div>
    </div>
  )
}
