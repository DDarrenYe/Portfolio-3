import * as THREE from "three";
import { mergeGeometries, mergeVertices } from "three/examples/jsm/utils/BufferGeometryUtils.js";

export const INK = new THREE.Color("#2a2d3a");

// Three hard bands: shade, mid, lit. Nearest filtering keeps the steps crisp.
const gradient = (() => {
  const t = new THREE.DataTexture(new Uint8Array([40, 165, 255]), 3, 1, THREE.RedFormat);
  t.minFilter = THREE.NearestFilter;
  t.magFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  t.needsUpdate = true;
  return t;
})();

const toonCache = new Map<string, THREE.MeshToonMaterial>();

/** Swap a Blender palette material (pal_<name>) for a flat toon material of the same colour. */
export function toonFor(src: THREE.Material): THREE.MeshToonMaterial {
  const key = src.name || (src as THREE.MeshStandardMaterial).color.getHexString();
  let m = toonCache.get(key);
  if (!m) {
    const color = (src as THREE.MeshStandardMaterial).color.clone();
    m = new THREE.MeshToonMaterial({ color, gradientMap: gradient, name: key });
    // lamps and windows glow a little so they never fall into the shade band
    if (key === "pal_lamp") m.emissive = color.clone().multiplyScalar(0.45);
    toonCache.set(key, m);
  }
  return m;
}

/** Shared by every outline material, so one update resizes all the lines. */
export const outlineUniforms = {
  uWidth: { value: 3 }, // line width in CSS pixels
  uResolution: { value: new THREE.Vector2(1, 1) }, // drawing-buffer size in CSS pixels
};

/**
 * Inverted-hull outline drawn at a constant width on screen, like an ink line.
 * Each vertex is pushed out along its smoothed normal in screen space; only back
 * faces are drawn, so the hull shows just beyond the silhouette. Each material has
 * its own colour so an NPC's outline can light up on hover.
 */
export function makeOutlineMaterial(color: THREE.ColorRepresentation = INK) {
  return new THREE.ShaderMaterial({
    uniforms: { ...outlineUniforms, uColor: { value: new THREE.Color(color) } },
    side: THREE.BackSide,
    vertexShader: /* glsl */ `
      uniform float uWidth;
      uniform vec2 uResolution;
      void main() {
        vec4 clip = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        vec3 n = normalize(normalMatrix * normal);
        vec2 dir = normalize(n.xy + vec2(1e-6));
        clip.xy += dir * uWidth * 2.0 / uResolution * clip.w;
        clip.z += 0.0004 * clip.w;
        gl_Position = clip;
      }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uColor;
      void main() { gl_FragColor = vec4(uColor, 1.0); }`,
  });
}

export const outlineMaterial = makeOutlineMaterial();

/**
 * Hull geometry for the outline: same positions, but with normals smoothed across
 * shared corners so the hull doesn't split open at hard box edges.
 */
export function outlineGeometry(src: THREE.BufferGeometry): THREE.BufferGeometry {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", src.getAttribute("position").clone());
  if (src.index) g.setIndex(src.index.clone());
  const merged = mergeVertices(g, 1e-4);
  merged.computeVertexNormals();
  return merged;
}

function toFloat(attr: THREE.BufferAttribute | THREE.InterleavedBufferAttribute): THREE.BufferAttribute {
  const out = new Float32Array(attr.count * attr.itemSize);
  for (let i = 0; i < attr.count; i++) {
    out[i * attr.itemSize] = attr.getX(i);
    out[i * attr.itemSize + 1] = attr.getY(i);
    if (attr.itemSize > 2) out[i * attr.itemSize + 2] = attr.getZ(i);
  }
  return new THREE.BufferAttribute(out, attr.itemSize);
}

/** Meshes too small to carry a line (eyes, blush, brows) stay unoutlined. */
function wantsOutline(mesh: THREE.Mesh, minRadius: number) {
  mesh.geometry.computeBoundingSphere();
  const s = new THREE.Vector3();
  mesh.getWorldScale(s);
  return (mesh.geometry.boundingSphere?.radius ?? 0) * Math.max(s.x, s.y, s.z) > minRadius;
}

/**
 * Give every mesh under root a toon material and its own outline child.
 * Used for animated models, where meshes must keep their own transforms.
 */
export function toonify(root: THREE.Object3D, minRadius = 0.05, outline: THREE.Material = outlineMaterial) {
  if (root.userData.toonified) return; // cached glTF scenes come back on remount
  root.userData.toonified = true;
  const meshes: THREE.Mesh[] = [];
  root.traverse((o) => {
    if ((o as THREE.Mesh).isMesh) meshes.push(o as THREE.Mesh);
  });
  root.updateMatrixWorld(true);
  for (const mesh of meshes) {
    mesh.material = toonFor(mesh.material as THREE.Material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    if (wantsOutline(mesh, minRadius)) {
      const hull = new THREE.Mesh(outlineGeometry(mesh.geometry), outline);
      hull.raycast = () => {};
      mesh.add(hull);
    }
  }
}

/**
 * Bake a static model into one mesh per material plus a single outline mesh.
 * The town has hundreds of small parts; this keeps it to a few dozen draw calls.
 */
export function bakeStatic(root: THREE.Object3D, minRadius = 0.05): THREE.Group {
  root.updateMatrixWorld(true);
  const byMat = new Map<string, { mat: THREE.MeshToonMaterial; geos: THREE.BufferGeometry[] }>();
  const hulls: THREE.BufferGeometry[] = [];
  root.traverse((o) => {
    const mesh = o as THREE.Mesh;
    if (!mesh.isMesh) return;
    const mat = toonFor(mesh.material as THREE.Material);
    const g = new THREE.BufferGeometry();
    // models arrive quantized (int16 positions, int8 normals); expand to floats before baking
    // in world transforms, or values outside [-1, 1] would be clamped
    for (const name of ["position", "normal"] as const) g.setAttribute(name, toFloat(mesh.geometry.getAttribute(name)));
    if (mesh.geometry.index) g.setIndex(mesh.geometry.index.clone());
    g.applyMatrix4(mesh.matrixWorld);
    const entry = byMat.get(mat.name) ?? { mat, geos: [] };
    entry.geos.push(g);
    byMat.set(mat.name, entry);
    if (wantsOutline(mesh, minRadius)) hulls.push(outlineGeometry(g));
  });
  const out = new THREE.Group();
  for (const { mat, geos } of byMat.values()) {
    const merged = mergeGeometries(geos.map((g) => (g.index ? g.toNonIndexed() : g)));
    const m = new THREE.Mesh(merged, mat);
    m.castShadow = true;
    m.receiveShadow = true;
    out.add(m);
  }
  const hull = new THREE.Mesh(mergeGeometries(hulls), outlineMaterial);
  hull.raycast = () => {};
  out.add(hull);
  return out;
}
