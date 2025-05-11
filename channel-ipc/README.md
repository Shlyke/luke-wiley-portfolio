# Channel IPC

A thread-safe channel system in C for inter-thread communication via message-passing.  
Implements both blocking and non-blocking send/receive operations using `pthread_mutex`, `pthread_cond`, and a circular buffer.  
Developed for CMPSC 473: Operating Systems at Penn State.

---

## Features

- Blocking and non-blocking `send` and `receive` functions
- Graceful `close()` and `destroy()` channel lifecycle management
- Support for multiple concurrent senders and receivers
- Optional `channel_select` function for advanced multiplexing (bonus)

---

## Key Concepts

- Channels consist of a queue (`buffer_t*`) with fixed capacity
- Blocking functions use `pthread_cond_wait()` to suspend until ready
- `channel_close()` wakes all waiting threads and prevents further sends/receives
- `channel_destroy()` safely frees resources after channel closure
- Mutex and condition variables protect shared state without polling or sleep

---

## File Overview

- `channel.c` – Core implementation of all channel operations (your main work)
- `channel.h` – Interface and type definitions
- `buffer.c` / `buffer.h` – Provided helper code for circular buffer (not thread-safe)
- `linked_list.c` / `linked_list.h` – Optional helper structures (not used in this solution)
- `Makefile` – Builds test runners and sanitizer version
- `test.c` – Instructor-provided test cases

---

## How to Build and Test

```bash
make           # Builds the normal and sanitizer versions
make test      # Runs all test cases using grade.py
