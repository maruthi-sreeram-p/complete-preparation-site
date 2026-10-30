import Markdown from './blocks/Markdown.jsx'
import CodeBlock from './blocks/CodeBlock.jsx'
import DiagramBlock from './blocks/DiagramBlock.jsx'
import {
  CalloutBlock,
  FigureBlock,
  QuestionsBlock,
  RelatedBlock,
  StepsBlock,
  TableBlock,
} from './blocks/SimpleBlocks.jsx'

/**
 * Block type → component. To support a new kind of content, add a component
 * here; content files and the page layout do not change.
 */
const blockComponents = {
  markdown: ({ text }) => <Markdown>{text}</Markdown>,
  code: CodeBlock,
  diagram: DiagramBlock,
  figure: FigureBlock,
  table: TableBlock,
  callout: CalloutBlock,
  steps: StepsBlock,
  questions: QuestionsBlock,
  related: RelatedBlock,
}

export function Block({ block }) {
  const Component = blockComponents[block.type]
  if (!Component) {
    return (
      <div className="rounded-lg border border-warn/30 bg-warn/5 p-3 text-sm text-warn">
        Unknown block type "{String(block.type)}".
      </div>
    )
  }
  return <Component {...block} />
}
