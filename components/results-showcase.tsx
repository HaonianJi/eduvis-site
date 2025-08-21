import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, Target, Zap, Users } from "lucide-react"

export default function ResultsShowcase() {
  const results = [
    {
      icon: <TrendingUp className="h-5 w-5" />,
      title: "Performance Improvement",
      value: "40.2%",
      description: "EduVisAgent outperforms best baseline (v0) by 40.2% relative improvement",
      color: "text-green-600",
    },
    {
      icon: <Target className="h-5 w-5" />,
      title: "Overall Score",
      value: "81.6%",
      description: "Average score across all evaluation dimensions and subjects",
      color: "text-blue-600",
    },
    {
      icon: <Zap className="h-5 w-5" />,
      title: "Benchmark Coverage",
      value: "1,154",
      description: "Questions across 15 domains in Math, Physics, and Chemistry",
      color: "text-purple-600",
    },
    {
      icon: <Users className="h-5 w-5" />,
      title: "Multi-Agent System",
      value: "5",
      description: "Specialized agents for planning, mapping, reasoning, review, and visualization",
      color: "text-orange-600",
    },
  ]

  const comparisonData = [
    { model: "EduVisAgent (Ours)", score: 81.6, isOurs: true },
    { model: "v0 (Best Baseline)", score: 58.2, isOurs: false },
    { model: "Claude 3.7 Sonnet", score: 54.6, isOurs: false },
    { model: "Gemini 2.0 Flash", score: 43.6, isOurs: false },
    { model: "GPT-4o", score: 38.1, isOurs: false },
    { model: "Mistral-Small-3.1", score: 30.2, isOurs: false },
  ]

  return (
    <div className="space-y-6">
      {/* Key Results Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {results.map((result, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className={`${result.color}`}>{result.icon}</div>
                <div className="flex-1">
                  <div className={`text-2xl font-bold ${result.color}`}>{result.value}</div>
                  <div className="text-sm font-medium">{result.title}</div>
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-2">{result.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Performance Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Model Performance Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {comparisonData.map((item, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-32 text-sm font-medium truncate">{item.model}</div>
                <div className="flex-1 bg-muted rounded-full h-2 relative">
                  <div
                    className={`h-2 rounded-full ${item.isOurs ? "bg-green-500" : "bg-blue-400"}`}
                    style={{ width: `${(item.score / 100) * 100}%` }}
                  />
                </div>
                <div className="w-12 text-sm font-semibold text-right">{item.score}%</div>
                {item.isOurs && (
                  <Badge variant="default" className="ml-2">
                    Ours
                  </Badge>
                )}
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-4">
            Scores represent average performance across all evaluation dimensions (Context Visualization, Diagram
            Design, Text-Graphic Integration, Thought Guidance, and Interactivity).
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
