// labil v2 — objetos, sus versiones y borradores. Rutas: #/ · #/<objeto>/<estado> · #/historial
const app = document.getElementById("app");
const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;
let DATOS = null;
let VER = "";

const TIPO = {
  version: { txt: "impresa", cls: "version" },
  pendiente: { txt: "por imprimir", cls: "pendiente" },
  prueba: { txt: "prueba", cls: "prueba" },
  borrador: { txt: "borrador", cls: "borrador" },
};
// el objeto puede cambiar las palabras (la web se «publica», no se «imprime»)
const tipoDe = (e, o) => {
  const t = e.tipo === "version" && e.por_imprimir ? TIPO.pendiente : TIPO[e.tipo];
  const p = (o && o.palabras) || {};
  if (t === TIPO.version && p.version) return { ...t, txt: p.version };
  if (t === TIPO.pendiente && p.pendiente) return { ...t, txt: p.pendiente };
  return t;
};

const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
const fecha = (iso) => { const [a, m, d] = iso.split("-").map(Number); return `${d} ${MESES[m - 1]}`; };
const fechaLarga = (iso) => { const [a, m, d] = iso.split("-").map(Number); return `${d} ${MESES[m - 1]} ${a}`; };
const eur = (n) => n.toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
const gr = (n) => n.toLocaleString("es-ES", { maximumFractionDigits: n < 10 ? 1 : 0 }) + " g";
const firma = (n, f) => (n > 0 ? "+" : n < 0 ? "−" : "±") + f(Math.abs(n));
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const conVer = (src) => (VER ? `${src}?v=${VER}` : src);

