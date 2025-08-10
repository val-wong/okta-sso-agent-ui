import React, { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

const S = {
  page: { maxWidth: 960, margin: "32px auto", padding: "0 16px", fontFamily: "Inter, ui-sans-serif, system-ui" },
  h1: { margin: 0, fontSize: 28, fontWeight: 700 },
  sub: { color: "#556", fontSize: 13, marginTop: 6 },
  card: { border: "1px solid #e6e8ef", borderRadius: 12, padding: 16, background: "#fff", marginTop: 16 },
  title: { margin: 0, fontSize: 18, fontWeight: 650, marginBottom: 8 },
  row: { display: "grid", gap: 12, marginTop: 8 },
  input: { width: "100%", padding: 10, borderRadius: 10, border: "1px solid #d7dbe6", fontSize: 14 },
  textarea: { width: "100%", minHeight: 160, padding: 10, borderRadius: 10, border: "1px solid #d7dbe6", fontSize: 13, fontFamily: "ui-monospace, Menlo, SFMono-Regular, monospace" },
  btnRow: { display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" },
  btn: { padding: "10px 14px", borderRadius: 10, border: "1px solid #cfd5e3", background: "#f8fafc", cursor: "pointer", fontSize: 14 },
  btnPrimary: { padding: "10px 14px", borderRadius: 10, border: "1px solid #3b82f6", background: "#3b82f6", color: "#fff", cursor: "pointer", fontSize: 14 },
  error: { color: "#a40000", background: "#ffecec", border: "1px solid #ffc6c6", padding: 10, borderRadius: 10 },
  code: { background: "#0b1020", color: "#e6e6e6", padding: 12, borderRadius: 10, overflowX: "auto", fontSize: 13 },
  hint: { color: "#67728a", fontSize: 12 },
  statWrap: { display: "grid", gridTemplateColumns: "repeat(3, minmax(0,1fr))", gap: 12 },
  stat: { border: "1px solid #e6e8ef", borderRadius: 10, padding: 10 },
  statLabel: { fontSize: 12, color: "#6b7280" },
  statValue: { fontSize: 14, fontWeight: 600 },
};

export default function App() {
  // Backend status
  const [config, setConfig] = useState(null);
  const [fatal, setFatal] = useState("");

  // Fixed to Zoom flow (no template dropdown)
  const template = "zoom_saml_only";

  // Form state
  const [appLabel, setAppLabel] = useState("Zoom SAML");
  const [oktaAppId, setOktaAppId] = useState("");
  const [ssoAcsUrl, setSsoAcsUrl] = useState("");
  const [ssoEntityId, setSsoEntityId] = useState("");
  const [idpX509, setIdpX509] = useState("");

  // UX
  const [loadingApp, setLoadingApp] = useState(false);
  const [genLoading, setGenLoading] = useState(false);
  const [tfOut, setTfOut] = useState({ filename: "", content: "" });
  const [savedPath, setSavedPath] = useState("");
  const [err, setErr] = useState("");

  // Load backend config
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/config`);
        const j = await r.json();
        setConfig(j);
      } catch {
        setFatal(`Cannot reach backend at ${API_BASE}. Is it running?`);
      }
    })();
  }, []);

  async function loadFromOkta() {
    setErr("");
    setSavedPath("");
    setTfOut({ filename: "", content: "" });
    if (!oktaAppId.trim()) return setErr("Enter an Okta App ID (e.g., 0oattcrmmgwZFhvkb697).");
    setLoadingApp(true);
    try {
      // 1) App details → ACS + Entity
      const r1 = await fetch(`${API_BASE}/apps/${oktaAppId.trim()}`);
      if (!r1.ok) throw new Error(`${r1.status} ${await r1.text()}`);
      const app = await r1.json();
      const signOn = app?.settings?.signOn || {};
      const acs = signOn.recipient || signOn.ssoAcsUrl || "";
      const entity = signOn.audience || signOn.idpIssuer || "";
      if (app?.label) setAppLabel(app.label);
      if (acs) setSsoAcsUrl(acs);
      if (entity) setSsoEntityId(entity);

      // 2) IdP cert (PEM)
      const r2 = await fetch(`${API_BASE}/apps/${oktaAppId.trim()}/saml/cert`);
      if (!r2.ok) throw new Error(`${r2.status} ${await r2.text()}`);
      const j2 = await r2.json();
      if (!j2?.pem) throw new Error("No certificate found in metadata.");
      setIdpX509(j2.pem.trim());
    } catch (e) {
      setErr(`Failed to load from Okta: ${e.message}`);
    } finally {
      setLoadingApp(false);
    }
  }

  async function generateTf() {
    setErr("");
    setSavedPath("");
    setTfOut({ filename: "", content: "" });

    if (!appLabel.trim()) return setErr("App Label is required.");
    if (!ssoAcsUrl.trim()) return setErr("SAML ACS URL is required.");
    if (!ssoEntityId.trim()) return setErr("SAML Entity ID is required.");
    if (!idpX509.trim().includes("-----BEGIN CERTIFICATE-----"))
      return setErr("IdP X509 Cert must be a PEM block with BEGIN/END lines.");

    setGenLoading(true);
    try {
      const payload = {
        template, // backend enforces Zoom rules (NameID=email, entity=https://zoom.us if missing)
        app_label: appLabel.trim(),
        sso_acs_url: ssoAcsUrl.trim(),
        sso_entity_id: ssoEntityId.trim(),
        idp_x509_cert: idpX509.trim(),
      };
      const r = await fetch(`${API_BASE}/tf/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
      const j = await r.json();
      setTfOut(j);
    } catch (e) {
      setErr(`Failed to generate: ${e.message}`);
    } finally {
      setGenLoading(false);
    }
  }

  async function saveTf() {
    if (!tfOut.content || !tfOut.filename) return;
    setErr("");
    try {
      const r = await fetch(`${API_BASE}/files/tf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: tfOut.filename, content: tfOut.content }),
      });
      const j = await r.json();
      if (j.saved) setSavedPath(j.path);
    } catch (e) {
      setErr(`Failed to save: ${e.message}`);
    }
  }

  function downloadTf() {
    if (!tfOut.content || !tfOut.filename) return;
    const blob = new Blob([tfOut.content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = tfOut.filename; a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div style={S.page}>
      <div>
        <h1 style={S.h1}>Zoom SAML Terraform Generator</h1>
        <div style={S.sub}>API: {API_BASE}</div>
      </div>

      {fatal && <div style={{ ...S.error, marginTop: 12 }}>{fatal}</div>}

      <div style={S.card}>
        <h3 style={S.title}>Status</h3>
        {config ? (
          <div style={S.statWrap}>
            <div style={S.stat}><div style={S.statLabel}>Health</div><div style={S.statValue}>ok</div></div>
            <div style={S.stat}><div style={S.statLabel}>Org URL</div><div style={S.statValue}>{config.org_url || config.used_org_url || "—"}</div></div>
            <div style={S.stat}><div style={S.statLabel}>Token</div><div style={S.statValue}>{config.has_token ? "present" : "missing"}</div></div>
          </div>
        ) : (
          <div>Loading config…</div>
        )}
      </div>

      <div style={S.card}>
        <h3 style={S.title}>Load from Okta</h3>
        <div style={S.row}>
          <label>
            Okta App ID
            <input
              placeholder="e.g., 0oattcrmmgwZFhvkb697"
              value={oktaAppId}
              onChange={e => setOktaAppId(e.target.value)}
              style={S.input}
            />
          </label>
          <div style={S.btnRow}>
            <button onClick={loadFromOkta} disabled={loadingApp} style={S.btn}>
              {loadingApp ? "Loading…" : "Load details (ACS/Entity) & PEM"}
            </button>
          </div>
          <div style={S.hint}>
            Pulls <code>/apps/&lt;id&gt;</code> and <code>/apps/&lt;id&gt;/saml/cert</code> from your Okta tenant using your backend.
          </div>
        </div>
      </div>

      <div style={S.card}>
        <h3 style={S.title}>SAML Settings (auto-filled)</h3>
        <div style={S.row}>
          <label>
            App Label
            <input value={appLabel} onChange={e => setAppLabel(e.target.value)} style={S.input}/>
          </label>
          <label>
            SAML ACS URL
            <input value={ssoAcsUrl} onChange={e => setSsoAcsUrl(e.target.value)} style={S.input} placeholder="https://zoom.us/saml/SSO"/>
          </label>
          <label>
            SAML Entity ID
            <input value={ssoEntityId} onChange={e => setSsoEntityId(e.target.value)} style={S.input} placeholder="https://zoom.us"/>
          </label>
          <label>
            IdP X509 Cert (PEM)
            <textarea value={idpX509} onChange={e => setIdpX509(e.target.value)} style={S.textarea}
              placeholder={"-----BEGIN CERTIFICATE-----\n<base64 lines>\n-----END CERTIFICATE-----"} />
          </label>
          <div style={S.hint}>
            NameID rules for Zoom (email + emailAddress format) are enforced server-side by the <code>zoom_saml_only</code> template.
          </div>

          {err && <div style={S.error}>{err}</div>}

          <div style={S.btnRow}>
            <button onClick={generateTf} disabled={genLoading} style={S.btnPrimary}>
              {genLoading ? "Generating…" : "Generate Terraform"}
            </button>
            <button onClick={saveTf} disabled={!tfOut.content} style={S.btn}>Save .tf</button>
            <button onClick={downloadTf} disabled={!tfOut.content} style={S.btn}>Download .tf</button>
            {savedPath && <span style={{ color: "#0a7", fontSize: 12 }}>Saved to {savedPath}</span>}
          </div>
        </div>
      </div>

      {tfOut.content && (
        <div style={S.card}>
          <h3 style={S.title}>Preview</h3>
          <pre style={S.code}>{tfOut.content}</pre>
        </div>
      )}
    </div>
  );
}
