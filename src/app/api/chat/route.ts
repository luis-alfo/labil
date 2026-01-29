import Anthropic from '@anthropic-ai/sdk'
import { NextRequest, NextResponse } from 'next/server'
import { ORCHESTRATOR_PROMPT, getAgentPrompt } from '@/lib/agents/prompts'

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || '',
})

interface ChatRequest {
  message: string
  currentDiagram: string
  diagramType?: 'flowchart' | 'erDiagram' | 'sequenceDiagram'
  requestPlan?: boolean // Si true, devuelve plan antes de ejecutar
}

async function callClaude(systemPrompt: string, userMessage: string): Promise<string> {
  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 2048,
    system: systemPrompt,
    messages: [{ role: 'user', content: userMessage }],
  })

  const textBlock = response.content.find((block) => block.type === 'text')
  return textBlock ? textBlock.text : ''
}

async function determineAgentType(message: string): Promise<'flow' | 'erd' | 'sequence'> {
  const response = await callClaude(ORCHESTRATOR_PROMPT, message)
  const agentType = response.toLowerCase().trim()

  if (agentType === 'erd' || agentType === 'sequence') {
    return agentType
  }
  return 'flow' // default
}

// Genera un título corto para el historial basado en el prompt
async function generateTitle(message: string): Promise<string> {
  const titlePrompt = `Genera un título muy corto (máximo 5 palabras) que describa esta acción sobre un diagrama. Solo responde con el título, sin explicaciones ni puntuación extra.

Ejemplos:
- "añade un paso de validación" → "Añadir validación"
- "crea un diagrama de login" → "Flujo de login"
- "agrega dolor en paso 3" → "Punto de dolor añadido"

Mensaje del usuario: "${message}"`

  const response = await callClaude('Eres un asistente que genera títulos cortos y descriptivos.', titlePrompt)
  return response.trim().substring(0, 50) // Limitar a 50 chars
}

// Genera un plan de cambios antes de ejecutar
async function generatePlan(
  agentType: 'flow' | 'erd' | 'sequence',
  message: string,
  currentDiagram: string
): Promise<string[]> {
  const planPrompt = `Analiza qué cambios se harían al diagrama según la solicitud del usuario. Genera una lista de 2-4 pasos concretos que se realizarán.

Diagrama actual (Mermaid):
${currentDiagram || '(vacío)'}

Solicitud: "${message}"

Responde SOLO con una lista numerada de pasos, sin explicaciones adicionales. Ejemplo:
1. Añadir nodo "Validación"
2. Conectar "Input" → "Validación"
3. Marcar como punto de dolor`

  const response = await callClaude(
    'Eres un asistente que planifica cambios en diagramas. Sé conciso.',
    planPrompt
  )

  // Parsear la respuesta en array
  const lines = response.split('\n').filter(line => line.trim())
  const steps = lines
    .map(line => line.replace(/^\d+\.\s*/, '').trim())
    .filter(step => step.length > 0)

  return steps.slice(0, 5) // Máximo 5 pasos
}

async function generateDiagram(
  agentType: 'flow' | 'erd' | 'sequence',
  message: string,
  currentDiagram: string
): Promise<string> {
  const systemPrompt = getAgentPrompt(agentType, currentDiagram)
  const response = await callClaude(systemPrompt, message)

  // Clean up response - remove markdown code blocks if present
  let cleanedResponse = response
    .replace(/```mermaid\n?/gi, '')
    .replace(/```\n?/g, '')
    .trim()

  return cleanedResponse
}

async function validateDiagram(diagram: string): Promise<string> {
  const systemPrompt = getAgentPrompt('validator', '')
  const response = await callClaude(systemPrompt, diagram)

  return response
    .replace(/```mermaid\n?/gi, '')
    .replace(/```\n?/g, '')
    .trim()
}

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequest = await request.json()
    const { message, currentDiagram, requestPlan } = body

    if (!message) {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 })
    }

    if (!process.env.ANTHROPIC_API_KEY) {
      return NextResponse.json(
        { error: 'ANTHROPIC_API_KEY not configured' },
        { status: 500 }
      )
    }

    // Step 1: Determine which agent should handle this
    const agentType = await determineAgentType(message)

    // Step 2: Generar título para historial
    const title = await generateTitle(message)

    // Step 3: Si requestPlan, generar plan y Mermaid pero devolver para confirmación
    if (requestPlan) {
      const plan = await generatePlan(agentType, message, currentDiagram)
      const generatedDiagram = await generateDiagram(agentType, message, currentDiagram)
      const validatedDiagram = await validateDiagram(generatedDiagram)

      return NextResponse.json({
        mermaidCode: validatedDiagram,
        agentUsed: agentType,
        title,
        plan, // Array de pasos para mostrar al usuario
        requiresConfirmation: true,
      })
    }

    // Flujo normal: generar y aplicar directamente
    const generatedDiagram = await generateDiagram(agentType, message, currentDiagram)
    const validatedDiagram = await validateDiagram(generatedDiagram)

    return NextResponse.json({
      mermaidCode: validatedDiagram,
      agentUsed: agentType,
      title,
    })
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}
