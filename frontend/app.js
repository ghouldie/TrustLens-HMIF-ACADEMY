const $ = id => document.getElementById(id);
const num = v => (v === "" ? null : Number(v));
$("go").onclick = async () => {
  const body = {account: $("account").value || null, category: $("category").value || null,
    price: num($("price").value), account_age_days: num($("age").value),
    followers: num($("followers").value), chat_text: $("chat").value || null};
  const r = await (await fetch("/api/assess", {method: "POST",
    headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)})).json();
  const li = a => a.map(x => `<li>${x}</li>`).join("");
  const el = $("result"); el.classList.remove("hidden");
  el.innerHTML = `<small>Skor risiko</small><div class="score ${r.level}">${r.score}/100 · ${r.level}</div>
  <small>Tingkat keyakinan ${Math.round(r.confidence*100)}%</small>
  <div class="bar"><i style="width:${r.confidence*100}%"></i></div>
  ${r.missing_inputs.length ? `<small>Data belum diisi: ${r.missing_inputs.join(", ")}. Keyakinan naik jika dilengkapi.</small>` : ""}
  <h2>Alasan</h2><ul>${li(r.reasons)}</ul><h2>Langkah aman</h2><ul>${li(r.safe_steps)}</ul>
  <small>${r.disclaimer}</small>`;
};