// ── cifra en bitmap (BitFigure): 5 filas, columnas de 3 px ─────────────────────
const GLIFOS = {
  "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
  "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
  "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
  "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "001", "001", "001"],
  "8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "111"],
  ",": ["0", "0", "0", "1", "1"], ".": ["0", "0", "0", "0", "1"],
  "€": ["0111", "1000", "1110", "1000", "0111"], " ": ["0", "0", "0", "0", "0"],
  "+": ["000", "010", "111", "010", "000"], "−": ["000", "000", "111", "000", "000"],
};
function bit(texto, tam = "") {
  const glifos = [...texto].map((ch) => {
    const filas = GLIFOS[ch] || GLIFOS[" "];
    let celdas = "";
    for (let c = 0; c < filas[0].length; c++)
      for (let r = 0; r < 5; r++) celdas += `<i${filas[r][c] === "1" ? ' class="on"' : ""}></i>`;
    return `<span class="g">${celdas}</span>`;
  });
  return `<span class="bit ${tam}" role="img" aria-label="${esc(texto)}">${glifos.join("")}</span>`;
}
const bitEur = (n, tam) => bit(n.toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €", tam);

// ── descifrar: el texto llega como ruido y se ordena de izquierda a derecha ────
const RUIDO = "▖▗▘▙▚▛▜▝▞▟01/\\";
function descifra(el) {
  if (!el || reducido) return;
  const final = el.textContent;
  let i = 0;
  const paso = () => {
    i++;
    el.textContent = final.slice(0, i) +
      [...final.slice(i)].map((c) => (c === " " ? " " : RUIDO[(Math.random() * RUIDO.length) | 0])).join("");
    if (i < final.length) setTimeout(paso, 16);
  };
  paso();
}

// ── cabecera ─────────────────────────────────────────────────────────────────
function cabecera(actual, donde = "") {
  return `<header class="top${donde ? " en-objeto" : ""}">
    ${donde
      ? `<a class="volver control" href="#/" aria-label="volver a objetos">← objetos</a><span class="donde title">${esc(donde)}</span>`
      : `<a class="marca" href="#/"><img src="icon.svg" alt=""><span class="label">l a b i l</span></a>`}
  </header>`;
}
function pie() {
  return `<footer class="pie">
    <p class="caption">coste = plástico a ${DATOS.euros_kg} €/kg. Gramos estimados con un laminador simplificado
      (${esc(DATOS.perfil)}), contrastado con el laminador real: error medio 4 %, máximo 9 %.
      No incluye purga de cambios de color ni la luz de la impresora.</p>
    <p class="caption"><a class="enlace" href="#/historial">historial</a> · <a class="enlace" href="v1/">archivo · web v1</a> · actualizado ${esc(DATOS.generado.slice(0, 10))}</p>
  </footer>`;
}

// ── inicio: de la letra al objeto (motion graphics) y, debajo, los objetos ────
// Casi sin texto: la marca y una palabra por fase.
//   1 definición · una frase se escribe
//   2 diseño     · sus letras se ordenan en la pieza, en la rejilla de píxeles
//   3 cálculo    · una fuerza de 20 N en el borde; la tensión crece hasta la unión
//                  brazo-pata y su valor (17 MPa) se compara con el límite (20)
//   4 impresión  · una impresora 3D imprime la placa real de el secadero v2, capa a capa
//   5 montaje    · las piezas salen de la placa y se montan en el grifo
const FASES = [
  { palabra: "definición", ms: 2400 },
  { palabra: "diseño", ms: 1900 },
  { palabra: "cálculo", ms: 3800 },
  { palabra: "impresión", ms: 5600 },
  { palabra: "montaje", ms: 7200 },
];
const FRASE = "un soporte para el estropajo";

function vistaInicio() {
  const filas = DATOS.objetos.map((o) => {
    const ultimo = o.estados[o.estados.length - 1];
    const impresas = o.estados.filter((e) => e.tipo === "version" && !e.por_imprimir).length;
    return `<li><a class="panel obj" href="#/${o.id}">
      <div class="obj-cab"><h2 class="title">${esc(o.nombre)}</h2>
        ${ultimo.coste ? `<span class="strong signal">${eur(ultimo.coste.euros)}</span>` : ""}</div>
      <p class="body muted">${esc(o.que)}</p>
      <div class="ticks" aria-hidden="true">${o.estados.map((e) => `<i class="${tipoDe(e, o).cls}"></i>`).join("")}</div>
      <p class="caption">${o.estados.length} estados · ${impresas} ${((o.palabras && o.palabras.version) || "impresa") + (impresas === 1 ? "" : "s")} · ${esc(o.estado)} · ${fecha(ultimo.fecha)}</p>
    </a></li>`;
  }).join("");
  app.innerHTML = `<section class="portada">
      <h1 class="sr">labil: de la letra al objeto</h1>
      <div class="escenario" aria-hidden="true"><canvas id="lienzo-3d"></canvas><canvas id="lienzo-portada"></canvas></div>
      <header class="portada-cab"><img src="icon.svg" alt=""><span class="label">l a b i l</span></header>
      <div class="portada-pie">
        <p class="fase-palabra" id="fase-palabra" aria-hidden="true"></p>
        <ol class="fases" aria-hidden="true">${FASES.map(() => "<li></li>").join("")}</ol>
        <button class="bajar" id="bajar" aria-label="ver los objetos"><span aria-hidden="true">↓</span></button>
      </div>
    </section>
    <main id="objetos">
      <h2 class="label titulo-objetos">objetos</h2>
      <ol class="lista">${filas}</ol>
      <div class="leyenda caption">
        <span class="status version">impresa</span><span class="status pendiente">por imprimir</span>
        <span class="status prueba">prueba</span><span class="status borrador">borrador</span>
      </div>
      ${pie()}
    </main>`;
  document.getElementById("bajar").addEventListener("click", () =>
    document.getElementById("objetos").scrollIntoView({ behavior: reducido ? "auto" : "smooth" }));
  document.title = "labil · de la letra al objeto";
  animarPortada();
}

const C = { apagado: "rgba(201,225,201,0.07)", tinta: "#f3fbf1", muda: "#c9e1c9", tenue: "#86a08a",
  senal: "#24e824", aviso: "#f2a516" };
// la pieza en la rejilla (40 × 26): el secadero de perfil — abrazadera, brazo, pata y cuna
function piezaPortada() {
  const W = 40, H = 26, on = new Set();
  const rect = (x0, y0, x1, y1) => { for (let x = x0; x <= x1; x++) for (let y = y0; y <= y1; y++) on.add(x + "," + y); };
  rect(3, 0, 13, 1); rect(3, 0, 4, 7); rect(12, 0, 13, 7);
  rect(3, 6, 31, 8); rect(28, 6, 30, 23);
  rect(21, 22, 38, 24); rect(21, 15, 22, 24); rect(37, 15, 38, 24);
  return { W, H, celdas: [...on].map((k) => k.split(",").map(Number)) };
}

let animacion = 0;
function animarPortada() {
  const plano = document.getElementById("lienzo-portada");
  const lienzo3d = document.getElementById("lienzo-3d");
  if (!plano) return;
  const ctx = plano.getContext("2d");
  const palabra = document.getElementById("fase-palabra");
  const marcas = [...document.querySelectorAll(".fases li")];
  const pieza = piezaPortada();
  const INICIO = FASES.map((_, k) => FASES.slice(0, k).reduce((a, f) => a + f.ms, 0));
  const TOTAL = FASES.reduce((a, f) => a + f.ms, 0);
  const id = ++animacion;
  let dims = null, origen = [], faseVista = -1, impresora = null;

  const tamFrase = (w) => Math.max(12, Math.min(Math.floor(w / 14), Math.floor((w * 0.86) / (FRASE.length * 0.6))));
  function medir() {
    const r = plano.getBoundingClientRect(), dpr = Math.min(2, devicePixelRatio || 1);
    plano.width = Math.round(r.width * dpr); plano.height = Math.round(r.height * dpr);
    const cel = Math.max(4, Math.floor(Math.min((r.width * 0.86) / pieza.W, (r.height * 0.5) / pieza.H)));
    dims = { w: r.width, h: r.height, dpr, cel, ox: Math.floor((r.width - pieza.W * cel) / 2), oy: Math.floor((r.height - pieza.H * cel) / 2) };
    // píxeles de la frase: de aquí salen los píxeles que forman la pieza
    const t = document.createElement("canvas"); t.width = Math.ceil(r.width); t.height = Math.ceil(r.height);
    const tc = t.getContext("2d"); tc.fillStyle = "#fff"; tc.textAlign = "center"; tc.textBaseline = "middle";
    tc.font = `500 ${tamFrase(r.width)}px "JetBrains Mono", monospace`;
    tc.fillText(FRASE, r.width / 2, r.height / 2);
    const px = tc.getImageData(0, 0, t.width, t.height).data, paso = 3;
    origen = [];
    for (let y = 0; y < t.height; y += paso) for (let x = 0; x < t.width; x += paso)
      if (px[(y * t.width + x) * 4 + 3] > 128) origen.push([x, y]);
    if (!origen.length) origen = [[r.width / 2, r.height / 2]];
    if (impresora) impresora.medir();
  }
  medir();
  addEventListener("resize", () => id === animacion && medir());

  const celda = (x, y, color) => {
    const { cel, ox, oy, dpr } = dims, m = Math.max(1, Math.floor(cel * 0.14));
    ctx.fillStyle = color;
    ctx.fillRect((ox + x * cel + m) * dpr, (oy + y * cel + m) * dpr, (cel - 2 * m) * dpr, (cel - 2 * m) * dpr);
  };
  const escalon = (t, n) => Math.floor(Math.min(1, Math.max(0, t)) * n) / n; // a saltos (solo en la rejilla)
  const curva = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));       // transiciones suaves

  function mostrarFase(k) {
    if (k === faseVista) return;
    faseVista = k;
    palabra.classList.remove("entra"); void palabra.offsetWidth; palabra.classList.add("entra");
    palabra.textContent = FASES[k].palabra; descifra(palabra);
    marcas.forEach((m, j) => { m.classList.toggle("hecha", j < k); m.classList.toggle("ahora", j === k); });
  }

  // la impresora 3D (three.js) se carga aparte; si no se puede, la impresión se hace en la rejilla
  cargarImpresora(lienzo3d).then((imp) => { if (id === animacion) impresora = imp; }).catch(() => {});

  // tensión de cada celda: crece hacia la unión brazo-pata (29, 7), donde se concentra el par
  const tension = new Map(pieza.celdas.map(([x, y]) => [x + "," + y, Math.max(0, 1 - Math.hypot(x - 29, y - 7) / 26)]));
  // camino de la carga: desde el fondo de la cuna (33, 22) por la estructura
  const pasos = new Map(); {
    const cola = [[33, 22]]; pasos.set("33,22", 0);
    while (cola.length) {
      const [x, y] = cola.shift();
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const kk = `${x + dx},${y + dy}`;
        if (tension.has(kk) && !pasos.has(kk)) { pasos.set(kk, pasos.get(`${x},${y}`) + 1); cola.push([x + dx, y + dy]); }
      }
    }
  }
  const maxPaso = Math.max(...pasos.values());
  function texto(t, x, y, color, tam = 12, alin = "left") {
    ctx.fillStyle = color; ctx.textAlign = alin; ctx.textBaseline = "middle";
    ctx.font = `500 ${tam * dims.dpr}px "JetBrains Mono", monospace`;
    ctx.fillText(t, x * dims.dpr, y * dims.dpr);
  }
  function dibujarCalculo(f) {
    const { cel, ox, oy, dpr } = dims;
    // 1) la fuerza: una flecha de píxeles que baja hasta el fondo de la cuna (33, 22)
    const baja = curva(f / 0.18);
    const punta = oy + 21.6 * cel - (1 - baja) * cel * 3, fx = ox + 33.5 * cel, p = cel * 0.6;
    ctx.fillStyle = C.tinta;
    for (let i = 1; i <= 4; i++) ctx.fillRect((fx - p / 2) * dpr, (punta - p * (i + 1.2)) * dpr, p * dpr, p * 0.8 * dpr);
    ctx.fillRect((fx - p * 1.5) * dpr, (punta - p * 1.2) * dpr, p * 3 * dpr, p * 0.6 * dpr);
    ctx.fillRect((fx - p / 2) * dpr, (punta - p * 0.6) * dpr, p * dpr, p * 0.6 * dpr);
    texto("20 N", fx, punta - p * 6.5, C.tinta, 12, "center");
    // 2) la tensión recorre la estructura desde la carga y se colorea según su valor
    const frente = curva((f - 0.15) / 0.5) * maxPaso;
    pieza.celdas.forEach(([x, y]) => {
      const kk = x + "," + y;
      if (pasos.get(kk) > frente) return celda(x, y, C.muda);
      const v = tension.get(kk);
      celda(x, y, v > 0.85 ? C.aviso : v > 0.55 ? C.senal : C.tenue);
    });
    // 3) el valor: 17 MPa en la unión, frente al límite de 20
    if (f > 0.62) {
      const g = curva((f - 0.62) / 0.3);
      const hx = ox + 29.5 * cel, hy = oy + 7.5 * cel;
      ctx.strokeStyle = C.aviso; ctx.lineWidth = dpr;
      ctx.beginPath(); ctx.moveTo(hx * dpr, hy * dpr); ctx.lineTo((hx + cel * 3) * dpr, (hy - cel * 4) * dpr); ctx.stroke();
      texto(`${Math.round(17 * g)} MPa`, hx + cel * 3.5, hy - cel * 4, C.aviso, 13);
      // medidor: 0 ── 17 ── 20 (límite del PLA en el plano de capa)
      const mx = ox, my = oy + pieza.H * cel + cel * 2.2, mw = pieza.W * cel;
      ctx.fillStyle = C.apagado.replace("0.07", "0.2"); ctx.fillRect(mx * dpr, my * dpr, mw * dpr, 3 * dpr);
      ctx.fillStyle = C.aviso; ctx.fillRect(mx * dpr, my * dpr, mw * (17 / 20) * g * dpr, 3 * dpr);
      texto("0", mx, my + 12, C.tenue, 11);
      texto(g >= 1 ? "límite 20 MPa ✓" : "límite 20 MPa", mx + mw, my + 12, g >= 1 ? C.senal : C.tenue, 11, "right");
    }
  }

  function dibujar(ms) {
    if (id !== animacion || !document.body.contains(plano)) return;
    const { w, h, dpr } = dims;
    const t = reducido ? TOTAL - 1 : ms % TOTAL;
    const k = INICIO.findIndex((ini, j) => t >= ini && t < ini + FASES[j].ms);
    const f = (t - INICIO[k]) / FASES[k].ms;
    mostrarFase(k);
    ctx.clearRect(0, 0, w * dpr, h * dpr);

    // capas visibles: la rejilla hasta «se imprime»; la impresora desde ahí
    // fundidos: la rejilla se funde con la impresora (1,3 s) y, al final del montaje,
    // todo se apaga despacio antes de volver a escribir
    const con3d = impresora && k >= 3;
    let fundido = con3d && k === 3 ? curva(f / 0.24) : con3d ? 1 : 0;
    if (con3d && k === 4) fundido = 1 - curva((f - 0.93) / 0.07);
    plano.style.opacity = String(con3d ? 1 - (k === 3 ? curva(f / 0.24) : 1) : k === 0 ? curva(f / 0.15) : 1);
    lienzo3d.style.opacity = String(fundido);

    if (k === 0) { // escribes
      const n = Math.floor(FRASE.length * Math.min(1, f * 1.25));
      ctx.fillStyle = C.tinta; ctx.textAlign = "left"; ctx.textBaseline = "middle";
      ctx.font = `500 ${tamFrase(w) * dpr}px "JetBrains Mono", monospace`;
      const x0 = (w * dpr - ctx.measureText(FRASE).width) / 2;
      ctx.fillText(FRASE.slice(0, n) + (Math.floor(ms / 380) % 2 ? "▌" : ""), x0, (h / 2) * dpr);
    } else {
      for (let x = 0; x < pieza.W; x++) for (let y = 0; y < pieza.H; y++) celda(x, y, C.apagado);
      if (k === 1) { // se diseña: las letras se ordenan en la pieza
        const s = curva(f * 1.15), { cel, ox, oy } = dims;
        pieza.celdas.forEach(([x, y], i) => {
          const [sx, sy] = origen[(i * 7) % origen.length];
          const px = sx + (ox + x * cel - sx) * s, py = sy + (oy + y * cel - sy) * s;
          ctx.fillStyle = s < 1 ? C.tinta : C.muda;
          ctx.fillRect(px * dpr, py * dpr, (cel - 2) * dpr, (cel - 2) * dpr);
        });
      } else if (k === 2) { // cálculo: fuerza → tensión que crece → valor frente al límite
        dibujarCalculo(f);
      } else if (!impresora) { // sin 3d: se imprime en la rejilla, capa a capa
        const capas = k === 3 ? Math.floor(escalon(f, pieza.H) * pieza.H) : pieza.H, nivel = pieza.H - capas;
        if (k === 4) { pieza.celdas.forEach(([x, y]) => celda(x, y, C.senal)); return requestAnimationFrame(dibujar); }
        pieza.celdas.forEach(([x, y]) => celda(x, y, y >= nivel ? C.senal : "rgba(201,225,201,0.18)"));
      } else {
        pieza.celdas.forEach(([x, y]) => celda(x, y, C.muda));
      }
    }
    if (impresora && k >= 3) impresora.pintar(ms, k === 3 ? f : 1, k === 4 ? f : 0);
    if (!reducido) requestAnimationFrame(dibujar);
  }
  const arrancar = () => { medir(); requestAnimationFrame(dibujar); };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(arrancar); else arrancar();
}

