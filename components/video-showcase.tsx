import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Play, ExternalLink } from "lucide-react"

export default function VideoShowcase() {
  const videoUrl = "https://x.com/i/status/1938794758258008151"

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Play className="h-5 w-5" />
          Video Demo
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="aspect-video bg-muted rounded-lg overflow-hidden">
          {/* Twitter/X embed */}
          <iframe
            src={`https://platform.twitter.com/embed/Tweet.html?id=1938794758258008151`}
            className="w-full h-full border-0"
            title="EduVisAgent Demo Video"
            allowFullScreen
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold">EduVisAgent in Action</h3>
            <p className="text-sm text-muted-foreground">
              Watch how our multi-agent system generates interactive educational visualizations
            </p>
          </div>
          <Button variant="outline" size="sm" asChild>
            <a href={videoUrl} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="mr-2 h-4 w-4" />
              View on X
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
