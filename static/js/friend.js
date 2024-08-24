// Event listener for the 'friend_status_update' event
socket.on('friend_status_update', function (data) {
    const friendUsername = data.username;
    const status = data.status;
    updateStatusUI(friendUsername, status); // Use the combined function
});

function sendFriendRequest() {
    const userUsername = document.getElementById('currentUsername').value;
    const friendUsername = document.getElementById('friendUsername').value;

    if (!friendUsername) {
        alert("Please enter a friend's username.");
        return;
    }

    socket.emit('send_friend_request', {
        username: userUsername,
        friendUsername: friendUsername
    });
}

// Listening for server response on friend request
socket.on('friend_request_response', function(data) {
    alert(data.message);
    if (data.success) {
        document.getElementById('friendUsername').value = '';
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const friendRequestsList = document.getElementById('friend_requests_list');
    const friendListTableBody = document.getElementById('friend-list-table').getElementsByTagName('tbody')[0];

    socket.on('new_friend_request', function(data) {
        // Remove "No incoming friend requests" if it exists
        const noRequestsItem = document.getElementById('no_requests');
        if (noRequestsItem) {
            noRequestsItem.remove();
        }

        // Add new friend request to list
        const newRequestHTML = `<li id="request_${data.id}">
            ${data.sender} wants to be your friend
            <button onclick="acceptFriendRequest('${data.id}')">Accept</button>
            <button onclick="declineFriendRequest('${data.id}')">Decline</button>
        </li>`;
        friendRequestsList.insertAdjacentHTML('beforeend', newRequestHTML);
    });

    // Listening for friend request acceptance or declination
    socket.on('friend_request_answer', function(data) {
        alert(data.message);
        if (data.success) {
            // Successfully processed the friend request
            // Remove the friend request from the list if it exists
            var requestItem = document.getElementById('request_' + data.requestId);
            if (requestItem) {
                requestItem.parentNode.removeChild(requestItem);
            }

            // If all requests are processed, show the no requests message
            var friendRequestsList = document.getElementById('friend_requests_list');
            if (friendRequestsList.children.length === 0) {
                var noRequestsItem = document.createElement('li');
                noRequestsItem.id = 'no_requests';
                noRequestsItem.textContent = 'No incoming friend requests.';
                friendRequestsList.appendChild(noRequestsItem);
            }
        } else {
            console.error('Friend request processing error:', data.message);
        }
    });

    socket.on('friend_request_accepted', function (data) {
        // Add new friend to the friend list
        const newRowHTML = `<tr id="friend_${data.username}">
            <td><span class="clickable_name" username="${data.username}">${data.username}</span></td>
            <td><button onclick="removeFriend('${data.username}')" class="remove-button">Remove</button></td>
        </tr>`;
        friendListTableBody.insertAdjacentHTML('beforeend', newRowHTML);
        updateStatusUI(data.username, data.status);
        updateClickableNames();
    });

    socket.on('friend_request_resolved', function(data) {
        const requestItem = document.getElementById('request_' + data.requestId);
        if (requestItem) {
            requestItem.remove();
        }

        if (!friendRequestsList.hasChildNodes()) {
            friendRequestsList.innerHTML = '<li id="no_requests">No incoming friend requests.</li>';
        }
    });

    function updateClickableNames() {
        // Attach click event to all clickable names
        document.querySelectorAll('.clickable_name').forEach(user => {
            user.addEventListener('click', function() {
                const username = this.getAttribute('username'); // Get the username from the attribute
                openChatWindow(username);
                this.style.color = 'grey';
            });
        });
    }

    function openChatWindow(username) {
        // Placeholder for opening the chat window
        console.log(`Open chat window for: ${username}`);
    
        const chatBox = document.getElementById('chat_box');
        const receiverInput = document.getElementById('receiver');
    
        if (chatBox && receiverInput) {
            receiverInput.value = username;
            chatBox.style.display = 'block';
            document.getElementById('message').focus();
            join_room();
        }
    }
    // Call to update events for initially loaded elements
    updateClickableNames();
});

// Function to handle accepting a friend request using sockets
async function acceptFriendRequest(requestId) {
    await socket.emit('accept_friend_request', { request_id: requestId });
}

// Function to handle declining a friend request using sockets
async function declineFriendRequest(requestId) {
    await socket.emit('decline_friend_request', { request_id: requestId });
}
