// labil v2 — simulación de cargas de un objeto, dentro de su página.
// El modelo ocupa la pantalla y los mandos van alrededor, como en el resto de la web:
//   arriba   el tablero: la barra como viga sobre dos apoyos y un dial por apoyo
//   lados    los objetos de cada lado (en móvil, una tira deslizable). cada botón
//            pasa con un clic por sus formas: arriba (▲, de pie sobre la línea),
//            abajo (▼, colgado bajo la línea) y quitado; si solo tiene una, puesto/quitado
//   abajo    «i» (qué significan las cifras) y la secuencia
// Los datos salen de 3d-models/<diseño>/cargas.json; el modelo nombra cada objeto
// como obj_<id>_<n> (forma de arriba) y objb_<id>_<n> (forma colgada), y sus enganches
// jinete_<id> y jineteb_<id>, para poder moverlos.

const G = 9.81 / 1000; // newtons por gramo
const n1 = (v) => v.toLocaleString("es-ES", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const gramos = (n) => `${(Math.round(Math.abs(n) / G / 10) * 10).toLocaleString("es-ES")} g`;
const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;
const SVG = "http://www.w3.org/2000/svg";

// ── estática: viga sobre dos apoyos ───────────────────────────────────────────
function estatica(D) {
  const XC = -D.ctc / 2, XM = D.ctc / 2, I = D.depth * D.line_h ** 3 / 12;
  const enBrazo = (o, s, raiz) => s * (o.x - raiz) > 0 && s * o.x > D.ctc / 2;
  function estado(set) {
    const on = D.objetos.filter((o) => set.has(o.id));
    const total = on.reduce((t, o) => t + o.gramos * G, 0);
    const manilla = on.reduce((t, o) => t + o.gramos * G * (o.x - XC), 0) / D.ctc;
    const e = { peso: total / G, cano: total - manilla, manilla };
    for (const [lado, s, raiz] of [["izq", -1, XC], ["der", 1, XM]]) {
      let m = 0, f = 0;
      for (const o of on) if (enBrazo(o, s, raiz)) {
        const a = s * (o.x - raiz), p = o.gramos * G;
        m += p * a; f += p * a * a * (3 * D.arm_len - a);
      }
      e[`tension_${lado}`] = m * 6 / (D.depth * D.line_h ** 2);
      e[`flecha_${lado}`] = D.taper * f / (6 * D.E * I);
    }
    return e;
  }
  // deformada de un brazo en voladizo, para dibujarla
  function curva(set, s, raiz, pasos = 20) {
    const L = D.arm_len, pts = [];
    for (let i = 0; i <= pasos; i++) {
      const u = L * i / pasos; let d = 0;
      for (const o of D.objetos) if (set.has(o.id) && enBrazo(o, s, raiz)) {
        const a = s * (o.x - raiz), p = o.gramos * G;
        d += u <= a ? p * u * u * (3 * a - u) : p * a * a * (3 * u - a);
      }
      pts.push([raiz + s * u, D.taper * d / (6 * D.E * I)]);
    }
    return pts;
  }
  return { estado, curva, XC, XM };
}

const el = (tag, attrs = {}, texto) => {
  const n = document.createElementNS(SVG, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (texto != null) n.textContent = texto;
  return n;
};
const html = (tag, cls, texto) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (texto != null) n.textContent = texto;
  return n;
};

// ── un dial por apoyo: a la izquierda «apoya», a la derecha «tiran» ───────────
function dial(nombre) {
  const caja = html("div", "sim-dial");
  const svg = el("svg", { viewBox: "0 0 120 70", "aria-hidden": "true" });
  const arco = (a0, a1, cls) => {
    const p = (a) => [60 + 46 * Math.sin(a * Math.PI / 180), 62 - 46 * Math.cos(a * Math.PI / 180)];
    const [x0, y0] = p(a0), [x1, y1] = p(a1);
    svg.appendChild(el("path", { d: `M${x0.toFixed(1)} ${y0.toFixed(1)}A46 46 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}`, class: cls }));
  };
  arco(-90, -3, "apoya"); arco(3, 54, "tiran"); arco(54, 90, "limite");
  for (let a = -90; a <= 90; a += 30) {
    const s = Math.sin(a * Math.PI / 180), c = Math.cos(a * Math.PI / 180);
    svg.appendChild(el("line", { x1: 60 + 38 * s, y1: 62 - 38 * c, x2: 60 + 42 * s, y2: 62 - 42 * c, class: "marca" }));
  }
  const aguja = el("line", { x1: 60, y1: 62, x2: 60, y2: 22, class: "aguja" });
  svg.appendChild(aguja); svg.appendChild(el("rect", { x: 57, y: 59, width: 6, height: 6, class: "eje" }));
  const titulo = html("span", "label", nombre), valor = html("span", "control sim-valor"), nota = html("span", "caption");
  caja.append(svg, titulo, valor, nota);
  return {
    caja,
    pon(r, aguanta) {
      const tiran = r < -0.05, uso = tiran ? -r / aguanta : 0;
      const ang = tiran ? Math.min(90, uso * 90) : -Math.min(90, Math.max(r, 0) / 15 * 90);
      aguja.style.transform = `rotate(${ang.toFixed(1)}deg)`;
      caja.dataset.nivel = uso >= 1 ? "mal" : uso >= 0.6 ? "justo" : tiran ? "tiran" : "bien";
      valor.textContent = `${tiran ? "tiran" : "apoya"} ${n1(Math.abs(r))} n`;
      nota.textContent = tiran ? `≈ ${gramos(r)} · margen ×${n1(1 / uso)}` : `≈ ${gramos(r)} · clic sin usar`;
      return uso;
    },
  };
}

// ── esquema de la viga ────────────────────────────────────────────────────────
function pintaViga(svg, D, est, set, e) {
  svg.replaceChildren();
  const W = 420, K = W / (D.ctc + 2 * D.arm_len + 40), X0 = W / 2, Y = 62, EX = 10;
  const px = (x) => X0 + x * K;
  const add = (tag, a, t) => svg.appendChild(el(tag, a, t));
  add("line", { x1: px(est.XC - D.arm_len), y1: Y, x2: px(est.XM + D.arm_len), y2: Y, class: "guia" });
  for (const [s, raiz] of [[-1, est.XC], [1, est.XM]])
    add("polyline", { points: est.curva(set, s, raiz).map(([x, d]) => `${px(x).toFixed(1)},${(Y + d * EX * K).toFixed(1)}`).join(" "), class: "barra" });
  add("line", { x1: px(est.XC), y1: Y, x2: px(est.XM), y2: Y, class: "barra" });
  for (const [x, r] of [[est.XC, e.cano], [est.XM, e.manilla]]) {
    const X = px(x), sube = r >= -0.05, h = Math.min(26, 6 + Math.abs(r) * 2.2), cls = sube ? "apoya" : "tiran";
    add("polygon", { points: `${X - 6},${Y + 14} ${X + 6},${Y + 14} ${X},${Y + 3}`, class: "apoyo" });
    const y1 = sube ? Y + 17 + h : Y + 17, y2 = sube ? Y + 17 : Y + 17 + h, p = sube ? 5 : -5;
    add("line", { x1: X, y1, x2: X, y2, class: `fuerza ${cls}` });
    add("polygon", { points: `${X - 4},${y2 + p} ${X + 4},${y2 + p} ${X},${y2}`, class: `punta ${cls}` });
  }
  for (const o of D.objetos) {
    const X = px(o.x), on = set.has(o.id), h = 8 + o.gramos * 0.085;
    add("line", { x1: X, y1: Y - 6 - h, x2: X, y2: Y - 6, class: `peso${on ? "" : " fuera"}` });
    add("polygon", { points: `${X - 3.5},${Y - 11} ${X + 3.5},${Y - 11} ${X},${Y - 5}`, class: `punta-peso${on ? "" : " fuera"}` });
    add("text", { x: X, y: Y - 10 - h, class: on ? "" : "fuera", "text-anchor": "middle" }, o.gramos);
  }
}

const LECCION = [
  ["n · newton", ["es la unidad de fuerza: cuánto empuja o tira algo. para andar por casa: 100 g pesan 1 n.",
    "la colonia (370 g) tira hacia abajo con 3,6 n. todo junto (1.050 g), con 10 n.",
    "un lazo que aguanta 24 n es como colgarle 2,4 kg tirando hacia arriba."]],
  ["apoya / tiran", ["la barra es un balancín con dos apoyos, los lazos. con los dos lados cargados, los dos lazos apoyan: descansan sobre el grifo y no pueden fallar.",
    "si vacías un lado, el otro hace palanca y quiere levantar el lazo lejano: de ese lazo tiran, y solo lo sujeta su clic."]],
  ["mpa · megapascal", ["es la tensión: la fuerza repartida por dentro del plástico. 1 mpa = 10 kg apretando sobre 1 cm².",
    "el pla se rompe hacia los 50 mpa. a 15 aguanta años sin ceder; ese es el tope que se usa.",
    "la barra, en su peor caso, trabaja a 1,8 mpa."]],
  ["margen ×", ["cuántas veces más aguanta de lo que se le pide. ×3,4: haría falta 3,4 veces esa fuerza para que fallara.",
    "por debajo de ×1 se suelta. en una pieza de plástico de uso diario se busca ×2 o más."]],
  ["mm · lo que baja la punta", ["cuánto se dobla el brazo con lo que tiene colgado. el pla cede con los años: puede llegar al doble."]],
  ["de dónde salen", ["los pesos son los de la báscula. lo que aguanta cada lazo es un cálculo, no un ensayo.",
    "no está calculado un tirón al coger el secador ni la torsión de la barra. los objetos del dibujo son aproximados."]],
];

export async function montar(escena, { glb, datos }) {
  const D = await (await fetch(datos)).json();
  const est = estatica(D);
  const formas = new Map(D.objetos.map((o) => [o.id, o.formas || ["puesto"]]));
  const forma = new Map(D.objetos.map((o) => [o.id, formas.get(o.id)[0]]));   // forma actual o "fuera"
  const ultima = new Map(forma);                                              // la última que estuvo puesta
  const puestos = new Set(D.objetos.map((o) => o.id));
  const SIGNO = { arriba: "▲", abajo: "▼", puesto: "●", fuera: "×" };
  const DICE = { arriba: "de pie, sobre la línea", abajo: "colgado, bajo la línea", puesto: "puesto", fuera: "quitado" };
  let vivo = true, mover = () => {}, cola = [], reloj = 0;

  const raiz = html("div", "sim");
  const lienzo = html("div", "sim-lienzo");
  const tablero = html("div", "sim-tablero");
  const dCano = dial("lazo caño"), dMani = dial("lazo manilla");
  const centro = html("div", "sim-centro");
  const viga = el("svg", { viewBox: "0 0 420 96", class: "sim-viga", role: "img", "aria-label": "pesos, reacciones de los dos lazos y curva de la barra, exagerada" });
  const veredicto = html("p", "sim-veredicto control");
  const brazos = html("p", "caption sim-brazos");
  const paso = html("p", "caption sim-paso"); paso.setAttribute("aria-live", "polite");
  centro.append(viga, veredicto, brazos, paso);
  tablero.append(dCano.caja, centro, dMani.caja);

  const objetos = html("div", "sim-objetos");
  const botones = new Map();
  for (const [lado, filtro, titulo] of [["izq", (o) => o.x < 0, "izquierda"], ["der", (o) => o.x > 0, "derecha"]]) {
    const grupo = html("div", `sim-lado ${lado}`);
    grupo.setAttribute("role", "group"); grupo.setAttribute("aria-label", `objetos a la ${titulo} del grifo`);
    for (const o of D.objetos.filter(filtro).sort((a, b) => Math.abs(a.x) - Math.abs(b.x))) {
      const b = html("button", "sim-obj control");
      b.type = "button";
      b.append(html("span", "sim-obj-signo"), html("span", "sim-obj-nombre", o.nombre), html("span", "caption", `${o.gramos} g`));
      b.addEventListener("click", () => {       // un clic: la forma siguiente, y al final quitado
        parar();
        const ciclo = [...formas.get(o.id), "fuera"];
        cambia(o.id, ciclo[(ciclo.indexOf(forma.get(o.id)) + 1) % ciclo.length]);
      });
      botones.set(o.id, b); grupo.appendChild(b);
    }
    objetos.appendChild(grupo);
  }

  const acciones = html("div", "sim-acciones");
  const bInfo = html("button", "sim-accion control", "i"); bInfo.type = "button"; bInfo.setAttribute("aria-label", "qué significan las cifras");
  const bPlay = html("button", "sim-accion control", "▶ secuencia"); bPlay.type = "button";
  const bTodos = html("button", "sim-accion control", "▼ todo abajo"); bTodos.type = "button";
  acciones.append(bInfo, bPlay, bTodos);
  bTodos.addEventListener("click", () => {      // todo lo que tiene dos formas, a la vez
    parar();
    const dobles = D.objetos.filter((o) => formas.get(o.id).length > 1);
    const destino = dobles.some((o) => ultima.get(o.id) === "arriba") ? "abajo" : "arriba";
    dobles.forEach((o) => cambia(o.id, destino));
  });

  const leccion = html("section", "sim-leccion"); leccion.hidden = true; leccion.setAttribute("aria-label", "qué significan las cifras");
  const cerrar = html("button", "sim-leccion-cerrar control", "×"); cerrar.type = "button"; cerrar.setAttribute("aria-label", "cerrar");
  const rejilla = html("div", "sim-leccion-rejilla");
  for (const [t, ps] of LECCION) {
    const c = html("div", "sim-carta"); c.appendChild(html("h3", "control", t));
    ps.forEach((p) => c.appendChild(html("p", "caption", p))); rejilla.appendChild(c);
  }
  leccion.append(html("h2", "label", "qué significan las cifras"), cerrar, rejilla);
  bInfo.addEventListener("click", () => { leccion.hidden = false; cerrar.focus(); });
  cerrar.addEventListener("click", () => { leccion.hidden = true; bInfo.focus(); });

  raiz.append(lienzo, tablero, objetos, acciones, leccion);
  escena.querySelector(".lienzo").after(raiz);
  escena.classList.add("simulando");

  function pinta() {
    const e = est.estado(puestos);
    const uso = Math.max(dCano.pon(e.cano, D.aguanta_cano_N), dMani.pon(e.manilla, D.aguanta_manilla_N),
      e.tension_izq / D.sigma_ok, e.tension_der / D.sigma_ok);
    const nivel = uso >= 1 ? "mal" : uso >= 0.6 ? "justo" : "bien";
    veredicto.dataset.nivel = nivel;
    veredicto.textContent = `${nivel === "mal" ? "se suelta" : nivel === "justo" ? "aguanta, con poco margen" : uso > 0.001 ? `estable · margen ×${n1(1 / uso)}` : "estable"} · ${Math.round(e.peso).toLocaleString("es-ES")} g`;
    brazos.textContent = `brazo izq ${n1(e.tension_izq)} mpa · punta ${n1(e.flecha_izq)} mm   |   brazo der ${n1(e.tension_der)} mpa · punta ${n1(e.flecha_der)} mm`;
    pintaViga(viga, D, est, puestos, e);
  }
  function rotula(id) {
    const f = forma.get(id), b = botones.get(id), o = D.objetos.find((x) => x.id === id);
    b.dataset.forma = f; b.firstChild.textContent = SIGNO[f];
    b.setAttribute("aria-label", `${o.nombre}, ${o.gramos} g: ${DICE[f]}. pulsa para cambiar`);
    const dobles = D.objetos.filter((x) => formas.get(x.id).length > 1);
    bTodos.textContent = dobles.some((x) => ultima.get(x.id) === "arriba") ? "▼ todo abajo" : "▲ todo arriba";
  }
  function cambia(id, f) {
    forma.set(id, f);
    if (f === "fuera") puestos.delete(id); else { puestos.add(id); ultima.set(id, f); }
    rotula(id); mover(id); pinta();
  }
  const pon = (id, si) => cambia(id, si ? ultima.get(id) : "fuera");
  D.objetos.forEach((o) => rotula(o.id));
  function parar() { cola = []; clearTimeout(reloj); paso.textContent = ""; }
  function sigue() {
    const p = cola.shift();
    if (!p || !vivo) return;
    paso.textContent = p.texto;
    p.cambios.forEach(([id, si]) => pon(id, si));
    reloj = setTimeout(sigue, reducido ? Math.min(p.espera, 1200) : p.espera);
  }
  bPlay.addEventListener("click", () => {
    parar();
    const ids = D.objetos.map((o) => o.id), nombre = (id) => D.objetos.find((o) => o.id === id).nombre;
    const orden = [...D.objetos].sort((a, b) => b.gramos - a.gramos).map((o) => o.id);
    const izq = D.objetos.filter((o) => o.x < 0).map((o) => o.id), der = D.objetos.filter((o) => o.x > 0).map((o) => o.id);
    cola.push({ texto: "barra vacía", cambios: ids.map((id) => [id, false]), espera: 1100 });
    orden.forEach((id) => cola.push({ texto: `entra ${nombre(id)}`, cambios: [[id, true]], espera: 1300 }));
    cola.push({ texto: "todo puesto: los dos lazos apoyan", cambios: [], espera: 2200 });
    cola.push({ texto: "te llevas lo de la izquierda: tiran del lazo del caño", cambios: izq.map((id) => [id, false]), espera: 3200 });
    cola.push({ texto: "vuelve lo de la izquierda", cambios: izq.map((id) => [id, true]), espera: 1500 });
    cola.push({ texto: "te llevas lo de la derecha: tiran del lazo de la manilla", cambios: der.map((id) => [id, false]), espera: 3200 });
    cola.push({ texto: "todo en su sitio", cambios: der.map((id) => [id, true]), espera: 1500 });
    cola.push({ texto: "", cambios: [], espera: 0 });
    sigue();
  });
  pinta();

  // ── el modelo ───────────────────────────────────────────────────────────────
  try {
    const THREE = await import("three");
    const { GLTFLoader } = await import("three/addons/loaders/GLTFLoader.js");
    const { RoomEnvironment } = await import("three/addons/environments/RoomEnvironment.js");
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
    renderer.toneMapping = THREE.LinearToneMapping; renderer.toneMappingExposure = 0.9;
    renderer.setClearColor(0x000000, 0);
    const canvas = renderer.domElement; lienzo.appendChild(canvas);
    const scene = new THREE.Scene();
    scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
    const camera = new THREE.PerspectiveCamera(26, 1, 0.001, 50);
    const casa = { az: -0.2, pol: 1.42, zoom: 0.62 }, vista = { ...casa };
    const mira = new THREE.Vector3(); let radio = 1, pedido = false;
    const grupos = new Map(), anim = new Map();

    const dibuja = (t) => {
      pedido = false;
      if (!vivo || !canvas.isConnected) { renderer.dispose(); return; }
      const w = lienzo.clientWidth, h = lienzo.clientHeight;
      if (!w || !h) return;
      const pr = renderer.getPixelRatio();
      if (canvas.width !== Math.round(w * pr) || canvas.height !== Math.round(h * pr)) { renderer.setSize(w, h, false); camera.aspect = w / h; }
      let sigueAnim = false;
      for (const [id, a] of anim) {
        const k = reducido ? 1 : Math.min(1, (t - a.t0) / 520), s = k * k * (3 - 2 * k), v = a.de + (a.a - a.de) * s, g = grupos.get(id);
        g.position.set(0, (1 - v) * 0.07, (1 - v) * 0.11); g.visible = v > 0.02;
        g.traverse((o) => { if (o.isMesh) o.material.opacity = v; });
        a.v = v; if (k < 1) sigueAnim = true; else anim.delete(id);
      }
      const mitad = camera.fov * Math.PI / 360;
      const d = radio / Math.sin(Math.min(mitad, Math.atan(Math.tan(mitad) * camera.aspect))) * vista.zoom;
      camera.position.set(mira.x + d * Math.sin(vista.pol) * Math.sin(vista.az), mira.y + d * Math.cos(vista.pol), mira.z + d * Math.sin(vista.pol) * Math.cos(vista.az));
      camera.lookAt(mira); camera.updateProjectionMatrix(); renderer.render(scene, camera);
      if (sigueAnim) pide();
    };
    const pide = () => { if (!pedido) { pedido = true; requestAnimationFrame(dibuja); } };

    const gltf = await new GLTFLoader().loadAsync(glb);
    if (!vivo) { renderer.dispose(); return desmontar; }
    scene.add(gltf.scene);
    const sueltos = [], jinetes = new Map();
    const FORMA = { obj: "arriba", objb: "abajo", jinete: "arriba", jineteb: "abajo" };
    gltf.scene.traverse((o) => {
      if (o.name === "pared") o.visible = false;      // el fondo de la web ya hace de pared
      const m = /^(objb?)_([a-z]+)_\d+$/.exec(o.name || "");
      if (m && o.isMesh) sueltos.push([`${m[2]}|${FORMA[m[1]]}`, o]);
      const j = /^(jineteb?)_([a-z]+)$/.exec(o.name || "");
      if (j) jinetes.set(`${j[2]}|${FORMA[j[1]]}`, o);
    });
    for (const [clave, malla] of sueltos) {
      if (!grupos.has(clave)) { const g = new THREE.Group(); scene.add(g); grupos.set(clave, g); }
      malla.material = malla.material.clone(); malla.material.transparent = true; grupos.get(clave).attach(malla);
    }
    // un objeto de una sola forma usa el grupo "arriba" esté como esté
    const clave = (id, f) => (grupos.has(`${id}|${f}`) ? `${id}|${f}` : `${id}|arriba`);
    const esfera = new THREE.Box3().setFromObject(scene).getBoundingSphere(new THREE.Sphere());
    mira.copy(esfera.center); radio = esfera.radius;
    const lleva = (k, a) => {
      const g = grupos.get(k); if (!g) return;
      const ahora = anim.has(k) ? anim.get(k).v : (g.visible ? 1 : 0);
      if (ahora !== a) anim.set(k, { de: ahora, a, t0: performance.now(), v: ahora });
    };
    mover = (id) => {
      const f = forma.get(id), visible = f === "fuera" ? null : clave(id, f);
      for (const k of grupos.keys()) if (k.startsWith(`${id}|`)) lleva(k, k === visible ? 1 : 0);
      // el enganche que se ve es el de la forma puesta (o la última, si está quitado)
      const u = jinetes.has(`${id}|${ultima.get(id)}`) ? ultima.get(id) : "arriba";
      for (const [k, j] of jinetes) if (k.startsWith(`${id}|`)) j.visible = k === `${id}|${u}`;
      pide();
    };
    for (const g of grupos.values()) g.visible = false;
    D.objetos.forEach((o) => { const k = forma.get(o.id) === "fuera" ? null : clave(o.id, forma.get(o.id)); if (k) grupos.get(k).visible = true; mover(o.id); });

    // arrastrar gira, pellizcar o la rueda acercan
    const dedos = new Map(); let sep = 0;
    const separa = () => { const [a, b] = [...dedos.values()]; return Math.hypot(a.x - b.x, a.y - b.y); };
    const tope = (z) => Math.max(0.15, Math.min(1.5, z));
    canvas.addEventListener("pointerdown", (ev) => { dedos.set(ev.pointerId, { x: ev.clientX, y: ev.clientY }); canvas.setPointerCapture?.(ev.pointerId); if (dedos.size === 2) sep = separa(); });
    canvas.addEventListener("pointermove", (ev) => {
      const p = dedos.get(ev.pointerId); if (!p) return;
      const dx = ev.clientX - p.x, dy = ev.clientY - p.y; p.x = ev.clientX; p.y = ev.clientY;
      if (dedos.size === 1) { vista.az -= dx * 0.008; vista.pol = Math.max(0.2, Math.min(Math.PI - 0.2, vista.pol - dy * 0.008)); }
      else if (dedos.size === 2) { const s = separa(); if (sep > 0 && s > 0) vista.zoom = tope(vista.zoom * sep / s); sep = s; }
      pide();
    });
    const suelta = (ev) => dedos.delete(ev.pointerId);
    canvas.addEventListener("pointerup", suelta); canvas.addEventListener("pointercancel", suelta);
    canvas.addEventListener("wheel", (ev) => { ev.preventDefault(); vista.zoom = tope(vista.zoom * (ev.deltaY > 0 ? 1.08 : 0.93)); pide(); }, { passive: false });
    canvas.addEventListener("dblclick", () => { Object.assign(vista, casa); pide(); });
    new ResizeObserver(pide).observe(lienzo);
    pide();
  } catch (err) {
    lienzo.appendChild(html("p", "caption sim-sin3d", "no se pudo cargar el modelo. el tablero funciona igual."));
  }

  function desmontar() {
    vivo = false; parar();
    raiz.remove(); escena.classList.remove("simulando");
  }
  return desmontar;
}
