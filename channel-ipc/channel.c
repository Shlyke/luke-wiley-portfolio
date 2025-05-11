#include "channel.h"
//pthread library functions
//for my own reference to remeber helpful library functions i havent used before
//special emphasis on pthread_cond... functions as our lock is a struct
//there are more than mentioned here

//pthread_mutex_init
//pthread_cond_init because our lock is a struct
//pthread_mutex_lock
//pthread_mutex_unlock
//pthread_cond_wait wait whie a cond of channel is true
//pthread_cond_broadcast

// Creates a new channel with the provided size and returns it to the caller
channel_t* channel_create(size_t size) {
	//create channel
	//malloc size of struct channel_t
	//check malloc success
	channel_t* channel = malloc(sizeof(channel_t));
	if (!channel) {
		return NULL;
	}
	//create channel buffer
	//check success, else free and return
	channel->buffer = buffer_create(size);
	if (!channel->buffer) {
		free(channel);
		return NULL;
	}
	//channel_t struct initialization
	pthread_mutex_init(&channel->lock, NULL);
	pthread_cond_init(&channel->open, NULL);
	pthread_cond_init(&channel->recv, NULL);
	channel->closed = false;
	return channel;
}

// Writes data to the given channel
// This is a blocking call i.e., the function only returns on a successful completion of send
// In case the channel is full, the function waits till the channel has space to write the new data
// Returns SUCCESS for successfully writing data to the channel,
// CLOSED_ERROR if the channel is closed, and
// GENERIC_ERROR on encountering any other generic error of any sort
enum channel_status channel_send(channel_t *channel, void* data) {
	//similar to nonblocking, but wait if channel is full 
	if (!channel) {
                return GENERIC_ERROR;
        }
        pthread_mutex_lock(&(channel)->lock);
        //channel closed, unlock CLOSED_ERROR
        if (channel->closed) {
                pthread_mutex_unlock(&(channel)->lock);
                return CLOSED_ERROR;
        }
        //try to add to buffer
	//in while loop, if error dont return full, wait
	//must continually check if channel closes
        while (buffer_add(channel->buffer, data) == BUFFER_ERROR) {
		if (channel->closed) {
			pthread_mutex_unlock(&(channel)->lock);
                	return CLOSED_ERROR;
		}
                pthread_cond_wait(&channel->open, &channel->lock);
	}
        //wake thread and unlock
        pthread_cond_signal(&channel->recv);
        pthread_mutex_unlock(&(channel)->lock);
        return SUCCESS;
}

// Reads data from the given channel and stores it in the function's input parameter, data (Note that it is a double pointer)
// This is a blocking call i.e., the function only returns on a successful completion of receive
// In case the channel is empty, the function waits till the channel has some data to read
// Returns SUCCESS for successful retrieval of data,
// CLOSED_ERROR if the channel is closed, and
// GENERIC_ERROR on encountering any other generic error of any sort
enum channel_status channel_receive(channel_t* channel, void** data) {
	//simialr to nonblocking
	//instead of channel empty, while loop and wait
	if (!channel || !data) {
                return GENERIC_ERROR;
        }
        pthread_mutex_lock(&(channel)->lock);
	//start while loop
	//while buffer_error, continually check close status
	//no channel_empty, cond_wait
        while (buffer_remove(channel->buffer, data) == BUFFER_ERROR) {
                if (channel->closed) {
			pthread_mutex_unlock(&(channel)->lock);
                        return CLOSED_ERROR;
		}
                pthread_cond_wait(&channel->recv, &channel->lock);
        }
        //wake thread and unlock
        pthread_cond_signal(&channel->open);
        pthread_mutex_unlock(&(channel)->lock);
        return SUCCESS;
}

// Writes data to the given channel
// This is a non-blocking call i.e., the function simply returns if the channel is full
// Returns SUCCESS for successfully writing data to the channel,
// CHANNEL_FULL if the channel is full and the data was not added to the buffer,
// CLOSED_ERROR if the channel is closed, and
// GENERIC_ERROR on encountering any other generic error of any sort
enum channel_status channel_non_blocking_send(channel_t* channel, void* data) {
	//ensure valid channel
	//lock before performing any operation
	//check channel closed status
	//add data to buffer
	//if channel is full, return error, no waiting
	//wake thread waiting to recv, alter channel->recv
	if (!channel) {
		return GENERIC_ERROR;
	}
	pthread_mutex_lock(&(channel)->lock);
	//channel closed, unlock CLOSED_ERROR
	if (channel->closed) {
		pthread_mutex_unlock(&(channel)->lock);
		return CLOSED_ERROR;
	}
	//buffor error,unlock, CHANNEL_FULL
	if (buffer_add(channel->buffer, data) == BUFFER_ERROR) {
		pthread_mutex_unlock(&(channel)->lock);
		return CHANNEL_FULL;
	}
	//wake thread and unlock
	pthread_cond_signal(&channel->recv);
	pthread_mutex_unlock(&(channel)->lock);
	return SUCCESS;
}

