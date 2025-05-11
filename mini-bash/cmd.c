// SPDX-License-Identifier: BSD-3-Clause
#include <stdio.h>
#include <stdlib.h>
#include <string.h> 

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>

#include <fcntl.h>
#include <unistd.h>

#include "cmd.h"
#include "utils.h"

#define READ		0
#define WRITE		1

/**
 * Internal change-directory command.
 */
static bool shell_cd(word_t *dir) {
	//change directory, using get_word() to use chdir()
	//FREE get_word!!!
	//edge cases, no input -> return true
	//edge cases, no directoy -> chdir fails
	//check if not 1 arguement, fail if more or less
	int count = 0;
	word_t *p = dir;
	while (p) {
		count ++;
		p = p->next_word;
	}
	if (count != 1) {
		return true;
	}
	char *path = get_word(dir);
	if (!path) {
		return false;
	}
	if (chdir(path) != 0) {
		fprintf(stderr, "no such file or directory\n");
		free(path);
		return false;
	}
	free(path);
	return true;
}

/**
 * Internal exit/quit command.
 */
static int shell_exit(void) {
	//exit check is in main, return SHELL_EXIT from cmd.h
	return SHELL_EXIT;
}


static void redirection(simple_command_t *s) {
	//Input redirection: get infile, open, dup2
	//output redirection: > vs >>, get outfile, dup2
	//Error redirection:  &> vs 2>>, get errfile, dup2
	//Set s->io_flags
	
	//input
	if (s->in) {
		char *in_file = get_word(s->in);
		if (!in_file) {
			perror("get_word");
			exit(EXIT_FAILURE);
		}
		int file_in = open(in_file, O_RDONLY);
		if (file_in < 0) {
			perror("open input");
			free(in_file);
			exit(EXIT_FAILURE);
		}
		dup2(file_in, STDIN_FILENO);
		close(file_in);
		free(in_file);
	}
	//if &> we must check if s->err and s-> out are the same
	//if so, set them to the same file  and perform operations
	if (s->out && s->err) {
		char *out_str = get_word(s->out);
		char *err_str = get_word(s->err);
		if (out_str && err_str && strcmp(out_str, err_str) == 0) {
			int both_file = open(out_str, O_WRONLY | O_CREAT | O_TRUNC, 0644);
			if (both_file < 0) {
				perror("open");
				free(out_str);
				free(err_str);
				exit(EXIT_FAILURE);
			}
			dup2(both_file, STDOUT_FILENO);
			dup2(both_file, STDERR_FILENO);
			close(both_file);
			free(out_str);
			free(err_str);
			s->out = NULL;
			s->err = NULL;
		}
	}
	//output
	//distinguish > and >> with io_flags
	//add to flags var bitwise or
	if (s->out) {
		int flags = O_WRONLY | O_CREAT;
		if (s->io_flags == IO_OUT_APPEND) {
			flags |= O_APPEND;
		} else {
			flags |= O_TRUNC;
		}
		char *out_file = get_word(s->out);
		if (!out_file) {
			perror("get_word");
			exit(EXIT_FAILURE);
		}
		int file_out = open(out_file, flags, 0644);
		if (file_out < 0) {
			perror("open output");
			free(out_file);
			exit(EXIT_FAILURE);
		}
		dup2(file_out, STDOUT_FILENO);
		close(file_out);
		free(out_file);
	}
	//error
	//distinguish &> and 2>> with io_flags
	//add to flags var bitwise or
	if (s->err) {
                int flags = O_WRONLY | O_CREAT;
                if (s->io_flags == IO_ERR_APPEND) {
                        flags |= O_APPEND;
		} else{
                        flags |= O_TRUNC;
                }
                char *err_file = get_word(s->err);
                if (!err_file) {
                        perror("get_word");
                        exit(EXIT_FAILURE);
                }
                int file_err = open(err_file, flags, 0644);
                if (file_err < 0) {
                        perror("open error");
                        free(err_file);
                        exit(EXIT_FAILURE);
                }
                dup2(file_err, STDERR_FILENO);
                close(file_err);
                free(err_file);
        }
}

/**
 * Parse a simple command (internal, environment variable assignment,
 * external command).
 */
static int parse_simple(simple_command_t *s, int level, command_t *father) {
	//use parsed lexicons to determine what action to take
	//edge case no input string, no command (verb)
	//see structs in parser.h
	//1st, handle cd, exit, and assignment 
	if (!s ||!s->verb) {
		return 0;
	}
	//get the command from s->verb, using get_word()
	char *command = get_word(s->verb);
	if (!command) {
		return 0;
	}
	//if command has exit or quit, run shell_exit()
	if (strcmp(command, "quit") == 0) {
		free(command);
		return shell_exit();
	} 
	if (strcmp(command, "exit") == 0) {
		free(command);
		return shell_exit();
	}
	//if command has cd, run shell_cd, get path from s->params
	if (strcmp(command, "cd") == 0) {
		if (shell_cd(s->params) == true) {
			free(command);
			return 0;
		} else {
			free(command);
			return 1;
		}
	}
	//variable assignment, search for '=', if so putenv()
	char *eq_ptr = strchr(command, '=');
	if (eq_ptr != NULL) {
		putenv(command);
		return 0;
	}

	//commands with child process
	//get args
	//fork
	//redirect if child
	//execvp
	//parent wait for child
	int argc = 0;
	char **argv = get_argv(s, &argc);
	if (!argv) {
		free(command);
		return 1;
	}
	pid_t pid = fork();
	if (pid < 0) {
		perror("fork");
		free(command);
		for (int i = 0; i < argc; i ++) {
			free(argv[i]);
		}
		free(argv);
		return 1;
	}
	//child
	if (pid == 0) {
		redirection(s);
		execvp(argv[0], argv);
		perror("execvp");
		exit(EXIT_FAILURE);
	} else {
	//parent
		free(command);
		for (int i = 0; i < argc; i ++) {
			free(argv[i]);
		}
		free(argv);
		int status;
		waitpid(pid, &status, 0);
		if (WIFEXITED(status)) {
			return WEXITSTATUS(status);
		}
		return 1;
	}
}

