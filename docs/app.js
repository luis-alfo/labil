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
const tipoDe = (e) => (e.tipo === "version" && e.por_imprimir ? TIPO.pendiente : TIPO[e.tipo]);

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
    <nav>
      <a class="control" href="#/" ${actual === "objetos" ? 'aria-current="page"' : ""}>objetos</a>
      <a class="control" href="#/historial" ${actual === "historial" ? 'aria-current="page"' : ""}>historial</a>
    </nav>
  </header>`;
}
function pie() {
  return `<footer class="pie">
    <p class="caption">coste = plástico a ${DATOS.euros_kg} €/kg. Gramos estimados con un laminador simplificado
      (${esc(DATOS.perfil)}), contrastado con el laminador real: error medio 4 %, máximo 9 %.
      No incluye purga de cambios de color ni la luz de la impresora.</p>
    <p class="caption"><a class="enlace" href="v1/">archivo · web v1</a> · actualizado ${esc(DATOS.generado.slice(0, 10))}</p>
  </footer>`;
}

// ── inicio: lista de objetos ─────────────────────────────────────────────────
function vistaInicio() {
  const todos = DATOS.objetos.flatMap((o) => o.estados);
  const total = todos.reduce((s, e) => s + (e.coste ? e.coste.euros : 0), 0);
  const gramos = todos.reduce((s, e) => s + (e.coste ? e.coste.gramos : 0), 0);
  const filas = DATOS.objetos.map((o) => {
    const ultimo = o.estados[o.estados.length - 1];
    const impresas = o.estados.filter((e) => e.tipo === "version" && !e.por_imprimir).length;
    return `<li><a class="panel obj" href="#/${o.id}">
      <div class="obj-cab"><h2 class="title">${esc(o.nombre)}</h2>
        ${ultimo.coste ? `<span class="strong signal">${eur(ultimo.coste.euros)}</span>` : ""}</div>
      <p class="body muted">${esc(o.que)}</p>
      <div class="ticks" aria-hidden="true">${o.estados.map((e) => `<i class="${tipoDe(e).cls}"></i>`).join("")}</div>
      <p class="caption">${o.estados.length} estados · ${impresas} ${impresas === 1 ? "impresa" : "impresas"} · ${esc(o.estado)} · ${fecha(ultimo.fecha)}</p>
    </a></li>`;
  }).join("");
  app.innerHTML = cabecera("objetos") + `<main>
    <section class="hero">
      <p class="label">de la letra al objeto</p>
      <h1 class="display" id="titulo">objetos</h1>
      <p class="body muted">Cada objeto con sus versiones impresas, sus pruebas y sus borradores, en el orden en que se hicieron.</p>
      <div class="cifra">${bitEur(total, "lg")}
        <p class="caption">${gr(gramos)} de plástico si se imprimiera todo el archivo · ${todos.length} estados</p></div>
    </section>
    <ol class="lista">${filas}</ol>
    <div class="leyenda caption">
      <span class="status version">impresa</span><span class="status pendiente">por imprimir</span>
      <span class="status prueba">prueba</span><span class="status borrador">borrador</span>
    </div>
    ${pie()}
  </main>`;
  descifra(document.getElementById("titulo"));
  document.title = "labil · objetos";
}

// ── objeto: un estado a la vez, con raíl arriba y pasos abajo ────────────────
function vistaObjeto(oid, eid) {
  const o = DATOS.objetos.find((x) => x.id === oid);
  if (!o) return (location.hash = "#/");
  let i = o.estados.findIndex((e) => e.id === eid);
  if (i < 0) i = o.estados.length - 1; // sin estado: el más reciente
  const e = o.estados[i];
  const ant = o.estados[i - 1];
  const sig = o.estados[i + 1];
  const t = tipoDe(e);
  const enlace = (x) => `#/${o.id}/${x.id}`;

  const rail = o.estados.map((x) => `<a class="chip" href="${enlace(x)}" ${x === e ? 'aria-current="true"' : ""}>
      <span class="status ${tipoDe(x).cls}">${tipoDe(x).txt}</span>
      <span class="control">${esc(x.nombre)}</span>
      <span class="caption">${fecha(x.fecha)}</span></a>`).join("");

  const visor = e.modelos.length
    ? `<model-viewer id="mv" src="${conVer(e.modelos[0].src)}" alt="${esc(o.nombre)} · ${esc(e.nombre)}"
         camera-controls touch-action="pan-y" interaction-prompt="none" shadow-intensity="0"
         exposure="1.05" ar ar-modes="webxr scene-viewer quick-look"></model-viewer>
       ${e.modelos.length > 1 ? `<div class="vistas" role="group" aria-label="vistas">${e.modelos.map((m, k) =>
         `<button class="seg control" data-src="${conVer(m.src)}" aria-pressed="${k === 0}">${esc(m.nombre)}</button>`).join("")}</div>` : ""}
       <p class="caption ayuda">arrastra para girar · pellizca para acercar</p>`
    : e.imagenes.length
      ? `<img src="${e.imagenes[0].src}" alt="${esc(e.imagenes[0].pie)}" style="width:100%;display:block;background:#f3f2ee">`
      : `<div class="sin-modelo caption">sin modelo 3D en el repositorio</div>`;

  // qué cambia respecto al estado anterior con coste
  const previo = o.estados.slice(0, i).reverse().find((x) => x.coste);
  const delta = e.coste && previo
    ? (() => {
        const dg = e.coste.gramos - previo.coste.gramos;
        const de = e.coste.euros - previo.coste.euros;
        const cls = dg > 0 ? "mas" : "menos";
        return `<div class="delta"><p class="caption">respecto a «${esc(previo.nombre)}»</p>
          <p class="body strong ${cls}">${firma(dg, gr)} · ${firma(de, eur)}</p></div>`;
      })()
    : "";

  const piezas = e.piezas.length
    ? `<section class="seccion"><h3 class="label">piezas</h3><ul class="flujo">
        ${e.piezas.map((p) => `<li><span>${esc(p.nombre)}${p.cantidad > 1 ? ` × ${p.cantidad}` : ""}
          <span class="caption"> · ${esc(p.fuente)}</span></span>
          <span class="num muted">${gr(p.gramos)}</span><span class="num strong">${eur(p.euros)}</span></li>`).join("")}
        ${e.piezas.length > 1 ? `<li class="total"><span class="caption">total</span><span class="num muted">${gr(e.coste.gramos)}</span><span class="num strong signal">${eur(e.coste.euros)}</span></li>` : ""}
      </ul></section>`
    : "";

  const coste = e.coste
    ? `<div class="coste">${bitEur(e.coste.euros, "lg")}
        <p class="caption">${gr(e.coste.gramos)} de plástico · ${e.coste.origen === "laminador" ? "dato del laminador real" : "estimado"}</p></div>`
    : "";

  const imagenes = e.imagenes.length && e.modelos.length
    ? `<section class="seccion"><h3 class="label">imágenes</h3><div class="imagenes">${e.imagenes.map((im) =>
        `<figure><a href="${im.src}"><img src="${im.src}" alt="${esc(im.pie)}" loading="lazy"></a><figcaption class="caption">${esc(im.pie)}</figcaption></figure>`).join("")}</div></section>`
    : e.imagenes.length > 1
      ? `<section class="seccion"><h3 class="label">imágenes</h3><div class="imagenes">${e.imagenes.slice(1).map((im) =>
          `<figure><a href="${im.src}"><img src="${im.src}" alt="${esc(im.pie)}" loading="lazy"></a><figcaption class="caption">${esc(im.pie)}</figcaption></figure>`).join("")}</div></section>`
      : "";

  const descargas = e.descargas.length
    ? `<section class="seccion"><h3 class="label">descargas</h3><ul class="descargas">${e.descargas.map((d) => {
        const nombre = d.split("/").pop();
        return `<li><a href="${d}" download><span class="ext control">${esc(nombre.split(".").pop())}</span><span class="nombre">${esc(nombre)}</span></a></li>`;
      }).join("")}</ul></section>`
    : "";

  app.innerHTML = cabecera("objetos", o.nombre) + `<main>
    <section class="obj-head">
      <p class="body muted">${esc(o.que)}</p>
      <p class="caption">${o.estados.length} estados · ${esc(o.estado)}${o.aprendizajes ? ` · <a class="enlace" href="${o.aprendizajes}">aprendizajes</a>` : ""}</p>
    </section>
    <nav class="rail" id="rail" aria-label="versiones y borradores">${rail}</nav>
    <article class="estado" id="estado">
      <div class="panel visor">${visor}</div>
      <div class="ficha" id="ficha">
        <div class="ficha-cab"><span class="status ${t.cls} control">${t.txt}</span>
          <span class="caption">${fechaLarga(e.fecha)}${e.archivo ? ` · archivo: ${esc(e.archivo)}` : ""}</span></div>
        <h1 class="display" id="titulo">${esc(e.nombre)}</h1>
        <p class="body">${esc(e.texto)}</p>
        ${coste}${delta}${piezas}${imagenes}${descargas}
      </div>
    </article>
    <nav class="pasos" id="pasos" aria-label="anterior y siguiente">
      ${ant ? `<a class="ant" href="${enlace(ant)}" rel="prev"><span class="caption">← anterior</span><span class="control">${esc(ant.nombre)}</span></a>` : `<span class="vacio"></span>`}
      <span class="donde caption">${i + 1} / ${o.estados.length}</span>
      ${sig ? `<a class="sig" href="${enlace(sig)}" rel="next"><span class="caption">siguiente →</span><span class="control">${esc(sig.nombre)}</span></a>` : `<span class="vacio"></span>`}
    </nav>
    ${pie()}
  </main>`;

  document.title = `labil · ${o.nombre} · ${e.nombre}`;
  descifra(document.getElementById("titulo"));
  document.getElementById("ficha").classList.add("llega");
  const actual = document.querySelector('.chip[aria-current="true"]');
  if (actual) actual.scrollIntoView({ block: "nearest", inline: "center", behavior: reducido ? "auto" : "smooth" });

  // vistas del visor
  document.querySelectorAll(".seg").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".seg").forEach((x) => x.setAttribute("aria-pressed", x === b));
    document.getElementById("mv").src = b.dataset.src;
  }));

  // deslizar en la ficha o en la barra de pasos (no en el visor, que gira el modelo)
  const ir = (x) => x && (location.hash = enlace(x));
  for (const zona of [document.getElementById("ficha"), document.getElementById("pasos")]) {
    let x0 = null, y0 = null;
    zona.addEventListener("touchstart", (ev) => { x0 = ev.touches[0].clientX; y0 = ev.touches[0].clientY; }, { passive: true });
    zona.addEventListener("touchend", (ev) => {
      if (x0 === null) return;
      const dx = ev.changedTouches[0].clientX - x0, dy = ev.changedTouches[0].clientY - y0;
      x0 = null;
      if (Math.abs(dx) > 64 && Math.abs(dy) < 40) ir(dx < 0 ? sig : ant);
    }, { passive: true });
  }
  teclas = (ev) => {
    if (ev.target.closest("model-viewer, input, textarea")) return;
    if (ev.key === "ArrowLeft") ir(ant);
    if (ev.key === "ArrowRight") ir(sig);
  };
}
let teclas = null;
document.addEventListener("keydown", (ev) => teclas && teclas(ev));

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
          <span class="status ${tipoDe(e).cls} caption">${tipoDe(e).txt}</span></span>
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
  const partes = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean).map(decodeURIComponent);
  if (!partes.length) vistaInicio();
  else if (partes[0] === "historial") vistaHistorial();
  else vistaObjeto(partes[0], partes[1]);
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
