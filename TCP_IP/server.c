/*
** selectserver.c -- a cheezy multiperson chat server
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include "server.h"
#define MAXDATASIZE 100 // max number of bytes we can get at once 
struct user{
    char username[MAXDATASIZE];
    int usersocket;
    struct user *nextuser;
};

struct user *createnewuser(char name[], int socket){
    struct user *clientuser = NULL;
    clientuser = (struct user *)malloc(sizeof(struct user));
    if(clientuser == NULL){
        printf("malloc fair\n");
    }
    memset(clientuser, 0, sizeof(struct user));
    memcpy(clientuser->username, name, strlen(name));
    clientuser->usersocket = socket;
    clientuser->nextuser = NULL;
    return clientuser;
};

// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

int usedsocket(int socket, struct user *useduser){
   // printf("test 1\n");
    while(useduser->nextuser != NULL){
        if(useduser -> usersocket != socket){
            //printf("test 7\n");
            useduser = useduser->nextuser;
        }
        else
            return 1;
    }
       // printf("test 8\n");
        if(useduser -> usersocket == socket){
           // printf("test 9\n");            
            return 1;
        }
        else{
           // printf("test 10\n");
            return 0;
        }
}

void broadcast(int nbytes, char buf[], int listener, int j, int i){
        // except the listener and ourselves
        if (j != listener && j != i) {
            if (send(j, buf, nbytes, 0) == -1) {
            perror("send");
        }
    }
}

int searchsocket(char name[], struct user *searchuser){
    while(searchuser->nextuser != NULL){
        if(searchuser->username != name)
            searchuser = searchuser->nextuser;
        else
            return searchuser->usersocket;
    }
        if(searchuser->username != name)
            return 0;
        else
            return searchuser->usersocket;
}

int server(int argc, char **argv)
{
    
    fd_set master;    // master file descriptor list
    fd_set read_fds;  // temp file descriptor list for select()
    int fdmax;        // maximum file descriptor number

    int listener;     // listening socket descriptor
    int newfd;        // newly accept()ed socket descriptor
    struct sockaddr_storage remoteaddr; // client address
    socklen_t addrlen;

    char buf[256];    // buffer for client data
    int nbytes;

    char remoteIP[INET6_ADDRSTRLEN];

    int yes=1;        // for setsockopt() SO_REUSEADDR, below
    int i, j, rv;
    
    struct addrinfo hints, *ai, *p;

    struct user *firstuser=NULL;
    char *message, *type, *picker; 
    
    FD_ZERO(&master);    // clear the master and temp sets
    FD_ZERO(&read_fds);

    // get us a socket and bind it
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;
    
    if ((rv = getaddrinfo(NULL, argv[1], &hints, &ai)) != 0) {
        fprintf(stderr, "selectserver: %s\n", gai_strerror(rv));
        exit(1);
    }
    
    for(p = ai; p != NULL; p = p->ai_next) {
        listener = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (listener < 0) { 
            continue;
        }
        
        // lose the pesky "address already in use" error message
        setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int));

        if (bind(listener, p->ai_addr, p->ai_addrlen) < 0) {
            close(listener);
            continue;
        }

        break;
    }

    // if we got here, it means we didn't get bound
    if (p == NULL) {
        fprintf(stderr, "selectserver: failed to bind\n");
        exit(2);
    }

    freeaddrinfo(ai); // all done with this

    
    ////////////////////////////////////////////////////////////////
    // listen
    if (listen(listener, 10) == -1) {
        perror("listen");
        exit(3);
    }

    // add the listener to the master set
    FD_SET(listener, &master);

    // keep track of the biggest file descriptor
    fdmax = listener; // so far, it's this one

    // main loop
    for(;;) {
        read_fds = master; // copy it
        if (select(fdmax+1, &read_fds, NULL, NULL, NULL) == -1) {
            perror("select");
            exit(4);
        }
        // run through the existing connections looking for data to read
        for(i = 0; i <= fdmax; i++) {
            if (FD_ISSET(i, &read_fds)) { // we got one!!
                if (i == listener) {
                    // handle new connections
                    addrlen = sizeof remoteaddr;
                    newfd = accept(listener,
                        (struct sockaddr *)&remoteaddr,
                        &addrlen);

                    if (newfd == -1) {
                        perror("accept");
                    }else {
                       
                        
                        FD_SET(newfd, &master); // add to master set
                        if (newfd > fdmax) {    // keep track of the max
                            fdmax = newfd;
                        }
                        printf("selectserver: new connection from %s on "
                            "socket %d\n",
                            inet_ntop(remoteaddr.ss_family,
                                get_in_addr((struct sockaddr*)&remoteaddr),
                                remoteIP, INET6_ADDRSTRLEN),
                            newfd);
                    }
                } else {
                    // handle data from a client
                    if ((nbytes = recv(i, buf, sizeof buf, 0)) <= 0) {
                        // got error or connection closed by client
                        if (nbytes == 0) {
                            // connection closed
                            printf("selectserver: socket %d hung up\n", i);
                        } else {
                            perror("recv");
                        }
                        close(i); // bye!
                        FD_CLR(i, &master); // remove from master set
                    } else {            
                        ////////////////////////  Below is to create user accounts
                        buf[nbytes] = '\0';
                       
                            if(firstuser == NULL){
                                firstuser = createnewuser(buf, newfd);
                                continue;
                                //printf("test 4");
                            }
                            else{
                                if((usedsocket(newfd, firstuser)) == 0){
                                    struct user *lateruser = createnewuser(buf, newfd);
                                    struct user *nextuser = firstuser;

                                    while(nextuser->nextuser != NULL){
                                        nextuser = nextuser->nextuser;
                                    }
                                        nextuser->nextuser = lateruser;
                                        continue;
                                }
                                //printf("test 11\n");
                            }
                                buf[nbytes-1] = '\0';
                                    //printf("test 2\n");
                                        picker = strtok(buf, " ");
                                        type = picker;
                                    while(picker)
                                    {   //printf("test 3\n");
                                        message = picker;
                                        picker = strtok(NULL, " ");
                                    }
                                        
                        printf("%s\n",message);
                        printf("%s\n",type);
                        
                        printf("username %s socket# %d\n", firstuser->username, firstuser->usersocket);
                        if(firstuser->nextuser != NULL){
                            printf("username %s socket# %d\n", firstuser->nextuser->username, firstuser->nextuser->usersocket);
                        } 
                        ///////////////////////////////////////
                        // we got some data from a client
                        for(j = 0; j <= fdmax; j++) {
                            // send to everyone!
                            if (FD_ISSET(j, &master)) {
                                // except the listener and ourselves
                                broadcast(nbytes, message, listener, j, i);
                            }
                        }
                    }
                } // END handle data from client
            } // END got new incoming connection
        } // END looping through file descriptors
    } // END for(;;)--and you thought it would never end!
    
    return 0;
}