"""PDF download in the authorized session, without a public /media file URL.

CCv2 transports bytes inside that session's rendered component data. A local
browser Blob supplies the download; it is never registered in media storage.
The caller must fetch bytes through EvaluationStore's owner check each run.
"""
import base64
import streamlit as st
from app_theme import download_css

_DOWNLOAD = st.components.v2.component(
    "impulso_private_pdf",
    html='<button type="button"></button><a hidden></a>',
    css=download_css(),
    js="""
export default function ({data, parentElement}) {
  const button = parentElement.querySelector('button');
  const anchor = parentElement.querySelector('a');
  button.textContent = data.label;
  button.onclick = () => {
    const bytes = Uint8Array.from(atob(data.pdf), c => c.charCodeAt(0));
    const url = URL.createObjectURL(new Blob([bytes], {type:'application/pdf'}));
    anchor.href = url;
    anchor.download = data.filename;
    anchor.click();
    setTimeout(() => { URL.revokeObjectURL(url); anchor.removeAttribute('href'); }, 1000);
  };
  return () => { button.onclick = null; anchor.removeAttribute('href'); };
}
""",
)


def private_pdf_download(label: str, pdf: bytes, filename: str, key: str):
    if not pdf.startswith(b"%PDF-"):
        raise ValueError("No se ha generado un PDF válido.")
    _DOWNLOAD(data=dict(label=label,pdf=base64.b64encode(pdf).decode('ascii'),filename=filename),
              key=key,width="stretch",height="content")
