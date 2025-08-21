import SiteHeader from "@/components/site-header"
import Footer from "@/components/footer"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Mail, Github, Globe } from "lucide-react"

export default function ContactPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      <main className="flex-1 mx-auto max-w-4xl w-full px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-2xl font-semibold">Contact</h1>
        <Card className="mt-6">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground">
              For questions about the paper, benchmark, or code, feel free to reach out.
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <Button asChild>
                <a href="mailto:huaxiu@cs.unc.edu?subject=EduVisBench/EduVisAgent Inquiry">
                  <Mail className="mr-2 h-4 w-4" />
                  Email
                </a>
              </Button>
              <Button asChild variant="outline">
                <a href="https://github.com/aiming-lab" target="_blank" rel="noopener noreferrer">
                  <Github className="mr-2 h-4 w-4" />
                  GitHub Org
                </a>
              </Button>
              <Button asChild variant="outline">
                <a href="/" rel="noopener">
                  <Globe className="mr-2 h-4 w-4" />
                  Home
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
      <Footer />
    </div>
  )
}
