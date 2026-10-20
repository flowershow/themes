---
title: Empty and broken lists
description: What a list looks like when its folder has nothing to show, and when the block has mistakes.
---

## Nothing to list

The `drafts` folder only holds a draft, so this list is empty:

```list
from: features/listings/drafts
```

## A block with problems

This block names a folder that doesn't exist and uses a wrong key, so it renders the error card:

```list
from: no-such-folder
perPage: 3
```
