"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { ArrowUpRight, FileText, Github, LinkIcon, PlayCircle } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import SiteHeader from "@/components/site-header"
import Footer from "@/components/footer"
import CarnotDemo from "@/components/carnot-demo"
import Stats from "@/components/stats"
import { useEffect, useState } from "react"
import PaperInfo from "@/components/paper-info"
import ResultsShowcase from "@/components/results-showcase"
import MediaGallery from "@/components/media-gallery"

export default function Page() {
  // Allow users to store their Paper URL locally (no envs required)
  const [paperUrl, setPaperUrl] = useState<string>("https://arxiv.org/pdf/2505.16832")
  const [codeUrl, setCodeUrl] = useState<string>("https://github.com/aiming-lab/EduVisBench")
  const [benchUrl, setBenchUrl] = useState<string>("https://github.com/aiming-lab/EduVisAgent")

  useEffect(() => {
    const u = localStorage.getItem("paperUrl") || "https://arxiv.org/pdf/2505.16832"
    const c = localStorage.getItem("codeUrl") || "https://github.com/aiming-lab/EduVisBench"
    const d = localStorage.getItem("benchUrl") || "https://github.com/aiming-lab/EduVisAgent"
    setPaperUrl(u)
    setCodeUrl(c)
    setBenchUrl(d)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function saveLinks() {
    localStorage.setItem("paperUrl", paperUrl)
    localStorage.setItem("codeUrl", codeUrl)
    localStorage.setItem("benchUrl", benchUrl)
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50/30">
      <SiteHeader />

      <main className="flex-1">
        {/* Hero */}
        <section className="relative bg-white">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
            <div className="text-center">
              <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 border border-blue-100 px-4 py-2 text-sm">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span className="font-medium text-blue-700">Latest Research</span>
                <Separator orientation="vertical" className="mx-1 h-4" />
                <span className="text-blue-600">Reasoning-Driven Pedagogical Visualization</span>
              </div>

              <h1 className="mt-8 text-3xl sm:text-5xl md:text-6xl font-semibold tracking-tight text-gray-900">
                From EduVisBench to{" "}
                <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  EduVisAgent
                </span>
              </h1>
              <p className="mt-6 text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                A Benchmark and Multi-Agent Framework for Reasoning-Driven Pedagogical Visualization
              </p>

              {/* Main Hero Image */}
              <div className="mt-12 mb-12">
                <div className="relative rounded-2xl overflow-hidden shadow-2xl bg-white p-4 sm:p-6">
                  <Image
                    src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/%E4%B8%BB%E5%9B%BE-Jwftq9vbwO6ZhF1H0e64VCKZefRMO6.png"
                    alt="EduVisAgent system demonstration across Mathematics, Chemistry, and Physics domains showing interactive educational visualizations with performance scores"
                    width={1200}
                    height={600}
                    className="w-full h-auto rounded-xl"
                    priority
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/5 to-transparent rounded-2xl pointer-events-none" />
                </div>
                <p className="mt-4 text-sm text-gray-500 max-w-4xl mx-auto">
                  EduVisAgent generates interactive educational visualizations across STEM domains, achieving high
                  scores in visual guidance, design, coordination, learning guidance, and interactivity.
                </p>
              </div>

              <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                <Badge variant="secondary" className="bg-gray-100 text-gray-700 hover:bg-gray-200">
                  Haonian Ji*
                </Badge>
                <Badge variant="secondary" className="bg-gray-100 text-gray-700 hover:bg-gray-200">
                  Shi Qiu*
                </Badge>
                <Badge variant="secondary" className="bg-gray-100 text-gray-700 hover:bg-gray-200">
                  Siyang Xin*
                </Badge>
                <Badge variant="secondary" className="bg-gray-100 text-gray-700 hover:bg-gray-200">
                  Siwei Han*
                </Badge>
                <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-200">UNC-Chapel Hill</Badge>
                <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-200">UChicago</Badge>
                <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-200">Rutgers</Badge>
              </div>

              <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
                <Button asChild className="bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/25">
                  <a href={paperUrl || "#"} target={paperUrl ? "_blank" : "_self"} rel="noopener noreferrer">
                    <FileText className="mr-2 h-4 w-4" />
                    Read Paper
                    <ArrowUpRight className="ml-1 h-4 w-4" />
                  </a>
                </Button>
                <Button variant="outline" asChild className="border-gray-300 hover:bg-gray-50 bg-transparent">
                  <a href={codeUrl} target="_blank" rel="noopener noreferrer">
                    <Github className="mr-2 h-4 w-4" />
                    View Code
                    <ArrowUpRight className="ml-1 h-4 w-4" />
                  </a>
                </Button>
                <Button variant="outline" asChild className="border-gray-300 hover:bg-gray-50 bg-transparent">
                  <a href={benchUrl} target="_blank" rel="noopener noreferrer">
                    <LinkIcon className="mr-2 h-4 w-4" />
                    Benchmark
                    <ArrowUpRight className="ml-1 h-4 w-4" />
                  </a>
                </Button>
                <Button variant="secondary" asChild className="bg-gray-100 hover:bg-gray-200 text-gray-700">
                  <Link href="/v0-playground">
                    <PlayCircle className="mr-2 h-4 w-4" />
                    Try Playground
                  </Link>
                </Button>
                <Button variant="secondary" asChild className="bg-gray-100 hover:bg-gray-200 text-gray-700">
                  <a href="#demo">
                    <PlayCircle className="mr-2 h-4 w-4" />
                    Live Demo
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* About section */}
        <section className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-12">
          <div className="space-y-8">
            <PaperInfo />
            <div className="grid gap-8 md:grid-cols-2">
              <Card className="border-0 shadow-sm bg-white">
                <CardContent className="p-8">
                  <h3 className="text-xl font-semibold text-gray-900">What is EduVisBench?</h3>
                  <p className="mt-4 text-gray-600 leading-relaxed">
                    EduVisBench is a multi-domain, multi-level benchmark for evaluating the capacity of foundation
                    models to generate pedagogically effective, step-by-step visual reasoning across STEM scenarios.
                    It emphasizes interpretability, cognitive alignment, and instructional clarity.
                  </p>
                  <Separator className="my-6" />
                  <h3 className="text-xl font-semibold text-gray-900">What is EduVisAgent?</h3>
                  <p className="mt-4 text-gray-600 leading-relaxed">
                    EduVisAgent is a multi-agent framework coordinating specialized agents for instructional
                    planning, reasoning decomposition, metacognitive prompting, and visualization design to produce
                    interactive, learning-aligned visual explanations.
                  </p>
                </CardContent>
              </Card>

              <Stats />
            </div>
          </div>
        </section>

        {/* Results */}
        <section className="py-16 bg-white">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-semibold text-gray-900">Key Results</h2>
              <p className="mt-4 text-lg text-gray-600">
                EduVisAgent significantly outperforms existing baselines across all evaluation metrics
              </p>
            </div>
            <ResultsShowcase />
          </div>
        </section>

        {/* Media Gallery */}
        <section className="py-16">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-semibold text-gray-900">Media & Demonstrations</h2>
              <p className="mt-4 text-lg text-gray-600">Watch EduVisAgent in action and explore interactive examples</p>
            </div>
            <MediaGallery />
          </div>
        </section>

        {/* Demo */}
        <section id="demo" className="py-16 bg-white">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-semibold text-gray-900">Interactive Demo</h2>
              <p className="text-lg text-gray-600">Carnot Efficiency Explorer</p>
            </div>
            <CarnotDemo />
          </div>
        </section>

        {/* Citation teaser */}
        <section className="py-16">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <Card className="border-0 shadow-sm bg-white">
              <CardContent className="p-8 text-center">
                <h3 className="text-xl font-semibold text-gray-900">Cite this work</h3>
                <p className="mt-4 text-gray-600">Use the BibTeX entry. See the Cite page for full details.</p>
                <div className="mt-6 flex flex-wrap justify-center gap-3">
                  <Button asChild className="bg-blue-600 hover:bg-blue-700">
                    <Link href="/cite">View Citation</Link>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={async () => {
                      const bib = getBibtex()
                      await navigator.clipboard.writeText(bib)
                      alert("BibTeX copied.")
                    }}
                    className="border-gray-300 hover:bg-gray-50"
                  >
                    Copy BibTeX
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}

function getBibtex() {
  return `@article{ji2025eduvisagent,
  title={From EduVisBench to EduVisAgent: A Benchmark and Multi-Agent Framework for Reasoning-Driven Pedagogical Visualization},
  author={Ji, Haonian and Qiu, Shi and Xin, Siyang and Han, Siwei and Chen, Zhaorun and Zhang, Dake and Wang, Hongyi and Yao, Huaxiu},
  journal={arXiv preprint arXiv:2505.16832},
  year={2025}
}`
}
