"use client"

import SiteHeader from "@/components/site-header"
import Footer from "@/components/footer"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useState } from "react"

const sample = {
  question: "A force of 50 N is applied to a 5 kg block. What is the acceleration of the block?",
  hint: "Use Newton's Second Law: a = F / m",
  answer: "10 m/s^2",
}

export default function QuestionsPage() {
  const [show, setShow] = useState(false)
  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      <main className="flex-1 mx-auto max-w-4xl w-full px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-2xl font-semibold">Example Question</h1>
        <Card className="mt-6">
          <CardContent className="p-6">
            <p className="text-base">{sample.question}</p>
            <div className="mt-4">
              <div className="text-sm text-muted-foreground">Hint</div>
              <div className="text-sm">{sample.hint}</div>
            </div>
            <div className="mt-4 flex gap-2">
              <Button onClick={() => setShow((s) => !s)}>{show ? "Hide" : "Reveal"} Answer</Button>
              {show && <div className="text-sm rounded-md border px-3 py-2 bg-muted">{sample.answer}</div>}
            </div>
          </CardContent>
        </Card>
      </main>
      <Footer />
    </div>
  )
}
