import { test, expect } from '@playwright/test'

test.describe('Agent to Canvas Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    // Esperar que la app cargue
    await page.waitForSelector('[data-testid="canvas"]', { timeout: 10000 })
  })

  test('opens agent panel with keyboard shortcut', async ({ page }) => {
    // Presionar Cmd/Ctrl + K para abrir el panel de agente
    await page.keyboard.press('Meta+k')

    // Verificar que el panel de agente aparece
    await expect(page.locator('text=Agente')).toBeVisible()
    await expect(page.locator('textarea[placeholder*="Describe"]')).toBeVisible()
  })

  test('canvas shows nodes after creating diagram via agent', async ({ page }) => {
    // Abrir panel de agente
    await page.keyboard.press('Meta+k')
    await page.waitForSelector('textarea[placeholder*="Describe"]')

    // Escribir un prompt simple
    const textarea = page.locator('textarea[placeholder*="Describe"]')
    await textarea.fill('Crea un diagrama simple con 3 cajas: Inicio, Proceso, Fin')

    // Enviar el mensaje
    await page.click('button:has-text("Enviar")')

    // Esperar respuesta del agente (puede tardar)
    await expect(page.locator('text=Diagrama actualizado')).toBeVisible({ timeout: 30000 })

    // Verificar que aparecen nodos en el canvas
    // Los nodos de ReactFlow tienen la clase react-flow__node
    await expect(page.locator('.react-flow__node')).toHaveCount({ minimum: 1 }, { timeout: 5000 })
  })

  test('can close agent panel with Escape', async ({ page }) => {
    // Abrir panel
    await page.keyboard.press('Meta+k')
    await expect(page.locator('text=Agente')).toBeVisible()

    // Cerrar con Escape
    await page.keyboard.press('Escape')
    await expect(page.locator('text=Agente')).not.toBeVisible()
  })

  test('toolbar is visible on the canvas', async ({ page }) => {
    // Verificar que la toolbar está visible
    await expect(page.locator('[data-testid="toolbar"]')).toBeVisible()
  })

  test('can zoom in and out with controls', async ({ page }) => {
    // ReactFlow tiene controles de zoom por defecto
    const zoomIn = page.locator('.react-flow__controls-button[aria-label="zoom in"]')
    const zoomOut = page.locator('.react-flow__controls-button[aria-label="zoom out"]')

    if (await zoomIn.isVisible()) {
      await zoomIn.click()
      await zoomOut.click()
      // Si no hay error, el test pasa
    }
  })
})

test.describe('Canvas Interactions', () => {
  test('canvas is interactive and responsive', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('[data-testid="canvas"]')

    // El canvas debería ser visible y ocupar espacio
    const canvas = page.locator('[data-testid="canvas"]')
    await expect(canvas).toBeVisible()

    const box = await canvas.boundingBox()
    expect(box?.width).toBeGreaterThan(100)
    expect(box?.height).toBeGreaterThan(100)
  })
})
