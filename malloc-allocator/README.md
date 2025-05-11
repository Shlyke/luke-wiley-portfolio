# Malloc Allocator

A fully custom dynamic memory allocator for C programs implementing `malloc`, `free`, `realloc`, and `calloc`, along with a heap consistency checker.  
Developed for CMPSC 473: Operating Systems at Penn State.

## Features

- Segregated free list design with separate bins for small, medium, and large blocks
- Coalescing of adjacent free blocks (partial functionality)
- Block splitting to minimize fragmentation
- 16-byte alignment of all allocated memory
- Basic heap consistency checker via `mm_checkheap()`
- Custom `calloc` and support for `memcpy`, `memset`

## Implemented Functions

- `bool mm_init(void)` – Initializes heap with a prologue, epilogue, and initial free block
- `void* malloc(size_t size)` – Allocates a memory block with at least `size` bytes
- `void free(void* ptr)` – Frees a previously allocated memory block
- `void* realloc(void* ptr, size_t size)` – Resizes a memory block, preserving contents
- `void* calloc(size_t nmemb, size_t size)` – Allocates and zeroes a memory block
- `bool mm_checkheap(int line_number)` – Placeholder for a heap consistency checker

## File Structure

- `mm.c` – Core allocator implementation (your main contribution)
- `mm.h` – Function declarations
- `memlib.c`, `memlib.h` – Simulated memory system used by test driver
- `mdriver.c` – Test driver for correctness and performance (trace-based)
- `config.h` – Configuration for test framework
- `Makefile` – Build automation
- `traces/` – Directory containing trace files for automated testing

## How to Build and Run

```bash
make            # Build the allocator and test driver
make test       # Run all trace-based tests
./mdriver -f traces/xyz.rep   # Run specific trace file
./mdriver -h    # List test options
