---
title: Grid view
description: Cards with a featured item, an eyebrow, an extra meta field and placeholder tiles for items without an image.
---

```list
from: features/listings/stories
view: grid
featured: 1
limit: 7
fields:
  eyebrow: category
  meta: [location]
```

## Grouped

```list
from: features/listings/stories
view: grid
group: category
limit: 6
media: none
```
