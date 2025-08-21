"use client"

import type React from "react"

import { useEffect, useRef, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Upload, ExternalLink, FileText, Download } from "lucide-react"

type Props = {
  defaultUrl?: string
}

export default function PDFSection({ defaultUrl = "https://arxiv.org/pdf/2505.16832" }: Props) {
  const [url, setUrl] = useState<string>(defaultUrl)
  const [blobUrl, setBlobUrl] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    setUrl(defaultUrl)
  }, [defaultUrl])

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsLoading(true)
    const objectUrl = URL.createObjectURL(file)
    setBlobUrl(objectUrl)
    setIsLoading(false)
  }

  const openInNewTab = () => {
    const pdfUrl = blobUrl || url
    if (pdfUrl) {
      window.open(pdfUrl, "_blank")
    }
  }

  const downloadPdf = () => {
    const pdfUrl = blobUrl || url
    if (pdfUrl) {
      const a = document.createElement("a")
      a.href = pdfUrl
      a.download = "paper.pdf"
      a.click()
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl sm:text-4xl font-semibold text-gray-900">Research Paper</h2>
        <p className="mt-4 text-lg text-gray-600">Read the full paper or upload your own PDF</p>
      </div>

      <Card className="border-0 shadow-lg bg-white overflow-hidden">
        <CardContent className="p-0">
          {/* Controls */}
          <div className="p-6 bg-gray-50 border-b border-gray-200">
            <div className="flex flex-col lg:flex-row lg:items-center gap-4">
              <div className="flex-1">
                <label htmlFor="pdf-url" className="block text-sm font-medium text-gray-700 mb-2">
                  Paper URL (PDF)
                </label>
                <Input
                  id="pdf-url"
                  placeholder="https://arxiv.org/pdf/2505.16832"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="h-11 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              <div className="flex gap-3 lg:mt-6">
                <Button
                  onClick={() => fileRef.current?.click()}
                  variant="outline"
                  className="border-gray-300 hover:bg-gray-50 bg-white"
                  disabled={isLoading}
                >
                  <Upload className="mr-2 h-4 w-4" />
                  Upload PDF
                </Button>

                <Button onClick={openInNewTab} className="bg-blue-600 hover:bg-blue-700 text-white shadow-sm">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Open PDF
                </Button>

                <Button onClick={downloadPdf} variant="outline" className="border-gray-300 hover:bg-gray-50 bg-white">
                  <Download className="mr-2 h-4 w-4" />
                  Download
                </Button>
              </div>
            </div>

            <input ref={fileRef} type="file" accept="application/pdf" className="hidden" onChange={handleFileUpload} />

            {blobUrl && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center text-sm text-blue-700">
                  <FileText className="mr-2 h-4 w-4" />
                  <span>Custom PDF uploaded successfully</span>
                </div>
              </div>
            )}
          </div>

          {/* PDF Viewer */}
          <div className="relative">
            {blobUrl || url ? (
              <div className="bg-gray-100">
                <object
                  data={blobUrl || url}
                  type="application/pdf"
                  className="w-full h-[80vh] min-h-[600px]"
                  aria-label="PDF Viewer"
                >
                  <div className="flex flex-col items-center justify-center h-[80vh] min-h-[600px] bg-gray-50">
                    <FileText className="h-16 w-16 text-gray-400 mb-4" />
                    <p className="text-gray-600 text-lg font-medium mb-2">PDF Preview Not Available</p>
                    <p className="text-gray-500 text-sm mb-6 text-center max-w-md">
                      Your browser doesn't support PDF preview. Click the button below to open the PDF in a new tab.
                    </p>
                    <Button onClick={openInNewTab} className="bg-blue-600 hover:bg-blue-700 text-white">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Open PDF in New Tab
                    </Button>
                  </div>
                </object>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-[400px] bg-gray-50">
                <FileText className="h-16 w-16 text-gray-400 mb-4" />
                <p className="text-gray-600 text-lg font-medium mb-2">No PDF Selected</p>
                <p className="text-gray-500 text-sm text-center max-w-md">
                  Enter a PDF URL above or upload a file to preview your paper here.
                </p>
              </div>
            )}
          </div>

          {/* Paper Info Footer */}
          <div className="p-6 bg-gray-50 border-t border-gray-200">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="font-semibold text-gray-900">From EduVisBench to EduVisAgent</h3>
                <p className="text-sm text-gray-600 mt-1">
                  A Benchmark and Multi-Agent Framework for Reasoning-Driven Pedagogical Visualization
                </p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline" size="sm" asChild className="border-gray-300 hover:bg-gray-50 bg-white">
                  <a href="https://arxiv.org/abs/2505.16832" target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    arXiv Page
                  </a>
                </Button>
                <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white">
                  <a href="/cite">
                    <FileText className="mr-2 h-4 w-4" />
                    Cite Paper
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
