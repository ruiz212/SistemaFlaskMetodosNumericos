/**
 * ============================================================================
 * GEMELO DIGITAL 3D - SIMULADOR PANEL SOLAR (THREE.JS)
 * ============================================================================
 * Renderiza un modelo 3D físico de un panel solar y expone un método
 * para rotarlo programáticamente basándose en el cálculo de optimización.
 */

let scene, camera, renderer, panelGroup;
let targetRotationX = 0;
let currentRotationX = 0;

function init3DModel() {
    const container = document.getElementById('solar-3d-canvas');
    if (!container) return;

    // 1. SCENE & CAMERA
    scene = new THREE.Scene();
    
    // Add subtle ambient fog to blend with the dark background
    scene.fog = new THREE.FogExp2(0x09090b, 0.02);

    const width = container.clientWidth;
    const height = container.clientHeight;
    
    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 4, 10);
    camera.lookAt(0, 0, 0);

    // 2. RENDERER
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // Perf optimization
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // 3. LIGHTING
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 1.2);
    sunLight.position.set(5, 10, 5);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 1024;
    sunLight.shadow.mapSize.height = 1024;
    scene.add(sunLight);

    // Fill light from opposite side (bluish for sky reflection)
    const fillLight = new THREE.DirectionalLight(0x40a0ff, 0.3);
    fillLight.position.set(-5, 5, -5);
    scene.add(fillLight);

    // 4. CREATE THE SOLAR PANEL MODEL
    panelGroup = new THREE.Group();
    
    // Base/Pole
    const poleGeo = new THREE.CylinderGeometry(0.2, 0.3, 3, 16);
    const poleMat = new THREE.MeshStandardMaterial({ 
        color: 0x555555, 
        metalness: 0.8, 
        roughness: 0.4 
    });
    const pole = new THREE.Mesh(poleGeo, poleMat);
    pole.position.y = 1.5;
    pole.castShadow = true;
    scene.add(pole);

    // The Panel Surface (Pivot mechanism)
    const pivot = new THREE.Group();
    pivot.position.y = 3; // Top of the pole
    scene.add(pivot);

    // The Solar Panel itself
    const panelWidth = 6;
    const panelHeight = 0.1;
    const panelDepth = 4;
    
    const panelGeo = new THREE.BoxGeometry(panelWidth, panelHeight, panelDepth);
    
    // Multi-material for the panel (Dark blue top, silver frame)
    const glassMat = new THREE.MeshStandardMaterial({
        color: 0x051024,
        metalness: 0.9,
        roughness: 0.1,
        envMapIntensity: 1.0
    });
    const frameMat = new THREE.MeshStandardMaterial({
        color: 0xdddddd,
        metalness: 0.9,
        roughness: 0.2
    });

    const materials = [
        frameMat, // right
        frameMat, // left
        glassMat, // top
        frameMat, // bottom
        frameMat, // front
        frameMat  // back
    ];

    const panelMesh = new THREE.Mesh(panelGeo, materials);
    panelMesh.castShadow = true;
    
    // We want the panel to rotate around its center, which is at the pivot
    pivot.add(panelMesh);
    
    // Add grid lines to simulate solar cells
    createSolarCellsGrid(panelMesh, panelWidth, panelDepth);

    // We keep a reference to the pivot to animate its rotation later
    panelGroup.add(pivot);
    scene.add(panelGroup);

    // Ground Plane
    const groundGeo = new THREE.PlaneGeometry(30, 30);
    const groundMat = new THREE.MeshStandardMaterial({ 
        color: 0x111111, 
        roughness: 0.9 
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // 5. INTERACTION (Simple Mouse Drag)
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };

    renderer.domElement.addEventListener('mousedown', () => isDragging = true);
    window.addEventListener('mouseup', () => isDragging = false);
    window.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const deltaMove = {
                x: e.offsetX - previousMousePosition.x,
                y: e.offsetY - previousMousePosition.y
            };
            
            // Rotate the entire scene group around Y axis
            panelGroup.rotation.y += deltaMove.x * 0.01;
        }
        previousMousePosition = { x: e.offsetX, y: e.offsetY };
    });

    // Handle Window Resize
    window.addEventListener('resize', () => {
        const w = container.clientWidth;
        const h = container.clientHeight;
        renderer.setSize(w, h);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
    });

    // 6. RENDER LOOP
    function animate() {
        requestAnimationFrame(animate);

        // Smoothly interpolate current rotation to target rotation (easing)
        currentRotationX += (targetRotationX - currentRotationX) * 0.05;
        pivot.rotation.x = currentRotationX;

        renderer.render(scene, camera);
    }
    animate();
}

function createSolarCellsGrid(parentMesh, w, d) {
    // Add subtle white lines to make it look like a real solar panel
    const gridMat = new THREE.LineBasicMaterial({ color: 0x445577, transparent: true, opacity: 0.5 });
    
    const rows = 12;
    const cols = 8;
    
    // Horizontal lines
    for(let i = 1; i < rows; i++) {
        const z = (d/2) - (d/rows) * i;
        const pts = [];
        pts.push(new THREE.Vector3(-w/2 + 0.1, 0.06, z));
        pts.push(new THREE.Vector3(w/2 - 0.1, 0.06, z));
        const geo = new THREE.BufferGeometry().setFromPoints(pts);
        parentMesh.add(new THREE.Line(geo, gridMat));
    }

    // Vertical lines
    for(let i = 1; i < cols; i++) {
        const x = (w/2) - (w/cols) * i;
        const pts = [];
        pts.push(new THREE.Vector3(x, 0.06, -d/2 + 0.1));
        pts.push(new THREE.Vector3(x, 0.06, d/2 - 0.1));
        const geo = new THREE.BufferGeometry().setFromPoints(pts);
        parentMesh.add(new THREE.Line(geo, gridMat));
    }
}

/**
 * Public API to update the 3D model from the Flask frontend
 * @param {number} angleDegrees The calculated optimal angle
 */
window.actualizarModelo3D = function(angleDegrees) {
    // Convert degrees to radians.
    // Three.js rotation: +x tilts it backwards depending on setup.
    // We'll tilt it forward/backward by the angle.
    targetRotationX = THREE.MathUtils.degToRad(angleDegrees);
    
    // Update the UI badge
    const badge = document.getElementById('badge-angulo');
    if (badge) {
        badge.innerText = `${angleDegrees.toFixed(2)}°`;
        
        // Flash animation
        badge.style.transition = 'none';
        badge.style.backgroundColor = 'rgba(245, 158, 11, 0.8)';
        badge.style.color = '#fff';
        
        setTimeout(() => {
            badge.style.transition = 'all 0.8s ease';
            badge.style.backgroundColor = '';
            badge.style.color = '';
        }, 50);
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if Three.js loaded
    if (typeof THREE !== 'undefined') {
        init3DModel();
    } else {
        console.error("Three.js was not loaded.");
    }
});
