---
title: "Dynamic Array from Scratch (how Python's list works)"
area: dsa
tags: [data-structures, dynamic-array, amortized-analysis, python, build-from-scratch]
source: "pasted LLM explanation, extended with own additions"
created: 2026-07-12
updated: 2026-07-12
status: seed
---

# Dynamic Array from Scratch (how Python's list works)

## TL;DR
A Python `list` is a **dynamic array**: a fixed-size block of memory (`capacity`) that tracks how many slots are actually used (`size`). When an append finds the block full, it allocates a new block ~2x bigger and copies everything over. Doubling makes the occasional expensive copy rare enough that append is **amortized O(1)**. Insert/delete anywhere but the end are O(n) because elements must shift.

## How it works
Two numbers drive everything:

- `size` — how many items are stored (what `len()` reports).
- `capacity` — how many slots the underlying block has. Invariant: `size <= capacity`.

```
append("C") into a full block (capacity 2):

  old block (cap 2):  [A][B]        <- full, size == capacity
  new block (cap 4):  [A][B][C][ ]  <- allocate 2x, copy, then place C
```

Full implementation with the complete method set — grow on append, shift on insert/delete, shrink when mostly empty:

```python
class DynamicArray:
    def __init__(self):
        self.capacity = 2
        self.size = 0
        self.memory = [None] * self.capacity   # simulates a raw fixed block

    # -- internal ---------------------------------------------------------
    def _resize(self, new_capacity):
        new_memory = [None] * new_capacity
        for i in range(self.size):
            new_memory[i] = self.memory[i]
        self.memory = new_memory
        self.capacity = new_capacity

    def _check_index(self, index):
        if index < 0 or index >= self.size:
            raise IndexError(f"index {index} out of range for size {self.size}")

    # -- core operations ---------------------------------------------------
    def append(self, item):                    # amortized O(1)
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        self.memory[self.size] = item
        self.size += 1

    def insert(self, index, item):             # O(n): shift right
        if index < 0 or index > self.size:     # inserting AT size is legal
            raise IndexError(f"index {index} out of range for size {self.size}")
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        for i in range(self.size, index, -1):  # walk backwards to not overwrite
            self.memory[i] = self.memory[i - 1]
        self.memory[index] = item
        self.size += 1

    def delete(self, index):                   # O(n): shift left, returns item
        self._check_index(index)
        item = self.memory[index]
        for i in range(index, self.size - 1):
            self.memory[i] = self.memory[i + 1]
        self.size -= 1
        self.memory[self.size] = None          # don't hold a stale reference
        if 0 < self.size <= self.capacity // 4:  # shrink at 1/4, not 1/2
            self._resize(self.capacity // 2)
        return item

    def pop(self):                             # amortized O(1)
        return self.delete(self.size - 1)

    # -- dunders: make it feel like a real list ----------------------------
    def __getitem__(self, index):              # arr[i]
        self._check_index(index)
        return self.memory[index]

    def __setitem__(self, index, item):        # arr[i] = x
        self._check_index(index)
        self.memory[index] = item

    def __len__(self):                         # len(arr)
        return self.size

    def __contains__(self, item):              # x in arr — O(n) scan
        return any(self.memory[i] == item for i in range(self.size))

    def __repr__(self):
        items = ", ".join(repr(self.memory[i]) for i in range(self.size))
        return f"DynamicArray([{items}], size={self.size}, cap={self.capacity})"
```

## Why it's designed this way
- **Why double instead of growing by a fixed amount?** Growing by +k means a copy every k appends → n appends cost O(n²/k) total. Doubling means copies happen at sizes 2, 4, 8, … so n appends copy at most 2n elements total → **O(1) amortized** per append. Any constant factor > 1 works; CPython actually grows by ~1.125x to trade a few extra copies for less wasted memory.
- **Why shrink at 1/4 full instead of 1/2?** If you shrink the moment you drop below half, an append/delete sequence sitting exactly at the boundary would resize on *every* operation (thrashing). Shrinking at 1/4 to half-capacity leaves slack in both directions.
- **The rejected alternative — linked list** — gives O(1) insert/delete at a known node but loses O(1) random access and cache locality. Arrays win by default; that's why `list`, Java's `ArrayList`, C++'s `vector`, and Go slices are all dynamic arrays.

## Gotchas & edge cases
- **`size` vs `capacity` confusion** is the classic bug: iterate/print over `size` slots only; the slots beyond it are garbage (here, `None`).
- **Shift direction matters.** Insert shifts right *walking backwards*; delete shifts left walking forwards. Walking the wrong way overwrites the values you still need.
- **`insert` at `index == size` is legal** (it's an append); `get`/`delete` at `size` is not. Off-by-one central.
- **Raise `IndexError`, don't return an error string** — returning `"Error: ..."` (as the original clipping did) makes the error look like a stored value.
- **Clear the vacated slot on delete** — in a GC'd language a stale reference in `memory[size]` keeps the object alive (loitering).
- Appends are amortized O(1), but an *individual* append that triggers a resize is O(n) — relevant in latency-sensitive paths.

## Reusable skeleton for future from-scratch builds
Every structure in this build-from-scratch series follows the same shape, so notes and code stay comparable:

1. **State + invariant** — the instance variables and the one sentence that must always hold (here: `size <= capacity`; for a BST: left < node < right).
2. **Internal helpers** — underscore-prefixed maintenance ops the user never calls (`_resize`; later: `_rebalance`, `_sift_up`).
3. **Core operations** — each annotated with its complexity in a comment.
4. **Dunders last** — `__len__`, `__getitem__`, `__contains__`, `__repr__` so the structure behaves like a builtin.
5. **A `if __name__ == "__main__":` demo** that exercises every public method and prints internal state, so running the file *shows* the mechanism:

```python
if __name__ == "__main__":
    arr = DynamicArray()
    for fruit in ["Apple", "Banana", "Cherry", "Date", "Elderberry"]:
        arr.append(fruit)
        print(f"after append({fruit!r}): {arr!r}")   # watch cap: 2 -> 4 -> 8

    arr.insert(1, "Blueberry")
    print("after insert(1):", arr)
    print("deleted:", arr.delete(0), "->", arr)
    print("popped: ", arr.pop(), "->", arr)
    print("len:", len(arr), "| 'Cherry' in arr:", "Cherry" in arr)
    while len(arr) > 1:
        arr.pop()                                     # watch capacity shrink
    print("after draining:", arr)
```

## Where it shows up
- Python `list`, Java `ArrayList`, C++ `std::vector`, Go slices — all this exact mechanism.
- Interview staples: "implement ArrayList", "why is append amortized O(1)?", amortized analysis as a topic.
- Foundation for later builds: a stack is a dynamic array restricted to `append`/`pop`; a binary heap is a dynamic array plus sift operations; hash tables use the same resize-and-rehash idea.

## Related notes
- (none yet — first data-structure build; future stack / heap / hash-table notes should link back here)

## Open questions
- How does CPython's actual `list` over-allocation formula (`new_allocated = size + (size >> 3) + 6`) behave vs plain doubling for small lists?
- When does the O(n) resize pause matter in practice (e.g. real-time systems), and how do deques/segmented arrays avoid it?
