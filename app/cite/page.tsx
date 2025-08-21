"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import SiteHeader from "@/components/site-header"
import Footer from "@/components/footer"
import { Copy } from "lucide-react"

export default function CitePage() {
  const bib = `@article{ji2025eduvisagent,
  title={From EduVisBench to EduVisAgent: A Benchmark and Multi-Agent Framework for Reasoning-Driven Pedagogical Visualization},
  author={Ji, Haonian and Qiu, Shi and Xin, Siyang and Han, Siwei and Chen, Zhaorun and Zhang, Dake and Wang, Hongyi and Yao, Huaxiu},
  journal={arXiv preprint arXiv:2505.16832},
  year={2025}
}`

  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      <main className="flex-1 mx-auto max-w-5xl w-full px-4 sm:px-6 lg:px-8 py-10">
        <Card>
          <CardContent className="p-6">
            <h1 className="text-2xl font-semibold">Cite</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Please use the following BibTeX entry to cite this work.
            </p>
            <pre className="mt-6 rounded-md border bg-muted/30 p-4 text-xs whitespace-pre-wrap">{bib}</pre>
            <div className="mt-3">
              <Button
                onClick={async () => {
                  await navigator.clipboard.writeText(bib)
                  alert("Copied!")
                }}
              >
                <Copy className="mr-2 h-4 w-4" />
                Copy BibTeX
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
      <Footer />
    </div>
  )
}
