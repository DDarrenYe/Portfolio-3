// Shrinks town.glb for the web: bakes the hierarchy, joins parts that share a material,
// welds and quantizes vertices. No decoder is needed to load the result.
// Pruning drops empty nodes, so the named markers (spot_*, smoke_*) are recorded first
// and added back afterwards at the same world positions.
import { NodeIO } from "@gltf-transform/core";
import { KHRONOS_EXTENSIONS } from "@gltf-transform/extensions";
import { flatten, join, prune, quantize, weld } from "@gltf-transform/functions";

const [input, output] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(KHRONOS_EXTENSIONS);
const doc = await io.read(input);

const markers = doc
  .getRoot()
  .listNodes()
  .filter((n) => /^(spot|smoke)_/.test(n.getName()))
  .map((n) => ({ name: n.getName(), matrix: n.getWorldMatrix() }));

await doc.transform(flatten(), join({ keepNamed: false }), weld(), quantize(), prune());

const scene = doc.getRoot().listScenes()[0];
for (const { name, matrix } of markers) scene.addChild(doc.createNode(name).setMatrix(matrix));

await io.write(output, doc);
console.log(`${output}: ${doc.getRoot().listMeshes().length} meshes, ${markers.length} markers`);
