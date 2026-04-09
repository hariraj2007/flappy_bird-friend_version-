/* ── Image preview & drag-drop ─────────────────── */

function setupDropzone(inputId, dropId, prevId, innerId) {
  const input  = document.getElementById(inputId);
  const drop   = document.getElementById(dropId);
  const prev   = document.getElementById(prevId);
  const inner  = document.getElementById(innerId);
  if (!input || !drop) return;

  function applyFile(file) {
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = e => {
      prev.src = e.target.result;
      prev.classList.add('visible');
      drop.classList.add('has-file');
      inner.querySelector('.dropzone__icon').textContent = '✅';
      inner.querySelector('.dropzone__text').textContent = file.name.length > 22
        ? file.name.slice(0, 20) + '…'
        : file.name;
      inner.querySelector('.dropzone__hint').textContent =
        Math.round(file.size / 1024) + ' KB';
    };
    reader.readAsDataURL(file);
    checkReady();
  }

  input.addEventListener('change', () => applyFile(input.files[0]));

  drop.addEventListener('dragover', e => { e.preventDefault(); drop.classList.add('dragover'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('dragover'));
  drop.addEventListener('drop', e => {
    e.preventDefault();
    drop.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) {
      const dt = new DataTransfer();
      dt.items.add(file);
      input.files = dt.files;
      applyFile(file);
    }
  });
}

setupDropzone('friend_image', 'drop1', 'prev1', 'drop1inner');
setupDropzone('jump_image',   'drop2', 'prev2', 'drop2inner');

/* ── Enable submit only when both images picked ─── */
function checkReady() {
  const btn  = document.getElementById('submitBtn');
  const img1 = document.getElementById('friend_image');
  const img2 = document.getElementById('jump_image');
  if (btn && img1 && img2) {
    btn.disabled = !(img1.files.length && img2.files.length);
  }
}

/* ── Copy command ──────────────────────────────── */
function copyCmd() {
  const text = document.getElementById('cmdText')?.textContent;
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector('.cmd-copy');
    if (!btn) return;
    const prev = btn.textContent;
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = prev, 1600);
  });
}

/* ── Sound field: clear placeholder if user focuses ─ */
const soundInput = document.getElementById('jump_sound');
if (soundInput) {
  soundInput.addEventListener('focus', function() {
    if (this.value === 'win.ogg') this.select();
  });
}
