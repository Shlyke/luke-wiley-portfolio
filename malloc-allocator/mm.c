/*
 * mm.c
 *
 * Name: Luke Wiley
 *
 * NOTE TO STUDENTS: Replace this header comment with your own header
 * comment that gives a high level description of your solution.
 * Also, read the README carefully and in its entirety before beginning.
 *
 */
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>

#include "mm.h"
#include "memlib.h"

/*
 * If you want to enable your debugging output and heap checker code,
 * uncomment the following line. Be sure not to have debugging enabled
 * in your final submission.
 */
// #define DEBUG

#ifdef DEBUG
// When debugging is enabled, the underlying functions get called
#define dbg_printf(...) printf(__VA_ARGS__)
#define dbg_assert(...) assert(__VA_ARGS__)
#else
// When debugging is disabled, no code gets generated
#define dbg_printf(...)
#define dbg_assert(...)
#endif // DEBUG

// do not change the following!
#ifdef DRIVER
// create aliases for driver tests
#define malloc mm_malloc
#define free mm_free
#define realloc mm_realloc
#define calloc mm_calloc
#define memset mm_memset
#define memcpy mm_memcpy
#endif // DRIVER

#define ALIGNMENT 16
#define NUM_LISTS 7

//globals and constants
static char* hlst_ptr = NULL; //heap list pointer
//static char* free_list_ptr = NULL; //free list pointer
static char* seg_lists[NUM_LISTS]; //segregated approach

//helper functions
static size_t get_size(void* ptr) {
	uint64_t value = *(uint64_t*)((char*)ptr - 8);
	return value & ~(uint64_t)0xF;
}

static bool get_alloc(void* ptr) {
	uint64_t value = *(uint64_t*)((char*)ptr - 8);
	return (value & 0x1) != 0;
}

static void* get_prev(void* ptr) {
	return *(void**)ptr;
}

static void* get_next(void* ptr) {
	return *(void**)((char*)ptr + 8);
}

static void set_size(void* ptr, size_t size) {
	uint64_t old_size = *(uint64_t*)((char*)ptr - 8);
	bool alloc = (old_size & 0x1) != 0;
	uint64_t value = ((uint64_t)size & ~(uint64_t)0xF)|(alloc ? 1ULL : 0ULL);
	*(uint64_t*)((char*)ptr - 8) = value;
	if (size >= 16) {
		*(uint64_t*)((char*)ptr + size - 16) =value;
	}
}

static void set_alloc(void* ptr, bool alloc) {
	uint64_t old_header = *(uint64_t*)((char*)ptr - 8);
        uint64_t old_size = (old_header & ~(uint64_t)0xF);
        uint64_t value = old_size | (alloc ? 1ULL : 0ULL);
        *(uint64_t*)((char*)ptr - 8) = value;
	if (old_size >= 16) {
		*(uint64_t*)((char*)ptr + old_size - 16)= value;
	}
}

static void set_prev(void* ptr, void* prev_ptr) {
	*(void**)ptr = prev_ptr;
}

static void set_next(void* ptr, void* next_ptr) {
//	printf("[set_next] ptr=%p => next=%p\n", ptr, next_ptr);
	*(void**)((char*)ptr + 8) = next_ptr;
}

// rounds up to the nearest multiple of ALIGNMENT
static size_t align(size_t x)
{
    return ALIGNMENT * ((x+ALIGNMENT-1)/ALIGNMENT);
}

static int get_list(size_t size) {
	if (size <= 32) { return 0;}
	if (size <= 64) { return 1;}
	if (size <= 128) { return 2;}
	if (size <= 256) { return 3;}
	if (size <= 512) { return 4;}
	if (size <= 1024) { return 5;}
	return 6;
}

static void insert_block(void* ptr) {
        //insert to begining of list
        size_t size = get_size(ptr);
        char* head = seg_lists[ get_list(size)];
        set_next(ptr, head);
        set_prev(ptr, NULL);
        if (head != NULL) {
                set_prev(head, ptr);
        }
        head = ptr;
}

static void* extend_heap(size_t size)
{
	size_t space = size + 16;
        if (space % 16 != 0) {
                space += (16 - (space % 16));
        }

        //min block size
        if (space < 32) {
                space = 32;
        }

	//mm_sbrk
	char* ptr = mm_sbrk(space);
	if (ptr == (void*)-1) {
		return NULL;
	}
	//init block
	set_size(ptr, space);
	set_alloc(ptr, false);
	insert_block(ptr);
	

	//epilogue
	*(uint64_t*)((char*)ptr + space - 8) = 0x1;
	return ptr;
}

static void remove_block(void* ptr) {
	size_t size = get_size(ptr);
	int index = get_list(size);
	void* prev = get_prev(ptr);
	void* next = get_next(ptr);
	//check prev
	if (prev != NULL) {
		set_next(prev, next);
	} else {
		seg_lists[index] = next;
	}
	//check next
	if (next != NULL) {
		set_prev(next, prev);
	}
	set_prev(ptr, NULL);
	set_next(ptr,NULL);
}

