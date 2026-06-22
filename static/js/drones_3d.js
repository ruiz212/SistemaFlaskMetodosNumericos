import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls;
let container;
let animationId;
let terrainGroup, pathGroup, droneMesh;

export function initScene(containerId) {
    container = document.getElementById(containerId);
    
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.FogExp2(0xb0d4e8, 0.00012);

    camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 1, 100000);
    camera.position.set(500, 800, 1200);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    container.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.maxPolarAngle = Math.PI / 2 - 0.05;

    // === ILUMINACIÓN SOLAR REALISTA ===
    const hemiLight = new THREE.HemisphereLight(0x87ceeb, 0x556633, 0.5);
    scene.add(hemiLight);

    const sunLight = new THREE.DirectionalLight(0xfff5e0, 1.6);
    sunLight.position.set(400, 900, 500);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.top = 3000;
    sunLight.shadow.camera.bottom = -3000;
    sunLight.shadow.camera.left = -3000;
    sunLight.shadow.camera.right = 3000;
    sunLight.shadow.camera.far = 6000;
    scene.add(sunLight);

    const fillLight = new THREE.DirectionalLight(0x8ec5e6, 0.3);
    fillLight.position.set(-300, 400, -400);
    scene.add(fillLight);

    // === SUELO BASE (tierra/pasto fuera de la ciudad) ===
    const groundGeo = new THREE.PlaneGeometry(80000, 80000);
    const groundMat = new THREE.MeshStandardMaterial({ color: 0x6b8a54, roughness: 1.0 });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.5;
    ground.receiveShadow = true;
    scene.add(ground);

    // Grupos
    terrainGroup = new THREE.Group();
    scene.add(terrainGroup);

    pathGroup = new THREE.Group();
    scene.add(pathGroup);

    droneMesh = createDroneMesh();
    scene.add(droneMesh);
    droneMesh.visible = false;

    window.addEventListener('resize', onWindowResize);
    animate();
}

function createDroneMesh() {
    const group = new THREE.Group();
    
    const bodyGeo = new THREE.CylinderGeometry(8, 8, 4, 6);
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0x222222, metalness: 0.8, roughness: 0.2 });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.castShadow = true;
    group.add(body);

    const armGeo = new THREE.BoxGeometry(40, 1.5, 3);
    const armMat = new THREE.MeshStandardMaterial({ color: 0x333333, metalness: 0.6, roughness: 0.3 });
    const arm1 = new THREE.Mesh(armGeo, armMat);
    arm1.rotation.y = Math.PI / 4;
    group.add(arm1);
    const arm2 = new THREE.Mesh(armGeo, armMat);
    arm2.rotation.y = -Math.PI / 4;
    group.add(arm2);

    const rotorGeo = new THREE.CylinderGeometry(10, 10, 0.5, 16);
    const rotorMat = new THREE.MeshStandardMaterial({ color: 0x10b981, transparent: true, opacity: 0.5 });
    const rotors = [];
    [[15,2,15],[-15,2,15],[15,2,-15],[-15,2,-15]].forEach(pos => {
        const rotor = new THREE.Mesh(rotorGeo, rotorMat);
        rotor.position.set(pos[0], pos[1], pos[2]);
        group.add(rotor);
        rotors.push(rotor);
    });
    group.userData.rotors = rotors;

    const pointLight = new THREE.PointLight(0xff3333, 3, 150);
    pointLight.position.set(0, -5, 0);
    group.add(pointLight);

    return group;
}

// ============================================================
//  RENDERIZADO DE CIUDAD REALISTA
// ============================================================

