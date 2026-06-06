/**
 * text_animator.js
 * Lógica separada para animar el cambio de texto con efecto 3D (Anime.js SplitText replica).
 */

function animateMethodNameChange(elementId, newText) {
    const el = document.getElementById(elementId);
    if (!el) return;

    if (el.dataset.currentText === newText) return;
    el.dataset.currentText = newText;

    const createAndAnimateNewText = () => {
        el.innerHTML = '';
        const chars = newText.split('');
        chars.forEach(char => {
            const span = document.createElement('span');
            span.className = 'char-3d';
            
            const v = char === ' ' ? '&nbsp;' : char;
            span.innerHTML = `
                <em class="face face-top">${v}</em>
                <em class="face-front">${v}</em>
                <em class="face face-bottom">${v}</em>
            `;
            el.appendChild(span);
        });

        // Effect from animejs docs
        const charsStagger = anime.stagger(50, { start: 0 });

        anime.timeline({
            defaults: { easing: 'easeOutElastic(1, .6)', duration: 1000 }
        })
        .add({
            targets: el.querySelectorAll('.char-3d'),
            rotateX: [90, 0], // Animate from bottom face to front face
            opacity: [0, 1],
            delay: charsStagger
        }, 0)
        .add({
            targets: el.querySelectorAll('.char-3d .face-front'),
            opacity: [0, 1],
            delay: charsStagger
        }, 0)
        .add({
            targets: el.querySelectorAll('.char-3d .face-bottom'),
            opacity: [1, 0],
            delay: charsStagger
        }, 0);
    };

    const existingChars = el.querySelectorAll('.char-3d');
    if (existingChars.length > 0) {
        // Animate out existing chars
        anime({
            targets: existingChars,
            rotateX: [0, -90], // Rotate to top face
            opacity: [1, 0],
            duration: 300,
            easing: 'easeInSine',
            delay: anime.stagger(30),
            complete: createAndAnimateNewText
        });
    } else {
        createAndAnimateNewText();
    }
}