/**
 * Process two commands in parallel, by creating two children.
 */
static bool run_in_parallel(command_t *cmd1, command_t *cmd2, int level, command_t *father) {
	//first 1 fork for cmd 1, and 1 fork for cmd 2
	//if child, parse_command
	//parents wait for children before returning
	//both results must be true for a successful return value
	
	//command 1
	pid_t pid1 = fork();
	if (pid1 < 0) {
		perror("fork cmd1");
		return false;
	}
	if (pid1 == 0) {
		int command1 = parse_command(cmd1, level + 1, father);
		exit(command1);
	}
	//command 2
	pid_t pid2 = fork();
	if (pid2 < 0) {
		perror("fork cmd2");
		return false;
	}
	if (pid2 == 0) {
		int command2 = parse_command(cmd2, level + 1, father);
		exit(command2);
	}
	//parent branch, wait for children
	int status1, status2;
	waitpid(pid1, &status1, 0);
	waitpid(pid2, &status2, 0);
	bool result1 = WIFEXITED(status1) && (WEXITSTATUS(status1) == 0);
	bool result2 = WIFEXITED(status2) && (WEXITSTATUS(status2) == 0);
	return (result1 && result2);
	
}

/**
 * Run commands by creating an anonymous pipe (cmd1 | cmd2).
 */
static int run_on_pipe(command_t *cmd1, command_t *cmd2, int level, command_t *father) {
	//create pipe
	//create array, index 0 is read, index 1 is write
	//fork twice for each command
	//child 1, copy output to write end of pipe
	//child 2, copy input to read end of pipe
	//parse both commands
	//parents wait
	int fds[2];
	if (pipe(fds) < 0) {
		perror("pipe");
		return 1;
	}
	//child 1 write
	pid_t pid1 = fork();
	if (pid1 < 0) {
		perror("fork cmd1");
		return 1;
	}
	if (pid1 == 0) {
		dup2(fds[1], STDOUT_FILENO);
		close(fds[0]);
		close(fds[1]);
		int command1 = parse_command(cmd1, level + 1, father);
		exit(command1);
	}
	//child 2 read
	pid_t pid2 = fork();
	if (pid2 < 0) {
		perror("fork cmd2");
		return 1;
	}
	if (pid2 == 0) {
                dup2(fds[0], STDIN_FILENO);
                close(fds[1]);
                close(fds[0]);
                int command2 = parse_command(cmd2, level + 1, father);
                exit(command2);
        }
	//parent branch
	close(fds[0]);
	close(fds[1]);
	int status1, status2;
        waitpid(pid1, &status1, 0);
        waitpid(pid2, &status2, 0);
        if (WIFEXITED(status2)) {
		return WEXITSTATUS(status2);
	}
	return 1;
}

/**
 * Parse and execute a command.
 */
int parse_command(command_t *c, int level, command_t *father) {
	//entry point
	//parse commands into simple parse based on input structure
	//edge case
	if (!c) {
		return 0;
	}
	//no operator
	if (c->op == OP_NONE) {
		return parse_simple(c->scmd, level, father);
	}

	switch (c->op) {
	//run commands sequentially, cmd1 then cmd2
	case OP_SEQUENTIAL: {
		parse_command(c->cmd1, level + 1, c);
	      	int command2 = parse_command(c->cmd2, level + 1, c);
		return command2;	
	}
	//run commands in parallel, at the same time
	case OP_PARALLEL: {
		if (run_in_parallel(c->cmd1, c->cmd2, level +1, c) == false) {
			return 0;
		} else {
			return 1;
		}
	}
	//run cmd2 if cmd1 results in non zero
	case OP_CONDITIONAL_NZERO: {
		int command1 = parse_command(c->cmd1, level + 1, c);
		if (command1 != 0) {
			return parse_command(c->cmd2, level + 1, c);
		} else {
			return command1;
		}
	}
	//run cmd2 if cmd1 results in zer0
	case OP_CONDITIONAL_ZERO: {
		int command1 = parse_command(c->cmd1, level + 1, c);
                if (command1 == 0) {
                        return parse_command(c->cmd2, level + 1, c);
                } else {
                        return command1;
                }
	}
	//send ouput cmd1 to input cmd2
	case OP_PIPE: {
		if (run_on_pipe(c->cmd1, c->cmd2, level +1, c) == false) {
                        return 0;
                } else {
                        return 1;
                }
	}

	default:
		return shell_exit();
	}

	return 0; 
}
