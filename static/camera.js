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
    var snapshotCanvas = document.getElementById('snapshot');
    //console.log("snapshotCanvas = " + snapshotCanvas);
    var context = snapshotCanvas.getContext('2d');
    //console.log("context = " + context);
    console.log("player.videoHeight = " + player.videoHeight);
    console.log("player.videoWidth = " + player.videoWidth);
    var newW = 200;
    var newH = player.videoHeight * (newW / player.videoWidth);
    console.log("new height, width = " + newH + ", " + newW);
    snapshotCanvas.width = newW;
    snapshotCanvas.height = newH;

    
    // Delete disp-area after calculating player size.
    document.getElementById('disp-area').style.display = "none";
    //document.getElementById('cap').style.display = "none";
    document.getElementById('disp-area2').style.display = "block";
    //document.getElementById('camback').style.display = "block";
 
    context.drawImage(player, 0, 0, newW, newH);

    // To output the canvas to image data : HTMLCanvasElement.toBlob()
    // See: https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement
    // Example: <output> = shapshotCanvas.toBlob()...
}