// ── impresora 3D: imprime la placa real de el secadero v2 (docs/models) ──────
// Un plano de corte sube capa a capa; en el corte brilla la capa que se está
// imprimiendo y el cabezal la recorre. Al final la impresora se desvanece.
let impresoraCache = null;
async function cargarImpresora(lienzo) {
  if (reducido) throw new Error("sin movimiento");
  const THREE = await import("three");
  const { GLTFLoader } = await import("three/addons/loaders/GLTFLoader.js");
  const gltf = await new GLTFLoader().loadAsync(conVer("models/el_secadero_v2_placa.glb"));
  const renderer = new THREE.WebGLRenderer({ canvas: lienzo, antialias: true, alpha: true });
  renderer.localClippingEnabled = true;
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1));
  const escena = new THREE.Scene();
  const camara = new THREE.PerspectiveCamera(32, 1, 0.01, 10);
  escena.add(new THREE.HemisphereLight(0xf3fbf1, 0x2b312b, 2.2));
  escena.add(new THREE.AmbientLight(0xffffff, 0.4));
  const sol = new THREE.DirectionalLight(0xffffff, 1.6); sol.position.set(0.3, 0.6, 0.4); escena.add(sol);

  // separar la cama de las piezas y centrar la placa
  const raiz = gltf.scene;
  raiz.updateMatrixWorld(true);
  const caja = new THREE.Box3().setFromObject(raiz), centro = caja.getCenter(new THREE.Vector3());
  raiz.position.sub(new THREE.Vector3(centro.x, caja.min.y, centro.z));
  escena.add(raiz); raiz.updateMatrixWorld(true);
  const mallas = []; raiz.traverse((n) => n.isMesh && mallas.push(n));
  // el GLB sale de trimesh sin normales: sin ellas las caras no reciben luz y se ven negras
  mallas.forEach((m) => { if (!m.geometry.attributes.normal) m.geometry.computeVertexNormals(); });
  // el color tal como lo escribe trimesh en el GLB (sin convertir), para reconocer cada pieza
  const srgb = (mat) => [mat.color.r, mat.color.g, mat.color.b].map((v) => Math.round(v * 255));
  const igual = (a, b) => a.every((v, i) => Math.abs(v - b[i]) <= 3);
  mallas.forEach((m) => { m.userData.rgb = srgb(m.material); });
  const esCama = (m) => new THREE.Box3().setFromObject(m).getSize(new THREE.Vector3()).x > 0.2;
  const piezas = mallas.filter((m) => !esCama(m));
  const camaMat = new THREE.MeshStandardMaterial({ color: 0x333a33, roughness: 0.9, transparent: true });
  mallas.filter(esCama).forEach((m) => { m.material = camaMat; });
  const cajaPiezas = new THREE.Box3(); piezas.forEach((m) => cajaPiezas.expandByObject(m));
  const y0 = cajaPiezas.min.y, y1 = cajaPiezas.max.y, banda = 0.0012;

  const corte = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);      // deja lo que está por debajo de la capa
  const bajoBanda = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);   // y lo que está por encima de capa − banda
  const plastico = new THREE.MeshStandardMaterial({ color: 0xc9e1c9, roughness: 0.55, clippingPlanes: [corte] });
  const brillo = new THREE.MeshBasicMaterial({ color: 0x24e824, clippingPlanes: [corte, bajoBanda] });
  piezas.forEach((m) => {
    m.material = plastico;
    const capa = new THREE.Mesh(m.geometry, brillo);
    capa.position.copy(m.position); capa.quaternion.copy(m.quaternion); capa.scale.copy(m.scale);
    m.parent.add(capa);
    m.userData.capa = capa;
  });

  // montaje: transformaciones placa → objeto montado (3d-models/montaje.py) y el contexto
  // (grifo, encimera, fregadero, estropajo) del modelo montado
  const suave = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
  const I = new THREE.Quaternion(), CERO = new THREE.Vector3(), UNO = new THREE.Vector3(1, 1, 1);
  let montaje = null;
  try {
    const [datos, abajo] = await Promise.all([
      fetch(conVer("models/el_secadero_v2_montaje.json")).then((r) => r.json()),
      new GLTFLoader().loadAsync(conVer("models/el_secadero_v2_abajo.glb")),
    ]);
    const D = new THREE.Matrix4().fromArray(datos.desplazamiento);
    const V = (a) => new THREE.Vector3(...a);
    // movimiento real de montaje en el sistema del objeto montado (mm, z arriba):
    // s = 0 → posición de entrada; s = 1 → montada (identidad)
    const movimiento = (mv) => (s) => {
      const M = new THREE.Matrix4();
      if (!mv) return M;
      if (mv.tipo === "desliza") return M.makeTranslation(...V(mv.desde).multiplyScalar(1 - suave(s)).toArray());
      // gira: primero entra (inclinada) por su ranura y luego gira sobre su eje hasta su sitio
      const entra = suave(s / 0.45), gira = suave((s - 0.45) / 0.55);
      const ang = THREE.MathUtils.degToRad(mv.angulo) * (1 - gira);
      const pt = V(mv.punto);
      M.makeTranslation(...V(mv.entrada).multiplyScalar(1 - entra).toArray())
        .multiply(new THREE.Matrix4().makeTranslation(pt.x, pt.y, pt.z))
        .multiply(new THREE.Matrix4().makeRotationY(ang))
        .multiply(new THREE.Matrix4().makeTranslation(-pt.x, -pt.y, -pt.z));
      return M;
    };
    const mov = [];
    datos.orden.forEach((clave, i) => {
      const pz = datos.piezas[clave];
      const m = piezas.find((x) => igual(x.userData.rgb, pz.color));
      if (!m) return;
      m.updateMatrix();
      const base = m.matrix.clone(), T = new THREE.Matrix4().fromArray(pz.matriz);
      const real = movimiento(datos.movimientos && datos.movimientos[clave]);
      // tramo 1: de la placa a la posición de entrada (en arco); tramo 2: el movimiento real
      const entrada = D.clone().multiply(real(0)).multiply(T);
      const pos = new THREE.Vector3(), quat = new THREE.Quaternion(), esc = new THREE.Vector3();
      entrada.decompose(pos, quat, esc);
      [m, m.userData.capa].forEach((x) => { x.matrixAutoUpdate = false; x.matrix.copy(base); });
      mov.push({ m, base, pos, quat, T, real, i });
    });
    const ref = mov[0];
    const contexto = [];
    let cajaEstropajo = null;
    abajo.scene.traverse((n) => {
      if (!n.isMesh) return;
      const rgb = srgb(n.material), c = datos.contexto.find((x) => igual(x.color, rgb));
      if (!c) return;
      if (c.nombre === "estropajo") { n.geometry.computeBoundingBox(); cajaEstropajo = n.geometry.boundingBox.clone(); return; }
      if (!n.geometry.attributes.normal) n.geometry.computeVertexNormals();
      const mat = new THREE.MeshStandardMaterial({
        color: { cromo: 0xd1d6de, encimera: 0x86a08a, fregadero: 0x222722 }[c.nombre],
        roughness: c.nombre === "cromo" ? 0.3 : 0.8, metalness: c.nombre === "cromo" ? 0.6 : 0, transparent: true, opacity: 0 });
      const malla = new THREE.Mesh(n.geometry, mat);
      malla.matrixAutoUpdate = false;
      malla.matrix.copy(ref.base).multiply(D);
      ref.m.parent.add(malla);
      contexto.push({ malla, nombre: c.nombre });
    });
    // estropajo salvauñas de verdad: espuma amarilla porosa + capa verde de fibra, cantos redondeados
    let estropajo = null;
    if (cajaEstropajo) {
      const { RoundedBoxGeometry } = await import("three/addons/geometries/RoundedBoxGeometry.js");
      const tam = cajaEstropajo.getSize(new THREE.Vector3()), centro = cajaEstropajo.getCenter(new THREE.Vector3());
      const ruido = (fondo, puntos, n, r) => { // textura de poros/fibras dibujada en un lienzo
        const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d");
        g.fillStyle = fondo; g.fillRect(0, 0, 256, 256);
        for (let i = 0; i < n; i++) { g.fillStyle = puntos[i % puntos.length]; g.beginPath(); g.arc(Math.random() * 256, Math.random() * 256, Math.random() * r + 0.6, 0, 7); g.fill(); }
        const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(2, 2); return t;
      };
      const espumaT = ruido("#e8c14a", ["#c99f2c", "#f3d873", "#b88a1f"], 1800, 2.2);
      const fibraT = ruido("#2f6b35", ["#1f4f26", "#4a8c4a", "#3b7a3c"], 3000, 1.4);
      const grupo = new THREE.Group();
      const fibra = Math.min(10, tam.x * 0.22), espuma = tam.x - fibra;
      const cuerpo = new THREE.Mesh(new RoundedBoxGeometry(espuma, tam.y, tam.z, 4, Math.min(8, espuma / 3)),
        new THREE.MeshStandardMaterial({ map: espumaT, bumpMap: espumaT, bumpScale: 1.5, roughness: 1, transparent: true }));
      cuerpo.position.x = -fibra / 2;
      const capa = new THREE.Mesh(new RoundedBoxGeometry(fibra, tam.y - 2, tam.z - 2, 3, 2),
        new THREE.MeshStandardMaterial({ map: fibraT, bumpMap: fibraT, bumpScale: 2, roughness: 1, transparent: true }));
      capa.position.x = espuma / 2;
      grupo.add(cuerpo, capa);
      grupo.matrixAutoUpdate = false;
      ref.m.parent.add(grupo);
      estropajo = { grupo, centro, materiales: [cuerpo.material, capa.material], real: movimiento(datos.movimientos && datos.movimientos.estropajo) };
    }
    // centro del objeto montado (para la cámara)
    mov.forEach(({ m, base, T }) => m.matrix.copy(base).multiply(D).multiply(T));
    raiz.updateMatrixWorld(true);
    const cajaMontaje = new THREE.Box3(); mov.forEach(({ m }) => cajaMontaje.expandByObject(m));
    mov.forEach(({ m, base }) => m.matrix.copy(base));
    montaje = { D, mov, contexto, estropajo, centro: cajaMontaje.getCenter(new THREE.Vector3()), tam: cajaMontaje.getSize(new THREE.Vector3()).length() };
  } catch (err) { console.warn("sin montaje", err); montaje = null; } // sin montaje: la placa impresa gira y ya

  // la impresora: dos columnas, el puente que sube con la capa y el cabezal
  const marco = new THREE.MeshStandardMaterial({ color: 0x86a08a, roughness: 0.6, transparent: true });
  const metal = new THREE.MeshStandardMaterial({ color: 0xf3fbf1, roughness: 0.4, transparent: true });
  const ancho = 0.32, alto = 0.16;
  const impresora = new THREE.Group();
  for (const sx of [-1, 1]) {
    const col = new THREE.Mesh(new THREE.BoxGeometry(0.012, alto, 0.012), marco);
    col.position.set((sx * ancho) / 2, alto / 2, -0.06); impresora.add(col);
  }
  const techo = new THREE.Mesh(new THREE.BoxGeometry(ancho + 0.012, 0.012, 0.012), marco);
  techo.position.set(0, alto, -0.06); impresora.add(techo);
  const puente = new THREE.Mesh(new THREE.BoxGeometry(ancho, 0.01, 0.014), marco); impresora.add(puente);
  const cabezal = new THREE.Group();
  const cuerpo = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.034, 0.03), metal); cuerpo.position.y = 0.024; cabezal.add(cuerpo);
  const boquilla = new THREE.Mesh(new THREE.ConeGeometry(0.004, 0.008, 12), new THREE.MeshBasicMaterial({ color: 0x24e824 }));
  boquilla.rotation.x = Math.PI; boquilla.position.y = 0.004; cabezal.add(boquilla);
  impresora.add(cabezal);
  escena.add(impresora);

  function medir() {
    const r = lienzo.getBoundingClientRect();
    renderer.setSize(r.width, r.height, false);
    camara.aspect = r.width / Math.max(1, r.height);
    camara.updateProjectionMatrix();
  }
  medir();

  // ventanas del montaje: cada pieza sale de la placa (tramo 1) y hace su movimiento real (tramo 2)
  const VUELO = 0.1, REAL = 0.1, HUECO = 0.19;
  function montar(f) {
    if (!montaje) return 0;
    for (const { m, base, pos, quat, T, real, i } of montaje.mov) {
      const ini = 0.06 + i * HUECO;
      const t1 = suave((f - ini) / VUELO), t2 = (f - ini - VUELO) / REAL;
      let M;
      if (t2 <= 0) { // tramo 1: de la placa a la entrada, en arco
        const p = CERO.clone().lerp(pos, t1); p.z += 70 * Math.sin(Math.PI * t1);
        M = base.clone().multiply(new THREE.Matrix4().compose(p, I.clone().slerp(quat, t1), UNO));
      } else { // tramo 2: el movimiento real de montaje
        M = base.clone().multiply(montaje.D).multiply(real(Math.min(1, t2))).multiply(T);
      }
      m.matrix.copy(M); m.userData.capa.matrix.copy(M);
    }
    for (const { malla, nombre } of montaje.contexto) {
      const max = { encimera: 0.22, fregadero: 0.35, cromo: 1 }[nombre];
      malla.material.opacity = max * suave(f / 0.12);
      malla.visible = malla.material.opacity > 0.01;
    }
    if (montaje.estropajo) { // el estropajo cae en la cuna al final
      const e = montaje.estropajo, t = (f - 0.84) / 0.1;
      e.grupo.visible = t > 0;
      e.materiales.forEach((m) => { m.opacity = suave(t * 3); });
      e.grupo.matrix.copy(base0).multiply(montaje.D).multiply(e.real(Math.min(1, Math.max(0, t))))
        .multiply(new THREE.Matrix4().makeTranslation(e.centro.x, e.centro.y, e.centro.z));
    }
    camaMat.opacity = 1 - 0.8 * suave((f - 0.3) / 0.4);
    return suave(f / 0.14);
  }
  const base0 = montaje ? montaje.mov[0].base : null;

  function pintar(ms, imprimir, final) {
    const h = y0 + (y1 - y0) * imprimir;
    const viaje = montar(final);
    corte.constant = imprimir >= 1 ? 1 : h;
    bajoBanda.constant = -(h - banda);
    brillo.visible = imprimir < 1;
    // cabezal: recorre la capa en zigzag (rápido en x, lento en z)
    const x = Math.sin(ms / 90) * 0.11, z = Math.sin(ms / 1300) * 0.1 + 0.01;
    puente.position.set(0, h + 0.03, z);
    cabezal.position.set(x, h, z);
    const opac = 1 - Math.min(1, final * 6);
    marco.opacity = metal.opacity = opac; boquilla.visible = puente.visible = opac > 0.02;
    impresora.visible = opac > 0.02;
    // cámara: gira despacio alrededor de la placa; la distancia hace que quepa a lo ancho
    // (en un móvil en vertical el campo horizontal es estrecho); al final se acerca
    const hfov = 2 * Math.atan(Math.tan((camara.fov * Math.PI) / 360) * camara.aspect);
    const cabe = Math.max(0.42, 0.2 / Math.tan(hfov / 2));
    const objetivo = new THREE.Vector3(0, 0.012, 0);
    let dist = cabe;
    if (montaje && viaje > 0) {
      objetivo.lerp(montaje.centro, viaje);
      // que quepa el objeto montado (con el grifo) también a lo ancho, en vertical
      const cabeMontaje = Math.max(0.34, (montaje.tam * 0.75) / Math.tan(hfov / 2));
      dist = cabe + (cabeMontaje - cabe) * viaje;
    }
    const ang = ms / 9000;
    camara.position.set(objetivo.x + Math.sin(ang) * dist, objetivo.y + dist * (0.55 - viaje * 0.2), objetivo.z + Math.cos(ang) * dist);
    camara.lookAt(objetivo);
    renderer.render(escena, camara);
  }
  impresoraCache = { medir, pintar };
  return impresoraCache;
}

