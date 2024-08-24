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

            fetch(`/find_matching_user_and_redirect?skill_id=${skillId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.chatroom_url) {
                        window.location.href = data.chatroom_url; // Redirect to the chatroom
                    } else {
                        alert(data.error || 'No matching users found.'); // Handle case where no match is found
                    }
                })
                .catch(error => {
                    console.error('Error finding matching user:', error);
                    alert('An error occurred while finding a matching user.');
                });
        });
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
