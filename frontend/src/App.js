import React, { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import * as handpose from "@tensorflow-models/handpose";
import "@tensorflow/tfjs-backend-webgl";

const App = () => {
  const webcamRef = useRef(null);
  const [gesture, setGesture] = useState("Detecting...");

  const runHandpose = async () => {
    const net = await handpose.load();

    setInterval(() => {
      detect(net);
    }, 2000);
  };

  const detect = async (net) => {
    if (
      webcamRef.current &&
      webcamRef.current.video.readyState === 4
    ) {
      const video = webcamRef.current.video;
      const hand = await net.estimateHands(video);

      if (hand.length > 0) {
        const landmarks = hand[0].landmarks.map(([x, y]) => [x, y, 0]);

        fetch(`${process.env.REACT_APP_API_URL}/api/recognize`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ landmarks }),
        })
          .then((res) => res.json())
          .then((data) => {
            if (data.name) {
              setGesture(data.name);
            } else {
              setGesture("Not recognized");
            }
          })
          .catch((err) => {
            console.error("Error recognizing gesture:", err);
            setGesture("Error");
          });
      }
    }
  };

  useEffect(() => {
    runHandpose();
  }, []);

  return (
    <div style={{ textAlign: "center", marginTop: "40px" }}>
      <h1>🖐 Gesture to Text</h1>
      <Webcam
        ref={webcamRef}
        style={{
          width: 400,
          height: 300,
          margin: "0 auto",
          borderRadius: 10,
        }}
      />
      <h2>Detected Gesture: {gesture}</h2>
    </div>
  );
};

export default App;