// ── objeto: el modelo a pantalla completa y, encima, solo lo imprescindible ───
//   arriba:  icono (→ inicio) · nombre del objeto · precio
//   abajo:   versiones (desplegable) a la izquierda · posiciones a la derecha
//   banda:   «detalles», que sube una hoja con todo lo demás
function vistaObjeto(oid, eid, abrirDetalles = false) {
  const o = DATOS.objetos.find((x) => x.id === oid);
  if (!o) return (location.hash = "#/");
  let i = o.estados.findIndex((e) => e.id === eid);
  if (i < 0) i = o.estados.length - 1; // sin estado: el más reciente
  const e = o.estados[i];
  const ant = o.estados[i - 1];
  const sig = o.estados[i + 1];
  const t = tipoDe(e, o);
  const enlace = (x) => `#/${o.id}/${x.id}`;

  // posiciones: las vistas del modelo; si no hay modelo, las imágenes
  const posiciones = e.modelos.length
    ? e.modelos.map((m) => ({ nombre: m.nombre, src: conVer(m.src), tipo: "modelo", coste: m.coste }))
    : e.imagenes.map((im) => ({ nombre: im.pie, src: im.src, tipo: "imagen" }));
  const primera = posiciones[0];
  const lienzo = !primera
    ? `<div class="vacio-lienzo caption">sin modelo 3D en el repositorio</div>`
    : primera.tipo === "modelo"
      ? `<model-viewer id="mv" src="${primera.src}" alt="${esc(o.nombre)} · ${esc(e.nombre)}"
           camera-controls touch-action="none" interaction-prompt="none" shadow-intensity="0"
           exposure="1.05" ar ar-modes="webxr scene-viewer quick-look">
           <button slot="ar-button" class="boton-ar control">ver en tu espacio</button></model-viewer>`
      : `<img id="im" class="lienzo-img" src="${primera.src}" alt="${esc(primera.nombre)}">`;

  // desplegable propio (LG Señal): solo se ven las versiones; los borradores y las
  // pruebas que hubo entre una versión y la siguiente van plegados en un «toggle».
  const fila = (x) => {
    const tx = tipoDe(x, o);
    return `<li><a class="op" href="${enlace(x)}" data-id="${x.id}" ${x === e ? 'aria-current="true"' : ""}>
      <span class="status ${tx.cls}"></span>
      <span class="op-texto"><span class="control op-nombre">${esc(x.nombre)}</span>
        <span class="caption">${tx.txt} · ${fecha(x.fecha)}</span></span>
      <span class="caption op-precio">${x.coste ? eur(x.coste.euros) : ""}</span></a></li>`;
  };
  const hayVersiones = o.estados.some((x) => x.tipo === "version");
  const grupos = [];
  let pend = [];
  for (const x of o.estados) {
    if (x.tipo === "version") { grupos.push({ previos: pend, version: x }); pend = []; }
    else pend.push(x);
  }
  if (pend.length) grupos.push({ previos: pend, version: null });
  const cuenta = (xs) => {
    const b = xs.filter((x) => x.tipo === "borrador").length, p = xs.length - b;
    return [b && `${b} ${b === 1 ? "borrador" : "borradores"}`, p && `${p} ${p === 1 ? "prueba" : "pruebas"}`].filter(Boolean).join(" · ");
  };
  const opciones = !hayVersiones ? o.estados.map(fila).join("") : grupos.map((g, k) => {
    const abierto = g.previos.includes(e);
    const plegado = g.previos.length ? `<li class="grupo">
        <button class="op-toggle" aria-expanded="${abierto}" aria-controls="grupo-${k}">
          <span class="flecha" aria-hidden="true"></span>
          <span class="caption">${cuenta(g.previos)}</span>
          <span class="caption op-precio">${fecha(g.previos[0].fecha)}${g.previos.length > 1 ? ` – ${fecha(g.previos[g.previos.length - 1].fecha)}` : ""}</span>
        </button>
        <ul class="op-sub" id="grupo-${k}" ${abierto ? "" : "hidden"}>${g.previos.map(fila).join("")}</ul></li>` : "";
    return plegado + (g.version ? fila(g.version) : "");
  }).join("");

  // detalles
  const previo = o.estados.slice(0, i).reverse().find((x) => x.coste);
  const delta = e.coste && previo
    ? `<div class="delta"><p class="caption">respecto a «${esc(previo.nombre)}»</p>
        <p class="body strong ${e.coste.gramos > previo.coste.gramos ? "mas" : "menos"}">${firma(e.coste.gramos - previo.coste.gramos, gr)} · ${firma(e.coste.euros - previo.coste.euros, eur)}</p></div>`
    : "";
  const piezas = e.piezas.length
    ? `<section class="seccion"><h3 class="label">piezas</h3><ul class="flujo">
        ${e.piezas.map((p) => `<li><span>${esc(p.nombre)}${p.cantidad > 1 ? ` × ${p.cantidad}` : ""}<span class="caption"> · ${esc(p.fuente)}</span></span>
          <span class="num muted">${gr(p.gramos)}</span><span class="num strong">${eur(p.euros)}</span></li>`).join("")}
        ${e.piezas.length > 1 ? `<li class="total"><span class="caption">total</span><span class="num muted">${gr(e.coste.gramos)}</span><span class="num strong signal">${eur(e.coste.euros)}</span></li>` : ""}
      </ul></section>`
    : "";
  // pruebas: las vistas que son una pieza de prueba llevan su propio coste
  const pruebasPos = posiciones.filter((p) => p.coste);
  const pruebas = pruebasPos.length
    ? `<section class="seccion"><h3 class="label">pruebas antes de imprimir</h3><ul class="flujo">
        ${pruebasPos.map((p) => `<li><span>${esc(p.nombre)}</span>
          <span class="num muted">${gr(p.coste.gramos)}</span><span class="num strong">${eur(p.coste.euros)}</span></li>`).join("")}
        ${pruebasPos.length > 1 ? `<li class="total"><span class="caption">todas las pruebas</span><span class="num muted">${gr(pruebasPos.reduce((s, p) => s + p.coste.gramos, 0))}</span><span class="num strong">${eur(pruebasPos.reduce((s, p) => s + p.coste.euros, 0))}</span></li>` : ""}
      </ul><p class="caption">aparte del precio del diseño: son piezas pequeñas para comprobar el encaje.</p></section>`
    : "";
  // bajo el precio del diseño, el de la prueba que se está viendo
  const precioPos = (p) => p && p.coste
    ? `<span class="caption">${esc(p.nombre)}</span><span class="num strong">${eur(p.coste.euros)}</span><span class="caption">${gr(p.coste.gramos)}</span>`
    : "";
  const coste = e.coste
    ? `<div class="coste">${bitEur(e.coste.euros, "lg")}
        <p class="caption">${gr(e.coste.gramos)} de plástico · ${e.coste.origen === "laminador" ? "dato del laminador real" : `estimado a ${DATOS.euros_kg} €/kg`}</p></div>`
    : "";
  const imagenes = e.imagenes.length && e.modelos.length
    ? `<section class="seccion"><h3 class="label">imágenes</h3><div class="imagenes">${e.imagenes.map((im) =>
        `<figure><a href="${im.src}"><img src="${im.src}" alt="${esc(im.pie)}" loading="lazy"></a><figcaption class="caption">${esc(im.pie)}</figcaption></figure>`).join("")}</div></section>`
    : "";
  const memoria = memoriaHTML(e);
  const proceso = procesoHTML(e);
  const descargas = e.descargas.length
    ? `<section class="seccion"><h3 class="label">descargas</h3><ul class="descargas">${e.descargas.map((d) => {
        const nombre = d.split("/").pop();
        return `<li><a href="${d}" download><span class="ext control">${esc(nombre.split(".").pop())}</span><span class="nombre">${esc(nombre)}</span></a></li>`;
      }).join("")}</ul></section>`
    : "";

  // burbujas: qué cambió, el feedback y a qué paso llevó (como un chat, desde la derecha)
  const cerradas = (() => { try { return JSON.parse(sessionStorage.getItem("burbujas-cerradas") || "[]"); } catch (_) { return []; } })();
  const claveB = `${o.id}/${e.id}`;
  const burbujas = (e.cambio || e.feedback) && !cerradas.includes(claveB)
    ? `<aside class="burbujas" id="burbujas" aria-label="cómo se llegó aquí">
        ${e.cambio ? `<p class="burbuja"><span class="quien">qué cambió</span><span class="txt">${esc(e.cambio)}</span></p>` : ""}
        ${e.feedback ? `<p class="burbuja fb"><span class="quien">${esc(e.feedback_de || "feedback")}</span><span class="txt">${esc(e.feedback)}</span></p>` : ""}
        ${e.feedback && sig ? `<a class="burbuja sig" href="${enlace(sig)}"><span class="quien">nos llevó a</span><span class="txt">${esc(sig.nombre)} →</span></a>` : ""}
        <button class="burbujas-cerrar" id="burbujas-cerrar" aria-label="cerrar"><span aria-hidden="true">×</span></button>
      </aside>`
    : "";

  document.body.classList.add("en-escena");
  app.innerHTML = `<div class="escena">
    <div class="lienzo">${lienzo}</div>

    <header class="hud hud-arriba">
      <a class="ir-inicio" href="#/" aria-label="objetos"><img src="icon.svg" alt=""></a>
      <h1 class="hud-titulo title" id="titulo">${esc(o.nombre)}</h1>
      <span class="hud-precio">${e.coste ? bitEur(e.coste.euros, "sm") : ""}
        <span class="precio-pos" id="precio-pos" aria-live="polite">${precioPos(primera)}</span></span>
    </header>
${burbujas}

    <div class="hud hud-abajo">
      <div class="versiones" id="versiones">
        <ul class="versiones-lista" id="versiones-lista" aria-label="versiones de ${esc(o.nombre)}" hidden>${opciones}</ul>
        <button class="versiones-cara" id="versiones-boton" aria-expanded="false"
            aria-controls="versiones-lista" aria-label="versión: ${esc(e.nombre)}, ${i + 1} de ${o.estados.length}">
          <span class="status ${t.cls}"></span><span class="control">${esc(e.nombre)}</span>
          <span class="caption">${i + 1}/${o.estados.length}</span><span class="flecha" aria-hidden="true"></span>
        </button>
      </div>
      ${posiciones.length > 1 ? `<div class="posiciones${posiciones.length > 3 ? " compactas" : ""}" role="group" aria-label="posiciones">
        ${posiciones.length > 3 ? `<span class="pos-nombre caption" id="pos-nombre">${esc(posiciones[0].nombre)}</span>` : ""}
        <div class="pos-lista">${posiciones.map((p, k) =>
          `<button class="pos control" data-k="${k}" aria-pressed="${k === 0}" aria-label="${esc(p.nombre)}">${posiciones.length > 3 ? k + 1 : esc(p.nombre)}</button>`).join("")}</div></div>` : ""}
    </div>

    <button class="banda" id="banda" aria-controls="hoja" aria-expanded="false">
      <span aria-hidden="true">↑</span><span class="label">detalles</span></button>

    <div class="velo" id="velo" hidden></div>
    <section class="hoja" id="hoja" aria-label="detalles" aria-hidden="true">
      <button class="hoja-asa" id="cerrar" aria-label="cerrar detalles"><span></span></button>
      <div class="hoja-cuerpo">
        <div class="ficha-cab"><span class="status ${t.cls} control">${t.txt}</span>
          <span class="caption">${fechaLarga(e.fecha)} · ${i + 1} / ${o.estados.length}${e.archivo ? ` · archivo: ${esc(e.archivo)}` : ""}</span></div>
        <h2 class="display">${esc(e.nombre)}</h2>
        <p class="body">${esc(e.texto)}</p>
        ${coste}${delta}${memoria}${proceso}${piezas}${pruebas}${imagenes}${descargas}
        <section class="seccion"><h3 class="label">el objeto</h3>
          <p class="body muted">${esc(o.que)} · ${esc(o.estado)}</p>
          <p><a class="enlace" href="#/${o.id}/memoria">memoria completa →</a>${o.aprendizajes ? ` · <a class="enlace" href="${o.aprendizajes}">aprendizajes</a>` : ""}</p></section>
        <nav class="hoja-pasos">
          ${ant ? `<a href="${enlace(ant)}" rel="prev"><span class="caption">← anterior</span><span class="control">${esc(ant.nombre)}</span></a>` : "<span></span>"}
          ${sig ? `<a class="sig" href="${enlace(sig)}" rel="next"><span class="caption">siguiente →</span><span class="control">${esc(sig.nombre)}</span></a>` : "<span></span>"}
        </nav>
      </div>
    </section>
  </div>`;

  document.title = `labil · ${o.nombre} · ${e.nombre}`;
  const bCerrar = document.getElementById("burbujas-cerrar");
  if (bCerrar) bCerrar.addEventListener("click", () => {
    document.getElementById("burbujas").remove();
    try { sessionStorage.setItem("burbujas-cerradas", JSON.stringify([...cerradas, claveB])); } catch (_) { /* sin almacenamiento */ }
  });
  descifra(document.getElementById("titulo"));

  // versiones: botón + lista. Flechas para moverse entre lo visible, Intro para abrir
  // una versión o desplegar un grupo de borradores, Esc para cerrar.
  const vBoton = document.getElementById("versiones-boton");
  const vLista = document.getElementById("versiones-lista");
  const vAbierta = () => !vLista.hidden;
  const visibles = () => [...vLista.querySelectorAll(".op, .op-toggle")].filter((el) => el.offsetParent !== null);
  const vAbrir = (si) => {
    vLista.hidden = !si;
    vBoton.setAttribute("aria-expanded", si);
    document.getElementById("versiones").classList.toggle("abierta", si);
    document.querySelector(".escena").classList.toggle("desplegado", si);
    if (si) {
      const actual = vLista.querySelector('.op[aria-current="true"]') || visibles().pop();
      actual.focus({ preventScroll: true });
      actual.scrollIntoView({ block: "nearest" });
      vLista.querySelectorAll(".op-nombre").forEach((n) => n.offsetParent && descifra(n));
    }
  };
  vBoton.addEventListener("click", () => vAbrir(!vAbierta()));
  vBoton.addEventListener("keydown", (ev) => {
    if (["ArrowUp", "ArrowDown"].includes(ev.key)) { ev.preventDefault(); vAbrir(true); }
  });
  vLista.querySelectorAll(".op-toggle").forEach((t) => t.addEventListener("click", () => {
    const abrir = t.getAttribute("aria-expanded") !== "true";
    t.setAttribute("aria-expanded", abrir);
    const sub = document.getElementById(t.getAttribute("aria-controls"));
    sub.hidden = !abrir;
    if (abrir) sub.querySelectorAll(".op-nombre").forEach((n) => descifra(n));
  }));
  vLista.querySelectorAll(".op").forEach((a) => a.addEventListener("click", () => vAbrir(false)));
  vLista.addEventListener("keydown", (ev) => {
    const lista = visibles(), k = lista.indexOf(document.activeElement);
    const ir = (n) => { ev.preventDefault(); const el = lista[Math.max(0, Math.min(lista.length - 1, n))]; el.focus(); el.scrollIntoView({ block: "nearest" }); };
    if (ev.key === "ArrowDown") ir(k + 1);
    else if (ev.key === "ArrowUp") ir(k - 1);
    else if (ev.key === "Home") ir(0);
    else if (ev.key === "End") ir(lista.length - 1);
    else if (ev.key === "Escape") { ev.preventDefault(); vAbrir(false); vBoton.focus(); }
  });
  tocarFuera = (ev) => { if (vAbierta() && !ev.target.closest("#versiones")) vAbrir(false); };

  // posiciones
  document.querySelectorAll(".pos").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".pos").forEach((x) => x.setAttribute("aria-pressed", x === b));
    const p = posiciones[+b.dataset.k];
    const destino = document.getElementById(p.tipo === "modelo" ? "mv" : "im");
    destino.src = p.src;
    if (p.tipo === "imagen") destino.alt = p.nombre;
    const rotulo = document.getElementById("pos-nombre");
    if (rotulo) { rotulo.textContent = p.nombre; descifra(rotulo); }
    const pp = document.getElementById("precio-pos");
    if (pp) pp.innerHTML = precioPos(p);
  }));

  // hoja de detalles
  const hoja = document.getElementById("hoja"), banda = document.getElementById("banda"), velo = document.getElementById("velo");
  const abrir = (si) => {
    hoja.classList.toggle("abierta", si);
    hoja.setAttribute("aria-hidden", !si);
    banda.setAttribute("aria-expanded", si);
    velo.hidden = !si;
    if (si) hoja.querySelector(".hoja-cuerpo").scrollTop = 0;
  };
  banda.addEventListener("click", () => abrir(true));
  document.getElementById("cerrar").addEventListener("click", () => abrir(false));
  velo.addEventListener("click", () => abrir(false));
  // deslizar la banda hacia arriba abre; la hoja hacia abajo (desde arriba del todo) cierra
  let y0 = null;
  banda.addEventListener("touchstart", (ev) => { y0 = ev.touches[0].clientY; }, { passive: true });
  banda.addEventListener("touchend", (ev) => { if (y0 !== null && y0 - ev.changedTouches[0].clientY > 24) abrir(true); y0 = null; }, { passive: true });
  const cuerpo = hoja.querySelector(".hoja-cuerpo");
  hoja.addEventListener("touchstart", (ev) => { y0 = cuerpo.scrollTop <= 0 ? ev.touches[0].clientY : null; }, { passive: true });
  hoja.addEventListener("touchend", (ev) => { if (y0 !== null && ev.changedTouches[0].clientY - y0 > 80) abrir(false); y0 = null; }, { passive: true });
  if (abrirDetalles) abrir(true);

  const ir = (x) => x && (location.hash = enlace(x));
  teclas = (ev) => {
    if (ev.target.closest("model-viewer, input, textarea, select, #versiones")) return;
    if (ev.key === "Escape") abrir(false);
    if (ev.key === "ArrowLeft") ir(ant);
    if (ev.key === "ArrowRight") ir(sig);
  };
}
let teclas = null;
let tocarFuera = null;
document.addEventListener("keydown", (ev) => teclas && teclas(ev));
document.addEventListener("pointerdown", (ev) => tocarFuera && tocarFuera(ev));

