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
                .then(response => response.json())
                .then(data => {
                    if (data.chatroom_url) {
                        window.location.href = data.chatroom_url; // Redirect to the chatroom
                    } else {
                        alert('No matching users found.'); // Handle case where no match is found
                    }
                })
                .catch(error => {
                    console.error('Error finding matching user:', error);
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
        }
    ];

    const guideContainer = document.getElementById('guide-container');
    const guideText = document.getElementById('guide-text');
    const guideNextBtn = document.getElementById('guide-next-btn');

    function startGuide() {
        guideContainer.style.display = 'flex';
        showStep(currentStep);
    }

    function showStep(stepIndex) {
        if (stepIndex < steps.length) {
            const step = steps[stepIndex];
            guideText.textContent = step.text;
            highlightElement(step.element);
        } else {
            endGuide();
        }
    }

    function highlightElement(element) {
        steps.forEach(step => step.element.classList.remove('highlight'));
        element.classList.add('highlight');
    }

    function endGuide() {
        guideContainer.style.display = 'none';
        steps.forEach(step => step.element.classList.remove('highlight'));
    }

    guideNextBtn.addEventListener('click', function() {
        currentStep++;
        showStep(currentStep);
    });

    // Start the guide on page load
    startGuide();
});