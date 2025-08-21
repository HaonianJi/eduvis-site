import { type NextRequest, NextResponse } from "next/server"
import { spawn } from "child_process"
import { promises as fs } from "fs"
import path from "path"

export async function POST(request: NextRequest) {
  try {
    const { prompt, type } = await request.json()
    const authHeader = request.headers.get("authorization")

    if (!prompt?.trim()) {
      return NextResponse.json({ error: "Problem description is required" }, { status: 400 })
    }

    const apiKey = authHeader?.replace("Bearer ", "") || ""

    console.log("🚀 Starting v0 automation pipeline...")
    
    // Call our powerful automation pipeline
    const result = await runV0AutomationPipeline(prompt, apiKey)
    
    if (result.success) {
      return NextResponse.json({
        success: true,
        projectUrl: result.projectUrl,
        projectPath: result.projectPath,
        message: result.message
      })
    } else {
      // Fallback to enhanced mock if pipeline fails
      console.warn("Pipeline failed, using enhanced mock:", result.error)
      const mockCode = generateEnhancedMockVisualization(prompt)
      
      return NextResponse.json({
        success: false,
        code: mockCode,
        error: result.error,
        fallback: true,
        files: [
          {
            path: "index.html",
            content: mockCode,
          },
        ],
      })
    }
  } catch (error) {
    console.error("API Error:", error)
    
    // Always provide fallback
    const mockCode = generateEnhancedMockVisualization(request.body ? 
      (await request.json()).prompt : "General educational visualization")
    
    return NextResponse.json({
      success: false,
      code: mockCode,
      error: "Pipeline execution failed",
      fallback: true,
      files: [
        {
          path: "index.html", 
          content: mockCode,
        },
      ],
    })
  }
}

async function runV0AutomationPipeline(prompt: string, apiKey: string) {
  return new Promise<{success: boolean, projectUrl?: string, projectPath?: string, message?: string, error?: string}>((resolve) => {
    const toolkitPath = path.join(process.cwd(), "v0_automation_toolkit")
    const scriptPath = path.join(toolkitPath, "v0_api_integration.py")
    
    console.log(`📁 Toolkit path: ${toolkitPath}`)
    console.log(`🐍 Script path: ${scriptPath}`)

    // Validate API key
    if (!apiKey || apiKey.trim() === "") {
      console.warn("⚠️ No API key provided, pipeline will fail")
      resolve({
        success: false,
        error: "API key is required for v0 project generation"
      })
      return
    }

    // Prepare environment variables
    const env = { ...process.env }
    env.V0_API_KEY = apiKey.trim()

    // Run the Python pipeline
    const pythonProcess = spawn("python3", [scriptPath], {
      cwd: toolkitPath,
      env: env,
      stdio: ['pipe', 'pipe', 'pipe']
    })

    let stdout = ""
    let stderr = ""

    // Send the prompt to the Python process
    pythonProcess.stdin.write(prompt + "\n")
    pythonProcess.stdin.end()

    pythonProcess.stdout.on("data", (data) => {
      const output = data.toString()
      stdout += output
      console.log("📝 Pipeline stdout:", output.trim())
    })

    pythonProcess.stderr.on("data", (data) => {
      const error = data.toString()
      stderr += error
      console.log("📝 Pipeline stderr:", error.trim()) // Changed from error to log
    })

    pythonProcess.on("close", (code) => {
      console.log(`🏁 Pipeline finished with code: ${code}`)
      
      if (code === 0) {
        try {
          // Try to parse JSON result from stdout
          const lines = stdout.trim().split('\n')
          const lastLine = lines[lines.length - 1]
          
          if (lastLine.startsWith('{')) {
            const result = JSON.parse(lastLine)
            if (result.success && result.projectUrl) {
              resolve({
                success: true,
                projectUrl: result.projectUrl,
                projectPath: result.projectPath,
                message: result.message || `Successfully generated project at ${result.projectUrl}`
              })
              return
            }
          }
          
          // Fallback: extract URL from any line
          const urlMatch = stdout.match(/http:\/\/localhost:(\d+)/)
          if (urlMatch) {
            const projectUrl = urlMatch[0]
            const port = urlMatch[1]
            
            resolve({
              success: true,
              projectUrl: projectUrl,
              projectPath: `Generated project running on port ${port}`,
              message: `🎉 Successfully generated interactive educational project! Running at ${projectUrl}`
            })
          } else {
            resolve({
              success: false,
              error: "Pipeline completed but no valid result found in output"
            })
          }
        } catch (parseError) {
          console.error("Failed to parse pipeline output:", parseError)
          resolve({
            success: false,
            error: `Pipeline output parsing failed: ${parseError instanceof Error ? parseError.message : 'Unknown error'}`
          })
        }
      } else {
        // Check for specific error patterns
        let errorMessage = `Pipeline failed with exit code ${code}`
        
        if (stderr.includes('401 Unauthorized')) {
          errorMessage = "Invalid or expired API key. Please check your v0 API key."
        } else if (stderr.includes('SSL')) {
          errorMessage = "Network connection issue. Please try again."
        } else if (stderr.includes('Missing API key')) {
          errorMessage = "API key is required for v0 project generation."
        }
        
        resolve({
          success: false,
          error: errorMessage
        })
      }
    })

    pythonProcess.on("error", (error) => {
      console.error("🔥 Process error:", error)
      resolve({
        success: false,
        error: `Failed to start pipeline: ${error.message}`
      })
    })

    // Set a timeout for the pipeline
    setTimeout(() => {
      pythonProcess.kill()
      resolve({
        success: false,
        error: "Pipeline timed out after 6 minutes. The process may still be running in the background."
      })
    }, 360000) // 6 minutes timeout - allows for shadcn-ui component installation
  })
}

