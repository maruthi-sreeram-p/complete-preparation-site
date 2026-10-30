import { describe, expect, it } from 'vitest'
import { expandInlineListings, formatListing, isListing } from './prettyCode.js'

describe('formatListing', () => {
  it('lays out classes and statements over indented lines', () => {
    const code = 'class A { A() { System.out.print("A"); } } class B extends A { B() { System.out.print("B"); } } new B();'
    expect(formatListing(code)).toBe(
      [
        'class A {',
        '    A() {',
        '        System.out.print("A");',
        '    }',
        '}',
        'class B extends A {',
        '    B() {',
        '        System.out.print("B");',
        '    }',
        '}',
        'new B();',
      ].join('\n'),
    )
  })

  it('keeps for headers, empty bodies, initialisers and strings on one line', () => {
    expect(formatListing('class P { P(int x) {} } class C extends P { }')).toBe(
      ['class P {', '    P(int x) {}', '}', 'class C extends P { }'].join('\n'),
    )
    expect(formatListing('for (int i = 0; i < 3; i++) { run(i); }')).toBe(
      ['for (int i = 0; i < 3; i++) {', '    run(i);', '}'].join('\n'),
    )
    expect(formatListing('int[] a = {1, 2}; String s = "a;b{";')).toBe(['int[] a = {1, 2};', 'String s = "a;b{";'].join('\n'))
  })

  it('keeps else on the closing brace line', () => {
    expect(formatListing('if (a) { b(); } else { c(); }')).toBe(
      ['if (a) {', '    b();', '} else {', '    c();', '}'].join('\n'),
    )
  })
})

describe('expandInlineListings', () => {
  it('leaves short inline code in the sentence', () => {
    const text = 'Why is `class Stack extends ArrayList` bad? Use `int x = 1;` here.'
    expect(isListing('class Stack extends ArrayList')).toBe(false)
    expect(expandInlineListings(text)).toBe(text)
  })

  it('moves a listing into a code block, joining spans split by a line break', () => {
    const out = expandInlineListings('What does this print? `class A { A() { f(); }` `} new A();` Explain.')
    expect(out).toContain('What does this print?\n\n```java\nclass A {\n    A() {\n        f();\n    }\n}\nnew A();\n```\n\nExplain.')
  })

  it('indents the block inside a list item and leaves fences alone', () => {
    expect(expandInlineListings('1. Run `alpha(); beta(); gamma(); delta();`')).toContain('1. Run\n\n   ```\n   alpha();')
    const fenced = '```\n`alpha(); beta(); gamma(); delta();`\n```'
    expect(expandInlineListings(fenced)).toBe(fenced)
  })
})
