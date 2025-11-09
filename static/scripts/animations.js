// Create floating particles
document.addEventListener('DOMContentLoaded', function() {
    // Create particles container
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles';
    document.body.appendChild(particlesContainer);

    // Create particles
    function createParticles() {
        const particleCount = 50;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random size between 2px and 6px
            const size = Math.random() * 4 + 2;
            
            // Random position
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            
            // Random animation duration between 10s and 30s
            const duration = Math.random() * 20 + 10;
            
            // Random delay up to 15s
            const delay = Math.random() * 15;
            
            // Random color between cyan and magenta
            const colors = ['#0ff', '#f0f', '#0f0', '#ff0'];
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            // Apply styles
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${posX}%`;
            particle.style.top = `${posY}%`;
            particle.style.background = color;
            particle.style.boxShadow = `0 0 ${size * 2}px ${size}px ${color}`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.animationDelay = `-${delay}s`;
            
            // Add to container
            particlesContainer.appendChild(particle);
        }
    }

    // Initialize particles
    createParticles();

    // Add parallax effect to background
    document.addEventListener('mousemove', function(e) {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        
        document.querySelector('.how-it-works-section').style.backgroundPosition = 
            `${x * 50}px ${y * 50}px`;
    });

    // Add color shift animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes colorShift {
            0% {
                filter: hue-rotate(0deg);
            }
            100% {
                filter: hue-rotate(360deg);
            }
        }
    `;
    document.head.appendChild(style);
});