export function buildTerrain(edificios, size, calles, manzanas) {
    // Limpiar
    while(terrainGroup.children.length > 0){ 
        const child = terrainGroup.children[0];
        terrainGroup.remove(child);
        if (child.geometry) child.geometry.dispose();
    }

    controls.target.set(size/2, 0, size/2);
    camera.position.set(size/2, size * 0.6, size * 1.0);
    camera.updateProjectionMatrix();

    // === MATERIALES ===
    const matAsphalt     = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.95 });
    const matAsphaltDark = new THREE.MeshStandardMaterial({ color: 0x2a2a2a, roughness: 0.92 });
    const matSidewalk    = new THREE.MeshStandardMaterial({ color: 0xaaaaaa, roughness: 0.9 });
    const matLineYellow  = new THREE.MeshStandardMaterial({ color: 0xddcc44, roughness: 0.8 });
    const matLineWhite   = new THREE.MeshStandardMaterial({ color: 0xeeeeee, roughness: 0.8 });
    const matGreenBlock  = new THREE.MeshStandardMaterial({ color: 0x5a8a4a, roughness: 1.0 });
    
    // Materiales de edificios
    const matConcreteLight = new THREE.MeshStandardMaterial({ color: 0xe8e4dc, roughness: 0.85, metalness: 0.05 });
    const matConcreteMed   = new THREE.MeshStandardMaterial({ color: 0xc8c4bc, roughness: 0.88, metalness: 0.05 });
    const matConcreteDark  = new THREE.MeshStandardMaterial({ color: 0xa09890, roughness: 0.9, metalness: 0.05 });
    const matBrickRed      = new THREE.MeshStandardMaterial({ color: 0xb0705a, roughness: 0.85 });
    const matBrickBrown    = new THREE.MeshStandardMaterial({ color: 0x9a7a5a, roughness: 0.85 });
    const matGlassBlue     = new THREE.MeshStandardMaterial({ color: 0x7ab8d4, roughness: 0.08, metalness: 0.92 });
    const matGlassTeal     = new THREE.MeshStandardMaterial({ color: 0x6aaca0, roughness: 0.1, metalness: 0.9 });
    const matRoof          = new THREE.MeshStandardMaterial({ color: 0x777777, roughness: 0.85 });
    const matRoofDark      = new THREE.MeshStandardMaterial({ color: 0x555555, roughness: 0.9 });

    const residentialMats = [matConcreteLight, matConcreteMed, matBrickRed, matBrickBrown];
    const commercialMats  = [matConcreteDark, matConcreteMed, matBrickBrown];
    const downtownMats    = [matGlassBlue, matGlassTeal];

    // === 1. DIBUJAR CALLES (Geometría Real) ===
    if (calles && calles.length > 0) {
        calles.forEach(calle => {
            if (!calle.points || calle.points.length < 2) return;
            
            for (let i = 0; i < calle.points.length - 1; i++) {
                const p1 = calle.points[i];
                const p2 = calle.points[i+1];
                const dx = p2.x - p1.x;
                const dy = p2.y - p1.y;
                const dist = Math.hypot(dx, dy);
                
                if (dist < 0.1) continue;
                
                const angle = Math.atan2(-dy, dx);
                const cx = (p1.x + p2.x) / 2;
                const cy = (p1.y + p2.y) / 2;
                
                // Segmento de asfalto
                const segmentGeo = new THREE.PlaneGeometry(dist, calle.width);
                const segment = new THREE.Mesh(segmentGeo, calle.is_avenue ? matAsphaltDark : matAsphalt);
                segment.rotation.x = -Math.PI / 2;
                segment.rotation.z = angle;
                segment.position.set(cx, 0.05, cy);
                segment.receiveShadow = true;
                terrainGroup.add(segment);
                
                // Línea central
                const lineW = calle.is_avenue ? 0.6 : 0.3;
                const lineGeo = new THREE.PlaneGeometry(dist * 0.95, lineW);
                const lineMat = calle.is_avenue ? matLineYellow : matLineWhite;
                const line = new THREE.Mesh(lineGeo, lineMat);
                line.rotation.x = -Math.PI / 2;
                line.rotation.z = angle;
                line.position.set(cx, 0.08, cy);
                terrainGroup.add(line);
            }
        });
    }

    // === 2. DIBUJAR EDIFICIOS (Polígonos Reales) ===
    edificios.forEach(ed => {
        if (!ed.points || ed.points.length < 3) return;
        
        const buildingGroup = new THREE.Group();
        buildingGroup.position.set(ed.cx, 0, ed.cy);
        
        const shape = new THREE.Shape();
        ed.points.forEach((pt, idx) => {
            const localX = pt.x - ed.cx;
            const localY = -(pt.y - ed.cy);
            if (idx === 0) shape.moveTo(localX, localY);
            else shape.lineTo(localX, localY);
        });
        // Auto-close shape
        shape.lineTo(ed.points[0].x - ed.cx, -(ed.points[0].y - ed.cy));

        // Elegir material según zona
        const zone = ed.zone || 'residential';
        let wallMat, roofMat;
        
        if (zone === 'downtown') {
            wallMat = downtownMats[Math.floor(Math.random() * downtownMats.length)];
            roofMat = matRoofDark;
        } else if (zone === 'commercial') {
            wallMat = commercialMats[Math.floor(Math.random() * commercialMats.length)];
            roofMat = matRoof;
        } else {
            wallMat = residentialMats[Math.floor(Math.random() * residentialMats.length)];
            roofMat = matRoof;
        }

        const extrudeSettings = {
            depth: ed.h,
            bevelEnabled: false
        };
        const geo = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        
        // materials: [roof/floor, walls]
        const materials = [roofMat, wallMat];
        const mesh = new THREE.Mesh(geo, materials);
        
        mesh.rotation.x = -Math.PI / 2;
        mesh.position.set(0, 0, 0);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        buildingGroup.add(mesh);
        
        terrainGroup.add(buildingGroup);

        // Árboles ocasionales cerca del edificio (zonas residenciales)
        if (zone === 'residential' && Math.random() > 0.7) {
            const trunkGeo = new THREE.CylinderGeometry(0.4, 0.6, 4, 6);
            const trunkMat = new THREE.MeshStandardMaterial({ color: 0x5a3a1a, roughness: 0.9 });
            const foliageGeo = new THREE.SphereGeometry(3, 8, 6);
            const foliageMats = [
                new THREE.MeshStandardMaterial({ color: 0x3a7a2a, roughness: 0.9 }),
                new THREE.MeshStandardMaterial({ color: 0x4a8a3a, roughness: 0.9 }),
                new THREE.MeshStandardMaterial({ color: 0x2a6a1a, roughness: 0.9 }),
            ];
            
            const treeGroup = new THREE.Group();
            const tx = ed.cx + (Math.random() - 0.5) * 20;
            const ty = ed.cy + (Math.random() - 0.5) * 20;
            treeGroup.position.set(tx, 0, ty);

            const trunk = new THREE.Mesh(trunkGeo, trunkMat);
            trunk.position.y = 2;
            treeGroup.add(trunk);

            const foliage = new THREE.Mesh(foliageGeo, foliageMats[Math.floor(Math.random() * 3)]);
            foliage.position.y = 5.5;
            foliage.scale.set(1, 0.8 + Math.random() * 0.4, 1);
            treeGroup.add(foliage);

            terrainGroup.add(treeGroup);
        }
    });
}

