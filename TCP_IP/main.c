/* 
 * File:   main.c
 * Author: caiyuhong
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <netdb.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include "client.h"

#define MAXDATASIZE 100 // max number of bytes we can get at once 
#define STDIN 0 
/*
 * 
 */
extern int sockfd;
int main(int argc, char** argv) {
    if(argc < 4 ){
        printf("Too few parameter!\n");
        exit(EXIT_FAILURE);
    }
    struct addrinfo *p;
    char message[MAXDATASIZE];
    
    fd_set read_fds, back_up;    // master file descriptor list
    FD_ZERO(&read_fds);    // clear the master and temp sets
    
    
    p = client(argc, argv);
    
    printf("-broadcast [message] \n-[user_name] [message] \n-list \n-exit \n" );
    
    FD_SET(STDIN, &read_fds);
    FD_SET(sockfd, &read_fds);
    assert(sockfd!=0);
    memcpy(&back_up,&read_fds,sizeof(fd_set));
    
    //printf("test 1\n");
    //printf("test 2\n");
    
    while(1){
        memcpy(&read_fds,&back_up,sizeof(fd_set));
        
        if (select(sockfd+1, &read_fds, NULL, NULL, NULL) == -1) {
            perror("select");
            exit(4);
        }
        
        if (FD_ISSET(STDIN, &read_fds)) { //read_fds == STDIN 
            printf("test 5\n");
            fgets(message, MAXDATASIZE, stdin);
            printf("test 3\n");
            sender(p, message);
        }
        else{
            printf("test 4\n");
            reciver();
            printf("%s \n",message);
            }
        
    }
    close(sockfd);
    return 0;
}

