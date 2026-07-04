import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

function Viewer3D({ model }) {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 2;
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    // Load 3D model
    const textureLoader = new THREE.TextureLoader();
    
    // Simple mesh placeholder (in production, use proper GLB/GLTF loader)
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshPhongMaterial({ color: 0x4CAF50 });
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // Animation
    const animate = () => {
      requestAnimationFrame(animate);
      mesh.rotation.x += 0.005;
      mesh.rotation.y += 0.005;
      renderer.render(scene, camera);
    };
    animate();

    // Handle window resize
    const handleResize = () => {
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, [model]);

  return (
    <div className="viewer-3d">
      <div className="viewer-header">
        <h3>3D Model Preview</h3>
        <div className="model-info">
          <span>Vertices: {model.vertices?.toLocaleString()}</span>
          <span>Faces: {model.faces?.toLocaleString()}</span>
          <span>Format: {model.format?.toUpperCase()}</span>
        </div>
      </div>
      <div className="viewer-container" ref={containerRef} />
      <div className="viewer-footer">
        <a href={model.download_url} className="download-btn">
          Download Model
        </a>
      </div>
    </div>
  );
}

export default Viewer3D;
