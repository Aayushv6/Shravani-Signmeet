import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import * as tf from '@tensorflow/tfjs';

const startApp = async () => {
  try {
    // Ensure TensorFlow.js is ready
    await tf.ready();

    // Try using WebGL backend first
    try {
      await tf.setBackend('webgl');
    } catch (e) {
      console.warn("⚠️ WebGL not supported. Falling back to CPU.");
      await tf.setBackend('cpu');
    }

    console.log("✅ TensorFlow.js backend:", tf.getBackend());

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  } catch (err) {
    console.error("❌ TensorFlow.js initialization failed:", err);
  }
};

startApp();