function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("defaultOpen").click();
});

document.addEventListener('DOMContentLoaded', function() {
    const skillLinks = document.querySelectorAll('.skill-link');

    skillLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const skillId = this.getAttribute('data-skill-id');
    
            // Emit an event to the server to find a matching user
            socket.emit('find_matching_user', { skill_id: skillId });
        });
    });
    
    // Listen for the server's response
    socket.on('matching_user_result', function(data) {
        if (data.chatroom_url) {
            openTab(null, 'Chat');
            // window.location.href = data.chatroom_url; // Redirect to the chatroom
            alert('Please heads to the chat tab to continue chatting');
        } else {
            alert(data.error || 'No matching users found.'); // Handle case where no match is found
        }
    });
    
});


function displayMatchingUsers(users) {
    const resultContainer = document.getElementById('matching-users-container');
    resultContainer.innerHTML = ''; // Clear previous results

    if (users.length > 0) {
        users.forEach(user => {
            const userElement = document.createElement('div');
            userElement.classList.add('user-item');
            userElement.textContent = `${user.username} - ${user.skill_name}`;
            resultContainer.appendChild(userElement);
        });
    } else {
        resultContainer.textContent = 'No matching users found.';
    }
}
