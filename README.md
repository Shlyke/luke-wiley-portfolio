# luke-wiley-portfolio

This repository showcases several systems-level and course-driven programming projects developed as part of my Computer Science coursework at Penn State. Projects span topics such as memory allocation, shell implementation, and inter-thread communication, all built in C with a focus on low-level control and performance.

---

## Projects

### [malloc-allocator](./malloc-allocator)

**Custom malloc/free/realloc/calloc implementation in C**  
Implements a dynamic memory allocator using segregated free lists, block splitting, and coalescing. Includes a `Makefile` and trace-based test suite via `mdriver`.

- Language: C
- Highlights: `malloc`, `free`, `realloc`, coalescing, `mm_checkheap`
- Build/Test: `make`, `make test`
- [See full README](./malloc-allocator/README.md)

---

### [mini-bash](./mini-bash)

**A lightweight Bash-style shell written in C**  
Supports built-in commands (`cd`, `exit`), pipes (`|`), redirection (`>`, `<`, etc.), parallel & conditional execution (`&&`, `||`, `&`, `;`), and parsing with Flex/Bison.

- Language: C with Flex/Bison
- Highlights: AST parsing, I/O redirection, process control, environment variable expansion
- Build: `make` → Run: `./shell`
- [See full README](./mini-bash/README.md)

---

### [channel-ipc](./channel-ipc)

**Thread-safe inter-process communication system**  
Implements a blocking and non-blocking message-passing channel using `pthread_mutex` and `pthread_cond`. Suitable for concurrent systems and producer-consumer models.

- Language: C (POSIX threads)
- Highlights: Blocking queues, condition variables, `channel_send`, `channel_receive`, `channel_close`, `channel_destroy`
- Build/Test: `make`, `./channel test_case`, `./channel_sanitize`
- [See full README](./channel-ipc/README.md)

---

## Technologies Used

- C (GCC), POSIX Threads
- Flex/Bison for parser generation
- Makefiles for build automation
- Git + GitHub for version control
- Valgrind & Sanitizers for memory and race detection

---

## Contact

**Luke Wiley**  
Computer Science @ Penn State  
Email: lmw6194@psu.edu  
GitHub: [Shlyke](https://github.com/Shlyke)