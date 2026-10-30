export const STATUS = Object.freeze({
  NOT_STARTED: 'not-started',
  IN_PROGRESS: 'in-progress',
  COMPLETED: 'completed',
})

export const STATUS_ORDER = [STATUS.NOT_STARTED, STATUS.IN_PROGRESS, STATUS.COMPLETED]

export const STATUS_LABEL = {
  [STATUS.NOT_STARTED]: 'Not started',
  [STATUS.IN_PROGRESS]: 'In progress',
  [STATUS.COMPLETED]: 'Completed',
}

export const isStatus = (value) => STATUS_ORDER.includes(value)

/** Cycle used by one-click status buttons: not started → in progress → completed → not started. */
export const nextStatus = (status) =>
  STATUS_ORDER[(STATUS_ORDER.indexOf(status) + 1) % STATUS_ORDER.length]