function generateEnhancedMockVisualization(prompt: string): string {
  // Analyze prompt to determine subject area
  const isPhysics = /force|acceleration|velocity|newton|physics|motion/i.test(prompt)
  const isMath = /equation|formula|calculate|math|algebra|geometry|circle|area/i.test(prompt)
  const isChemistry = /chemical|reaction|molecule|atom|chemistry|photosynthesis/i.test(prompt)

  let subject = "General"
  let color = "#3b82f6"
  let examples: string[] = []

  if (isPhysics) {
    subject = "Physics"
    color = "#ef4444"
    examples = ["F = ma", "v = u + at", "KE = ½mv²"]
  } else if (isMath) {
    subject = "Mathematics"
    color = "#10b981"
    examples = ["A = πr²", "y = mx + b", "x = (-b ± √(b²-4ac))/2a"]
  } else if (isChemistry) {
    subject = "Chemistry"
    color = "#8b5cf6"
    examples = ["6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂", "H₂ + Cl₂ → 2HCl"]
  }

  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=width, initial-scale=1.0">
    <title>${subject} Educational Visualization</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .card { 
            background: white; 
            border-radius: 12px; 
            padding: 24px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            margin-bottom: 24px;
            border: 1px solid #e5e7eb;
        }
        .header { 
            text-align: center; 
            background: ${color}; 
            color: white; 
            margin: -24px -24px 24px -24px; 
            padding: 24px; 
            border-radius: 12px 12px 0 0;
        }
        .slider { 
            width: 100%; 
            margin: 16px 0; 
            height: 8px;
            border-radius: 4px;
            background: #e5e7eb;
            outline: none;
            -webkit-appearance: none;
        }
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: ${color};
            cursor: pointer;
        }
        .result { 
            font-size: 28px; 
            font-weight: bold; 
            color: ${color}; 
            text-align: center;
            padding: 16px;
            background: rgba(59, 130, 246, 0.1);
            border-radius: 8px;
            margin: 16px 0;
        }
        .step { 
            padding: 16px; 
            margin: 12px 0; 
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
            border-left: 4px solid ${color}; 
            border-radius: 0 8px 8px 0;
            transition: transform 0.2s ease;
        }
        .step:hover { transform: translateX(4px); }
        .btn { 
            background: ${color}; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: 600;
            transition: all 0.2s ease;
            margin: 8px;
        }
        .btn:hover { 
            background: ${color}dd; 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .formula-box {
            background: #f8fafc;
            border: 2px dashed ${color};
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            font-family: 'Courier New', monospace;
            font-size: 18px;
            margin: 16px 0;
        }
        .interactive-area {
            background: rgba(255,255,255,0.8);
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
        }
        .progress-bar {
            width: 100%;
            height: 12px;
            background: #e5e7eb;
            border-radius: 6px;
            overflow: hidden;
            margin: 16px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, ${color} 0%, ${color}aa 100%);
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        function EducationalVisualization() {
            const [value, setValue] = React.useState(50);
            const [showSteps, setShowSteps] = React.useState(false);
            const [currentStep, setCurrentStep] = React.useState(0);
            
            const steps = [
                "Identify the given information and what we need to find",
                "Choose the appropriate formula or method",
                "Substitute the known values into the formula",
                "Perform the calculations step by step",
                "Check the result and units for reasonableness"
            ];

            React.useEffect(() => {
                if (showSteps) {
                    const timer = setInterval(() => {
                        setCurrentStep(prev => (prev + 1) % steps.length);
                    }, 2000);
                    return () => clearInterval(timer);
                }
            }, [showSteps]);
            
            return (
                <div className="container">
                    <div className="card">
                        <div className="header">
                            <h1>${subject} Problem Solver</h1>
                            <p>Interactive Educational Visualization</p>
                        </div>
                        <div>
                            <h2>Problem Statement</h2>
                            <p style={{fontSize: '16px', lineHeight: '1.6'}}><strong>Problem:</strong> ${prompt}</p>
                            
                            ${
                              examples.length > 0
                                ? `
                            <div className="formula-box">
                                <strong>Key Formula:</strong> ${examples[0]}
                            </div>
                            `
                                : ""
                            }
                        </div>
                    </div>
                    
                    <div className="card">
                        <h2>Step-by-Step Solution</h2>
                        <div style={{display: 'flex', gap: '12px', marginBottom: '16px'}}>
                            <button className="btn" onClick={() => setShowSteps(!showSteps)}>
                                {showSteps ? 'Hide Steps' : 'Show Steps'}
                            </button>
                            <button className="btn" onClick={() => setCurrentStep(0)}>
                                Reset Steps
                            </button>
                        </div>
                        
                        {showSteps && (
                            <div>
                                {steps.map((step, index) => (
                                    <div 
                                        key={index}
                                        className="step" 
                                        style={{
                                            opacity: index <= currentStep ? 1 : 0.3,
                                            transform: index === currentStep ? 'scale(1.02)' : 'scale(1)'
                                        }}
                                    >
                                        <strong>Step {index + 1}:</strong> {step}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    
                    <div className="card">
                        <h2>Interactive Visualization</h2>
                        <div className="interactive-area">
                            <label style={{fontSize: '18px', fontWeight: '600'}}>
                                Adjust Parameter: {value}
                            </label>
                            <input 
                                type="range" 
                                min="0" 
                                max="100" 
                                value={value}
                                onChange={(e) => setValue(parseInt(e.target.value))}
                                className="slider"
                            />
                            <div className="progress-bar">
                                <div className="progress-fill" style={{width: value + '%'}}></div>
                            </div>
                            <div className="result">
                                Result: {(value * 1.5).toFixed(2)} units
                            </div>
                            <div style={{display: 'flex', justifyContent: 'center', gap: '12px'}}>
                                <button className="btn" onClick={() => setValue(25)}>Low</button>
                                <button className="btn" onClick={() => setValue(50)}>Medium</button>
                                <button className="btn" onClick={() => setValue(75)}>High</button>
                                <button className="btn" onClick={() => setValue(100)}>Maximum</button>
                            </div>
                        </div>
                    </div>
                    
                    <div className="card">
                        <h2>Visual Representation</h2>
                        <div style={{textAlign: 'center'}}>
                            <svg width="500" height="300" style={{border: '2px solid #e5e7eb', borderRadius: '8px', background: 'white'}}>
                                <defs>
                                    <linearGradient id="barGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" style={{stopColor: '${color}', stopOpacity: 1}} />
                                        <stop offset="100%" style={{stopColor: '${color}', stopOpacity: 0.6}} />
                                    </linearGradient>
                                </defs>
                                
                                {/* Grid lines */}
                                {[0,1,2,3,4,5].map(i => (
                                    <g key={i}>
                                        <line x1="50" y1={50 + i * 40} x2="450" y2={50 + i * 40} 
                                              stroke="#f3f4f6" strokeWidth="1" />
                                        <text x="30" y={55 + i * 40} fontSize="12" fill="#6b7280">
                                            {100 - i * 20}
                                        </text>
                                    </g>
                                ))}
                                
                                {/* Main bar */}
                                <rect x="100" y={250 - (value * 2)} 
                                      width="60" height={value * 2} 
                                      fill="url(#barGradient)" 
                                      rx="4" />
                                
                                {/* Value label */}
                                <text x="130" y={240 - (value * 2)} 
                                      textAnchor="middle" fontSize="14" fontWeight="bold" fill="white">
                                    {value}
                                </text>
                                
                                {/* Axis labels */}
                                <text x="130" y="280" textAnchor="middle" fontSize="14" fill="#374151">
                                    Parameter Value
                                </text>
                                <text x="20" y="150" fontSize="14" fill="#374151" transform="rotate(-90 20 150)">
                                    Output
                                </text>
                                
                                {/* Result visualization */}
                                <circle cx="300" cy="150" r={value * 0.8} fill="${color}" fillOpacity="0.3" stroke="${color}" strokeWidth="2" />
                                <text x="300" y="155" textAnchor="middle" fontSize="16" fontWeight="bold" fill="${color}">
                                    {(value * 1.5).toFixed(1)}
                                </text>
                            </svg>
                        </div>
                    </div>
                    
                    <div className="card">
                        <h2>Summary & Next Steps</h2>
                        <div style={{background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e5e7eb'}}>
                            <p><strong>What we learned:</strong> This interactive visualization demonstrates the relationship between input parameters and calculated results in ${subject.toLowerCase()}.</p>
                            <p><strong>Key insight:</strong> As we adjust the parameter value, we can observe how it directly affects the final outcome.</p>
                            <p><strong>Try this:</strong> Experiment with different values and observe the patterns in both the numerical results and visual representation.</p>
                        </div>
                    </div>
                </div>
            );
        }
        
        ReactDOM.render(<EducationalVisualization />, document.getElementById('root'));
    </script>
</body>
</html>`
}
