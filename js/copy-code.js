// Copy-to-clipboard for Hugo code blocks

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.copy-code-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const wrapper = btn.closest('.codeblock-wrapper');
      const codeElem = wrapper.querySelector('pre code');
      if (!codeElem) return;
      const code = codeElem.innerText;
      navigator.clipboard.writeText(code).then(function () {
        // Feedback: change icon or show text
        btn.innerHTML = '<span style="color:green;font-size:14px;">Copied!</span>';
        setTimeout(function () {
          btn.innerHTML = `<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"20\" height=\"20\" fill=\"none\" viewBox=\"0 0 20 20\"><rect x=\"6\" y=\"6\" width=\"9\" height=\"9\" rx=\"2\" fill=\"#888\"/><rect x=\"3\" y=\"3\" width=\"9\" height=\"9\" rx=\"2\" fill=\"#bbb\"/></svg>`;
        }, 1200);
      });
    });
  });
});
