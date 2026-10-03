document.addEventListener('DOMContentLoaded', () => {
  if (!navigator.clipboard) return;
  document.querySelectorAll('pre').forEach(block => {
    const text = (block.querySelector('code') || block).textContent;
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = '📋 복사';
    button.className = 'copy-button';
    button.setAttribute('aria-label', '코드 복사');
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = '✅ 복사됨!';
        setTimeout(() => { button.textContent = '📋 복사'; }, 2000);
      } catch {
        button.textContent = '직접 선택해 복사';
      }
    });
    block.appendChild(button);
  });
});
