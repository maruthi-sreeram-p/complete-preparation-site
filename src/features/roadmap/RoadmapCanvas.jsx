import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Background,
  BackgroundVariant,
  MarkerType,
  MiniMap,
  Panel,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
  useStore,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Funnel, Maximize, Search, ZoomIn, ZoomOut } from 'lucide-react'
import { useRoadmapScope } from './RoadmapScope.jsx'
import TopicNode from './TopicNode.jsx'
import { NODE_SIZE, computeLayout } from '@/lib/roadmap/layout.js'
import { ancestorsOf, descendantsOf } from '@/lib/roadmap/model.js'
import { STATUS, STATUS_LABEL } from '@/lib/progress/status.js'
import StatusIcon from '@/components/ui/StatusIcon.jsx'
import { cn, paths } from '@/lib/util.js'

const nodeTypes = { topic: TopicNode }
// The search/filter panel sits over the top of the canvas, so overviews leave room for it.
const FIT = { padding: { top: '170px', right: '40px', bottom: '100px', left: '40px' }, maxZoom: 1 }
const TOP_MARGIN = 170
const MIN_START_ZOOM = 0.55

const EDGE_COLORS = { idle: '#2f3350', done: '#5d54b3', active: '#a99cff' }

function RoadmapFlow() {
  const scope = useRoadmapScope()
  const { roadmap, statusOf, subProgress, setTopicStatus } = scope
  const navigate = useNavigate()
  const { zoomIn, zoomOut, fitView, setCenter, setViewport } = useReactFlow()
  const zoom = useStore((s) => s.transform[2])
  const width = useStore((s) => s.width)
  const started = useRef(false)

  const [hoverId, setHoverId] = useState(null)
  const [query, setQuery] = useState('')
  const [focusedCategories, setFocusedCategories] = useState(() => new Set())
  const [filtersOpen, setFiltersOpen] = useState(false)

  const layout = useMemo(() => computeLayout(roadmap), [roadmap])

  const hoverSet = useMemo(() => {
    if (!hoverId) return null
    return new Set([hoverId, ...ancestorsOf(roadmap, hoverId), ...descendantsOf(roadmap, hoverId)])
  }, [roadmap, hoverId])

  const matches = useCallback(
    (topic) => {
      const q = query.trim().toLowerCase()
      const textOk =
        !q ||
        topic.title.toLowerCase().includes(q) ||
        topic.summary.toLowerCase().includes(q) ||
        roadmap.categoryById[topic.categoryId].title.toLowerCase().includes(q)
      const categoryOk = focusedCategories.size === 0 || focusedCategories.has(topic.categoryId)
      return textOk && categoryOk
    },
    [query, focusedCategories, roadmap],
  )

  const nodes = useMemo(
    () =>
      roadmap.topics.map((topic) => ({
        id: topic.id,
        type: 'topic',
        position: layout.positions[topic.id],
        width: NODE_SIZE.width,
        height: NODE_SIZE.height,
        draggable: false,
        connectable: false,
        data: {
          topic,
          category: roadmap.categoryById[topic.categoryId],
          status: statusOf(topic.id),
          sub: subProgress(topic.id),
          dimmed: (hoverSet ? !hoverSet.has(topic.id) : false) || !matches(topic),
          onCycleStatus: setTopicStatus,
        },
      })),
    [roadmap, layout, statusOf, subProgress, hoverSet, matches, setTopicStatus],
  )

  const edges = useMemo(
    () =>
      roadmap.edges.map((edge) => {
        const active = hoverSet?.has(edge.source) && hoverSet.has(edge.target)
        const done = statusOf(edge.source) === STATUS.COMPLETED
        const color = active ? EDGE_COLORS.active : done ? EDGE_COLORS.done : EDGE_COLORS.idle
        return {
          ...edge,
          type: 'default',
          animated: false,
          style: { stroke: color, strokeWidth: active ? 2 : 1.5, opacity: hoverSet && !active ? 0.2 : 1 },
          markerEnd: { type: MarkerType.ArrowClosed, color, width: 16, height: 16 },
        }
      }),
    [roadmap, statusOf, hoverSet],
  )

  // Start at a readable zoom, centred on the map and anchored at its top, rather than
  // shrinking a large roadmap to fit. The "Fit to screen" button gives the overview.
  useEffect(() => {
    if (started.current || !width) return
    started.current = true
    const boxes = Object.values(layout.positions)
    const minX = Math.min(...boxes.map((p) => p.x))
    const maxX = Math.max(...boxes.map((p) => p.x + NODE_SIZE.width))
    const minY = Math.min(...boxes.map((p) => p.y))
    const z = Math.min(1, Math.max(MIN_START_ZOOM, (width - 80) / (maxX - minX)))
    setViewport({
      x: (width - (maxX - minX) * z) / 2 - minX * z,
      y: TOP_MARGIN - minY * z,
      zoom: z,
    })
  }, [width, layout, setViewport])

  const focusFirstMatch = () => {
    const first = roadmap.topics.find(matches)
    if (!first) return
    const { x, y } = layout.positions[first.id]
    setCenter(x + 124, y + 38, { zoom: 1, duration: 400 })
  }

  const toggleCategory = (id) =>
    setFocusedCategories((prev) => {
      const next = new Set(prev)
      if (!next.delete(id)) next.add(id)
      return next
    })

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      colorMode="dark"
      minZoom={0.15}
      maxZoom={1.75}
      nodesDraggable={false}
      nodesConnectable={false}
      elementsSelectable={false}
      zoomOnDoubleClick={false}
      onNodeClick={(_, node) => navigate(paths.topic(roadmap.id, node.id))}
      onNodeMouseEnter={(_, node) => setHoverId(node.id)}
      onNodeMouseLeave={() => setHoverId(null)}
    >
      <Background variant={BackgroundVariant.Dots} gap={24} size={1.2} color="#1c1f31" />
      <MiniMap
        pannable
        zoomable
        className="hidden! md:block!"
        nodeColor={(n) => n.data.category.color}
        nodeStrokeWidth={0}
        nodeBorderRadius={2}
        maskColor="rgb(10 11 17 / 0.72)"
      />

      <Panel position="top-left" className="!m-3 flex max-w-[calc(100%-1.5rem)] flex-col gap-2">
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 rounded-lg border border-line bg-panel/90 px-2.5 py-1.5 backdrop-blur focus-within:border-accent/60">
            <Search size={14} className="text-faint" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && focusFirstMatch()}
              placeholder="Search topics"
              aria-label="Search topics"
              className="w-40 bg-transparent text-sm outline-none placeholder:text-faint sm:w-56"
            />
          </label>
          <button
            type="button"
            onClick={() => setFiltersOpen((v) => !v)}
            aria-pressed={filtersOpen}
            aria-label="Toggle category filters"
            className={cn(
              'rounded-lg border border-line bg-panel/90 p-2 text-muted backdrop-blur hover:text-ink md:hidden',
              filtersOpen && 'text-ink',
            )}
          >
            <Funnel size={14} />
          </button>
        </div>
        <div className={cn('flex-wrap gap-1.5', filtersOpen ? 'flex' : 'hidden md:flex')}>
          {roadmap.categories.map((category) => {
            const on = focusedCategories.has(category.id)
            return (
              <button
                key={category.id}
                type="button"
                onClick={() => toggleCategory(category.id)}
                aria-pressed={on}
                className={cn(
                  'inline-flex items-center gap-1.5 rounded-full border bg-panel/90 px-2.5 py-1 text-xs backdrop-blur transition-colors',
                  on ? 'border-line-strong text-ink' : 'border-line text-muted hover:text-ink',
                )}
              >
                <span className="size-2 rounded-full" style={{ background: category.color }} />
                {category.title}
              </button>
            )
          })}
        </div>
      </Panel>

      <Panel position="bottom-left" className="!m-3 flex flex-col gap-2">
        <div className="flex items-center overflow-hidden rounded-lg border border-line bg-panel/90 backdrop-blur">
          <ToolbarButton label="Zoom out" onClick={() => zoomOut({ duration: 200 })}>
            <ZoomOut size={15} />
          </ToolbarButton>
          <span className="w-12 text-center text-xs tabular-nums text-muted">{Math.round(zoom * 100)}%</span>
          <ToolbarButton label="Zoom in" onClick={() => zoomIn({ duration: 200 })}>
            <ZoomIn size={15} />
          </ToolbarButton>
          <span className="h-5 w-px bg-line" />
          <ToolbarButton label="Fit to screen" onClick={() => fitView({ ...FIT, duration: 300 })}>
            <Maximize size={15} />
          </ToolbarButton>
        </div>
        <div className="hidden items-center gap-3 rounded-lg border border-line bg-panel/90 px-3 py-1.5 text-[11px] text-muted backdrop-blur sm:flex">
          {Object.values(STATUS).map((status) => (
            <span key={status} className="inline-flex items-center gap-1">
              <StatusIcon status={status} size={12} /> {STATUS_LABEL[status]}
            </span>
          ))}
          <span className="inline-flex items-center gap-1">
            <span className="h-2.5 w-3.5 rounded-sm border border-dashed border-faint" /> No content yet
          </span>
        </div>
      </Panel>
    </ReactFlow>
  )
}

function ToolbarButton({ label, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      className="p-2 text-muted transition-colors hover:bg-panel-2 hover:text-ink"
    >
      {children}
    </button>
  )
}

export default function RoadmapCanvas() {
  return (
    <ReactFlowProvider>
      <RoadmapFlow />
    </ReactFlowProvider>
  )
}
