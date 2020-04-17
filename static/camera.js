function loadCamera() {
    
    // Erase 'disp-area2' and initialize other information
    document.getElementById('disp-area2').style.display = "none";
    var resultList = document.getElementById('result-list');
    if (resultList.hasChildNodes()) {
        while (resultList.firstChild) {
            console.log("resultList = " + resultList.firstChild);
            resultList.removeChild(resultList.firstChild);
        }
    }
    
    // Prepare user camera
    var player = document.getElementById('player');
    console.log("player = " + player);
 
    var handleSuccess = function(stream){
        player.srcObject = stream;
        document.getElementById('disp-area').style.display = "block";
        document.getElementById('player').style.display = "block";        
        document.getElementById('cap').style.display = "block";
    };

    constrains = {
                    audio: false,
                    video: true
                    //video: { facingMode: { exact: "environment" }}
                 } ;

    navigator.mediaDevices.getUserMedia(constrains)
        .then(handleSuccess)
        .catch(function(err){
            console.log("Camera open error: " + err);
            //document.getElementById('disp-area').innerHTML = "Camera open error:" + err;
            var cameraError = document.createElement("div");
            cameraError.className = "alert-message block-message warning";
            var cameraErrorMsg = document.createElement("p");
            cameraErrorMsg.innerText = "Camera open error. (" + err + ")";
            var cameraErrorMsg2 = document.createElement("p");
            cameraErrorMsg2.innerText = "Please make sure the camera is available.";
            cameraError.appendChild(cameraErrorMsg);
            cameraError.appendChild(cameraErrorMsg2);
            var btnReload = document.createElement("button");
            btnReload.className = "btn small pad";
            btnReload.innerText = "Retry";
            btnReload.onclick = function () {
                window.location.reload();
            }
            cameraError.appendChild(btnReload);
            document.getElementById('disp-area').appendChild(cameraError);
        });

}

function clickCapture() {
    var player = document.getElementById('player');

    var tempCanvas = document.createElement('canvas');
    tempCanvas.width = player.videoWidth;
    tempCanvas.height = player.videoHeight;
    

    var context = tempCanvas.getContext('2d');
    context.drawImage(player, 0, 0, tempCanvas.width, tempCanvas.height);

    // Send image to save on a server
    var dataURL = tempCanvas.toDataURL("image/png");
 
    $.ajax({
        method: 'POST',
        url: '/canvas',
        data: { 'image': dataURL }
        //processData: false,
        //processType: false
    })
    .done( function( response ) {
        if(response.length == 0) {
            $( "#result-list" ).append( "<option value=\"no_text\" disabled> (No text found.) </option>" );

        } else {

            for(let i = 0; i < response.length; i++){
                detection = response[i];
                detectConf = detection['conf'];
                detectText = detection['text'];
                $( "#result-list" ).append( "<option value=\"text" + i + "\">" + detectText + " (" + detectConf + ")</option>" );
            }
        }
    })
    .fail(function() {
        console.log("Save canvas ERROR!")
    });


    // Make an img to show the captured image
    console.log("player.videoHeight = " + player.videoHeight);
    console.log("player.videoWidth = " + player.videoWidth);
    var newW = 200;
    var newH = player.videoHeight * (newW / player.videoWidth);
    console.log("new height, width = " + newH + ", " + newW);

    tempCanvas.toBlob(function(blob) {
        var newImg = document.getElementById('snapshot');
        var url = URL.createObjectURL(blob);

        newImg.onload = function() {
            URL.revokeObjectURL(url);
        };

        newImg.src = url;
        newImg.height = newH;
        newImg.width = newW;
    });
    
    // Stop all video streams
    var videoTracks = player.srcObject.getVideoTracks();
    videoTracks.forEach(function(track) {track.stop(); console.log("video stopped!");});

    // Delete disp-area after calculating player size.
    document.getElementById('disp-area').style.display = "none";
    document.getElementById('disp-area2').style.display = "block";

    // To output the canvas to image data : HTMLCanvasElement.toBlob()
    // See: https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement
    // Example: <output> = shapshotCanvas.toBlob()...
}
