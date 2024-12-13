    window.onload = function () {
        var fileInput = document.getElementById("file-input");
        var imageElement = document.getElementById("image");
        var formElement = document.getElementById("image-upload-form");

        fileInput.addEventListener("change", function (event) {
            var file = event.target.files[0];
            if (!file) return;

            // Display the selected image locally if possible
            if (window.URL && window.URL.createObjectURL) {
                var imageURL = window.URL.createObjectURL(file);
                imageElement.src = imageURL;
                imageElement.onload = function() {
                    window.URL.revokeObjectURL(imageURL);
                };
            } else {
                console.log("Preview not supported on this device/browser.");
            }

            // Create FormData from the form element
            var formData = new FormData(formElement);

            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/process-image-ios-7", true);

            xhr.onload = function() {
                if (xhr.status === 200) {
                    var swag_percentage = parseInt(JSON.parse(xhr.responseText).swag_percentage);
                    // get element with id swag value change value
                    document.getElementById("swag-value").textContent = swag_percentage;

                    //get element with id swag text and make visible make element with id title hidden. do not use className
                    document.getElementById("swag-text").style.display = "block";
                    document.getElementById("title").style.display = "none";

                } else {
                    alert("Error uploading image: " + xhr.status + " " + xhr.responseText);
                }
            };

            xhr.onerror = function() {
                alert("Network error occurred while uploading image.");
            };

            // Send the form data (the file) to the server
            xhr.send(formData);
        });
    };