// Reads data from the given channel and stores it in the function's input parameter data (Note that it is a double pointer)
// This is a non-blocking call i.e., the function simply returns if the channel is empty
// Returns SUCCESS for successful retrieval of data,
// CHANNEL_EMPTY if the channel is empty and nothing was stored in data,
// CLOSED_ERROR if the channel is closed, and
// GENERIC_ERROR on encountering any other generic error of any sort
enum channel_status channel_non_blocking_receive(channel_t* channel, void** data) {
	//check for valid channel
	//data pointer must be valid, extracted buffer goes here
	//!!not same data variable role as send
	//obtain lock
	//buffer_remove
	//wake a thread waiting to send, spacce opened up
	if (!channel || !data) {
		return GENERIC_ERROR;
	}
	pthread_mutex_lock(&(channel)->lock);
	if (buffer_remove(channel->buffer, data) == BUFFER_ERROR){
		//multiple errors from BUFFER_ERROR
		//if closed CLOSED_ERROR
		//els CHANNEL_EMPTY
		enum channel_status output;
		if (channel->closed) {
			output= CLOSED_ERROR;
		} else {
			output = CHANNEL_EMPTY;
		}
		pthread_mutex_unlock(&(channel)->lock);
		return output;
	}
	//wake thread and unlock
	pthread_cond_signal(&channel->open);
	pthread_mutex_unlock(&(channel)->lock);
	return SUCCESS;
}

// Closes the channel and informs all the blocking send/receive/select calls to return with CLOSED_ERROR
// Once the channel is closed, send/receive/select operations will cease to function and just return CLOSED_ERROR
// Returns SUCCESS if close is successful,
// CLOSED_ERROR if the channel is already closed, and
// GENERIC_ERROR in any other error case
enum channel_status channel_close(channel_t* channel) {
	//check valid channel
	//obtain lock
	//check if already closed
	//pthread_cond_broadcast to end loops
	//unlock
	if (!channel) {
		return GENERIC_ERROR;
	}
	pthread_mutex_lock(&(channel)->lock);
	//check already closed
	if (channel->closed) {
		pthread_mutex_unlock(&(channel)->lock);
		return CLOSED_ERROR;
	}
	//set closed
	channel->closed = true;
	//wake all looping threads
	pthread_cond_broadcast(&channel->open);
	pthread_cond_broadcast(&channel->recv);
	pthread_mutex_unlock(&(channel)->lock);
	return SUCCESS;
}

// Frees all the memory allocated to the channel
// The caller is responsible for calling channel_close and waiting for all threads to finish their tasks before calling channel_destroy
// Returns SUCCESS if destroy is successful,
// DESTROY_ERROR if channel_destroy is called on an open channel, and
// GENERIC_ERROR in any other error case
enum channel_status channel_destroy(channel_t* channel) {
	//obtain lock
	//check if closed and buffer is empty -> safe
	//unlock!!
	//If not safe to free -> error
	if (!channel) {
		return GENERIC_ERROR;
	}
	pthread_mutex_lock(&(channel)->lock);
	bool freeable = channel->closed;
	pthread_mutex_unlock(&(channel)->lock);
	if (!freeable) {
		return DESTROY_ERROR;
	}
	//cleanup
	//free all mallocced memory
	//pthread_destroy functions
	buffer_free(channel->buffer);
	pthread_mutex_destroy(&channel->lock);
	pthread_cond_destroy(&channel->open);
	pthread_cond_destroy(&channel->recv);
	free(channel);
	return SUCCESS;
}

// Takes an array of channels (channel_list) of type select_t and the array length (channel_count) as inputs
// This API iterates over the provided list and finds the set of possible channels which can be used to invoke the required operation (send or receive) specified in select_t
// If multiple options are available, it selects the first option and performs its corresponding action
// If no channel is available, the call is blocked and waits till it finds a channel which supports its required operation
// Once an operation has been successfully performed, select should set selected_index to the index of the channel that performed the operation and then return SUCCESS
// In the event that a channel is closed or encounters any error, the error should be propagated and returned through select
// Additionally, selected_index is set to the index of the channel that generated the error
enum channel_status channel_select(select_t* channel_list, size_t channel_count, size_t* selected_index)
{
    /* ONLY FOR BONUS */
    /* IMPLEMENT THIS */
    return SUCCESS;
}
