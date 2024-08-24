let remoteStream = null;
let isInitiator = false; // Assuming this is set depending on the user's role (initiator or not)

document.addEventListener('DOMContentLoaded', function() {
    // Automatically start video chat for the initiator
    if (isInitiator) {
        startVideoChat();
    } else {
        showTextChat(); // Show text chat by default for the non-initiator
    }
});

function startVideoChat() {
    socket.emit('start_video_chat', { username: 'exampleUser' });
}

// Listen for a signal to start the video chat
socket.on('video_chat_start', (data) => {
    console.log('Starting video chat with', data);
    startVideoStream();
});

let localStream;
let peerConnection;
const servers = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
    ]
};

function stopVideoChat() {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        document.getElementById('localVideo').srcObject = null;
    }

    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }

    hideVideoChat();
    showTextChat();

    socket.emit('stop_video_chat');
}

// Listen for stop video chat event from the other peer
socket.on('stop_video_chat', () => {
    stopVideoChat();
});

async function startVideoStream() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        document.getElementById('localVideo').srcObject = localStream;

        socket.emit('ready_for_video_chat', { username: 'exampleUser' });

        peerConnection = new RTCPeerConnection(servers);
        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

        peerConnection.ontrack = (event) => {
            document.getElementById('remoteVideo').srcObject = event.streams[0];
        };

        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        socket.emit('video_offer', { offer: offer });
    } catch (error) {
        console.error('Error accessing media devices.', error);
        showTextChat(); // Show text chat if video fails
    }
}

socket.on('video_answer', async (message) => {
    try {
        if (peerConnection.signalingState === "have-local-offer") {
            const remoteDesc = new RTCSessionDescription(message.answer);
            await peerConnection.setRemoteDescription(remoteDesc);
        } else {
            console.error('Unexpected signaling state:', peerConnection.signalingState);
        }
    } catch (error) {
        console.error('Failed to set remote description:', error);
    }
});

socket.on('video_offer', async (data) => {
    if (!isInitiator) {
        showVideoChat();
        hideTextChat();
        peerConnection = new RTCPeerConnection(servers);
        peerConnection.ontrack = (event) => {
            remoteStream = event.streams[0];
            document.getElementById('remoteVideo').srcObject = remoteStream;

            if (!remoteStream.getVideoTracks().length) {
                showTextChat();
            }
        };

        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);

        socket.emit('video_answer', { answer: answer });
    }
});

function startVideoChat() {
    socket.emit('start_video_chat', { username: 'exampleUser' });
    showVideoChat();
    hideTextChat();
}

socket.on('ice_candidate', async (message) => {
    try {
        if (peerConnection && message.candidate) {
            await peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
        }
    } catch (error) {
        console.error('Error adding received ICE candidate', error);
    }
});

function hideVideoChat() {
    document.getElementById('localVideo').classList.add('hidden');
    document.getElementById('remoteVideo').classList.add('hidden');
}

function showVideoChat() {
    document.getElementById('localVideo').classList.remove('hidden');
    document.getElementById('remoteVideo').classList.remove('hidden');
}

function hideTextChat() {
    document.getElementById('textChat').classList.add('hidden');
}

function showTextChat() {
    document.getElementById('textChat').classList.remove('hidden');
}

function sendMessage() {
    const message = document.getElementById('chatInput').value;
    if (message.trim() !== '') {
        // Assuming you have socket.io set up to handle chat messages
        socket.emit('chat_message', { message: message });
        document.getElementById('chatInput').value = '';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (isInitiator) {
        startVideoChat(); // Initiator starts with video chat
    } else {
        hideVideoChat(); // Non-initiator starts with text chat
        showTextChat();
    }
});