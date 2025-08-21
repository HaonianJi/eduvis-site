"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Menu } from "lucide-react"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { useState } from "react"

export default function SiteHeader() {
  const [open, setOpen] = useState(false)
  const nav = [
    { href: "/", label: "Home" },
    { href: "/v0-playground", label: "Playground" },
    { href: "/questions", label: "Questions" },
    { href: "/news", label: "News" },
    { href: "/contact", label: "Contact" },
    { href: "/cite", label: "Cite" },
  ]
  return (
    <header className="sticky top-0 z-40 w-full border-b border-gray-200 bg-white/80 backdrop-blur-xl">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="font-semibold text-lg">
          <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">EduVis</span>
          <span className="text-gray-700 ml-1">Research</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          {nav.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors font-medium"
            >
              {n.label}
            </Link>
          ))}
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white shadow-sm">
            Get Started
          </Button>
        </nav>

        <div className="md:hidden">
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button size="icon" variant="ghost" aria-label="Open menu" className="text-gray-600">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-64 bg-white">
              <div className="flex flex-col gap-6 mt-8">
                {nav.map((n) => (
                  <Link
                    key={n.href}
                    href={n.href}
                    className="text-base font-medium text-gray-700 hover:text-gray-900"
                    onClick={() => setOpen(false)}
                  >
                    {n.label}
                  </Link>
                ))}
                <Button className="bg-blue-600 hover:bg-blue-700 mt-4" onClick={() => setOpen(false)}>
                  Get Started
                </Button>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
