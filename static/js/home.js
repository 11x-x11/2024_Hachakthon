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

document.addEventListener('DOMContentLoaded', function() {
    let currentStep = 0;

    const steps = [
        {
            element: document.getElementById('defaultOpen'),
            text: 'This is the Home tab. Here you can view your personal home page.'
        },
        {
            element: document.querySelector(".tab button:nth-child(2)"),
            text: 'This is the Skills tab. Here you can view and manage your skills.'
        },
        {
            element: document.querySelector(".tab button:nth-child(3)"),
            text: 'This is the Knowledge Repository tab. Here you can access your saved knowledge resources.'
        },
        {
            element: document.querySelector(".tab button:nth-child(4)"),
            text: 'This is the Chat tab. Here you can connect with your friends.'
        },
        {
            element: document.querySelector(".tab button:nth-child(5)"),
            text: 'This is the Friends tab. Here you can manage your friends.'
        },
        {
            element: document.querySelector(".profile-icon img"),
            text: "On the top right side is your Profile setting as well as Log Out. Click on profile icon to view and edit your personal information and preferences."
        }
    ];

    const guideContainer = document.getElementById('guide-container');
    const guideText = document.getElementById('guide-text');
    const guideNextBtn = document.getElementById('guide-next-btn');

    if (!localStorage.getItem('guideShown')) {
        startGuide();
    }

    function startGuide() {
        guideContainer.style.display = 'flex';
        showStep(currentStep);
    }

    function showStep(stepIndex) {
        if (stepIndex < steps.length) {
            const step = steps[stepIndex];
            guideText.textContent = step.text;
            console.log(step.element);
            highlightElement(step.element);
        } else {
            endGuide();
        }
    }

    function highlightElement(element) {
        steps.forEach(step => step.element.classList.remove('highlight'));
        console.log(element);
        element.classList.add('highlight');
    }

    function endGuide() {
        guideContainer.style.display = 'none';
        steps.forEach(step => step.element.classList.remove('highlight'));
        localStorage.setItem('guideShown', 'true');
    }

    guideNextBtn.addEventListener('click', function() {
        currentStep++;
        showStep(currentStep);
    });
});