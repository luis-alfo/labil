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

// ── inicio: qué es labil (portada animada) y, debajo, los objetos ───────────
const PASOS_IA = [
  { id: "escribir", txt: "escribes", dato: "«un soporte para el estropajo que abrace el grifo»" },
  { id: "modelar", txt: "la ia modela", dato: "openscad paramétrico · 4 piezas · sin soportes" },
  { id: "calcular", txt: "calcula resistencias", dato: "20 N en el borde → 17 MPa · admisible 20 ✓" },
  { id: "evaluar", txt: "evalúa el montaje", dato: "montaje simulado contra grifo, encimera y fregadero ✓" },
  { id: "prototipar", txt: "prototipa", dato: "pieza de prueba: abrazadera · 15 min · 0,34 €" },
  { id: "imprimir", txt: "se imprime", dato: "a1 · pla · capas de 0,2 mm · 43 g · 0,86 €" },
];

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
  app.innerHTML = `<section class="portada" aria-labelledby="titulo">
      <header class="portada-cab"><img src="icon.svg" alt=""><span class="label">l a b i l</span></header>
      <div class="portada-texto">
        <p class="label">de la letra al objeto</p>
        <h1 class="display" id="titulo">escribes. la ia lo modela, lo calcula y lo prueba. sale impreso.</h1>
        <p class="body muted">labil es el taller de luis en lagu: descripciones digitales que se convierten en objetos reales, con cada paso a la vista.</p>
      </div>
      <canvas id="lienzo-portada" aria-hidden="true"></canvas>
      <div class="portada-pasos">
        <ol class="pasos-ia" id="pasos-ia">${PASOS_IA.map((p, k) => `<li data-k="${k}"><i></i><span class="caption">${p.txt}</span></li>`).join("")}</ol>
        <p class="caption paso-dato" id="paso-dato" aria-live="polite"></p>
      </div>
      <button class="bajar" id="bajar"><span class="label">objetos</span><span aria-hidden="true">↓</span></button>
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

// ── portada: de la letra al objeto impreso, en una rejilla de píxeles ────────
// fases: escribir → los píxeles del texto se ordenan en la pieza (modelar) →
// mapa de tensiones (calcular) → barrido de comprobación (evaluar) →
// solo la abrazadera (prototipar) → capa a capa (imprimir) → objeto.
const C = { fondo: "#2b312b", apagado: "rgba(201,225,201,0.07)", tinta: "#f3fbf1", muda: "#c9e1c9",
  tenue: "#86a08a", senal: "#24e824", aviso: "#f2a516" };
// pieza en rejilla de 40 × 26: abrazadera, brazo, pata y cuna (el secadero, de perfil)
function piezaPortada() {
  const W = 40, H = 26, on = new Set();
  const rect = (x0, y0, x1, y1) => { for (let x = x0; x <= x1; x++) for (let y = y0; y <= y1; y++) on.add(x + "," + y); };
  rect(3, 0, 13, 1); rect(3, 0, 4, 7); rect(12, 0, 13, 7);   // abrazadera (rodea la columna)
  rect(3, 6, 31, 8);                                          // brazo a ras de la encimera
  rect(28, 6, 30, 23);                                        // pata del marco
  rect(21, 22, 38, 24); rect(21, 15, 22, 24); rect(37, 15, 38, 24); // cuna
  const celdas = [...on].map((k) => k.split(",").map(Number));
  const prueba = new Set(celdas.filter(([x, y]) => x <= 14 && y <= 8).map(([x, y]) => x + "," + y));
  return { W, H, celdas, prueba };
}
let animacion = 0;
function animarPortada() {
  const lienzo = document.getElementById("lienzo-portada");
  if (!lienzo) return;
  const ctx = lienzo.getContext("2d");
  const pasos = [...document.querySelectorAll("#pasos-ia li")];
  const dato = document.getElementById("paso-dato");
  const pieza = piezaPortada();
  const DUR = [2600, 2200, 1800, 1600, 1600, 3000, 1800]; // la última: objeto terminado
  const INICIO = DUR.reduce((acc, d, k) => (acc.push((acc[k - 1] || 0) + (k ? DUR[k - 1] : 0)), acc), []);
  const TOTAL = DUR.reduce((a, b) => a + b, 0);
  const id = ++animacion;
  let dims = null, origen = [], pasoActual = -1;

  const FRASE = PASOS_IA[0].dato.replace(/[«»]/g, "");
  // tamaño de letra que deja la frase dentro del lienzo (JetBrains Mono: ~0,6 em por carácter)
  const tamFrase = (w) => Math.max(10, Math.min(Math.floor(w / 22), Math.floor((w * 0.92) / (FRASE.length * 0.6))));
  function medir() {
    const r = lienzo.getBoundingClientRect(), dpr = Math.min(2, devicePixelRatio || 1);
    lienzo.width = Math.round(r.width * dpr); lienzo.height = Math.round(r.height * dpr);
    const cel = Math.max(4, Math.floor(Math.min(r.width / (pieza.W + 4), r.height / (pieza.H + 6))));
    const ox = Math.floor((r.width - pieza.W * cel) / 2), oy = Math.floor((r.height - pieza.H * cel) / 2) + cel;
    dims = { w: r.width, h: r.height, dpr, cel, ox, oy };
    // píxeles del texto escrito: se muestrean para que «vuelen» a la pieza
    const t = document.createElement("canvas"); t.width = Math.ceil(r.width); t.height = Math.ceil(r.height);
    const tc = t.getContext("2d"); tc.fillStyle = "#fff";
    tc.font = `500 ${tamFrase(r.width)}px "JetBrains Mono", monospace`;
    tc.textAlign = "center"; tc.textBaseline = "middle";
    tc.fillText(FRASE, r.width / 2, r.height / 2);
    const px = tc.getImageData(0, 0, t.width, t.height).data, paso = Math.max(3, Math.floor(cel / 2));
    origen = [];
    for (let y = 0; y < t.height; y += paso) for (let x = 0; x < t.width; x += paso)
      if (px[(y * t.width + x) * 4 + 3] > 128) origen.push([x, y]);
    if (!origen.length) origen = [[r.width / 2, r.height / 2]];
  }
  medir();
  addEventListener("resize", () => id === animacion && medir());

  const celda = (x, y, color, s = 1) => {
    const { cel, ox, oy, dpr } = dims, m = Math.max(1, Math.floor(cel * 0.12));
    ctx.fillStyle = color;
    ctx.fillRect((ox + x * cel + m) * dpr, (oy + y * cel + m) * dpr, (cel * s - 2 * m) * dpr, (cel * s - 2 * m) * dpr);
  };
  const escalon = (t, n = 6) => Math.floor(Math.min(1, Math.max(0, t)) * n) / n; // a saltos, no en curvas

  function marcarPaso(k) {
    if (k === pasoActual) return;
    pasoActual = k;
    pasos.forEach((li, j) => { li.classList.toggle("hecho", j < k); li.classList.toggle("ahora", j === k); });
    if (dato) { dato.textContent = k < PASOS_IA.length ? PASOS_IA[k].dato : "impreso ✓ · de la letra al objeto"; descifra(dato); }
  }

  function dibujar(ms) {
    if (id !== animacion || !document.body.contains(lienzo)) return;
    const { w, h, dpr, cel, ox, oy } = dims;
    ctx.clearRect(0, 0, w * dpr, h * dpr);
    // rejilla de píxeles apagados
    for (let x = 0; x < pieza.W; x++) for (let y = 0; y < pieza.H; y++) celda(x, y, C.apagado);
    const t = reducido ? TOTAL - 1 : ms % TOTAL;
    let fase = INICIO.findIndex((ini, k) => t >= ini && t < ini + DUR[k]);
    const f = (t - INICIO[fase]) / DUR[fase];
    marcarPaso(Math.min(fase, PASOS_IA.length));

    if (fase === 0) { // escribir: el texto aparece letra a letra
      const txt = FRASE;
      const n = Math.floor(txt.length * Math.min(1, f * 1.3));
      ctx.fillStyle = C.tinta; ctx.textAlign = "left"; ctx.textBaseline = "middle";
      ctx.font = `500 ${tamFrase(w) * dpr}px "JetBrains Mono", monospace`;
      const x0 = (w * dpr - ctx.measureText(txt).width) / 2; // crece hacia la derecha desde donde acabará
      ctx.fillText(txt.slice(0, n) + (Math.floor(ms / 400) % 2 ? "▌" : " "), x0, (h / 2) * dpr);
    } else if (fase === 1) { // modelar: los píxeles del texto se ordenan en la pieza
      const k = escalon(f * 1.15, 8);
      pieza.celdas.forEach(([x, y], i) => {
        const [sx, sy] = origen[(i * 7) % origen.length];
        const tx = ox + x * cel, ty = oy + y * cel;
        const px = sx + (tx - sx) * k, py = sy + (ty - sy) * k;
        ctx.fillStyle = k < 1 ? C.tinta : C.muda;
        ctx.fillRect(px * dpr, py * dpr, (cel - 2) * dpr, (cel - 2) * dpr);
      });
    } else if (fase === 2) { // calcular: tensiones, más altas en la unión brazo-pata
      const barrido = escalon(f, 10) * pieza.W;
      pieza.celdas.forEach(([x, y]) => {
        if (x > barrido) return celda(x, y, C.muda);
        const d = Math.hypot(x - 29, y - 7);
        celda(x, y, d < 3 ? C.aviso : d < 7 ? C.senal : C.tenue);
      });
    } else if (fase === 3) { // evaluar: una línea recorre la pieza comprobando
      const fila = Math.floor(escalon(f, 13) * pieza.H);
      pieza.celdas.forEach(([x, y]) => celda(x, y, y === fila ? C.senal : y < fila ? C.muda : C.tenue));
    } else if (fase === 4) { // prototipar: primero solo la abrazadera
      pieza.celdas.forEach(([x, y]) => celda(x, y, pieza.prueba.has(x + "," + y) ? C.senal : C.apagado.replace("0.07", "0.22")));
    } else { // imprimir capa a capa (y el objeto terminado)
      const capas = fase === 5 ? Math.floor(escalon(f, pieza.H) * pieza.H) : pieza.H;
      const nivel = pieza.H - capas; // de abajo arriba
      pieza.celdas.forEach(([x, y]) => celda(x, y, y >= nivel ? C.senal : C.apagado.replace("0.07", "0.18")));
      if (fase === 5 && capas < pieza.H) { // la boquilla recorre la capa actual
        const fila = pieza.celdas.filter(([, y]) => y === nivel - 1).map(([x]) => x);
        if (fila.length) celda(fila[Math.floor(ms / 60) % fila.length], nivel - 1, C.tinta);
      }
    }
    if (!reducido) requestAnimationFrame(dibujar);
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { medir(); requestAnimationFrame(dibujar); });
  else requestAnimationFrame(dibujar);
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
    ? e.modelos.map((m) => ({ nombre: m.nombre, src: conVer(m.src), tipo: "modelo" }))
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
      <span class="hud-precio">${e.coste ? bitEur(e.coste.euros, "sm") : ""}</span>
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
        ${coste}${delta}${memoria}${proceso}${piezas}${imagenes}${descargas}
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