/*
 * Returns whether the pointer is in the heap.
 * May be useful for debugging.
 */
static bool in_heap(const void* p)
{
    return p <= mm_heap_hi() && p >= mm_heap_lo();
}

/*
 * Returns whether the pointer is aligned.
 * May be useful for debugging.
 */
static bool aligned(const void* p)
{
    size_t ip = (size_t) p;
    return align(ip) == ip;
}
	

/*
 * mm_init: returns false on error, true on success.
 */
bool mm_init(void)
{
	//create initial heap space
	//16 for prologue header & footer
	//8 for epilogue header
	//8 for padding
	//make sure mm_sbrk success
	if ((hlst_ptr = mm_sbrk(32)) == (void*)-1) {
		return false;
	}
	hlst_ptr += 8;

	//Alignment padding, for 16 byte allignment
	

	//prologue header, store size & alloc bit
	*(uint64_t*)(hlst_ptr + 0) = 0x11; //16 size, 1 alloc 

	//prologue footer, same as header
	*(uint64_t*)(hlst_ptr + 8) = 0x11;

	//epilogue header, set size to 0
	*(uint64_t*)(hlst_ptr + 16) = 0x1;

	for (int i=0; i < NUM_LISTS; i++) {
		seg_lists[i] = NULL;
	}

	//extend heap
	if (extend_heap(1024) == NULL) {
		return false;
	}

	return true;
}

/*
 * malloc
 */
void* malloc(size_t size)
{
	//check 0 lenght
	if (size == 0) {
		return NULL;
	}

	//adjust size for easy 16 base + header/footer
	size_t space = size + 16;
	if (space % 16 != 0) {
		space += (16 - (space % 16));
	}

	//min block size
	if (space < 32) {
		space = 32;
	}

	//search for block
	//find size of block, iterate through closest fit list
	//if none found, move to larger list
	//split after
	int list = get_list(space);

	//iterate through lowest sutible list, then if not found advance lists
	char* free_block = NULL;
	for (int i = list; i < NUM_LISTS; i++) {
		free_block = seg_lists[i];
		while (free_block != NULL) {
			size_t block_size = get_size(free_block);
			if (block_size >= space) {
				break; //no return split later
			}
			free_block = get_next(free_block);
		}
		if (free_block != NULL) {
			break;
		}
	}
	//if there is no free block, mm_sbrk
	if (free_block == NULL) {
		//make new_size large for less mm_sbrk calls and more splitting
		size_t new_size = (space > 4096) ? space : 4096;
		free_block = extend_heap(new_size);
		if (free_block == NULL) {
			return NULL;
		}
	}

	//remove block from free list
	remove_block(free_block);
//	printf("[malloc] Allocating block at %p, block_size=%zu, needed=%zu\n", (void*)temp_free_ptr, (size_t)get_size(temp_free_ptr), (size_t)space);

	//split logic
	size_t needed_size = get_size(free_block);
	if ((needed_size - space) >= 32) {
		//create and init new block
		set_size(free_block, space);
		set_alloc(free_block, true);
		char* leftover_ptr = free_block + space;
		size_t leftover = needed_size - space;
		set_size(leftover_ptr, leftover);
		set_alloc(leftover_ptr, false);

//		printf("[malloc] leftover block at %p, leftover_size=%zu\n", (void*)leftover_ptr, (size_t)get_size(leftover_ptr));

		set_prev(leftover_ptr, NULL);
		set_next(leftover_ptr, false);
		insert_block(leftover_ptr);

//		printf("[malloc] Setting block %p allocated, final size=%zu\n", (void*)temp_free_ptr, (size_t)get_size(temp_free_ptr));


	} else {
		set_alloc(free_block, true);
	}

	return free_block;
}


