function loadCamera() {
    document.getElementById('disp-area2').style.display = "none";
    var player = document.getElementById('player');

    console.log("player = " + player);
 
    var handleSuccess = function(stream){
        player.srcObject = stream;
        //document.getElementById('player').style.visibility = "visible";
        //document.getElementById('cap').style.display = "block";
        document.getElementById('disp-area').style.display = "block";
        document.getElementById('player').style.display = "block";        
        document.getElementById('cap').style.display = "block";
    }

    constrains = {
                    audio: false,
                    video: true
                    //video: { facingMode: { exact: "environment" }}
                 } ;

    navigator.mediaDevices.getUserMedia(constrains)
        .then(handleSuccess)
        .catch(function(err){
            console.log("Camera open error: " + err);
            ducument.getElementById('disp-area').innerHTML = "Camera open error:" + err;
        });

}

//window.onload = loadCamera();
function clickCapture() {
    var player = document.getElementById('player');
    //var snapshotCanvas = document.getElementById('snapshot');

    var tempCanvas = document.createElement('canvas');
    tempCanvas.width = player.videoWidth;
    tempCanvas.height = player.videoHeight;
    

    var context = tempCanvas.getContext('2d');
    context.drawImage(player, 0, 0, tempCanvas.width, tempCanvas.height);

    // Send image to save on a server
    var dataURL = tempCanvas.toDataURL("image/png");

    console.log("dataURL = " + dataURL);
    //var fd = new FormData();
    //fd.append("image", dataURL);
    //fd.append("check", "ok");

    $.ajax({
        method: 'POST',
        url: '/canvas',
        data: { 'image': dataURL, 'check': 'ok'}
        //processData: false,
        //processType: false
    })
    .done(function(msg) {
        console.log("Save canvas done!")
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
    
    // Delete disp-area after calculating player size.
    document.getElementById('disp-area').style.display = "none";
    //document.getElementById('cap').style.display = "none";
    document.getElementById('disp-area2').style.display = "block";
    //document.getElementById('camback').style.display = "block";
 
    //context.drawImage(player, 0, 0, newW, newH);

    // To output the canvas to image data : HTMLCanvasElement.toBlob()
    // See: https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement
    // Example: <output> = shapshotCanvas.toBlob()...
}
