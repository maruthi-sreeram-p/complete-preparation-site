import { describe, expect, it } from 'vitest'
import {
  addCustom,
  emptyPractice,
  isDone,
  overallStats,
  removeCustom,
  resolveLink,
  sanitizePractice,
  setAnswer,
  setDone,
  subjectStats,
} from './state.js'

const subject = { id: 's', questions: [{ id: 'q1' }, { id: 'q2' }, { id: 'q3' }, { id: 'q4' }] }

describe('done and answers', () => {
  it('marks and unmarks a question', () => {
    let s = setDone(emptyPractice(), 'q1', true, 5)
    expect(isDone(s, 'q1')).toBe(true)
    s = setDone(s, 'q1', false)
    expect(isDone(s, 'q1')).toBe(false)
  })

  it('an empty answer removes the entry', () => {
    let s = setAnswer(emptyPractice(), 'q1', 'SELECT 1')
    expect(s.answers).toEqual({ q1: 'SELECT 1' })
    s = setAnswer(s, 'q1', '')
    expect(s.answers).toEqual({})
  })
})

describe('resolveLink', () => {
  it('keeps URLs, expands a bare LeetCode number and gives up on anything it cannot place', () => {
    expect(resolveLink('Other', 'https://example.com/p/1')).toBe('https://example.com/p/1')
    expect(resolveLink('LeetCode', '128')).toBe('https://leetcode.com/problemset/?search=128')
    expect(resolveLink('GeeksforGeeks', 'kadane algorithm')).toBe('https://www.google.com/search?q=site%3Ageeksforgeeks.org%20kadane%20algorithm')
    expect(resolveLink('Other', '128')).toBeNull()
    expect(resolveLink('LeetCode', '   ')).toBeNull()
  })
})

describe('custom items', () => {
  it('adds an item that counts towards the subject and removes it with its done mark', () => {
    let s = addCustom(emptyPractice(), 's', { title: 'My problem', platform: 'LeetCode', link: '128' }, 'c1', 9)
    expect(s.custom.s).toHaveLength(1)
    s = setDone(setDone(s, 'q1', true), 'c1', true)
    expect(subjectStats(subject, s)).toEqual({ total: 5, done: 2, percent: 40 })
    s = removeCustom(s, 's', 'c1')
    expect(s.custom).toEqual({})
    expect(isDone(s, 'c1')).toBe(false)
    expect(subjectStats(subject, s).total).toBe(4)
  })

  it('ignores input that cannot become a link', () => {
    const s = emptyPractice()
    expect(addCustom(s, 's', { title: 'x', platform: 'Other', link: '128' }, 'c1')).toBe(s)
  })

  it('names an untitled problem from its number, or else from its link', () => {
    expect(addCustom(emptyPractice(), 's', { title: '', platform: 'LeetCode', link: '128' }, 'c1').custom.s[0].title).toBe('LeetCode #128')
  })

  it('uses the link as the title when none is given', () => {
    const s = addCustom(emptyPractice(), 's', { title: '', platform: 'Other', link: 'https://x.dev/a' }, 'c1')
    expect(s.custom.s[0].title).toBe('https://x.dev/a')
  })
})

describe('stats and sanitising', () => {
  it('adds up across subjects', () => {
    const s = setDone(emptyPractice(), 'q1', true)
    expect(overallStats([subject, { id: 't', questions: [{ id: 'z' }] }], s)).toEqual({ total: 5, done: 1, percent: 20 })
  })

  it('repairs whatever storage returns', () => {
    expect(sanitizePractice('garbage')).toEqual(emptyPractice())
    const s = sanitizePractice({
      done: { a: 1, b: 'x' },
      answers: { a: 'ok', b: '', c: 3 },
      custom: { s: [{ id: 'i', title: 't', url: 'u', platform: 'Nope' }, { id: 1 }] },
    })
    expect(s.done).toEqual({ a: 1 })
    expect(s.answers).toEqual({ a: 'ok' })
    expect(s.custom.s).toEqual([{ id: 'i', title: 't', url: 'u', platform: 'Other', addedAt: 0 }])
  })
})