// ── memoria y proceso ────────────────────────────────────────────────────────
function memoriaHTML(e) {
  if (!e.memoria || !e.memoria.length) return "";
  return `<section class="seccion"><h3 class="label">qué cambia y por qué</h3><ul class="memoria">
    ${e.memoria.map((m) => `<li><span class="tema">${esc(m.tema)}</span><p class="body">${esc(m.texto)}</p></li>`).join("")}</ul></section>`;
}
function procesoHTML(e) {
  if (!e.proceso || !e.proceso.length) return "";
  return `<section class="seccion"><h3 class="label">proceso</h3><div class="imagenes proceso">${e.proceso.map((im) =>
    `<figure><a href="${im.src}"><img src="${im.src}" alt="${esc(im.pie)}" loading="lazy"></a>
      <figcaption class="caption">${fecha(im.fecha)} · ${esc(im.pie)}</figcaption></figure>`).join("")}</div></section>`;
}

// ── memoria de un objeto: línea de tiempo, de lo más reciente a lo más antiguo ─
function vistaMemoria(o) {
  const n = o.estados.length;
  const filas = o.estados.map((e, i) => ({ e, i })).reverse().map(({ e, i }) => {
    const t = tipoDe(e, o);
    const sig = o.estados[i + 1];
    return `<li class="hito ${t.cls}">
      <span class="nodo" aria-hidden="true"></span>
      <div class="hito-cuerpo">
        <div class="ficha-cab"><span class="status ${t.cls} control">${t.txt}</span>
          <span class="caption">${fechaLarga(e.fecha)} · ${i + 1} / ${n}${e.coste ? ` · ${eur(e.coste.euros)} · ${gr(e.coste.gramos)}` : ""}</span></div>
        <h2 class="title"><a href="#/${o.id}/${e.id}">${esc(e.nombre)} <span class="signal">→</span></a></h2>
        ${e.cambio || e.feedback ? `<div class="hito-chat">
          ${e.cambio ? `<p class="burbuja"><span class="quien">qué cambió</span><span class="txt">${esc(e.cambio)}</span></p>` : ""}
          ${e.feedback ? `<p class="burbuja fb"><span class="quien">${esc(e.feedback_de || "feedback")}</span><span class="txt">${esc(e.feedback)}</span></p>` : ""}
          ${e.feedback && sig ? `<a class="burbuja sig" href="#/${o.id}/${sig.id}"><span class="quien">nos llevó a</span><span class="txt">${esc(sig.nombre)} ↑</span></a>` : ""}
        </div>` : ""}
        <p class="body muted">${esc(e.texto)}</p>
        ${memoriaHTML(e)}${procesoHTML(e)}
      </div>
    </li>`;
  }).join("");
  app.innerHTML = `<header class="top top-memoria">
      <a class="atras" href="#/${o.id}" aria-label="volver a ${esc(o.nombre)}"><span aria-hidden="true">←</span></a>
      <span class="label">memoria</span>
    </header>
    <main class="memoria-pag">
      <section class="hero"><h1 class="display" id="titulo">${esc(o.nombre)}</h1>
        <p class="body muted">${esc(o.que)}. Cómo cambia de un estado a otro y por qué, de lo más reciente a lo más antiguo.</p></section>
      <ol class="timeline">${filas}</ol>
      ${pie()}
    </main>`;
  descifra(document.getElementById("titulo"));
  document.title = `labil · ${o.nombre} · memoria`;
}

