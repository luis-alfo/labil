// Color combinations for 3D STL viewer
// Each "version" is a pair of (primary, secondary) colors blended along the Y axis

export type ColorPair = {
  name: string
  primary: string
  secondary: string
}

export type Palette = {
  name: string
  hex: string
}

export const palette: Palette[] = [
  { name: 'Cream', hex: '#FDF6F0' },
  { name: 'Coral', hex: '#FFB5A7' },
  { name: 'Rose', hex: '#FF8FA3' },
  { name: 'Yellow', hex: '#FFE066' },
  { name: 'Mint', hex: '#B5EAD7' },
  { name: 'Sage', hex: '#7DC89E' },
  { name: 'Sky', hex: '#A2D2FF' },
  { name: 'Ocean', hex: '#5E9EFF' },
  { name: 'Lavender', hex: '#E2BBE9' },
  { name: 'Violet', hex: '#A78BFA' },
  { name: 'Sand', hex: '#F0CFA0' },
  { name: 'Charcoal', hex: '#3A3A3A' },
]

export const versions: ColorPair[] = [
  { name: 'Sakura',  primary: '#FF8FA3', secondary: '#FDF6F0' },
  { name: 'Ocean',   primary: '#A2D2FF', secondary: '#B5EAD7' },
  { name: 'Sunset',  primary: '#FFB5A7', secondary: '#FFE066' },
  { name: 'Forest',  primary: '#7DC89E', secondary: '#FDF6F0' },
  { name: 'Galaxy',  primary: '#A78BFA', secondary: '#FF8FA3' },
  { name: 'Lemon',   primary: '#FFE066', secondary: '#B5EAD7' },
  { name: 'Berry',   primary: '#E2BBE9', secondary: '#FFB5A7' },
  { name: 'Sky',     primary: '#5E9EFF', secondary: '#FDF6F0' },
  { name: 'Sand',    primary: '#F0CFA0', secondary: '#FDF6F0' },
  { name: 'Mono',    primary: '#FDF6F0', secondary: '#FDF6F0' },
  { name: 'Noir',    primary: '#3A3A3A', secondary: '#FFE066' },
  { name: 'Mint',    primary: '#B5EAD7', secondary: '#A2D2FF' },
]
