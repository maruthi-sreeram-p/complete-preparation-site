let mermaidPromise = null
let queue = Promise.resolve()
let counter = 0

/** Mermaid is large, so it is loaded on first use and themed once. */
function loadMermaid() {
  mermaidPromise ??= import('mermaid').then(({ default: mermaid }) => {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme: 'base',
      fontFamily: '"Inter Variable", ui-sans-serif, system-ui, sans-serif',
      themeVariables: {
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
    })
    return mermaid
  })
  return mermaidPromise
}

/**
 * Render Mermaid source to an SVG string. Renders run one at a time because
 * Mermaid renders into shared temporary DOM nodes.
 */
export function renderMermaid(code) {
  const run = async () => {
    const mermaid = await loadMermaid()
    const { svg } = await mermaid.render(`mermaid-${++counter}`, code)
    return svg
  }
  const result = queue.then(run)
  queue = result.catch(() => {})
  return result
}