// ── historial: todo lo hecho, por meses ──────────────────────────────────────
function vistaHistorial() {
  const filas = DATOS.objetos.flatMap((o) => o.estados.map((e, n) => ({ o, e, n })))
    .sort((a, b) => b.e.fecha.localeCompare(a.e.fecha) || b.n - a.n);
  const meses = {};
  for (const f of filas) (meses[f.e.fecha.slice(0, 7)] ||= []).push(f);
  const html = Object.entries(meses).map(([m, fs]) => {
    const [a, mm] = m.split("-").map(Number);
    const suma = fs.reduce((s, f) => s + (f.e.coste ? f.e.coste.euros : 0), 0);
    return `<section class="mes"><h2 class="label">${MESES[mm - 1]} ${a} · ${eur(suma)}</h2><ol class="hist">
      ${fs.map(({ o, e }) => `<li><a href="#/${o.id}/${e.id}">
        <span class="caption">${fecha(e.fecha)}</span>
        <span class="que"><span class="control">${esc(o.nombre)} · ${esc(e.nombre)}</span>
          <span class="status ${tipoDe(e, o).cls} caption">${tipoDe(e, o).txt}</span></span>
        <span class="strong">${e.coste ? eur(e.coste.euros) : "—"}</span></a></li>`).join("")}
    </ol></section>`;
  }).join("");
  app.innerHTML = cabecera("historial") + `<main>
    <section class="hero"><p class="label">lo hecho</p><h1 class="display" id="titulo">historial</h1>
      <p class="body muted">Todo lo diseñado, del más reciente al más antiguo.</p></section>
    ${html}${pie()}</main>`;
  descifra(document.getElementById("titulo"));
  document.title = "labil · historial";
}

// ── rutas ────────────────────────────────────────────────────────────────────
function ruta() {
  teclas = null;
  tocarFuera = null;
  document.body.classList.remove("en-escena");
  const partes = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean).map(decodeURIComponent);
  if (!partes.length) vistaInicio();
  else if (partes[0] === "historial") vistaHistorial();
  else if (partes[1] === "memoria") {
    const o = DATOS.objetos.find((x) => x.id === partes[0]);
    o ? vistaMemoria(o) : (location.hash = "#/");
  } else vistaObjeto(partes[0], partes[1]);
  window.scrollTo(0, 0);
}

(async function inicio() {
  try {
    const r = await fetch("models/version.txt?_=" + Date.now(), { cache: "no-store" });
    if (r.ok) VER = (await r.text()).trim();
  } catch (_) { /* sin cache-buster */ }
  const r = await fetch("data/objetos.json?_=" + (VER || Date.now()), { cache: "no-store" });
  DATOS = await r.json();
  addEventListener("hashchange", ruta);
  ruta();
})();
