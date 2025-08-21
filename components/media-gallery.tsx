import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Play, ImageIcon, ExternalLink } from "lucide-react"
import Image from "next/image"

export default function MediaGallery() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Media & Demos</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="video" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="video">Video Demo</TabsTrigger>
            <TabsTrigger value="screenshots">Screenshots</TabsTrigger>
            <TabsTrigger value="interactive">Interactive</TabsTrigger>
          </TabsList>

          <TabsContent value="video" className="mt-4">
            <div className="space-y-4">
              <div className="aspect-video bg-muted rounded-lg overflow-hidden">
                <iframe
                  src="https://platform.twitter.com/embed/Tweet.html?id=1938794758258008151"
                  className="w-full h-full border-0"
                  title="EduVisAgent Demo Video"
                  allowFullScreen
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">EduVisAgent Demo</h3>
                  <p className="text-sm text-muted-foreground">
                    See our multi-agent system generate step-by-step educational visualizations
                  </p>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <a href="https://x.com/i/status/1938794758258008151" target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    View on X
                  </a>
                </Button>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="screenshots" className="mt-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Image
                  src="https://sjc.microlink.io/tZo8r4vN24lzvURmjTn6dajXgPiP4sIL7dlFGJkAl8lpocaawvBjpgyng5frkUvgRLxWK0YYYheffQBZpN413Q.jpeg"
                  alt="EduVisAgent Interface Screenshot"
                  width={400}
                  height={300}
                  className="w-full rounded-lg border"
                />
                <p className="text-sm text-muted-foreground">EduVisAgent generating educational content</p>
              </div>
              <div className="space-y-2">
                <div className="w-full h-[300px] bg-muted rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <ImageIcon className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">More screenshots coming soon</p>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">Benchmark evaluation results</p>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="interactive" className="mt-4">
            <div className="text-center py-8">
              <Play className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="font-semibold mb-2">Try EduVisAgent</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Experience our multi-agent system for educational visualization generation
              </p>
              <Button asChild>
                <a href="/v0-playground">
                  <Play className="mr-2 h-4 w-4" />
                  Launch Playground
                </a>
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
