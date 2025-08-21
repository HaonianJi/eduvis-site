"use client"

import { useRef, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RefreshCw, Maximize2 } from "lucide-react"

interface Props {
  code: string
  title?: string
}

export default function V0CodeRenderer({ code, title = "Generated Visualization" }: Props) {
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const [isFullscreen, setIsFullscreen] = useState(false)

  const refreshPreview = () => {
    if (iframeRef.current) {
      iframeRef.current.src = iframeRef.current.src
    }
  }

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  // Create a safe HTML document from the code
  const createSafeHTML = (rawCode: string) => {
    // If it's already a complete HTML document, use it as-is
    if (rawCode.includes("<!DOCTYPE html>") || rawCode.includes("<html")) {
      return rawCode
    }

    // If it's React/JSX code, wrap it in a basic HTML template
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; }
        .error { color: red; padding: 20px; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        try {
            ${rawCode}
        } catch (error) {
            document.getElementById('root').innerHTML = 
                '<div class="error">Error rendering component: ' + error.message + '</div>';
        }
    </script>
</body>
</html>`
  }

  const safeHTML = createSafeHTML(code)

  return (
    <Card className={isFullscreen ? "fixed inset-0 z-50 rounded-none" : ""}>
      <CardContent className="p-0">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold">{title}</h3>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={refreshPreview}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="outline" onClick={toggleFullscreen}>
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className={`bg-white ${isFullscreen ? "h-[calc(100vh-80px)]" : "h-[500px]"}`}>
          <iframe
            ref={iframeRef}
            srcDoc={safeHTML}
            className="w-full h-full border-0"
            title={title}
            sandbox="allow-scripts allow-same-origin allow-forms"
          />
        </div>
      </CardContent>
    </Card>
  )
}
