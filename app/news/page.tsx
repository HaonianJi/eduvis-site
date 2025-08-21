import SiteHeader from "@/components/site-header"
import Footer from "@/components/footer"
import { Card, CardContent } from "@/components/ui/card"

const items = [
  { date: "2025-05-27", text: "arXiv v2 released with extended experiments." },
  { date: "2025-05-20", text: "Benchmark and agent repositories public." },
  { date: "2025-05-15", text: "Project website launched." },
]

export default function NewsPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      <main className="flex-1 mx-auto max-w-4xl w-full px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-2xl font-semibold">News</h1>
        <div className="mt-6 grid gap-4">
          {items.map((n, i) => (
            <Card key={i}>
              <CardContent className="p-5">
                <div className="text-sm text-muted-foreground">{n.date}</div>
                <div className="text-base mt-1">{n.text}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
      <Footer />
    </div>
  )
}