static void* coalesce(void* ptr)
{
//	printf("[coalesce] called with ptr=%p, block_size=%zu\n", ptr, (size_t)get_size(ptr));
	if (ptr == NULL) {
		return NULL;
	}
	if (!in_heap(ptr) || !aligned(ptr)) {
		return ptr;
	}
	
	size_t size = get_size(ptr);
	char* temp_ptr = (char*)ptr - 8;
	
	//check prev block
	bool prev_alloc;
	if ((temp_ptr - 8) < ((char*)mm_heap_lo() + 8) || !in_heap(temp_ptr - 16)) {
		prev_alloc = true;
	} else { uint64_t prev_footer = *(uint64_t*)(temp_ptr - 16);
		prev_alloc = (prev_footer & 0x1) != 0;
	}

	//check next block
	char* next_header = temp_ptr + size;
	bool next_alloc;
	if (!in_heap(next_header) || (next_header + 8) >(char*) mm_heap_hi()) {
		next_alloc = true;
	} else {
		next_alloc = ((*(uint64_t*)next_header) & 0x1)!=0;
	}
	

	//check 4 cases, do proper merger, insert into correct list
	if (prev_alloc && next_alloc) {
		return ptr;
	}
	else if (prev_alloc && !next_alloc) {
		char* next_ptr = next_header + 8;
		if (in_heap(next_ptr)) {
			remove_block(next_ptr);
			size_t next_size = get_size(next_ptr);
			size += next_size;
			set_size(ptr, size);
			set_alloc(ptr, false);
		}
		return ptr;
	}
	else if (!prev_alloc && next_alloc) {
		uint64_t prev_footer = *(uint64_t*)(temp_ptr -16);
		size_t prev_size = prev_footer & ~(uint64_t)0xF;
		char* prev_ptr = temp_ptr - prev_size;
		if (in_heap(prev_ptr)) {
			remove_block(prev_ptr);
			size += prev_size;
			set_size(prev_ptr, size);
			set_alloc(prev_ptr, false);
			ptr = prev_ptr;
		}
		return ptr;
	}
	else {
		uint64_t prev_footer = *(uint64_t*)(temp_ptr -16);
                size_t prev_size = prev_footer & ~(uint64_t)0xF;
                char* prev_ptr = temp_ptr - prev_size;
		char*next_ptr = next_header + 8;
		if (in_heap(prev_ptr)) {
			remove_block(prev_ptr);
		}
		if (in_heap(next_ptr)) {
			remove_block(next_ptr);
		}
		size_t next_size = get_size(next_ptr);
                size += next_size + prev_size;
                set_size(prev_ptr, size);
                set_alloc(prev_ptr, false);
		ptr = prev_ptr;
		return ptr;
	}
	return ptr;
}

/*
 * free
 */
void free(void* ptr)
{
	//check NULL ptr
	if (ptr == NULL) {
		return;
	}

	//Free block
	uint64_t old_header = *(uint64_t*)((char*)ptr - 8);
	size_t block_size = old_header & ~(uint64_t)0xF;

	//set alloc bits to 0
	*(uint64_t*)((char*)ptr - 8) = block_size;
	*(uint64_t*)((char*)ptr + block_size - 16) = block_size;

	//coalesce if able
//	printf("[free] freeing ptr=%p, block_size=%zu\n", ptr, (size_t)block_size);
//	ptr = coalesce(ptr);

	insert_block(ptr);
}

/*
 * realloc
 */
void* realloc(void* oldptr, size_t size)
{
	//check NULL ptr
	if (oldptr == NULL) {
		return malloc(size);
	}

	//check NULL 0 size
	if (size == 0) {
		free(oldptr);
		return NULL;
	}

	//make base 16 size & add footer/header
	size_t space = size + 16;
	if (space % 16 != 0) {
		space += (16 - (space % 16));
	}

	if (space < 32) {
		space = 32;
	}

	//check if space fits in current block
	size_t block_size = get_size(oldptr);
	if (block_size >= space) {
		//not calling malloc, therefore implement split
		size_t leftover = block_size - space;
		if (leftover >= 32) {
			set_size(oldptr, space);
			set_alloc(oldptr, true);
			char* leftover_ptr = (char*)oldptr + space;
			set_size(leftover_ptr, leftover);
			set_alloc(leftover_ptr, false);
			set_prev(leftover_ptr, NULL);
			set_next(leftover_ptr, NULL);
			insert_block(leftover_ptr);
		}
		return oldptr;
	} else {

	//else, malloc new ptr, copy data to here
	void* new_ptr = malloc(size);
	if (new_ptr == NULL) {
		return NULL;
	}

	size_t data = block_size - 16;
	if (size < data) {
		data = size;
	}
	memcpy(new_ptr, oldptr, data);
	free(oldptr);
	return new_ptr;
	}
}

/*
 * calloc
 * This function is not tested by mdriver, and has been implemented for you.
 */
void* calloc(size_t nmemb, size_t size)
{
    void* ptr;
    size *= nmemb;
    ptr = malloc(size);
    if (ptr) {
        memset(ptr, 0, size);
    }
    return ptr;
}

/*
 * Returns whether the pointer is in the heap.
 * May be useful for debugging.
 
static bool in_heap(const void* p)
{
    return p <= mm_heap_hi() && p >= mm_heap_lo();
}


 * Returns whether the pointer is aligned.
 * May be useful for debugging.
 
static bool aligned(const void* p)
{
    size_t ip = (size_t) p;
    return align(ip) == ip;
}
*/

/*
 * mm_checkheap
 * You call the function via mm_checkheap(__LINE__)
 * The line number can be used to print the line number of the calling
 * function where there was an invalid heap.
 */
bool mm_checkheap(int line_number)
{
#ifdef DEBUG
    // Write code to check heap invariants here
    // IMPLEMENT THIS
#endif // DEBUG
    return true;
}