export function drawPaths(rutaCruda, rutaSuave) {
    while(pathGroup.children.length > 0){ 
        pathGroup.remove(pathGroup.children[0]); 
    }

    const ptsCrudos = rutaCruda.map(p => new THREE.Vector3(p[0], p[2], p[1]));
    const geoCruda = new THREE.BufferGeometry().setFromPoints(ptsCrudos);
    const matCruda = new THREE.LineDashedMaterial({ 
        color: 0xef4444, linewidth: 1, scale: 1, dashSize: 10, gapSize: 10 
    });
    const lineCruda = new THREE.Line(geoCruda, matCruda);
    lineCruda.computeLineDistances();
    pathGroup.add(lineCruda);

    const ptsSuaves = rutaSuave.map(p => new THREE.Vector3(p[0], p[2], p[1]));
    const geoSuave = new THREE.BufferGeometry().setFromPoints(ptsSuaves);
    const matSuave = new THREE.LineBasicMaterial({ color: 0x10b981, linewidth: 3 });
    const lineSuave = new THREE.Line(geoSuave, matSuave);
    pathGroup.add(lineSuave);

    const wpGeo = new THREE.SphereGeometry(6, 16, 16);
    const wpMat = new THREE.MeshBasicMaterial({ color: 0x06b6d4 });
    ptsCrudos.forEach((pt, i) => {
        if(i > 0 && i < ptsCrudos.length - 1 && i % 2 !== 0) return;
        const mesh = new THREE.Mesh(wpGeo, wpMat);
        mesh.position.copy(pt);
        pathGroup.add(mesh);
    });

    droneMesh.position.copy(ptsSuaves[0]);
    droneMesh.visible = true;
}

export function resetScene() {
    while(terrainGroup.children.length > 0) terrainGroup.remove(terrainGroup.children[0]);
    while(pathGroup.children.length > 0) pathGroup.remove(pathGroup.children[0]);
    droneMesh.visible = false;
    if(animationId) cancelAnimationFrame(animationId);
}

export function animateFlight(rutaSuave, telemetria, onUpdateMetrics, onComplete) {
    const pts = rutaSuave.map(p => new THREE.Vector3(p[0], p[2], p[1]));
    const n = pts.length;
    let index = 0;
    
    let totalFrames = 60 * 8;
    let framesPerSegment = Math.max(1, Math.floor(totalFrames / n));
    let currentFrame = 0;

    let smoothDirection = new THREE.Vector3(0, 0, 1);

    function renderFlight() {
        if (index >= n - 1) {
            if(onComplete) onComplete();
            return;
        }

        const p0 = pts[index];
        const p1 = pts[index + 1];
        
        const t = currentFrame / framesPerSegment;
        const currentPos = new THREE.Vector3().lerpVectors(p0, p1, t);
        
        droneMesh.position.copy(currentPos);
        
        // Dirección de vuelo real (no Euler)
        const flightDir = new THREE.Vector3().subVectors(p1, p0).normalize();
        smoothDirection.lerp(flightDir, 0.1);
        smoothDirection.normalize();
        
        const lookTarget = currentPos.clone().add(smoothDirection.clone().multiplyScalar(50));
        droneMesh.lookAt(lookTarget);
        
        if(droneMesh.userData.rotors) {
            droneMesh.userData.rotors.forEach(r => { r.rotation.y += 0.5; });
        }
        
        const vel = telemetria.velocidad[index];
        const posInt = telemetria.posicion_integrada[index];
        onUpdateMetrics(vel, posInt);

        // Cámara DETRÁS del dron usando vector de dirección
        const behindOffset = smoothDirection.clone().multiplyScalar(-200);
        behindOffset.y += 80;
        const desiredCameraPos = currentPos.clone().add(behindOffset);
        camera.position.lerp(desiredCameraPos, 0.06);
        
        const lookAhead = currentPos.clone().add(smoothDirection.clone().multiplyScalar(100));
        lookAhead.y -= 20;
        controls.target.lerp(lookAhead, 0.08);

        currentFrame++;
        if (currentFrame >= framesPerSegment) {
            currentFrame = 0;
            index++;
        }

        animationId = requestAnimationFrame(renderFlight);
    }
    
    renderFlight();
}

function onWindowResize() {
    if (!camera || !renderer || !container) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
