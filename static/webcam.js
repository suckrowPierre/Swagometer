const video = document.getElementById("webcam");
const canvas = document.getElementById("snapshot");
const ctx = canvas.getContext("2d");
const imageEndpoint = "/process-image";

function simulateCameraFlash(ms) {
    video.style.display = "none";
    setTimeout(() => {
        video.style.display = "block";
    }, ms);
}

function hideVideo() {
    video.classList.add("hidden");
}

function showVideo() {
    video.classList.remove("hidden");
}

function captureFrame() {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.classList.remove("hidden");
}

function getShownScreenTextElement() {
    return document.querySelector(".screen-text:not(.hidden)")
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function showSwagPercentage(percentage) {
    const percetageInt = parseInt(percentage);
    const screenTextElements = document.querySelectorAll(".screen-text");
    screenTextElements.forEach((el) => el.classList.add("hidden"));
    const swagElement = document.getElementById("swag-response");
    const swagPercentageElement = document.getElementById("swag-score");
    swagPercentageElement.textContent = percetageInt + "%";
    swagElement.classList.remove("hidden");
}

function getProcessingTextElements() {
    const processingTextElement1 = document.getElementById("processing-1");
    const processingTextElement2 = document.getElementById("processing-2");
    const processingTextElement3 = document.getElementById("processing-3");
    const processingTextElement4 = document.getElementById("processing-4");

    return [processingTextElement1, processingTextElement2, processingTextElement3, processingTextElement4];

}

function showProcessingLoop() {
    // TODO

}

function hideProcessingLoop() {
    // TODO
}

async function reset() {
    await sleep(3000);
    const screenTextElements = document.querySelectorAll(".screen-text");
    screenTextElements.forEach((el) => el.classList.add("hidden"));

    const initialTextElement = document.getElementById("initial-text");
    initialTextElement.classList.remove("hidden");

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    canvas.classList.add("hidden");
    showVideo();
}

async function sendImageToServer() {
    showProcessingLoop();
    const imageData = canvas.toDataURL("image/jpeg", 1.0);
    fetch(imageEndpoint, {
        method: "POST",
        body: JSON.stringify({
            image: imageData
        }),
        headers: {
            "Content-Type": "image/jpeg"
        }
    })
    .then((response) => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error("Error processing image");
        }
    })
    .then(async (data) => {
        hideProcessingLoop();
        const swagPercentage = data.swag_percentage;
        showSwagPercentage(swagPercentage);
        await reset();
    })
    .catch(async (err) => {
        const errorTextElement = document.getElementById("error-text");
        errorTextElement.classList.remove("hidden");
        console.error(err);
        await reset();
    });
}




async function clickScreen() {
    console.log("clickScreen");
    let screenTextElement = getShownScreenTextElement();
    if (!screenTextElement) {
        return;
    }
    if (screenTextElement.id === "initial-text") {
        screenTextElement.classList.add("hidden");
        screenTextElement = document.getElementById("instruction-text")
        screenTextElement.classList.remove("hidden");
        await sleep(2000);
        screenTextElement.classList.add("hidden");
        screenTextElement = document.getElementById("count-down-1")
        screenTextElement.classList.remove("hidden");
        await sleep(1000);
        screenTextElement.classList.add("hidden");
        screenTextElement = document.getElementById("count-down-2")
        screenTextElement.classList.remove("hidden");
        await sleep(1000);
        screenTextElement.classList.add("hidden");
        screenTextElement = document.getElementById("count-down-3")
        screenTextElement.classList.remove("hidden");
        await sleep(1000);
        screenTextElement.classList.add("hidden");
        simulateCameraFlash(10);
        hideVideo();
        captureFrame();
        await sendImageToServer(10);

    }
}

function initCanvas() {
    // get video dimensions
    const width = video.offsetWidth;
    const height = video.offsetHeight
    canvas.width = width;
    canvas.height = height;
}

function initWebcam() {
    video.controls = false;
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: "user",
            }
        })
        .then((stream) => {
            video.srcObject = stream;
        })
        .catch((err) => {
            alert("Error accessing webcam:" + err);
        });
    } else {
        alert("Webcam not supported by this browser.");
    }

}



document.addEventListener("DOMContentLoaded", () => {
    initWebcam();
    initCanvas();
    window.clickScreen = clickScreen;
});