document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("webcam");

    // Check if the browser supports media devices
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: "user" // Use the front camera
            }
        })
        .then((stream) => {
            // Set the video stream as the source of the video element
            video.srcObject = stream;
        })
        .catch((err) => {
            console.error("Error accessing webcam:", err);
        });
    } else {
        console.error("Webcam not supported by this browser.");
    }
});
