document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('camera-feed');
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    let stream;
  
    startCameraBtn.addEventListener('click', startCamera);
    stopCameraBtn.addEventListener('click', stopCamera);
  
    function startCamera() {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then((mediaStream) => {
          stream = mediaStream;
          video.srcObject = mediaStream;
          video.play();
          startCameraBtn.disabled = true;
          stopCameraBtn.disabled = false;
        })
        .catch((error) => {
          console.error('Error accessing the camera: ', error);
        });
    }
  
    function stopCamera() {
      if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
        startCameraBtn.disabled = false;
        stopCameraBtn.disabled = true;
      }
    }

  });
   