let mermaidPromise = null
let queue = Promise.resolve()
let counter = 0
let currentTheme = null

const THEMES = {
  dark: {
    darkMode: true,
    background: 'transparent',
    fontSize: '14px',
    primaryColor: '#1f1c3d',
    primaryBorderColor: '#7c6cf0',
    primaryTextColor: '#e7e9f3',
    secondaryColor: '#14233d',
    secondaryBorderColor: '#4a7fd8',
    secondaryTextColor: '#e7e9f3',
    tertiaryColor: '#1c1c1c',
    tertiaryBorderColor: '#404040',
    tertiaryTextColor: '#e7e9f3',
    lineColor: '#9a9a9a',
    textColor: '#cfd3e6',
    mainBkg: '#1f1c3d',
    nodeBorder: '#7c6cf0',
    clusterBkg: '#191919',
    clusterBorder: '#404040',
    edgeLabelBackground: '#111111',
    actorBkg: '#1f1c3d',
    actorBorder: '#7c6cf0',
    actorTextColor: '#e7e9f3',
    actorLineColor: '#4a4f72',
    signalColor: '#a1a7c0',
    signalTextColor: '#cfd3e6',
    noteBkgColor: '#2a2440',
    noteTextColor: '#e7e9f3',
    noteBorderColor: '#7c6cf0',
    labelBoxBkgColor: '#1f1c3d',
    labelBoxBorderColor: '#7c6cf0',
    labelTextColor: '#e7e9f3',
    loopTextColor: '#cfd3e6',
  },
  light: {
    darkMode: false,
    background: 'transparent',
    fontSize: '14px',
    primaryColor: '#ede9fe',
    primaryBorderColor: '#6d5ce7',
    primaryTextColor: '#18181b',
    secondaryColor: '#dbeafe',
    secondaryBorderColor: '#2f6fe0',
    secondaryTextColor: '#18181b',
    tertiaryColor: '#f4f4f5',
    tertiaryBorderColor: '#d4d4d8',
    tertiaryTextColor: '#18181b',
    lineColor: '#52525b',
    textColor: '#27272a',
    mainBkg: '#ede9fe',
    nodeBorder: '#6d5ce7',
    clusterBkg: '#fafafa',
    clusterBorder: '#d4d4d8',
    edgeLabelBackground: '#ffffff',
    actorBkg: '#ede9fe',
    actorBorder: '#6d5ce7',
    actorTextColor: '#18181b',
    actorLineColor: '#a1a1aa',
    signalColor: '#52525b',
    signalTextColor: '#27272a',
    noteBkgColor: '#f5f3ff',
    noteTextColor: '#18181b',
    noteBorderColor: '#6d5ce7',
    labelBoxBkgColor: '#ede9fe',
    labelBoxBorderColor: '#6d5ce7',
    labelTextColor: '#18181b',
    loopTextColor: '#27272a',
  },
}

/** Mermaid is large, so it is loaded on first use. */
function loadMermaid() {
  mermaidPromise ??= import('mermaid').then(({ default: mermaid }) => mermaid)
  return mermaidPromise
}

/**
 * Render Mermaid source to an SVG string for the given theme. Renders run one at a
 * time because Mermaid renders into shared temporary DOM nodes.
 */
export function renderMermaid(code, theme = 'dark') {
  const run = async () => {
    const mermaid = await loadMermaid()
    if (currentTheme !== theme) {
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: 'strict',
        theme: 'base',
        fontFamily: '"Inter Variable", ui-sans-serif, system-ui, sans-serif',
        themeVariables: THEMES[theme],
      })
      currentTheme = theme
    }
    const { svg } = await mermaid.render(`mermaid-${++counter}`, code)
    return svg
  }
  const result = queue.then(run)
  queue = result.catch(() => {})
  return result
}
