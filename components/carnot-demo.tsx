"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { useMemo, useState } from "react"

export default function CarnotDemo() {
  const [Tc, setTc] = useState(300) // cold reservoir (K)
  const [Th, setTh] = useState(500) // hot reservoir (K)

  const efficiency = useMemo(() => {
    const e = 1 - Tc / Math.max(Th, Tc + 1)
    // clamp to [0,1]
    return Math.max(0, Math.min(1, e))
  }, [Tc, Th])

  return (
    <Card>
      <CardContent className="p-6">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <div>
              <div className="text-sm font-medium">Hot Reservoir Temperature Th (K)</div>
              <Slider
                defaultValue={[Th]}
                min={310}
                max={900}
                step={10}
                onValueChange={(v) => setTh(v[0] ?? 500)}
                className="mt-3"
              />
              <div className="mt-1 text-sm text-muted-foreground">Th = {Th} K</div>
            </div>
            <div>
              <div className="text-sm font-medium">Cold Reservoir Temperature Tc (K)</div>
              <Slider
                defaultValue={[Tc]}
                min={200}
                max={Th - 10}
                step={10}
                onValueChange={(v) => setTc(v[0] ?? 300)}
                className="mt-3"
              />
              <div className="mt-1 text-sm text-muted-foreground">Tc = {Tc} K</div>
            </div>
            <div className="rounded-md border p-3">
              <div className="text-sm">Carnot Efficiency</div>
              <div className="text-2xl font-semibold">{(efficiency * 100).toFixed(1)}%</div>
              <div className="text-xs text-muted-foreground mt-1">η = 1 − Tc / Th</div>
            </div>
          </div>

          {/* Simple diagram */}
          <div className="flex items-center justify-center">
            <div className="w-full max-w-sm">
              <svg viewBox="0 0 380 240" className="w-full h-auto">
                {/* reservoirs */}
                <rect x="30" y="20" width="140" height="60" rx="8" className="fill-red-100 stroke-red-400" />
                <text x="100" y="55" textAnchor="middle" className="fill-red-700 text-sm">
                  {"Hot (Th=" + Th + "K)"}
                </text>
                <rect x="30" y="160" width="140" height="60" rx="8" className="fill-blue-100 stroke-blue-400" />
                <text x="100" y="195" textAnchor="middle" className="fill-blue-700 text-sm">
                  {"Cold (Tc=" + Tc + "K)"}
                </text>

                {/* engine */}
                <rect x="210" y="90" width="120" height="60" rx="8" className="fill-emerald-50 stroke-emerald-500" />
                <text x="270" y="123" textAnchor="middle" className="fill-emerald-700 text-sm">
                  {"Engine"}
                </text>

                {/* arrows */}
                <defs>
                  <marker id="arrow" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto">
                    <path d="M0,0 L0,6 L6,3 z" className="fill-gray-600" />
                  </marker>
                </defs>

                {/* Qh */}
                <line x1="170" y1="50" x2="210" y2="110" stroke="#4b5563" strokeWidth="2" markerEnd="url(#arrow)" />
                <text x="188" y="70" className="fill-gray-700 text-xs">
                  {"Qh"}
                </text>

                {/* Qc */}
                <line x1="210" y1="130" x2="170" y2="190" stroke="#4b5563" strokeWidth="2" markerEnd="url(#arrow)" />
                <text x="175" y="175" className="fill-gray-700 text-xs">
                  {"Qc"}
                </text>

                {/* W */}
                <line x1="330" y1="120" x2="360" y2="120" stroke="#16a34a" strokeWidth="3" markerEnd="url(#arrow)" />
                <text x="340" y="110" className="fill-emerald-700 text-xs">
                  {"W = η·Qh"}
                </text>

                {/* efficiency bar */}
                <rect x="210" y="170" width="120" height="16" rx="4" className="fill-gray-200" />
                <rect
                  x="210"
                  y="170"
                  width={120 * Math.max(0, Math.min(1, efficiency))}
                  height="16"
                  rx="4"
                  className="fill-emerald-500"
                />
                <text x="270" y="200" textAnchor="middle" className="fill-gray-700 text-xs">
                  {"η = " + (efficiency * 100).toFixed(1) + "%"}
                </text>
              </svg>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
