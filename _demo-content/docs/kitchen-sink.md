---
title: Kitchen Sink
description: One page exercising the full range of Markdown syntax, for theme testing.
---

# Heading level 1

## Heading level 2

### Heading level 3

#### Heading level 4

##### Heading level 5

###### Heading level 6

A paragraph with **bold text**, _italic text_, ~~strikethrough~~, and `inline code`. Here's a [link to the Flowershow site](https://flowershow.app) and a footnote reference.[^1]

[^1]: This is the footnote content.

## Lists

- Unordered item one
- Unordered item two
  - Nested item
  - Another nested item
- Unordered item three

1. Ordered item one
2. Ordered item two
   1. Nested ordered item
3. Ordered item three

- [ ] An unchecked task
- [x] A checked task

## Blockquote

> A blockquote spanning
> multiple lines, to check quote styling.
>
> With a second paragraph inside it.

## Code

Inline `code` in a sentence.

```js
function greet(name) {
  // a comment, to check syntax highlighting
  return `Hello, ${name}!`;
}
```

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

## Table

| Feature      | Supported | Notes                  |
| ------------ | :-------: | ----------------------- |
| Callouts     |    Yes    | See below                |
| Footnotes    |    Yes    | See reference above       |
| Tables       |    Yes    | This one                |
| Math         |    Maybe  | Theme-dependent          |

## Callouts

> [!note]
> This is a note callout.

> [!tip]
> This is a tip callout.

> [!warning]
> This is a warning callout.

> [!danger]
> This is a danger callout.

> [!success]
> This is a success callout.

> [!example]
> This is an example callout.

> [!quote]
> This is a quote-style callout.

## Image

![An abstract test card for the theme image surface](/assets/demo-image.svg)

## Horizontal rule

---

Text after a horizontal rule, to check spacing.
