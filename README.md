# luke-wiley-portfolio

This repository showcases programming projects developed as part of my Computer Science Degree at Penn State. Projects span systems programming, artificial intelligence, machine learning, data mining, databases, and programming language implementation, primarily in C and Python with a focus on algorithms, software engineering, and low-level systems.

---

## Database Management

### [Nittany Auction Database](./NittanyAuction-database-management)

**Relational database application for online auctions**  
Implements a database-driven auction system with SQL queries, data management, and transaction processing.

- Language: Python / SQL
- Highlights: Relational databases, SQL, data management
- [See full README](./NittanyAuction-database-management/README.md)

---

## Data Analysis Mining

### [Credit Card Data Risk Prediction and Analysis](./credit-card-data-analysis)

**Exploratory data analysis and feature selection**  
Performs data cleaning, visualization, feature engineering, and classification analysis on a real-world credit card dataset.

- Language: Python
- Highlights: pandas, scikit-learn, feature selection, EDA
- [See full README](./credit-card-data-analysis/README.md)

---

### [Credit Card Data Clustering With Machine Learning](./credit-card-kmeans-clustering)

**Unsupervised learning and clustering algorithms**  
Implements K-Means and Bisecting K-Means clustering with PCA-based dimensionality reduction and cluster evaluation.

- Language: Python
- Highlights: K-Means, Bisecting K-Means, PCA, clustering
- [See full README](./credit-card-kmeans-clustering/README.md)

---

## Systems Programming

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

- Language: C (POSIX Threads)
- Highlights: Blocking queues, condition variables, `channel_send`, `channel_receive`, `channel_close`, `channel_destroy`
- Build/Test: `make`, `./channel test_case`, `./channel_sanitize`
- [See full README](./channel-ipc/README.md)

---

### [python-parser](./python-parser)

**Lexer, parser, and type checker for a toy language written in Python**  
Implements an AST-based parser with scope-aware symbol tables, custom grammar definitions, and type mismatch detection. Includes a test suite for validation.

- Language: Python
- Highlights: Tokenization, recursive descent parsing, semantic analysis, AST construction
- Run Tests: `python verify.py`
- [See full README](./python-parser/README.md)

---

## Artificial Intelligence

### [River Crossing Search Algorithms](./AI-projects/RiverCrossingProject)

**Classical AI search algorithms implemented from scratch**  
Solves the Missionaries and Cannibals river crossing problem using DFS, BFS, Uniform Cost Search, and A* Search with custom admissible heuristics.

- Language: Python
- Highlights: DFS, BFS, UCS, A*, heuristic search, state-space search
- Run: `python solution_q1.py`, `python solution_q2.py`, `python solution_q3.py`
- [See full README](./AI-projects/RiverCrossingProject/README.md)

---

### [Reinforcement Learning](./AI-projects/Q-learning%20Project)

**Model-free and model-based reinforcement learning algorithms**  
Implements Q-Learning for Blackjack and Value Iteration with policy extraction for FrozenLake using Gymnasium.

- Language: Python
- Highlights: Q-Learning, Value Iteration, Policy Extraction, MDPs, Gymnasium
- Run: `python solution_q1.py`, `python solution_q2.py`
- [See full README](./AI-projects/Q-learning%20Project/README.md)

---

### [Bayesian Networks](./AI-projects/BayesianNets)

**Probabilistic inference and Naive Bayes classification**  
Implements Variable Elimination for Bayesian Networks and a Naive Bayes classifier for diabetes prediction.

- Language: Python
- Highlights: Bayesian Networks, Variable Elimination, Naive Bayes, probabilistic inference
- Run: `python solution_q1.py`, `python solution_q2.py`
- [See full README](./AI-projects/BayesianNets/README.md)

---


## Technologies Used

### Languages

- C
- Python
- SQL

### Systems & Tools

- POSIX Threads
- Flex/Bison
- Make
- Git & GitHub
- Valgrind
- AddressSanitizer

### Libraries

- pandas
- NumPy
- scikit-learn
- Gymnasium
- Matplotlib
- Jupyter Notebook

---

## Contact

**Luke Wiley**  

Email: luke.w.2469@gmail.com

GitHub: https://github.com/Shlyke
