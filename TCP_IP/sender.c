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
#include <assert.h>
#define MAXDATASIZE 100 // max number of bytes we can get at once 

struct user {
    char username[MAXDATASIZE];
    int usersocket;
    struct user *nextuser;
};

struct user *createnewuser(char name[], int socket) {
    struct user *clientuser = NULL;
    clientuser = (struct user *) malloc(sizeof (struct user));
    if (clientuser == NULL) {
        printf("malloc fair\n");
    }
    memset(clientuser, 0, sizeof (struct user));
    memcpy(clientuser->username, name, strlen(name));
    clientuser->usersocket = socket;
    clientuser->nextuser = NULL;
    return clientuser;
};

// get sockaddr, IPv4 or IPv6:

void *get_in_addr(struct sockaddr *sa) {
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*) sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*) sa)->sin6_addr);
}

int usedsocket(struct user *useduser, char* buf) {

    struct user *t_head = useduser;

    while (t_head != NULL) {
        if ((strcmp(useduser ->username, buf)) == 0) {
            printf("Existing user name\n");
            return 1;
        }
        t_head = t_head->nextuser;
    }
    return 0;
}

void broadcast(int nbytes, char buf[], int listener, int j, int i) {
    // except the listener and ourselves
    if (j != listener && j != i) {
        if (send(j, buf, nbytes, 0) == -1) {
            perror("send");
        }
    }
}

int searchsocket(char name[], struct user *searchuser) {
    while (searchuser->nextuser != NULL) {
        if (searchuser->username != name)
            searchuser = searchuser->nextuser;
        else
            return searchuser->usersocket;
    }
    if (searchuser->username != name)
        return 0;
    else
        return searchuser->usersocket;
}

void deleteuser(struct user **head_ref, int key) {
    // Store head node
    struct user * temp = *head_ref, *prev;

    // If head node itself holds the key to be deleted
    if (temp != NULL && temp->usersocket == key) {
        *head_ref = temp->nextuser; // Changed head
        free(temp); // free old head
        return;
    }

    // Search for the key to be deleted, keep track of the
    // previous node as we need to change 'prev->next'
    while (temp != NULL && temp->usersocket != key) {
        prev = temp;
        temp = temp->nextuser;
    }

    // If key was not present in linked list
    if (temp == NULL) return;

    // Unlink the node from linked list
    prev->nextuser = temp->nextuser;

    free(temp); // Free memory
}

int server(int argc, char **argv) {

    fd_set master; // master file descriptor list
    fd_set read_fds; // temp file descriptor list for select()
    int fdmax; // maximum file descriptor number

    int listener; // listening socket descriptor
    int newfd; // newly accept()ed socket descriptor
    struct sockaddr_storage remoteaddr; // client address
    socklen_t addrlen;

    char buf[256]; // buffer for client data
    int nbytes;

    char remoteIP[INET6_ADDRSTRLEN];

    int yes = 1; // for setsockopt() SO_REUSEADDR, below
    int i, j, rv;

    struct addrinfo hints, *ai, *p;

    struct user *firstuser = NULL;
    struct user *currentuser = NULL;

    char *message, *type;

    FD_ZERO(&master); // clear the master and temp sets
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

    for (p = ai; p != NULL; p = p->ai_next) {
        listener = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (listener < 0) {
            continue;
        }

        // lose the pesky "address already in use" error message
        setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof (int));

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
    while (1) {
        read_fds = master; // copy it
        if (select(fdmax + 1, &read_fds, NULL, NULL, NULL) == -1) {
            perror("select");
            exit(4);
        }


        // run through the existing connections looking for data to read
        if (FD_ISSET(listener, &read_fds)) { // we got one!!

            // handle new connections
            addrlen = sizeof remoteaddr;
            newfd = accept(listener, (struct sockaddr *) &remoteaddr, &addrlen);

            if (newfd == -1) {
                perror("accept");
                exit(0);
            }

            FD_SET(newfd, &master); // add to master set
            if (newfd > fdmax) { // keep track of the max
                fdmax = newfd;
            }
            printf("selectserver: new connection from %s on "
                    "socket %d\n",
                    inet_ntop(remoteaddr.ss_family,
                    get_in_addr((struct sockaddr*) &remoteaddr),
                    remoteIP, INET6_ADDRSTRLEN),
                    newfd);

            //get user name
            nbytes = recv(newfd, buf, sizeof buf, 0);
            if (nbytes <= 0) {
                perror("recv");
                exit(0);
            }
            buf[nbytes] = '\0';

            if (firstuser == NULL) {
                firstuser = createnewuser(buf, newfd);
                printf("finished req for first user\n");
                continue;

            } else {

                if ((usedsocket(firstuser, buf)) == 1) {
                    close(newfd);
                    continue;
                }

                currentuser = createnewuser(buf, newfd);
                struct user *nextuser = firstuser;

                while (nextuser->nextuser != NULL) {
                    nextuser = nextuser->nextuser;
                }
                nextuser->nextuser = currentuser;
                continue;
            }
        }

        //if this is a already connected user
        assert(FD_ISSET(listener, &read_fds) == 0);

        for (i = 0; i < fdmax; i++) {
            if (FD_ISSET(i, &read_fds)) {
                printf("Server: found connection from sock %d\n", i);
                break;
            }
        }

        // handle data from a client
        nbytes = recv(i, buf, sizeof buf, 0);
        if (nbytes == 0) {
            // connection closed
            printf("selectserver: socket %d hung up\n", i);
            close(i); // bye!
            FD_CLR(i, &master); // remove from master set
            //TODO: remove username
        }

        if (nbytes < 0) {
            perror("recv");
            exit(0);
        }

        //we have message now
        printf("Server GET: %s\n", buf);

        //debug printf all user
        {
            currentuser = firstuser;
            int i = 0;
            while (currentuser != NULL) {
                printf("username #%d :%s sock#%d\n", i, currentuser->username, currentuser->usersocket);
                i = i + 1;
                currentuser = currentuser->nextuser;
            }
        }

        buf[nbytes - 1] = '\0';
        printf("%s\n", buf);
        type = strtok(buf, " ");
        message = strtok(NULL, "");

        if (message != NULL) {
            printf("%s\n", message);
            printf("%s\n", type);
        }


        if ((strcmp(type, "broadcast") == 0)) {
            for (j = 0; j <= fdmax; j++) {
                // send to everyone!
                if (FD_ISSET(j, &master)) {
                    // except the listener and ourselves
                    broadcast(nbytes, message, listener, j, i);
                }
            }
            continue;
        }

        if ((strcmp(type, "list") == 0)) {
            currentuser = firstuser;
            int i = 0;
            while (currentuser != NULL) {
                printf("username #%d :%s sock#%d\n", i, currentuser->username, currentuser->usersocket);
                i = i + 1;
                currentuser = currentuser->nextuser;
            }
            continue;
        }



        if ((strcmp(type, "exit") == 0)) {
            printf("Exiting %d.....\n", i);
            deleteuser(&firstuser, i);
            //debug printf all user          
            continue;
        }

        //else
        {
            struct user *current_user = firstuser;
            while (current_user != NULL) {
                printf("I am in while loop\n");
                if (strcmp(type, current_user->username) == 0) {

                    broadcast(nbytes, message, listener, current_user->usersocket, i);
                    break;
                } else {
                    current_user = current_user->nextuser;
                }
            }
            printf("User not found\n");
        }

    }
    return 0;
} // END handle data from client