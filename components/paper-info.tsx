"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ExternalLink, Calendar, Users, BookOpen } from "lucide-react"
import { useState } from "react"

export default function PaperInfo() {
  const [showFullAbstract, setShowFullAbstract] = useState(false)
  const paperData = {
    title:
      "From EduVisBench to EduVisAgent: A Benchmark and Multi-Agent Framework for Reasoning-Driven Pedagogical Visualization",
    authors: [
      { name: "Haonian Ji", affiliation: "UNC-Chapel Hill", isEqual: true },
      { name: "Shi Qiu", affiliation: "UNC-Chapel Hill", isEqual: true },
      { name: "Siyang Xin", affiliation: "UNC-Chapel Hill", isEqual: true },
      { name: "Siwei Han", affiliation: "UNC-Chapel Hill", isEqual: true },
      { name: "Zhaorun Chen", affiliation: "University of Chicago" },
      { name: "Dake Zhang", affiliation: "Rutgers University" },
      { name: "Hongyi Wang", affiliation: "Rutgers University" },
      { name: "Huaxiu Yao", affiliation: "UNC-Chapel Hill" },
    ],
    arxivId: "2505.16832",
    version: "v2",
    submittedDate: "27 May 2025",
    subjects: ["Artificial Intelligence", "Human-Computer Interaction", "Computers and Society"],
    abstract: `While foundation models (FMs), such as diffusion models and large vision-language models (LVLMs), have been widely applied in educational contexts, their ability to generate pedagogically effective visual explanations remains limited. Most existing approaches focus primarily on textual reasoning, overlooking the critical role of structured and interpretable visualizations in supporting conceptual understanding. To better assess the visual reasoning capabilities of FMs in educational settings, we introduce EduVisBench, a multi-domain, multi-level benchmark. EduVisBench features diverse STEM problem sets requiring visually grounded solutions, along with a fine-grained evaluation rubric informed by pedagogical theory. Our empirical analysis reveals that existing models frequently struggle with the inherent challenge of decomposing complex reasoning and translating it into visual representations aligned with human cognitive processes. To address these limitations, we propose EduVisAgent, a multi-agent collaborative framework that coordinates specialized agents for instructional planning, reasoning decomposition, metacognitive prompting, and visualization design. Experimental results show that EduVisAgent substantially outperforms all baselines, achieving a 40.2% improvement and delivering more educationally aligned visualizations.`,
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Paper Title */}
          <div>
            <h2 className="text-xl font-semibold leading-tight">{paperData.title}</h2>
            <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>Submitted {paperData.submittedDate}</span>
              <Badge variant="outline">{paperData.version}</Badge>
              <Badge variant="secondary">arXiv:{paperData.arxivId}</Badge>
            </div>
          </div>

          {/* Authors */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Users className="h-4 w-4" />
              <span className="text-sm font-medium">Authors</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {paperData.authors.map((author, index) => (
                <div key={index} className="text-sm">
                  <span className="font-medium">
                    {author.name}
                    {author.isEqual && <sup className="text-xs">*</sup>}
                  </span>
                  <span className="text-muted-foreground ml-1">({author.affiliation})</span>
                  {index < paperData.authors.length - 1 && <span className="mr-2">,</span>}
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-1">* Equal contribution</p>
          </div>

          {/* Subjects */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="h-4 w-4" />
              <span className="text-sm font-medium">Subjects</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {paperData.subjects.map((subject, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {subject}
                </Badge>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2 pt-2">
            <Button size="sm" asChild>
              <a href="https://arxiv.org/pdf/2505.16832" target="_blank" rel="noopener noreferrer">
                <ExternalLink className="mr-2 h-4 w-4" />
                View PDF
              </a>
            </Button>
            <Button size="sm" variant="outline" asChild>
              <a href="https://arxiv.org/abs/2505.16832" target="_blank" rel="noopener noreferrer">
                <ExternalLink className="mr-2 h-4 w-4" />
                arXiv Page
              </a>
            </Button>
            <Button size="sm" variant="outline" asChild>
              <a href="https://github.com/aiming-lab/EduVisBench" target="_blank" rel="noopener noreferrer">
                <ExternalLink className="mr-2 h-4 w-4" />
                Benchmark
              </a>
            </Button>
            <Button size="sm" variant="outline" asChild>
              <a href="https://github.com/aiming-lab/EduVisAgent" target="_blank" rel="noopener noreferrer">
                <ExternalLink className="mr-2 h-4 w-4" />
                Agent Code
              </a>
            </Button>
          </div>

          {/* Abstract */}
          <div className="border-t pt-4">
            <h3 className="text-sm font-medium mb-2">Abstract</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {showFullAbstract ? paperData.abstract : `${paperData.abstract.substring(0, 300)}...`}
            </p>
            <Button 
              variant="link" 
              size="sm" 
              className="p-0 h-auto mt-1"
              onClick={() => setShowFullAbstract(!showFullAbstract)}
            >
              {showFullAbstract ? 'Show less' : 'Read full abstract'}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
