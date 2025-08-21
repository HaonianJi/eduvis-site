import { Card, CardContent } from "@/components/ui/card"

export default function Stats() {
  const items = [
    { label: "Average Score (EduVisAgent)", value: "81.6%", color: "text-blue-600" },
    { label: "Improvement over Best Baseline", value: "+40.2%", color: "text-green-600" },
    { label: "Domains", value: "15", color: "text-indigo-600" },
    { label: "Questions", value: "1,154", color: "text-purple-600" },
  ]
  return (
    <Card className="border-0 shadow-sm bg-white">
      <CardContent className="p-8">
        <h3 className="text-xl font-semibold text-gray-900">Key Results</h3>
        <div className="mt-6 grid grid-cols-2 gap-6">
          {items.map((i, idx) => (
            <div key={idx} className="rounded-xl bg-gray-50 p-4 text-center">
              <div className={`text-2xl font-bold ${i.color}`}>{i.value}</div>
              <div className="text-xs text-gray-600 mt-1 leading-tight">{i.label}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
