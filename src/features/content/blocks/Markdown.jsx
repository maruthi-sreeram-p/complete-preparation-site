import { Children, Fragment, useMemo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import CodeBlock from './CodeBlock.jsx'
import { expandInlineListings } from '@/lib/content/prettyCode.js'

const remarkPlugins = [remarkGfm]

const components = {
  // Fenced code goes through our CodeBlock; inline code keeps a light style.
  pre({ children }) {
    const child = Children.only(children)
    const language = /language-([\w-]+)/.exec(child.props.className ?? '')?.[1]
    return <CodeBlock code={String(child.props.children).replace(/\n$/, '')} language={language} />
  },
  code({ children }) {
    return <code className="inline-code">{children}</code>
  },
  a({ href, children }) {
    const external = /^https?:/.test(href ?? '')
    return (
      <a href={href} {...(external ? { target: '_blank', rel: 'noreferrer noopener' } : {})}>
        {children}
      </a>
    )
  },
  table({ children }) {
    return (
      <div className="table-wrap">
        <table>{children}</table>
      </div>
    )
  },
}

/** Markdown (GitHub-flavoured). `inline` renders without paragraph wrappers, for table cells and similar. */
export default function Markdown({ children, inline = false }) {
  const text = typeof children === 'string' ? children : ''
  const expanded = useMemo(() => (inline ? text : expandInlineListings(text)), [text, inline])
  if (inline) {
    return (
      <ReactMarkdown remarkPlugins={remarkPlugins} components={{ ...components, p: Fragment }}>
        {text}
      </ReactMarkdown>
    )
  }
  return (
    <div className="doc">
      <ReactMarkdown remarkPlugins={remarkPlugins} components={components}>
        {expanded}
      </ReactMarkdown>
    </div>
  )
}
